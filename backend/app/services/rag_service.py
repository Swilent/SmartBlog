import dashscope
import requests
from app.services.embedding_service import generate_embedding
from app.services.chroma_service import chroma_service
from flask import current_app
import traceback


def rerank_results(query: str, candidates: list) -> list:
    """
    调用 Qwen3-Rerank API 对检索结果重排序

    使用 HTTP 请求调用（参考官方 curl 示例）

    Args:
        query: 用户查询
        candidates: 候选文档列表

    Returns:
        list: 重排序后的文档列表
    """
    try:
        api_key = current_app.config['DASHSCOPE_API_KEY']
        model = current_app.config['RERANK_MODEL']
        url = current_app.config.get('RERANK_API_URL', 'https://dashscope.aliyuncs.com/compatible-api/v1/reranks')

        # 构造候选文档列表
        documents = [c.get('document', c.get('metadata', {}).get('chunk_text', '')) for c in candidates]

        # 调用 Rerank API（参考官方 curl 示例）
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model,
            "query": query,
            "documents": documents,
            "top_n": len(documents)
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            result = response.json()

            # 解析重排序结果
            if 'results' in result:
                reranked_results = result['results']
                new_candidates = []

                for item in reranked_results:
                    index = item['index']
                    relevance_score = item.get('relevance_score', 0)

                    if index < len(candidates):
                        candidate = candidates[index].copy()
                        candidate['relevance_score'] = relevance_score
                        new_candidates.append(candidate)

                return new_candidates
            else:
                print(f"Rerank 响应格式异常: {result}")
                return candidates
        else:
            print(f"Rerank API 调用失败: {response.status_code} - {response.text}")
            return candidates

    except Exception as e:
        print(f"Rerank 过程出错: {str(e)}")
        traceback.print_exc()
        return candidates


def generate_answer(question: str, context_chunks: list) -> str:
    """
    调用 Qwen Plus 生成最终回答

    参考官方示例：使用 dashscope.Generation.call()

    Args:
        question: 用户问题
        context_chunks: 相关文档块列表

    Returns:
        str: AI 生成的回答
    """
    try:
        # 构造上下文
        context = ""
        for i, chunk in enumerate(context_chunks):
            metadata = chunk.get('metadata', {})
            title = metadata.get('title', '未知标题')
            chunk_text = chunk.get('document', metadata.get('chunk_text', ''))
            post_id = metadata.get('post_id', 0)

            context += f"\n[文档 {i+1}] (文章ID: {post_id}, 标题: {title})\n{chunk_text}\n"

        # 构造消息
        system_prompt = """你是一个个人博客问答助手。请严格基于作者已发布的博客内容回答问题。

回答要求：
1. 仅使用提供的博客内容作为依据
2. 如果内容中没有相关信息，请回答"博客中未提及相关内容"
3. 回答时请引用相关文章的标题，方便用户追溯原文
4. 保持简洁、友好、专业的语气"""

        user_message = f"""基于以下博客内容，回答用户的问题：

博客内容：
{context}

用户问题：{question}

请给出你的回答："""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        # 调用 Qwen Plus（参考官方示例）
        response = dashscope.Generation.call(
            api_key=current_app.config['DASHSCOPE_API_KEY'],
            model=current_app.config['LLM_MODEL'],
            messages=messages,
            result_format='message'
        )

        if response.status_code == 200:
            return response['output']['choices'][0]['message']['content']
        else:
            raise Exception(f"LLM API 调用失败: {response.message}")

    except Exception as e:
        traceback.print_exc()
        raise Exception(f"生成回答时出错: {str(e)}")


def rag_query(question: str) -> str:
    """
    完整的 RAG 问答流程

    1. 对问题生成向量
    2. 在 ChromaDB 中检索 top-10
    3. 使用 Rerank 重排序，取 top-5
    4. 调用 LLM 生成回答

    Args:
        question: 用户问题

    Returns:
        str: AI 生成的回答
    """
    try:
        # 1. 生成问题向量
        query_embedding = generate_embedding(question)

        # 2. ChromaDB 检索
        top_k = current_app.config.get('RAG_TOP_K', 10)
        search_results = chroma_service.search(query_embedding, top_k=top_k)

        if not search_results:
            return "博客中未提及相关内容"

        # 3. Rerank 重排序
        top_n = current_app.config.get('RAG_TOP_N_AFTER_RERANK', 5)
        reranked_results = rerank_results(question, search_results)
        top_chunks = reranked_results[:top_n]

        # 4. 生成回答
        answer = generate_answer(question, top_chunks)
        return answer

    except Exception as e:
        traceback.print_exc()
        return f"抱歉，问答服务暂时不可用，请稍后再试。错误信息：{str(e)}"
