# 招聘岗位需求分析系统

基于 **Hadoop + Spark + Dify AI** 的招聘市场大数据分析平台。集成 Scrapy 爬虫、分布式数据处理、AI 智能问答、前端可视化，完整覆盖「采集 → 存储 → 分析 → 展示 → AI 问答」全链路。

---

## 系统架构

```
                               用户浏览器
                    http://localhost:3000 (Vue 前端)
                                   │
                                   ▼
    ┌──────────────────────────────────────────────────────────────┐
    │  frontend (Nginx :80 托管 Vue SPA)                           │
    │  └─ /api/* → 反向代理到 backend:5000                          │
    └──────────────────────────┬───────────────────────────────────┘
                               │
                               ▼
    ┌──────────────────────────────────────────────────────────────┐
    │  backend (Flask :5000, Gunicorn 4 workers)                   │
    │  ├─ /api/jobs/*      岗位 CRUD + 搜索 + 自动补全               │
    │  ├─ /api/stats/*     城市需求/技能频率/薪资分布/学历薪资         │
    │  ├─ /api/analysis/*  触发 Spark 分析任务                       │
    │  └─ /api/ai/*        AI 聊天（Dify 主、规则回退）               │
    └──────┬──────────────┬──────────────┬─────────────────────────┘
           │              │              │
           ▼              ▼              ▼
    ┌──────────┐ ┌──────────────┐ ┌────────────────────────────┐
    │  MySQL   │ │ Spark 集群    │ │  Dify AI 平台 (:8080)       │
    │  :3306   │ │ Master :7077 │ │  api / web / worker        │
    │  业务数据 │ │ Worker :8081 │ │  postgres / redis / weaviate│
    └──────────┘ └──────┬───────┘ └────────────────────────────┘
                        │
                        ▼
    ┌──────────────────────────────────────────────────────────────┐
    │              Hadoop 集群 (HDFS + YARN, 6 节点)                 │
    │  namenode :9870  │  datanode1/2  │  resourcemanager :8088   │
    └──────────────────────────────────────────────────────────────┘

    ┌──────────────────────────────────────────────────────────────┐
    │          数据采集层：Scrapy + Playwright → 爬取 51job.com       │
    └──────────────────────────────────────────────────────────────┘
```

**数据流向：**

```
51job.com → Scrapy/Playwright → MySQL (jobs_raw)
    → Spark JDBC 读取 → PySpark 分析（城市需求/技能频率/薪资分布/学历薪资）
    → Flask REST API → Vue ECharts 可视化 + Dify AI 自然语言问答
```

---

## 功能特性

- **自动数据采集**：Scrapy + Playwright 无头浏览器，爬取前程无忧招聘数据，覆盖 10 个技术方向 + 3 种企业类型
- **分布式存储**：Hadoop HDFS 三节点集群，数据块双副本
- **分布式计算**：Apache Spark 集群计算，4 个分析维度（城市需求、技能频率、薪资分布、学历薪资）
- **可视化仪表盘**：Vue 3 + ECharts 图表展示
- **AI 智能问答**：集成 Dify 平台，支持自然语言查询（如"深圳 Python 岗位的平均薪资是多少？"）
- **Docker 一键部署**：20 个容器，Docker Compose 三层编排

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 数据采集 | Scrapy 2.11, Playwright (Chromium) |
| 分布式存储 | Hadoop 3.4.2 (HDFS + YARN) |
| 分布式计算 | Apache Spark 3.5.3 (PySpark) |
| 关系型数据库 | MySQL 8.0 |
| 后端 API | Python Flask + Gunicorn |
| 前端 | Vue 3 + Vite + ECharts + Axios |
| AI 平台 | Dify 0.15.3 + Weaviate 向量数据库 + PostgreSQL + Redis |
| 反向代理 | Nginx |
| 容器化 | Docker + Docker Compose (20 个容器) |

---

## 环境要求

| 项目 | 最低配置 | 推荐配置 |
|------|---------|---------|
| CPU | 4 核 | 8 核+ |
| 内存 | 8 GB | 16 GB+ |
| 磁盘 | 20 GB | 50 GB+ |
| 软件 | Docker 20.10+, Docker Compose 2.0+, Python 3.9+ |

---

## 配置说明（重要）

**克隆项目后，你必须替换以下文件中的默认密码/密钥，否则服务无法正常启动或存在安全风险。**

