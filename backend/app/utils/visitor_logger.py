from flask import request, current_app
from app.models import log_visit


def log_visitor():
    """
    Flask before_request 钩子，记录访客访问
    只记录 /api 开头的请求和首页访问
    """
    # 跳过管理后台的请求
    if request.path.startswith("/admin"):
        return

    # 跳过静态文件
    if request.path.startswith("/static"):
        return

    # 只记录页面访问
    if request.path in ["/", "/articles", "/about"] or request.path.startswith("/api"):
        db_path = current_app.config["DATABASE_PATH"]
        log_visit(db_path, request.remote_addr, request.path)
