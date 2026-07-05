from flask import Blueprint, request, jsonify, current_app
from app.models import db, JobsRaw, StatCityDemand, StatSkillFreq, StatSalaryDist, StatEduSalary
from datetime import date
import json
import re
import requests
import logging

ai_bp = Blueprint('ai', __name__)
logger = logging.getLogger(__name__)


def _latest_stat_date():
    """Get the latest stat_date from the stat tables, fallback to today."""
    row = db.session.execute(db.text("SELECT MAX(stat_date) FROM stat_city_demand")).scalar()
    return row.isoformat() if row else _latest_stat_date()


# 30 个主要城市
CITY_PATTERN = re.compile(
    r'(北京|上海|广州|深圳|杭州|南京|成都|武汉|西安|重庆|苏州|天津|'
    r'长沙|郑州|合肥|厦门|青岛|大连|济南|宁波|东莞|佛山|无锡|昆明|'
    r'贵阳|福州|哈尔滨|沈阳|长春|太原|南昌|石家庄|南宁|兰州|呼和浩特|'
    r'海口|银川|西宁|拉萨|乌鲁木齐)'
)


def _q(sql, params=None):
    """Execute raw SQL and return list of dicts."""
    result = db.session.execute(db.text(sql), params or {})
    return [dict(row._mapping) for row in result]


def _fmt_salary(val):
    if val is None:
        return '未知'
    v = float(val)
    if v >= 10000:
        return f'{v / 10000:.1f}万/月'
    return f'{v / 1000:.1f}千/月'


def _fmt_salary_range(mn, mx):
    """Format salary min-max range."""
    mn_str = _fmt_salary(mn) if mn else '?'
    mx_str = _fmt_salary(mx) if mx else '?'
    if mn_str == mx_str:
        return mn_str
    return f'{mn_str} ~ {mx_str}'


def _build_data_context() -> str:
    """Build a compact data context summary for Dify to use — recent 3 months only."""
    today = _latest_stat_date()

    # All direct jobs_raw queries use 3-month freshness window
    FRESH_CLAUSE = "crawl_time >= DATE_SUB(NOW(), INTERVAL 3 MONTH)"

    def _q_recent(sql, params=None):
        """Insert freshness clause, handling existing WHERE correctly."""
        import re
        if 'WHERE' in sql.upper():
            # Split before ORDER/GROUP/LIMIT to close the AND-parens correctly
            m = re.search(r'\b(ORDER|GROUP|LIMIT)\b', sql, re.IGNORECASE)
            if m:
                pos = m.start()
                sql = f"{sql[:pos].replace('WHERE', f'WHERE {FRESH_CLAUSE} AND (', 1)} ) {sql[pos:]}"
            else:
                sql = sql.replace('WHERE', f'WHERE {FRESH_CLAUSE} AND (', 1) + ')'
        elif 'ORDER' in sql.upper() or 'GROUP' in sql.upper():
            sql = re.sub(r'\b(ORDER|GROUP)\b', f'WHERE {FRESH_CLAUSE} \\1', sql, 1, re.IGNORECASE)
        else:
            sql = f"{sql} WHERE {FRESH_CLAUSE}"
        return _q(sql, params)

    total = _q_recent("SELECT COUNT(*) as cnt FROM jobs_raw")[0]['cnt']
    cities = _q_recent("SELECT COUNT(DISTINCT city) as cnt FROM jobs_raw")[0]['cnt']
    companies = _q_recent("SELECT COUNT(DISTINCT company) as cnt FROM jobs_raw")[0]['cnt']

    top_cities = _q(
        "SELECT city, job_count, avg_salary FROM stat_city_demand "
        "WHERE stat_date=:d ORDER BY job_count DESC LIMIT 5", {'d': today}
    )
    top_skills = _q(
        "SELECT skill, frequency FROM stat_skill_freq "
        "WHERE stat_date=:d ORDER BY frequency DESC LIMIT 10", {'d': today}
    )
    top_jobs = _q_recent(
        "SELECT job_title, company, city, salary_max FROM jobs_raw "
        "WHERE salary_max IS NOT NULL ORDER BY salary_max DESC LIMIT 3"
    )

    # Count enterprise-type jobs from tagged column
    htech = _q_recent(
        "SELECT COUNT(*) as cnt FROM jobs_raw WHERE enterprise_type = '高新技术企业'"
    )[0]['cnt']
    xjr = _q_recent(
        "SELECT COUNT(*) as cnt FROM jobs_raw WHERE enterprise_type = '小巨人'"
    )[0]['cnt']

    ctx = f"【当前招聘数据概况 — 最近3个月】\n"
    ctx += f"总岗位数: {total}, 覆盖城市: {cities}, 招聘公司: {companies}\n"
    ctx += f"高新技术企业岗位: {htech}, 小巨人企业岗位: {xjr}\n\n"
    ctx += f"热门城市TOP5: "
    ctx += ', '.join(f"{c['city']}({c['job_count']}岗,均薪{_fmt_salary(c['avg_salary'])})" for c in top_cities)
    ctx += f"\n\n热门技能TOP10: "
    ctx += ', '.join(f"{s['skill']}({s['frequency']})" for s in top_skills)
    ctx += f"\n\n薪资最高岗位TOP3: "
    ctx += '; '.join(f"{j['job_title']}@{j['company']}({j['city']}){_fmt_salary(j['salary_max'])}" for j in top_jobs)
    return ctx


