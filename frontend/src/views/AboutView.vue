<template>
    <div class="about-view">
        <div class="about-content">
            <div class="profile-header">
                <div class="avatar-wrapper">
                    <img src="/avatar.jpg" alt="Swilent" class="avatar">
                </div>
                <div class="profile-info">
                    <h1>Swilent</h1>
                    <p class="tagline">技术探索者 · 持续学习者 · 知识分享者</p>
                </div>
            </div>

            <div class="markdown-content">
                <p class="greeting">你好！欢迎来到我的个人博客。</p>

                <p>我叫 Swilent，是一名对技术、写作与持续学习充满热情的探索者。这个博客不仅是我记录思考、分享经验的地方，更是一个基于 <strong>RAG（检索增强生成）</strong>
                    技术构建的智能知识空间。</p>

                <div class="feature-section">
                    <h3>在这里，你可以</h3>
                    <ul>
                        <li>📚 阅读我撰写的关于编程、个人 PC、效率工具等领域的文章</li>
                        <li>💬 点击右下角的对话按钮，直接向 AI 提问</li>
                        <li>🤖 获得基于本博客内容生成的、有依据且上下文相关的回答</li>
                    </ul>
                </div>

                <p class="greeting">我相信，真正的知识不仅在于积累，更在于连接与激活。借助 RAG 技术，我希望让每一篇文章都能"活"起来，为你提供更精准、更有价值的信息服务。</p>

                <p class="thanks">感谢你的到访，愿我们在此共同探索、共同成长！</p>

                <div class="social-links">
                    <a href="https://github.com/Swilent" target="_blank" rel="noopener noreferrer" class="social-link github">
                        <svg viewBox="0 0 16 16" width="20" height="20">
                            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
                        </svg>
                        GitHub
                    </a>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
</script>

<style scoped>
.about-view {
    padding: 2rem;
    max-width: 900px;
    margin: 0 auto;
}

.about-content {
    background: var(--color-background);
    border-radius: 16px;
    padding: 3rem 2.5rem;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.profile-header {
    display: flex;
    align-items: center;
    gap: 2rem;
    margin-bottom: 2.5rem;
    padding-bottom: 2rem;
    border-bottom: 2px solid var(--color-border);
}

.avatar-wrapper {
    flex-shrink: 0;
}

.avatar {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    object-fit: cover;
    border: 4px solid var(--color-border);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.avatar:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

.profile-info h1 {
    margin: 0 0 0.5rem 0;
    font-size: 2.5rem;
    color: var(--color-heading);
}

.tagline {
    margin: 0;
    color: var(--color-text-secondary);
    font-size: 1rem;
    opacity: 0.8;
}

.markdown-content {
    line-height: 1.9;
    color: var(--color-text);
}

.markdown-content p {
    margin-bottom: 1.25rem;
    font-size: 1.05rem;
}

.greeting {
    font-size: 1.15rem;
    font-weight: 500;
}

.feature-section {
    background: var(--color-background-soft, rgba(0, 0, 0, 0.02));
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1.5rem 0;
}

.feature-section h3 {
    margin: 0 0 1rem 0;
    color: var(--color-heading);
    font-size: 1.2rem;
}

.feature-section ul {
    margin: 0;
    padding: 0;
    list-style: none;
}

.feature-section li {
    padding: 0.6rem 0;
    font-size: 1.05rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.thanks {
    font-weight: 500;
    color: var(--color-heading);
}

.social-links {
    margin-top: 2.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--color-border);
    display: flex;
    gap: 1rem;
}

.social-link {
    display: inline-flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.75rem 1.25rem;
    color: var(--color-text);
    text-decoration: none;
    background: var(--color-background-soft, rgba(0, 0, 0, 0.03));
    border-radius: 8px;
    transition: all 0.2s ease;
    font-weight: 500;
}

.social-link:hover {
    background: var(--color-accent, #2c974b);
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(44, 151, 75, 0.3);
}

.social-link svg {
    fill: currentColor;
}

@media (max-width: 640px) {
    .about-view {
        padding: 1rem;
    }

    .about-content {
        padding: 2rem 1.5rem;
    }

    .profile-header {
        flex-direction: column;
        text-align: center;
        gap: 1rem;
    }

    .profile-info h1 {
        font-size: 2rem;
    }

    .avatar {
        width: 100px;
        height: 100px;
    }

    .social-links {
        flex-direction: column;
    }

    .social-link {
        justify-content: center;
    }
}
</style>
