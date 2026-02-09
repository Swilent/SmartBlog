from flask import Flask
from flask_cors import CORS
from config import config
import os


def create_app(config_name="development"):
    """应用工厂函数"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config.from_object(config[config_name])

    # 启用 CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}, r"/admin/*": {"origins": "*"}})

    # 初始化数据库
    from app.models import init_db

    init_db(app.config["DATABASE_PATH"])

    # 注册路由
    from app.routes import api_bp, admin_bp

    app.register_blueprint(api_bp, url_prefix="/api/v1")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # 注册访客日志中间件
    from app.utils.visitor_logger import log_visitor

    app.before_request(log_visitor)

    return app