def answer_question(question: str) -> str:
    """
    Parse the question and answer from structured data.
    Handles COMBINED queries (e.g., "广州薪资最高的岗位") by extracting
    ALL intents and building appropriate SQL.
    Returns (answer, is_default) — is_default=True means no good match found.
    """
    q = question.strip()
    today = _latest_stat_date()

    # ── Extract all dimensions from the question ──
    city = None
    city_match = CITY_PATTERN.search(q)
    if city_match:
        city = city_match.group(1)

    # Intent detection
    wants_highest = any(kw in q for kw in [
        '最高', '最多', 'top', '最好', '高薪', '最高薪', '薪资最高',
        '工资最高', '待遇最好', '薪酬最高', '薪资高', '工资高',
    ])
    wants_distribution = any(kw in q for kw in ['分布', '区间', '占比', '比例'])
    wants_skills = any(kw in q for kw in [
        '技能', '技术', '语言', '框架', '工具', '会什么', '学什么',
        '需要什么', '要求会', '掌握', '能力',
    ])
    wants_education = any(kw in q for kw in [
        '学历', '本科', '大专', '硕士', '博士', '研究生', '教育',
    ])
    wants_experience = any(kw in q for kw in ['经验', '年限', '应届', '实习'])
    wants_company = any(kw in q for kw in ['公司', '企业', '招聘方', '招人', '雇主'])
    wants_overview = any(kw in q for kw in [
        '多少', '总数', '数量', '统计', '概况', '总览', '整体', '目前',
        '数据量', '一共',
    ])
    wants_salary = any(kw in q for kw in [
        '薪资', '工资', '收入', '待遇', '薪水', '多少钱', '薪酬', '月薪',
    ])
    wants_jobs = any(kw in q for kw in [
        '岗位', '职位', '工作', '推荐', '找工作', '求职', '招聘',
    ])

    # ── Build WHERE clause fragments ──
    wheres = []
    params = {}
    if city:
        wheres.append("city LIKE :city")
        params['city'] = f'%{city}%'

    # ── COMBINED QUERIES (checked first, before single-dimension branches) ──

    # Pattern A: City + Highest Salary → top jobs in that city
    if city and wants_highest:
        where_clause = "WHERE " + " AND ".join(wheres) + " AND salary_max IS NOT NULL"
        rows = _q(
            f"SELECT job_title, company, city, salary_max, salary_raw FROM jobs_raw "
            f"{where_clause} ORDER BY salary_max DESC LIMIT 5",
            params,
        )
        if rows:
            lines = [f'{i+1}. {r["job_title"]} — {r["company"]} — {_fmt_salary(r["salary_max"])}'
                     for i, r in enumerate(rows)]
            return f'{city}薪资最高的岗位 TOP5：\n' + '\n'.join(lines)
        return f'抱歉，暂时没有找到 {city} 有明确薪资数据的岗位。'

    # Pattern B: City + Skills → what skills are in demand in this city
    if city and wants_skills:
        rows = _q(
            "SELECT skill, frequency FROM stat_skill_freq "
            "WHERE stat_date=:d ORDER BY frequency DESC LIMIT 10",
            {'d': today},
        )
        # Also get city-specific top jobs to show skill context
        city_jobs = _q(
            "SELECT job_title, skills FROM jobs_raw "
            "WHERE city LIKE :c AND skills IS NOT NULL AND skills != '[]' LIMIT 5",
            {'c': f'%{city}%'},
        )
        lines = [f'{i+1}. {r["skill"]}（{r["frequency"]} 个岗位要求）' for i, r in enumerate(rows[:10])]
        answer = f'{city}当前最热门的技能：\n' + '\n'.join(lines)
        if city_jobs:
            answer += '\n\n举例（该城市岗位技能要求）：'
            for j in city_jobs[:3]:
                try:
                    import json
                    sk = json.loads(j['skills'])
                    sk_str = '、'.join(sk[:5]) if sk else '未标注'
                except Exception:
                    sk_str = j['skills'] or '未标注'
                answer += f'\n  · {j["job_title"]}：{sk_str}'
        return answer

    # Pattern C: City + Education → education-salary in that city
    if city and wants_education:
        rows = _q(
            "SELECT education, COUNT(*) as cnt, AVG(salary_max) as avg_salary "
            "FROM jobs_raw WHERE city LIKE :c AND education IS NOT NULL AND education != '' "
            "GROUP BY education ORDER BY avg_salary DESC",
            {'c': f'%{city}%'},
        )
        if rows:
            lines = [f'  {r["education"]}: {r["cnt"]}个岗位, 平均薪资 {_fmt_salary(r["avg_salary"])}'
                     for r in rows]
            return f'{city}各学历岗位与薪资：\n' + '\n'.join(lines)
        return f'{city}暂无学历相关统计数据。'

    # Pattern D: City + Experience
    if city and wants_experience:
        rows = _q(
            "SELECT experience, COUNT(*) as cnt FROM jobs_raw "
            "WHERE city LIKE :c AND experience IS NOT NULL AND experience != '' "
            "GROUP BY experience ORDER BY cnt DESC LIMIT 8",
            {'c': f'%{city}%'},
        )
        if rows:
            lines = [f'  {r["experience"]}: {r["cnt"]}个岗位' for r in rows]
            return f'{city}经验要求分布：\n' + '\n'.join(lines)
        return f'{city}暂无经验要求统计数据。'

    # Pattern E: City + Company
    if city and wants_company:
        rows = _q(
            "SELECT company, COUNT(*) as cnt FROM jobs_raw "
            "WHERE city LIKE :c GROUP BY company ORDER BY cnt DESC LIMIT 10",
            {'c': f'%{city}%'},
        )
        if rows:
            lines = [f'{i+1}. {r["company"]}（{r["cnt"]}个岗位）' for i, r in enumerate(rows)]
            return f'{city}招聘岗位最多的公司 TOP10：\n' + '\n'.join(lines)
        return f'{city}暂无公司招聘数据。'

    # Pattern F: City + Overview (just city, no specific intent)
    if city and not any([wants_highest, wants_skills, wants_education,
                         wants_experience, wants_company, wants_distribution]):
        rows = _q(
            "SELECT COUNT(*) as cnt, AVG(salary_min) as avg_min, "
            "AVG(salary_max) as avg_max, MIN(salary_min) as min_s, "
            "MAX(salary_max) as max_s "
            "FROM jobs_raw WHERE city LIKE :c",
            {'c': f'%{city}%'},
        )
        if rows and rows[0]['cnt'] > 0:
            r = rows[0]
            skills = _q(
                "SELECT skill, frequency FROM stat_skill_freq "
                "WHERE stat_date=:d ORDER BY frequency DESC LIMIT 5",
                {'d': today},
            )
            answer = (
                f'{city}目前有 {r["cnt"]} 个岗位在招。\n'
                f'平均薪资范围：{_fmt_salary(r["avg_min"])} ~ {_fmt_salary(r["avg_max"])}。\n'
                f'最低薪资：{_fmt_salary(r["min_s"])}，最高薪资：{_fmt_salary(r["max_s"])}。'
            )
            if skills:
                skill_list = '、'.join(s['skill'] for s in skills)
                answer += f'\n当前最热门的技能是：{skill_list}。'
            return answer
        return f'抱歉，暂时没有找到 {city} 的岗位数据。'

    # ── SINGLE-DIMENSION QUERIES ──

    # Highest salary (no city filter)
    if wants_highest:
        rows = _q(
            "SELECT job_title, company, city, salary_max, salary_raw FROM jobs_raw "
            "WHERE salary_max IS NOT NULL ORDER BY salary_max DESC LIMIT 5"
        )
        lines = [
            f'{i+1}. {r["job_title"]}（{r["company"]}，{r["city"]}）— {_fmt_salary(r["salary_max"])}'
            for i, r in enumerate(rows)
        ]
        return '全国薪资最高的岗位 TOP5：\n' + '\n'.join(lines)

    # Salary distribution
    if wants_distribution or (wants_salary and not wants_highest):
        rows = _q(
            "SELECT salary_range, job_count, percentage FROM stat_salary_dist "
            "WHERE stat_date=:d ORDER BY range_min", {'d': today}
        )
        if rows:
            lines = [f'  {r["salary_range"]}: {r["job_count"]} 个岗位（{r["percentage"]}%）' for r in rows]
            return '薪资分布情况：\n' + '\n'.join(lines)

    # Overall salary
    if wants_salary:
        rows = _q(
            "SELECT AVG(salary_min) as avg_min, AVG(salary_max) as avg_max, "
            "MIN(salary_min) as min_s, MAX(salary_max) as max_s "
            "FROM jobs_raw WHERE salary_min IS NOT NULL"
        )
        r = rows[0]
        return (
            f'整体薪资情况：\n'
            f'平均薪资范围：{_fmt_salary(r["avg_min"])} ~ {_fmt_salary(r["avg_max"])}\n'
            f'最低薪资：{_fmt_salary(r["min_s"])}\n'
            f'最高薪资：{_fmt_salary(r["max_s"])}'
        )

    # Skills
    if wants_skills:
        rows = _q(
            "SELECT skill, frequency FROM stat_skill_freq "
            "WHERE stat_date=:d ORDER BY frequency DESC LIMIT 15", {'d': today}
        )
        lines = [f'{i+1}. {r["skill"]}（{r["frequency"]} 个岗位要求）' for i, r in enumerate(rows)]
        return '当前最热门的技能 TOP15：\n' + '\n'.join(lines)

    # Education + Salary
    if wants_education:
        rows = _q(
            "SELECT education, avg_salary, job_count FROM stat_edu_salary "
            "WHERE stat_date=:d ORDER BY avg_salary DESC", {'d': today}
        )
        lines = [
            f'  {r["education"] or "不限"}: 平均薪资 {_fmt_salary(r["avg_salary"])}，{r["job_count"]} 个岗位'
            for r in rows
        ]
        return '学历与薪资关系：\n' + '\n'.join(lines)

    # Experience
    if wants_experience:
        rows = _q(
            "SELECT experience, COUNT(*) as cnt FROM jobs_raw "
            "WHERE experience IS NOT NULL AND experience != '' "
            "GROUP BY experience ORDER BY cnt DESC LIMIT 8"
        )
        lines = [f'  {r["experience"]}: {r["cnt"]} 个岗位' for r in rows]
        return '经验要求分布：\n' + '\n'.join(lines)

    # Companies
    if wants_company:
        rows = _q(
            "SELECT company, COUNT(*) as cnt FROM jobs_raw "
            "GROUP BY company ORDER BY cnt DESC LIMIT 10"
        )
        lines = [f'{i+1}. {r["company"]}（{r["cnt"]} 个岗位）' for i, r in enumerate(rows)]
        return '招聘岗位最多的公司 TOP10：\n' + '\n'.join(lines)

    # Overview / count
    if wants_overview:
        total = _q("SELECT COUNT(*) as cnt FROM jobs_raw")[0]['cnt']
        cities_cnt = _q("SELECT COUNT(DISTINCT city) as cnt FROM jobs_raw")[0]['cnt']
        companies_cnt = _q("SELECT COUNT(DISTINCT company) as cnt FROM jobs_raw")[0]['cnt']
        skills_cnt = _q(
            "SELECT COUNT(*) as cnt FROM stat_skill_freq WHERE stat_date=:d", {'d': today}
        )[0]['cnt']
        return (
            f'数据概况：\n'
            f'  岗位总数：{total} 个\n'
            f'  覆盖城市：{cities_cnt} 个\n'
            f'  招聘公司：{companies_cnt} 家\n'
            f'  涉及技能：{skills_cnt} 种'
        )

    # Job recommendations
    if wants_jobs:
        rows = _q(
            "SELECT job_title, company, city, salary_raw, salary_max FROM jobs_raw "
            "ORDER BY salary_max DESC LIMIT 5"
        )
        lines = [
            f'{i+1}. {r["job_title"]}（{r["company"]}，{r["city"]}）— '
            f'{r["salary_raw"] or _fmt_salary(r["salary_max"])}'
            for i, r in enumerate(rows)
        ]
        return '为您推荐薪资最高的岗位：\n' + '\n'.join(lines)

    # ── No match ──
    return (
        '我可以回答以下关于招聘数据的问题：\n'
        '  - 某个城市有多少岗位？（如"上海有多少岗位"）\n'
        '  - 某个城市薪资最高的岗位？（如"广州薪资最高的岗位是什么"）\n'
        '  - 薪资情况如何？（如"薪资分布"、"最高工资"）\n'
        '  - 需要什么技能？（如"热门技能"、"需要会什么"）\n'
        '  - 学历要求？（如"本科薪资多少"）\n'
        '  - 经验要求？（如"需要几年经验"）\n'
        '  - 招聘公司？（如"哪些公司在招人"）\n'
        '  - 数据概况？（如"总共有多少数据"）'
    )


