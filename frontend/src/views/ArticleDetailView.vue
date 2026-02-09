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
    </div>
</template>

<script setup>
import { onMounted, computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useArticleStore } from '../stores/articles'
import { marked } from 'marked'
import hljs from 'highlight.js'
import 'highlight.js/styles/github-dark.css'

const route = useRoute()
const articleStore = useArticleStore()

const renderedContent = ref('')

const article = computed(() => articleStore.currentArticle)
const loading = computed(() => articleStore.loading)
const error = computed(() => articleStore.error)

// 配置 marked
marked.setOptions({
    highlight: function(code, lang) {
        if (lang && hljs.getLanguage(lang)) {
            try {
                return hljs.highlight(code, { language: lang }).value
            } catch (err) {}
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
})

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
