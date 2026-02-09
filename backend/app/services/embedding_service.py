import dashscope
from app.models import delete_chunks_by_post, create_chunks, get_chunks_by_post
from app.utils.markdown_splitter import split_markdown
from app.services.chroma_service import chroma_service
from flask import current_app
import traceback


def generate_embedding(text: str) -> list:
    """
    调用通义千问 Text-Embedding-v4 API 生成向量

    参考官方示例：使用 dashscope.TextEmbedding.call()

    Args:
        text: 输入文本

    Returns:
        list: 1024 维向量
    """
    try:
        resp = dashscope.TextEmbedding.call(
            model=current_app.config["EMBEDDING_MODEL"], input=text
        )

        if resp.status_code == 200:
            embedding = resp["output"]["embeddings"][0]["embedding"]
            return embedding
        else:
            raise Exception(f"Embedding API 调用失败: {resp.message}")

    except Exception as e:
        traceback.print_exc()
        raise Exception(f"生成向量时出错: {str(e)}")


def update_post_embeddings(post_id: int, title: str, content: str):
    """
    更新文章的向量表示

    1. 删除旧的 chunks 和向量
    2. 分割 Markdown 内容
    3. 生成新的 chunks 和向量
    4. 存入 ChromaDB
    """
    db_path = current_app.config["DATABASE_PATH"]

    try:
        # 1. 删除旧的 chunks 和向量
        delete_chunks_by_post(db_path, post_id)
        chroma_service.delete_post_embeddings(post_id)

        # 2. 分割 Markdown 内容
        chunks = split_markdown(content, title)

        if not chunks:
            return

        # 3. 创建 chunks 记录
        create_chunks(db_path, post_id, chunks)

        # 4. 获取创建的 chunks（带 ID）
        chunk_records = get_chunks_by_post(db_path, post_id)

        # 5. 为每个 chunk 生成向量并存入 ChromaDB
        for chunk_record in chunk_records:
            chunk_id = chunk_record["id"]
            chunk_text = chunk_record["chunk_text"]
            chunk_index = chunk_record["chunk_index"]

            # 生成向量
            embedding = generate_embedding(chunk_text)

            # 存入 ChromaDB
            chroma_service.add_embedding(
                chunk_id=chunk_id,
                embedding=embedding,
                post_id=post_id,
                title=title,
                chunk_text=chunk_text,
                chunk_index=chunk_index,
            )

        print(f"文章 {post_id} 的向量更新成功，共 {len(chunks)} 个 chunk")

    except Exception as e:
        traceback.print_exc()
        raise Exception(f"更新文章向量时出错: {str(e)}")


def delete_post_embeddings(post_id: int):
    """
    删除文章的向量表示
    """
    try:
        chroma_service.delete_post_embeddings(post_id)
        print(f"文章 {post_id} 的向量删除成功")
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"删除文章向量时出错: {str(e)}")
