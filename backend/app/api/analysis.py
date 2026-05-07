from flask import Blueprint, jsonify, request
import subprocess


ANALYSIS_TASKS = ['city_demand', 'skill_freq', 'salary_dist', 'edu_salary']

analysis_bp = Blueprint('analysis', __name__)


def _run_task(task_type):
    return subprocess.run(
        ['spark-submit', '--master', 'spark://spark-master:7077',
         f'/opt/spark-jobs/analysis/{task_type}_analysis.py'],
        capture_output=True, text=True, timeout=300
    )


@analysis_bp.route('/trigger', methods=['POST'])
def trigger_analysis():
    analysis_type = request.json.get('type', 'all') if request.json else 'all'
    tasks = ANALYSIS_TASKS if analysis_type == 'all' else [analysis_type]

    results = {}
    for task in tasks:
        if task not in ANALYSIS_TASKS:
            results[task] = {'status': 'error', 'message': f'Unknown task: {task}'}
            continue
        try:
            r = _run_task(task)
            results[task] = {
                'status': 'success' if r.returncode == 0 else 'error',
                'stdout': r.stdout,
                'stderr': r.stderr,
            }
        except subprocess.TimeoutExpired:
            results[task] = {'status': 'error', 'message': 'Task timed out'}
        except Exception as e:
            results[task] = {'status': 'error', 'message': str(e)}

    return jsonify(results=results)


@analysis_bp.route('/status', methods=['GET'])
def analysis_status():
    return jsonify(
        status='ready',
        available_tasks=ANALYSIS_TASKS
    )
