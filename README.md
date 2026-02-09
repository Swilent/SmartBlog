# 个人博客 + RAG 问答系统

一个极简风格的个人博客系统，支持 Markdown 文章发布，并集成基于博客内容的 RAG 智能问答功能。

## 项目特点

- 极简现代的极客风格 UI（黑色背景 + 紫色强调 + 绿色代码高亮）
- 访客无需登录即可浏览文章和使用 AI 问答
- 管理员通过 IP 白名单 + 密码登录后台
- 基于 RAG 技术的智能问答，AI 回答严格基于博客内容

## 技术栈

### 后端
- Python 3.11
- Flask（Web 框架）
- SQLite（结构化数据存储）
- ChromaDB（向量数据库）
- 通义千问 API（Embedding、Rerank、LLM）

### 前端（访客端）
- Vue 3
- Vite
- Vue Router
- Pinia（状态管理）
- Axios（HTTP 客户端）
- Marked（Markdown 渲染）
- Highlight.js（代码高亮）

### 前端（管理端）
- Flask + Jinja2（服务端渲染）

## 项目结构

```
blog/
├── backend/                    # Flask 后端
│   ├── app/
│   │   ├── models.py          # 数据库模型
│   │   ├── routes/            # 路由
│   │   │   ├── api.py         # API 路由（访客）
│   │   │   └── admin.py       # 管理后台路由
│   │   ├── services/          # 业务逻辑
│   │   │   ├── chroma_service.py      # ChromaDB 服务
│   │   │   ├── embedding_service.py   # Embedding 服务
│   │   │   └── rag_service.py         # RAG 问答服务
│   │   ├── utils/             # 工具函数
│   │   │   ├── markdown_splitter.py   # Markdown 分块
│   │   │   ├── auth.py                 # 认证工具
│   │   │   └── visitor_logger.py      # 访客日志
│   │   ├── templates/         # 模板
│   │   │   └── admin/         # 管理后台模板
│   │   └── static/            # 静态文件
│   │       └── admin/         # 管理后台静态文件
│   ├── config.py              # 配置文件
│   ├── requirements.txt       # Python 依赖
│   ├── run.py                 # 启动文件
│   └── .env                   # 环境变量（需自行创建）
│
└── frontend/                   # Vue 3 前端
    ├── src/
    │   ├── components/        # 组件
    │   │   └── ChatWidget.vue # RAG 对话组件
    │   ├── views/             # 页面视图
    │   ├── router/            # 路由配置
    │   ├── stores/            # Pinia 状态管理
    │   ├── services/          # API 服务
    │   └── styles/            # 全局样式
    ├── package.json
    └── vite.config.js
```

## 快速开始

### 1. 环境准备

确保已安装：
- Python 3.11+
- Node.js 18+
- 通义千问 API Key

### 2. 后端设置

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt

# 复制环境变量模板
copy .env.example .env

# 编辑 .env 文件，填入配置
```

**.env 配置示例：**

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DASHSCOPE_API_KEY=your-dashscope-api-key
DATABASE_PATH=blog.db
CHROMADB_PATH=./chromadb_data
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-password
ADMIN_IP_WHITELIST=127.0.0.1,::1
```

### 3. 启动后端

```bash
cd backend
python run.py
```

后端将运行在 `http://localhost:5000`

### 4. 前端设置

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将运行在 `http://localhost:3000`

### 5. 访问应用

- **访客前端**：http://localhost:3000
- **管理后台**：http://localhost:5000/admin

## 功能说明

### 访客功能
- 浏览文章列表
- 阅读文章详情（支持 Markdown 渲染和代码高亮）
- 使用右下角的 AI 助手提问（基于博客内容的 RAG 问答）

### 管理员功能
- 文章管理（创建、编辑、删除、发布/草稿）
- 查看访客访问记录
- IP 白名单保护

### RAG 问答流程

1. 用户在聊天窗口输入问题
2. 系统调用通义千问 Text-Embedding-v4 生成问题向量
3. 在 ChromaDB 中检索最相关的 10 个文本块
4. 使用 Qwen 3-Rerank 对结果重排序，取前 5 个
5. 将问题和上下文发送给 Qwen Plus 生成回答
6. 返回给用户展示

## 部署说明

### 生产环境配置

1. **修改 .env 配置**
   - 设置 `DEBUG=False`
   - 修改 `SECRET_KEY` 为强随机字符串
   - 配置正确的 `ADMIN_IP_WHITELIST`

2. **启用 HTTPS**
   - 使用 Nginx 或 Caddy 反向代理
   - 配置 SSL 证书

3. **前端构建**
   ```bash
   cd frontend
   npm run build
   ```
   将 `dist` 目录部署到 Web 服务器

### Nginx 配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # 前端静态文件
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # 管理后台
    location /admin {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 验收标准（MVP）

- [x] 访客可浏览文章列表与详情
- [x] 管理员可增删改博客，操作后自动更新向量库
- [x] 访客可提问，系统基于博客内容生成回答
- [x] RAG 流程正确调用：Embedding → ChromaDB 检索 → Rerank → Qwen Plus 生成
- [x] 所有向量维度为 1024，ChromaDB 正确持久化
- [x] UI 符合"黑+紫+绿"极客风格

## 常见问题

### Q: 如何获取通义千问 API Key？
A: 访问阿里云百炼平台（https://dashscope.console.aliyun.com/）申请。

### Q: 如何添加管理员 IP？
A: 在 .env 文件中修改 `ADMIN_IP_WHITELIST`，用逗号分隔多个 IP。

### Q: ChromaDB 数据存储在哪里？
A: 默认存储在 `backend/chromadb_data` 目录，可通过 .env 修改路径。

### Q: 如何备份数据？
A: 备份以下文件/目录：
- `backend/blog.db`（SQLite 数据库）
- `backend/chromadb_data`（向量数据库）

## 许可证

MIT
