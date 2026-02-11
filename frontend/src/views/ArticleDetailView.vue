<template>
    <div class="article-detail-view">
        <router-link to="/" class="back-button">
            ← 返回列表
        </router-link>

        <div v-if="loading" class="loading">
            <div class="loading-spinner"></div>
            <p>加载中...</p>
        </div>

        <div v-else-if="error" class="empty-state">
            <div class="empty-state-icon">⚠️</div>
            <p class="empty-state-text">{{ error }}</p>
        </div>

        <article v-else-if="article" class="article-detail">
            <h1 class="article-detail-title">{{ article.title }}</h1>
            <div class="article-detail-date">
                📅 发布于 {{ formatDate(article.created_at) }}
            </div>
            <div class="markdown-content" v-html="renderedContent"></div>
        </article>

        <!-- 回到顶部按钮 -->
        <button v-show="showBackToTop" @click="scrollToTop" class="back-to-top" :class="{ 'visible': showBackToTop }">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"
                stroke-linecap="round" stroke-linejoin="round">
                <polyline points="18 15 12 9 6 15"></polyline>
            </svg>
        </button>
    </div>
</template>

<script setup>
import { onMounted, onUnmounted, computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useArticleStore } from '../stores/articles'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'

const route = useRoute()
const articleStore = useArticleStore()

const renderedContent = ref('')
const showBackToTop = ref(false)

const article = computed(() => articleStore.currentArticle)
const loading = computed(() => articleStore.loading)
const error = computed(() => articleStore.error)

// 配置 marked
marked.setOptions({
    highlight: function (code, lang) {
        if (lang && hljs.getLanguage(lang)) {
            try {
                return hljs.highlight(code, { language: lang }).value
            } catch (err) { }
        }
        return hljs.highlightAuto(code).value
    },
    breaks: true,
    gfm: true
})

onMounted(async () => {
    const id = route.params.id
    await articleStore.fetchArticleDetail(id)

    if (article.value) {
        renderedContent.value = marked(article.value.content)
    }

    window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
    window.removeEventListener('scroll', handleScroll)
})

function handleScroll() {
    showBackToTop.value = window.scrollY > 300
}

function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    })
}

function formatDate(dateString) {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    })
}
</script>

<style scoped>
.article-detail-view {
    position: relative;
}

/* 回到顶部按钮 */
.back-to-top {
    position: fixed;
    top: 90px;
    right: 30px;
    width: 50px;
    height: 50px;
    background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
    border: none;
    border-radius: 50%;
    color: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 20px rgba(168, 85, 247, 0.4);
    opacity: 0;
    visibility: hidden;
    transform: translateY(-20px);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 99;
}

.back-to-top.visible {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}

.back-to-top:hover {
    transform: translateY(4px);
    box-shadow: 0 8px 30px rgba(168, 85, 247, 0.5);
}

.back-to-top:active {
    transform: translateY(2px);
}

/* 响应式 */
@media (max-width: 768px) {
    .back-to-top {
        top: 75px;
        right: 20px;
        width: 45px;
        height: 45px;
    }
}
</style>
