from dotenv import load_dotenv
import os


load_dotenv()


class Config:
    """应用配置类"""

    # Flask 配置
    SECRET_KEY = os.getenv("SECRET_KEY")
    DEBUG = os.getenv("DEBUG") == "True"

    # 数据库配置
    DATABASE_PATH = os.getenv("DATABASE_PATH")

    # 通义千问 API 配置
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")

    # Text Embedding 配置
    EMBEDDING_MODEL = "text-embedding-v4"
    EMBEDDING_DIMENSION = 1024

    # Rerank 配置
    RERANK_MODEL = "qwen3-rerank"
    RERANK_API_URL = "https://dashscope.aliyuncs.com/compatible-api/v1/reranks"

    # LLM 配置
    LLM_MODEL = "qwen-plus"

    # RAG 配置
    RAG_TOP_K = 10
    RAG_TOP_N_AFTER_RERANK = 5

    # ChromaDB 配置
    CHROMADB_PATH = os.getenv("CHROMADB_PATH")
    CHROMADB_COLLECTION = "blog_chunks"

    # 管理员配置
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

    # IP 白名单配置（逗号分隔的字符串）
    # 例如: "127.0.0.1,192.168.1.100"
    ADMIN_IP_WHITELIST = os.getenv("ADMIN_IP_WHITELIST").split(",")

    # 访客日志配置
    LOG_VISITOR_ACCESS = True

    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        pass


class DevelopmentConfig(Config):
    """开发环境配置"""

    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置"""

    DEBUG = False


# 配置字典
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
