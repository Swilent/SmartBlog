import { defineStore } from 'pinia'
import { articleAPI } from '../services/api'

export const useArticleStore = defineStore('articles', {
    state: () => ({
        articles: [],
        currentArticle: null,
        loading: false,
        error: null
    }),

    actions: {
        async fetchArticles() {
            this.loading = true
            this.error = null

            try {
                const response = await articleAPI.getList()
                this.articles = response.data.posts || []
            } catch (error) {
                console.error('获取文章列表失败:', error)
                this.error = '获取文章列表失败，请稍后重试'
            } finally {
                this.loading = false
            }
        },

        async fetchArticleDetail(id) {
            this.loading = true
            this.error = null

            try {
                const response = await articleAPI.getDetail(id)
                this.currentArticle = response.data
            } catch (error) {
                console.error('获取文章详情失败:', error)
                this.error = '获取文章详情失败，请稍后重试'
            } finally {
                this.loading = false
            }
        }
    }
})