def _is_default_answer(reply: str) -> bool:
    """Check if the answer is the default help text (no data match)."""
    return reply.startswith('我可以回答以下关于招聘数据的问题')


def call_dify(query: str, user_id: str = 'anonymous', conversation_id: str = None) -> dict:
    """Call Dify chat API via streaming (required for agent-chat mode).
    Returns dict with reply and conversation_id."""
    api_url = current_app.config['DIFY_API_URL'].rstrip('/')
    api_key = current_app.config['DIFY_API_KEY']

    if not api_key:
        raise ValueError("DIFY_API_KEY not configured")

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }

    # Build data context so Dify has actual stats to work with
    data_context = ''
    try:
        data_context = _build_data_context()
    except Exception:
        pass

    # Inject data context directly into query so the agent reads it as reference
    if data_context:
        query = f"{query}\n\n{data_context}\n\n请基于以上数据直接回答用户问题。"

    body = {
        'query': query,
        'user': user_id,
        'response_mode': 'streaming',
        'inputs': {},
    }
    if conversation_id:
        body['conversation_id'] = conversation_id

    resp = requests.post(
        f'{api_url}/v1/chat-messages',
        headers=headers,
        json=body,
        stream=True,
        timeout=current_app.config.get('DIFY_API_TIMEOUT', 60),
    )
    resp.raise_for_status()

    # Parse SSE stream: collect agent_message answers and conversation_id
    answer_parts = []
    new_conversation_id = conversation_id

    for line in resp.iter_lines(decode_unicode=True):
        if not line or not line.startswith('data: '):
            continue
        try:
            event = json.loads(line[6:])
        except json.JSONDecodeError:
            continue

        if event.get('conversation_id'):
            new_conversation_id = event['conversation_id']
        if event.get('event') == 'agent_message' and event.get('answer'):
            answer_parts.append(event['answer'])
        elif event.get('event') == 'message' and event.get('answer'):
            answer_parts.append(event['answer'])

    return {
        'reply': ''.join(answer_parts),
        'conversation_id': new_conversation_id,
    }


