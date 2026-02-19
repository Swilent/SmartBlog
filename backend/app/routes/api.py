from flask import Blueprint, jsonify, current_app, request
from app.models import create_post, get_post, get_all_posts, log_visit
from app.services.embedding_service import update_post_embeddings
from app.services.rag_service import rag_query
import traceback

api_bp = Blueprint("api", __name__)


@api_bp.route("/posts", methods=["POST", "GET"])
def posts():
    """获取文章列表或创建新文章"""
    db_path = current_app.config["DATABASE_PATH"]

    if request.method == "GET":
        posts = get_all_posts(db_path, status="published")
        return jsonify(
            {
                "posts": [
                    {
                        "id": p["id"],
                        "title": p["title"],
                        "content": (
                            p["content"][:200] + "..."
                            if len(p["content"]) > 200
                            else p["content"]
                        ),
                        "created_at": p["created_at"],
                        "updated_at": p["updated_at"],
                    }
                    for p in posts
                ]
            }
        )

    elif request.method == "POST":
        data = request.get_json()
        title = data.get("title")
        content = data.get("content")
        status = data.get("status", "published")

        if not title or not content:
            return jsonify({"error": "标题和内容不能为空"}), 400

        try:
            # 创建文章
            post_id = create_post(db_path, title, content, status)

            # 如果是已发布状态，生成向量
            if status == "published":
                update_post_embeddings(post_id, title, content)

            return jsonify({"message": "文章创建成功", "post_id": post_id}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500


@api_bp.route("/posts/<int:post_id>", methods=["GET"])
def get_post_detail(post_id):
    """获取文章详情"""
    db_path = current_app.config["DATABASE_PATH"]
    post = get_post(db_path, post_id)

    if not post:
        return jsonify({"error": "文章不存在"}), 404

    if post["status"] != "published":
        return jsonify({"error": "文章未发布"}), 403

    return jsonify(
        {
            "id": post["id"],
            "title": post["title"],
            "content": post["content"],
            "created_at": post["created_at"],
            "updated_at": post["updated_at"],
        }
    )


@api_bp.route("/rag/query", methods=["POST"])
def rag_query_endpoint():
    """RAG 问答接口"""
    try:
        data = request.get_json()
        question = data.get("question")

        if not question:
            return jsonify({"error": "问题不能为空"}), 400

        answer = rag_query(question)
        return jsonify({"answer": answer})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"问答服务暂时不可用: {str(e)}"}), 500


@api_bp.route("/visitor/track", methods=["POST"])
def track_visitor():
    """访客追踪接口，供前端在路由变化时调用"""
    if not current_app.config.get("LOG_VISITOR_ACCESS", True):
        return jsonify({"tracked": False, "reason": "访客追踪未启用"}), 200

    data = request.get_json()
    path = data.get("path")

    if not path:
        return jsonify({"error": "path 参数不能为空"}), 400

    # 检查是否在需要记录的路径列表中
    log_visitor_paths = current_app.config.get("LOG_VISITOR_PATHS", [])

    # 如果配置了路径白名单，则只记录白名单中的路径
    if log_visitor_paths:
        # 支持精确匹配和前缀匹配（如 /article/:id）
        should_log = any(
            path == logged_path or path.startswith(logged_path.rstrip("/"))
            for logged_path in log_visitor_paths
        )
        if not should_log:
            return jsonify({"tracked": False, "reason": "路径不在追踪列表中"}), 200

    db_path = current_app.config["DATABASE_PATH"]
    log_visit(db_path, request.remote_addr, path)

    return jsonify({"tracked": True}), 201
