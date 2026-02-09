from flask import Blueprint, request, jsonify, current_app
from app.models import create_post, get_post, get_all_posts
from app.services.embedding_service import update_post_embeddings
from app.services.rag_service import rag_query
import traceback

api_bp = Blueprint("api", __name__)


@api_bp.route("/posts", methods=["POST", "GET"])
def posts():
    """获取文章列表或创建新文章"""
    db_path = current_app.config["DATABASE_PATH"]

    if request.method == "GET":
        """获取已发布的文章列表"""
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
        """创建新文章（内部使用，需要管理员权限）"""
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
