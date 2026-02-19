from flask import request, current_app
from app.models import log_visit


def log_visitor():
    """
    Flask before_request 钩子，记录访客访问

    注意：这是旧的后端中间件记录方式。
    新的访客记录机制：前端通过 /api/v1/visitor/track API 主动上报访问路径。

    保留此中间件是为了兼容直接访问后端根路径的情况。
    """
    # 检查是否启用了访客日志功能
    if not current_app.config.get("LOG_VISITOR_ACCESS", True):
        return

    # 跳过管理后台的请求
    if request.path.startswith("/admin"):
        return

    # 跳过静态文件
    if request.path.startswith("/static"):
        return

    # 跳过 CORS 预检请求
    if request.method == "OPTIONS":
        return

    # 跳过 API 请求（由前端主动调用访客记录 API）
    if request.path.startswith("/api"):
        return

    # 只记录非 API、非静态资源的直接请求
    log_visitor_paths = current_app.config.get("LOG_VISITOR_PATHS", [])
    if request.path in log_visitor_paths:
        db_path = current_app.config["DATABASE_PATH"]
        log_visit(db_path, request.remote_addr, request.path)
