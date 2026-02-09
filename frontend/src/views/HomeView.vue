<template>
    <div class="home-view">
        <h1 style="color: var(--accent-purple); margin-bottom: 30px; font-size: 2rem;">文章列表</h1>

        <div v-if="loading" class="loading">
            <div class="loading-spinner"></div>
            <p>加载中...</p>
        </div>

        <div v-else-if="error" class="empty-state">
            <div class="empty-state-icon">⚠️</div>
            <p class="empty-state-text">{{ error }}</p>
        </div>

        <div v-else-if="articles.length === 0" class="empty-state">
            <div class="empty-state-icon">📝</div>
            <p class="empty-state-text">暂无文章</p>
        </div>

        <div v-else class="article-list">
            <div
                v-for="article in articles"
                :key="article.id"
                class="article-card"
                @click="goToArticle(article.id)"
            >
                <h2 class="article-card-title">{{ article.title }}</h2>
                <p class="article-card-excerpt">{{ article.content }}</p>
                <div class="article-card-meta">
                    📅 {{ formatDate(article.created_at) }}
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useArticleStore } from '../stores/articles'

const router = useRouter()
const articleStore = useArticleStore()

const articles = computed(() => articleStore.articles)
const loading = computed(() => articleStore.loading)
const error = computed(() => articleStore.error)

onMounted(() => {
    articleStore.fetchArticles()
})

function goToArticle(id) {
    router.push(`/article/${id}`)
}

function formatDate(dateString) {
    const date = new Date(dateString)
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    })
}
</script>
