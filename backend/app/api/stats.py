from flask import Blueprint, request, jsonify
from app.models import StatCityDemand, StatSkillFreq, StatSalaryDist, StatEduSalary
from app.main import db
from datetime import date

stats_bp = Blueprint('stats', __name__)


def _latest_date(model):
    """Get the latest stat_date from a stat table, fallback to today."""
    row = db.session.query(db.func.max(model.stat_date)).scalar()
    return row.isoformat() if row else date.today().isoformat()


@stats_bp.route('/city-demand', methods=['GET'])
def city_demand():
    stat_date = request.args.get('date', _latest_date(StatCityDemand))
    results = StatCityDemand.query.filter_by(stat_date=stat_date) \
        .order_by(StatCityDemand.job_count.desc()).all()
    return jsonify([{
        'city': r.city,
        'job_count': r.job_count,
        'avg_salary': float(r.avg_salary) if r.avg_salary else None,
    } for r in results])


@stats_bp.route('/skill-freq', methods=['GET'])
def skill_freq():
    stat_date = request.args.get('date', _latest_date(StatSkillFreq))
    limit = request.args.get('limit', 20, type=int)
    results = StatSkillFreq.query.filter_by(stat_date=stat_date) \
        .order_by(StatSkillFreq.frequency.desc()).limit(limit).all()
    return jsonify([{
        'skill': r.skill,
        'frequency': r.frequency,
        'percentage': float(r.percentage) if r.percentage else None,
    } for r in results])


@stats_bp.route('/salary-dist', methods=['GET'])
def salary_dist():
    stat_date = request.args.get('date', _latest_date(StatSalaryDist))
    results = StatSalaryDist.query.filter_by(stat_date=stat_date) \
        .order_by(StatSalaryDist.range_min).all()
    return jsonify([{
        'salary_range': r.salary_range,
        'range_min': float(r.range_min),
        'range_max': float(r.range_max),
        'job_count': r.job_count,
        'percentage': float(r.percentage) if r.percentage else None,
    } for r in results])


@stats_bp.route('/edu-salary', methods=['GET'])
def edu_salary():
    stat_date = request.args.get('date', _latest_date(StatEduSalary))
    results = StatEduSalary.query.filter_by(stat_date=stat_date) \
        .order_by(StatEduSalary.avg_salary.desc()).all()
    return jsonify([{
        'education': r.education,
        'avg_salary': float(r.avg_salary) if r.avg_salary else None,
        'min_salary': float(r.min_salary) if r.min_salary else None,
        'max_salary': float(r.max_salary) if r.max_salary else None,
        'job_count': r.job_count,
    } for r in results])