@ai_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json(force=True)
    message = data.get('message', '').strip()
    if not message:
        return jsonify(reply='请输入您的问题。'), 400

    conversation_id = data.get('conversation_id')

    # Strategy: Dify first (AI agent with data context), keyword fallback on failure.
    try:
        dify_result = call_dify(message, user_id='web-user', conversation_id=conversation_id)
        return jsonify({
            'reply': dify_result['reply'],
            'conversation_id': dify_result['conversation_id'],
            'source': 'dify',
        })
    except Exception as e:
        logger.warning(f"Dify unavailable, falling back to keyword: {e}")

    # Fallback: try structured keyword matching when Dify is down
    try:
        keyword_reply = answer_question(message)
        return jsonify({'reply': keyword_reply, 'source': 'keyword'})
    except Exception:
        return jsonify(reply='抱歉，处理问题时出错，请稍后重试。'), 500


@ai_bp.route('/dify-health', methods=['GET'])
def dify_health():
    """Check if Dify API is reachable and configured."""
    api_key = current_app.config.get('DIFY_API_KEY', '')
    api_url = current_app.config.get('DIFY_API_URL', '')

    if not api_key:
        return jsonify(status='unconfigured', message='DIFY_API_KEY not set')

    try:
        resp = requests.post(
            f'{api_url.rstrip("/")}/v1/chat-messages',
            headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
            json={'query': 'hi', 'user': 'healthcheck', 'response_mode': 'blocking'},
            timeout=10,
        )
        if resp.status_code == 200:
            return jsonify(status='healthy', source='dify')
        return jsonify(status='error', source='dify', http_code=resp.status_code)
    except Exception as e:
        return jsonify(status='unreachable', source='dify', error=str(e))