### 需要替换的文件清单

| 文件 | 需替换的内容 | 备注 |
|------|-------------|------|
| `.env` | 所有密码和密钥 | 从 `.env.example` 复制后，替换全部 `your_xxx` 占位符 |
| `docker-compose.services.yml` | MySQL / Dify 密码默认值 | 已用 `请替换为你的xxx密码` 占位，如果你已在 `.env` 中设置了环境变量，则无需修改此文件 |
| `spark/analysis.py` | MySQL 密码 | 第 20 行附近：`请替换为你的MySQL密码` |
| `crawler/crawler/settings.py` | MySQL 密码 | 第 48 行附近：`请替换为你的MySQL密码` |
| `crawler/crawler/pipelines.py` | MySQL 密码默认值 | 第 22 行附近：`请替换为你的MySQL密码` |
| `backend/app/main.py` | MySQL 密码默认值 | 第 15 行附近：`请替换为你的MySQL密码` |
| `spark-jobs/analysis/salary_dist_analysis.py` | MySQL 密码默认值 | 第 12 行附近：`请替换为你的MySQL密码` |
| `spark-jobs/analysis/city_demand_analysis.py` | MySQL 密码默认值 | 第 13 行附近：`请替换为你的MySQL密码` |
| `spark-jobs/analysis/skill_freq_analysis.py` | MySQL 密码默认值 | 第 13 行附近：`请替换为你的MySQL密码` |
| `spark-jobs/analysis/edu_salary_analysis.py` | MySQL 密码默认值 | 第 12 行附近：`请替换为你的MySQL密码` |
| `scripts/start.sh` | MySQL root 密码 | 第 35 行附近 |
| `scripts/cleanup_old_data.sh` | MySQL 用户密码 | 第 14 行附近 |

### 配置步骤

**第 1 步 — 配置 .env（推荐）**

```bash
cp .env.example .env
vim .env   # 将所有 your_xxx 替换为你的真实密码和密钥
```

设置 `.env` 后，大部分密码会通过 Docker Compose 的 `${VAR}` 语法自动注入，覆盖各文件的硬编码默认值。但为确保安全，**仍然建议将所有 `请替换为你的xxx密码` 占位符替换为你的真实密码**。

**第 2 步 — 搜索并替换剩余占位符**

```bash
# 在项目根目录执行，搜索所有尚未替换的占位符
grep -rn "请替换为" --include="*.py" --include="*.sh" --include="*.yml" .
```

**第 3 步 — 验证没有遗漏**

```bash
# 确保没有硬编码的真实密码残留（仅供自查）
grep -rn "请替换为你的MySQL密码\|请替换为你的Dify数据库密码\|请替换为你的Dify_Redis密码\|sk-bigdata-dify" --include="*.py" --include="*.sh" --include="*.yml" .
# 该命令应返回空结果（如果你是从 GitHub 克隆的，应该已经清理干净）
```

### .env 需要配置的变量

| 变量 | 说明 |
|------|------|
| `MYSQL_ROOT_PASSWORD` | MySQL root 密码 |
| `MYSQL_PASSWORD` | MySQL 业务用户密码 |
| `DIFY_SECRET_KEY` | Dify 平台加密密钥 |
| `DIFY_DB_PASSWORD` | Dify PostgreSQL 数据库密码 |
| `DIFY_REDIS_PASSWORD` | Dify Redis 密码 |
| `DIFY_API_KEY` | Dify 应用的 API Key（在 Dify 控制台创建应用后获取） |
| `DIFY_CONSOLE_WEB_URL` 等 | Dify 服务端点 IP/域名（按你的实际部署地址填写） |

---

## 快速开始

### 1. 克隆项目

```bash
git clone git@github.com:cjz-6/bigdata-recruitment-analytics.git
cd bigdata-recruitment-analytics
# 请先完成上方「配置说明」中的步骤，否则服务无法正常启动！
```

### 2. 启动服务

```bash
# 一键启动全部 20 个容器
bash scripts/start.sh all

# 或分步启动（推荐首次部署，方便定位问题）
bash scripts/start.sh hadoop     # 第1步：Hadoop 集群
bash scripts/start.sh services   # 第2步：MySQL + Spark + 后端 + 前端
bash scripts/start.sh dify       # 第3步：Dify AI 平台
```

### 3. 运行数据采集

