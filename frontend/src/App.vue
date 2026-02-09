<template>
    <div id="app">
        <!-- 导航栏 -->
        <nav class="navbar">
            <router-link to="/" class="navbar-brand">我的博客</router-link>
            <div class="navbar-links">
                <router-link to="/" class="navbar-link">文章</router-link>
                <router-link to="/about" class="navbar-link">关于</router-link>
            </div>
        </nav>

        <!-- 主内容 -->
        <div class="main-container">
            <router-view />
        </div>

        <!-- RAG 对话组件 -->
        <ChatWidget />
    </div>
</template>

<script setup>
import ChatWidget from './components/ChatWidget.vue'
</script>
