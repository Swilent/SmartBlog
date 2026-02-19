import { createRouter, createWebHistory } from 'vue-router'
import axios from 'axios'

const routes = [
    {
        path: '/',
        name: 'Home',
        component: () => import('../views/HomeView.vue')
    },
    {
        path: '/article/:id',
        name: 'ArticleDetail',
        component: () => import('../views/ArticleDetailView.vue')
    },
    {
        path: '/about',
        name: 'About',
        component: () => import('../views/AboutView.vue')
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// 路由守卫：记录访客访问
router.afterEach((to) => {
    // 跳过同一页面的重复导航
    if (window.__last_visited_path === to.path) {
        return
    }
    window.__last_visited_path = to.path

    // 异步发送访客记录，不影响页面加载
    axios.post('/api/v1/visitor/track', {
        path: to.path
    }).catch(() => {
        // 静默忽略错误，不影响用户体验
    })
})

export default router
