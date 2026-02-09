import axios from 'axios'

const API_BASE_URL = '/api/v1'

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json'
    }
})

// 文章相关 API
export const articleAPI = {
    // 获取文章列表
    getList() {
        return api.get('/posts')
    },

    // 获取文章详情
    getDetail(id) {
        return api.get(`/posts/${id}`)
    }
}

// RAG 问答 API
export const ragAPI = {
    // 提问
    query(question) {
        return api.post('/rag/query', { question })
    }
}

export default api
