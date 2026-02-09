from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    session,
    redirect,
    url_for,
    current_app,
)
from functools import wraps
from app.models import get_all_posts, get_post, update_post, delete_post
from app.models import (
    create_post,
    create_chunks,
    delete_chunks_by_post,
    get_chunks_by_post,
    get_visits,
)
from app.services.embedding_service import (
    update_post_embeddings,
    delete_post_embeddings,
)
from app.utils.auth import verify_ip, verify_credentials
import traceback

admin_bp = Blueprint("admin", __name__)


def require_admin(f):
    """管理员权限验证装饰器"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 验证 IP 白名单
        if not verify_ip(request.remote_addr, current_app.config["ADMIN_IP_WHITELIST"]):
            return jsonify({"error": "访问被拒绝：IP 不在白名单中"}), 403

        # 验证登录状态
        if not session.get("logged_in"):
            if request.is_json:
                return jsonify({"error": "需要登录"}), 401
            return redirect(url_for("admin.login"))

        return f(*args, **kwargs)

    return decorated_function


@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    """管理员登录页面"""
    # 验证 IP 白名单
    if not verify_ip(request.remote_addr, current_app.config["ADMIN_IP_WHITELIST"]):
        return jsonify({"error": "访问被拒绝：IP 不在白名单中"}), 403

    if request.method == "POST":
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if verify_credentials(username, password, current_app):
            session["logged_in"] = True
            session["username"] = username
            return jsonify({"message": "登录成功"}), 200
        else:
            return jsonify({"error": "用户名或密码错误"}), 401

    return render_template("admin/login.html")


@admin_bp.route("/logout", methods=["POST"])
def logout():
    """登出"""
    session.clear()
    return jsonify({"message": "登出成功"}), 200


@admin_bp.route("/")
@require_admin
def dashboard():
    """管理后台首页"""
    return render_template("admin/index.html")


@admin_bp.route("/posts", methods=["GET"])
@require_admin
def list_posts():
    """获取所有文章（包括草稿）"""
    db_path = current_app.config["DATABASE_PATH"]
    posts = get_all_posts(db_path)
    return jsonify(
        {
            "posts": [
                {
                    "id": p["id"],
                    "title": p["title"],
                    "status": p["status"],
                    "created_at": p["created_at"],
                    "updated_at": p["updated_at"],
                }
                for p in posts
            ]
        }
    )


@admin_bp.route("/posts", methods=["POST"])
@require_admin
def create_post_admin():
    """创建文章"""
    db_path = current_app.config["DATABASE_PATH"]
    try:
        data = request.get_json()
        title = data.get("title")
        content = data.get("content")
        status = data.get("status", "published")

        if not title or not content:
            return jsonify({"error": "标题和内容不能为空"}), 400

        post_id = create_post(db_path, title, content, status)

        # 如果是已发布状态，更新向量
        if status == "published":
            update_post_embeddings(post_id, title, content)

        return jsonify({"message": "文章创建成功", "post_id": post_id}), 201

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/posts/<int:post_id>", methods=["GET"])
@require_admin
def get_post_admin(post_id):
    """获取单篇文章详情"""
    db_path = current_app.config["DATABASE_PATH"]
    post = get_post(db_path, post_id)

    if not post:
        return jsonify({"error": "文章不存在"}), 404

    return jsonify(
        {
            "id": post["id"],
            "title": post["title"],
            "content": post["content"],
            "status": post["status"],
            "created_at": post["created_at"],
            "updated_at": post["updated_at"],
        }
    )


@admin_bp.route("/posts/<int:post_id>", methods=["PUT"])
@require_admin
def update_post_admin(post_id):
    """更新文章"""
    db_path = current_app.config["DATABASE_PATH"]
    try:
        data = request.get_json()
        title = data.get("title")
        content = data.get("content")
        status = data.get("status")

        # 获取原文章信息
        old_post = get_post(db_path, post_id)
        if not old_post:
            return jsonify({"error": "文章不存在"}), 404

        # 更新文章
        update_post(db_path, post_id, title=title, content=content, status=status)

        # 如果状态变为 published 或内容发生变化，更新向量
        new_status = status if status is not None else old_post["status"]
        new_content = content if content is not None else old_post["content"]
        new_title = title if title is not None else old_post["title"]

        if new_status == "published":
            update_post_embeddings(post_id, new_title, new_content)

        return jsonify({"message": "文章更新成功"})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/posts/<int:post_id>", methods=["DELETE"])
@require_admin
def delete_post_admin(post_id):
    """删除文章"""
    db_path = current_app.config["DATABASE_PATH"]
    try:
        # 删除向量
        delete_post_embeddings(post_id)

        # 删除文章（级联删除 chunks）
        delete_post(db_path, post_id)

        return jsonify({"message": "文章删除成功"})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/visits", methods=["GET"])
@require_admin
def list_visits():
    """获取访问记录"""
    db_path = current_app.config["DATABASE_PATH"]
    visits = get_visits(db_path, limit=200)
    return jsonify(
        {
            "visits": [
                {
                    "id": v["id"],
                    "ip": v["ip"],
                    "visited_at": v["visited_at"],
                    "path": v["path"],
                }
                for v in visits
            ]
        }
    )
