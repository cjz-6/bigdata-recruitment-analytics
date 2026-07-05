from flask import Blueprint, jsonify, request
import subprocess
import json

analysis_bp = Blueprint('analysis', __name__)


@analysis_bp.route('/trigger', methods=['POST'])
def trigger_analysis():
    """触发 PySpark 分析任务"""
    analysis_type = request.json.get('type', 'all')
    try:
        result = subprocess.run(
            ['spark-submit', '--master', 'spark://spark-master:7077',
             f'/opt/spark-jobs/analysis/{analysis_type}_analysis.py'],
            capture_output=True, text=True, timeout=300
        )
        return jsonify(
            status='success' if result.returncode == 0 else 'error',
            stdout=result.stdout,
            stderr=result.stderr
        )
    except subprocess.TimeoutExpired:
        return jsonify(status='error', message='Analysis task timed out'), 504
    except Exception as e:
        return jsonify(status='error', message=str(e)), 500


@analysis_bp.route('/status', methods=['GET'])
def analysis_status():
    return jsonify(
        status='ready',
        available_tasks=['city_demand', 'skill_freq', 'salary_dist', 'edu_salary']
    )