```bash
pip install scrapy scrapy-playwright pymysql
python -m playwright install chromium
cd crawler && scrapy crawl boss
```

### 4. 运行数据分析

```bash
# 通过 API 触发
curl -X POST http://localhost:5000/api/analysis/trigger \
  -H "Content-Type: application/json" \
  -d '{"type": "all"}'

# 或直接进入 Spark 容器
docker exec -it cjz-spark-master bash
spark-submit --master spark://spark-master:7077 /opt/spark-jobs/analysis/city_demand_analysis.py
```

### 5. 停止服务

```bash
bash scripts/stop.sh
```

---

## 服务访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| Vue 前端 | http://localhost:3000 | 数据可视化仪表盘 |
| Flask API | http://localhost:5000/api/health | 后端 REST API |
| Dify 控制台 | http://localhost:8080 | AI 智能体管理后台 |
| HDFS NameNode | http://localhost:9870 | HDFS 文件系统 Web UI |
| YARN RM | http://localhost:8088 | YARN 集群资源管理 |
| Spark Master | http://localhost:8082 | Spark 集群管理 |

---

## 项目结构

```
bigdata-recruitment-analytics/
├── docker-compose.base.yml       # 网络 + 数据卷
├── docker-compose.hadoop.yml     # Hadoop 集群 (6 容器)
├── docker-compose.services.yml   # MySQL/Spark/Flask/Vue/Dify (14 容器)
├── .env.example                  # 环境变量模板
│
├── hadoop/                       # Hadoop 集群
│   ├── Dockerfile                #   openEuler + JDK 11 + Hadoop 3.4.2
│   ├── entrypoint.sh
│   └── config/                   #   core-site.xml, hdfs-site.xml, yarn-site.xml ...
│
├── spark/                        # Spark 集群
│   ├── Dockerfile                #   apache/spark:3.5.3 + PySpark + MySQL 驱动
│   └── entrypoint.sh
│
├── spark-jobs/analysis/          # PySpark 分析任务
│   ├── city_demand_analysis.py   #   城市需求统计
│   ├── skill_freq_analysis.py    #   技能频率统计
│   ├── salary_dist_analysis.py   #   薪资分布统计
│   └── edu_salary_analysis.py    #   学历薪资统计
│
├── backend/                      # Flask 后端
│   ├── app/
│   │   ├── main.py               #   应用工厂
│   │   ├── models.py             #   SQLAlchemy 模型 (5 张表)
│   │   └── api/                  #   jobs, stats, analysis, ai
│   └── requirements.txt
│
├── frontend/                     # Vue 3 前端
│   └── src/views/                #   Dashboard, Jobs, AIChat
│
├── crawler/                      # Scrapy 爬虫
│   └── crawler/spiders/          #   51job 爬虫
│
├── nginx/                        # Nginx 配置
├── scripts/                      # 运维脚本 (start/stop/crawl/analyze)
└── data/                         # 数据持久化目录 (gitignore)
```

---

## 数据库表结构

| 表名 | 用途 | 关键字段 |
|------|------|---------|
| `jobs_raw` | 爬虫原始数据 | job_title, company, city, salary_min/max, skills, education |
| `stat_city_demand` | 城市需求统计 | city, job_count, avg_salary |
| `stat_skill_freq` | 技能频率统计 | skill, frequency, percentage |
| `stat_salary_dist` | 薪资分布统计 | salary_range, job_count, percentage |
| `stat_edu_salary` | 学历薪资统计 | education, avg_salary, job_count |

---

## 常见问题

**NameNode 启动后退出**: 删除 `./data/namenode/name/current` 后重启。

**DataNode 无法连接 NameNode**: 等 NameNode 完全启动（约 30 秒），再检查 `docker logs cjz-datanode1`。

**Spark 无法连接 HDFS**: 已通过挂载 `core-site.xml` 和 `hdfs-site.xml` 到 Spark 容器解决。

**MySQL 连接被拒**: 检查 `docker ps | grep mysql`，等待 `healthy` 状态。

**Dify 初始化报错**: 检查 `docker logs cjz-dify-api | grep -i migrate`，确保 PostgreSQL 和 Redis 已 healthy。

**磁盘空间不足**: `docker system prune -a` 清理未使用的镜像和容器。

---

## 许可证

MIT License

---

## 作者

陈坚卓 @ 广东梅州职业技术学院

GitHub: [@cjz-6](https://github.com/cjz-6)
