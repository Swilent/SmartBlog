import chromadb
from chromadb.config import Settings
from flask import current_app
import os


class ChromaService:
    """ChromaDB 向量数据库服务"""

    def __init__(self):
        self.client = None
        self.collection = None

    def init_client(self):
        """初始化 ChromaDB 客户端"""
        persist_directory = current_app.config.get('CHROMADB_PATH', './chromadb_data')

        # 确保目录存在
        os.makedirs(persist_directory, exist_ok=True)

        self.client = chromadb.PersistentClient(path=persist_directory)

        # 获取或创建 collection
        collection_name = current_app.config.get('CHROMADB_COLLECTION', 'blog_chunks')
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_embedding(self, chunk_id: int, embedding: list, post_id: int,
                      title: str, chunk_text: str, chunk_index: int):
        """
        添加向量到 ChromaDB

        Args:
            chunk_id: 文本块 ID
            embedding: 1024 维向量
            post_id: 文章 ID
            title: 文章标题
            chunk_text: 文本块内容
            chunk_index: 文本块索引
        """
        if self.collection is None:
            self.init_client()

        # 构造文档 ID
        doc_id = f"chunk_{chunk_id}"

        # 添加到 collection
        self.collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            metadatas=[{
                "chunk_id": chunk_id,
                "post_id": post_id,
                "title": title,
                "chunk_text": chunk_text,
                "chunk_index": chunk_index
            }],
            documents=[chunk_text]
        )

    def search(self, embedding: list, top_k: int = 10):
        """
        在 ChromaDB 中搜索相似向量

        Args:
            embedding: 查询向量（1024 维）
            top_k: 返回前 K 个结果

        Returns:
            List[dict]: 搜索结果列表
        """
        if self.collection is None:
            self.init_client()

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )

        # 格式化结果
        formatted_results = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None,
                    'metadata': results['metadatas'][0][i] if 'metadatas' in results else None,
                    'document': results['documents'][0][i] if 'documents' in results else None
                })

        return formatted_results

    def delete_post_embeddings(self, post_id: int):
        """
        删除文章的所有向量

        Args:
            post_id: 文章 ID
        """
        if self.collection is None:
            self.init_client()

        # 查找该文章的所有 chunk
        results = self.collection.get(
            where={"post_id": post_id}
        )

        if results['ids']:
            self.collection.delete(ids=results['ids'])


# 全局单例
chroma_service = ChromaService()
