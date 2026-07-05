from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus
import os

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # 数据库配置（密码需要 URL 编码以处理特殊字符如 @）
    db_user = os.getenv('MYSQL_USER', 'bigdata')
    db_pass = quote_plus(os.getenv('MYSQL_PASSWORD', '请替换为你的MySQL密码'))
    db_host = os.getenv('MYSQL_HOST', 'mysql')
    db_port = os.getenv('MYSQL_PORT', '3306')
    db_name = os.getenv('MYSQL_DATABASE', 'job_analysis')
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    CORS(app)
    db.init_app(app)

    # Dify AI 配置
    app.config['DIFY_API_KEY'] = os.getenv('DIFY_API_KEY', '')
    app.config['DIFY_API_URL'] = os.getenv('DIFY_API_URL', 'http://dify-proxy:80')
    app.config['DIFY_API_TIMEOUT'] = int(os.getenv('DIFY_API_TIMEOUT', '60'))

    # 注册蓝图
    from app.api.jobs import jobs_bp
    from app.api.stats import stats_bp
    from app.api.analysis import analysis_bp
    from app.api.ai import ai_bp

    app.register_blueprint(jobs_bp, url_prefix='/api/jobs')
    app.register_blueprint(stats_bp, url_prefix='/api/stats')
    app.register_blueprint(analysis_bp, url_prefix='/api/analysis')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')

    @app.route('/api/health')
    def health():
        return jsonify(status='ok', message='Job Analysis API is running')

    return app


app = create_app()
