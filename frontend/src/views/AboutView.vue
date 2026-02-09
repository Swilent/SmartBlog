<template>
    <div class="about-view">
        <div class="about-content">
            <h2>关于我</h2>
            <div class="markdown-content">
                <p>你好！欢迎来到我的个人博客。</p>
                <p>这是一个基于 <strong>RAG（检索增强生成）</strong> 技术的智能博客系统。你可以：</p>
                <ul>
                    <li>浏览我发布的技术文章</li>
                    <li>通过右下角的对话按钮向 AI 提问</li>
                    <li>AI 会根据博客内容为你提供准确、有依据的回答</li>
                </ul>

                <h3>技术栈</h3>
                <p>本博客采用以下技术构建：</p>
                <ul>
                    <li><strong>前端</strong>：Vue 3 + Vite + Pinia</li>
                    <li><strong>后端</strong>：Python Flask</li>
                    <li><strong>向量数据库</strong>：ChromaDB</li>
                    <li><strong>AI 服务</strong>：通义千问（Embedding、Rerank、LLM）</li>
                </ul>

                <h3>联系方式</h3>
                <p>如果你有任何问题或建议，欢迎通过右下角的 AI 助手与我交流！</p>
            </div>
        </div>
    </div>
</template>

<script setup>
</script>
