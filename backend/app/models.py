from datetime import datetime, timedelta
from contextlib import contextmanager
import sqlite3


@contextmanager
def get_db_connection(db_path):
    """获取数据库连接上下文管理器"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db(db_path):
    """初始化数据库，创建所有表"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 创建 posts 表
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT CHECK(status IN ('published', 'draft')) DEFAULT 'published'
        )
    """
    )

    # 创建 chunks 表
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            chunk_text TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            FOREIGN KEY(post_id) REFERENCES posts(id) ON DELETE CASCADE
        )
    """
    )

    # 创建 visits 表
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL,
            visited_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            path TEXT NOT NULL
        )
    """
    )

    conn.commit()
    conn.close()


# ==================== Post 相关操作 ====================


def create_post(db_path, title, content, status="published"):
    """创建新文章"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO posts (title, content, status) VALUES (?, ?, ?)",
            (title, content, status),
        )
        conn.commit()
        return cursor.lastrowid


def get_post(db_path, post_id):
    """获取单篇文章"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
        return cursor.fetchone()


def get_all_posts(db_path, status=None):
    """获取所有文章"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        if status:
            cursor.execute(
                "SELECT * FROM posts WHERE status = ? ORDER BY created_at DESC",
                (status,),
            )
        else:
            cursor.execute("SELECT * FROM posts ORDER BY created_at DESC")
        return cursor.fetchall()


def update_post(db_path, post_id, title=None, content=None, status=None):
    """更新文章"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()

        # 使用白名单确保字段名安全
        allowed_fields = {
            "title": title,
            "content": content,
            "status": status,
        }

        updates = []
        params = []

        for field, value in allowed_fields.items():
            if value is not None:
                updates.append(f"{field} = ?")
                params.append(value)

        if updates:
            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(post_id)

            query = f"UPDATE posts SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()


def delete_post(db_path, post_id):
    """删除文章（会级联删除相关的 chunks）"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        conn.commit()


# ==================== Chunk 相关操作 ====================


def create_chunks(db_path, post_id, chunks):
    """为文章创建文本块"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        for idx, chunk_text in enumerate(chunks):
            cursor.execute(
                "INSERT INTO chunks (post_id, chunk_text, chunk_index) VALUES (?, ?, ?)",
                (post_id, chunk_text, idx),
            )
        conn.commit()


def get_chunks_by_post(db_path, post_id):
    """获取文章的所有文本块"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM chunks WHERE post_id = ? ORDER BY chunk_index", (post_id,)
        )
        return cursor.fetchall()


def delete_chunks_by_post(db_path, post_id):
    """删除文章的所有文本块"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chunks WHERE post_id = ?", (post_id,))
        conn.commit()


def get_chunk_by_id(db_path, chunk_id):
    """根据 ID 获取单个文本块"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chunks WHERE id = ?", (chunk_id,))
        return cursor.fetchone()


# ==================== Visit 相关操作 ====================


def log_visit(db_path, ip, path):
    """记录访客访问，同一IP半小时内重复访问不记录"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()

        # 使用与 SQLite CURRENT_TIMESTAMP 一致的格式
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")
        thirty_minutes_ago = now - timedelta(minutes=30)
        thirty_minutes_ago_str = thirty_minutes_ago.strftime("%Y-%m-%d %H:%M:%S")

        # 检查该IP在半小时内是否已经访问过
        cursor.execute(
            """
            SELECT COUNT(*) as count FROM visits
            WHERE ip = ? AND visited_at > ?
            """,
            (ip, thirty_minutes_ago_str),
        )
        result = cursor.fetchone()

        # 如果半小时内没有访问记录，则插入新记录
        if result["count"] == 0:
            cursor.execute(
                "INSERT INTO visits (ip, path, visited_at) VALUES (?, ?, ?)",
                (ip, path, now_str)
            )
            conn.commit()


def get_visits(db_path, limit=100):
    """获取访问记录"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM visits ORDER BY visited_at DESC LIMIT ?", (limit,)
        )
        return cursor.fetchall()
