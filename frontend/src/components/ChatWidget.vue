<template>
    <div class="chat-widget">
        <!-- 悬浮按钮 -->
        <button class="chat-toggle-button" @click="toggleChat" :class="{ 'active': isOpen }">
            <svg v-if="!isOpen" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                stroke-width="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
            </svg>
            <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
        </button>

        <!-- 聊天窗口 -->
        <div class="chat-window" :class="{ 'open': isOpen }">
            <div class="chat-header">
                <h3>AI 助手</h3>
                <p>基于博客内容的智能问答</p>
            </div>

            <div class="chat-messages" ref="messagesContainer">
                <div v-for="(message, index) in messages" :key="index" class="message" :class="message.role">
                    <div class="message-content">
                        <div class="message-text" v-html="formatMessage(message.content)"></div>
                        <div class="message-time">{{ formatTime(message.timestamp) }}</div>
                    </div>
                </div>

                <div v-if="isTyping" class="message assistant">
                    <div class="message-content">
                        <div class="typing-indicator">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="chat-input-container">
                <textarea v-model="inputMessage" class="chat-input" placeholder="问我任何关于博客内容的问题..." rows="1"
                    @keydown.enter.exact.prevent="sendMessage" @input="adjustTextareaHeight"
                    ref="inputTextarea"></textarea>
                <button class="send-button" @click="sendMessage" :disabled="!inputMessage.trim() || isTyping">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="22" y1="2" x2="11" y2="13"></line>
                        <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                    </svg>
                </button>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { ragAPI } from '../services/api'

const isOpen = ref(false)
const inputMessage = ref('')
const isTyping = ref(false)
const messages = ref([
    {
        role: 'assistant',
        content: '你好！我是基于博客内容的 AI 助手。你可以问我关于博主文章的任何问题，我会根据博客内容为你提供答案。',
        timestamp: Date.now()
    }
])

const messagesContainer = ref(null)
const inputTextarea = ref(null)

function toggleChat() {
    isOpen.value = !isOpen.value
    if (isOpen.value) {
        nextTick(() => {
            scrollToBottom()
        })
    }
}

async function sendMessage() {
    const message = inputMessage.value.trim()
    if (!message || isTyping.value) return

    // 添加用户消息
    messages.value.push({
        role: 'user',
        content: escapeHtml(message),
        timestamp: Date.now()
    })

    inputMessage.value = ''
    adjustTextareaHeight()
    isTyping.value = true
    scrollToBottom()

    try {
        const response = await ragAPI.query(message)
        const answer = response.data.answer || '抱歉，我无法回答这个问题。'

        messages.value.push({
            role: 'assistant',
            content: formatMarkdown(answer),
            timestamp: Date.now()
        })
    } catch (error) {
        console.error('发送消息失败:', error)
        messages.value.push({
            role: 'assistant',
            content: '抱歉，服务暂时不可用，请稍后再试。',
            timestamp: Date.now()
        })
    } finally {
        isTyping.value = false
        nextTick(() => {
            scrollToBottom()
        })
    }
}

function scrollToBottom() {
    if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
}

function adjustTextareaHeight() {
    const textarea = inputTextarea.value
    if (textarea) {
        textarea.style.height = 'auto'
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px'
    }
}

function formatTime(timestamp) {
    const date = new Date(timestamp)
    return date.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
    })
}

function escapeHtml(text) {
    const div = document.createElement('div')
    div.textContent = text
    return div.innerHTML
}

function formatMarkdown(text) {
    // 简单的 Markdown 格式化
    return text
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/`(.+?)`/g, '<code>$1</code>')
}

function formatMessage(content) {
    return content
}
</script>

<style scoped>
.chat-widget {
    position: fixed;
    bottom: 30px;
    right: 30px;
    z-index: 1000;
}

/* 悬浮按钮 */
.chat-toggle-button {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
    color: white;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 6px 20px rgba(168, 85, 247, 0.4), 0 0 0 0 rgba(168, 85, 247, 0.4);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
}

.chat-toggle-button::before {
    content: '';
    position: absolute;
    inset: -4px;
    border-radius: 50%;
    background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
    opacity: 0;
    transition: all 0.4s;
    z-index: -1;
}

.chat-toggle-button:hover {
    transform: scale(1.1);
    box-shadow: 0 8px 30px rgba(168, 85, 247, 0.5), 0 0 0 8px rgba(168, 85, 247, 0.1);
}

.chat-toggle-button.active {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
}

.chat-toggle-button.active:hover {
    box-shadow: 0 8px 30px rgba(239, 68, 68, 0.5), 0 0 0 8px rgba(239, 68, 68, 0.1);
}

/* 聊天窗口 */
.chat-window {
    position: absolute;
    bottom: 80px;
    right: 0;
    width: 400px;
    height: 550px;
    background: rgba(22, 22, 31, 0.95);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid rgba(168, 85, 247, 0.2);
    border-radius: 20px;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(168, 85, 247, 0.1);
    display: flex;
    flex-direction: column;
    opacity: 0;
    transform: translateY(30px) scale(0.92);
    pointer-events: none;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
}

.chat-window.open {
    opacity: 1;
    transform: translateY(0) scale(1);
    pointer-events: auto;
}

/* 聊天头部 */
.chat-header {
    padding: 24px;
    border-bottom: 1px solid rgba(168, 85, 247, 0.15);
    background: linear-gradient(135deg, rgba(168, 85, 247, 0.1) 0%, rgba(236, 72, 153, 0.05) 100%);
    border-radius: 20px 20px 0 0;
}

.chat-header h3 {
    background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 1.15rem;
    font-weight: 700;
    margin-bottom: 6px;
}

.chat-header p {
    color: var(--text-muted);
    font-size: 0.85rem;
}

/* 消息区域 */
.chat-messages {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.chat-messages::-webkit-scrollbar {
    width: 6px;
}

.chat-messages::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, var(--accent-purple), var(--accent-pink));
    border-radius: 3px;
}

.message {
    display: flex;
    animation: messageSlide 0.3s ease-out;
}

@keyframes messageSlide {
    from {
        opacity: 0;
        transform: translateY(10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.message.user {
    justify-content: flex-end;
}

.message.assistant {
    justify-content: flex-start;
}

.message-content {
    max-width: 82%;
}

.message.user .message-content {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
}

.message-text {
    padding: 14px 18px;
    border-radius: 16px;
    line-height: 1.55;
    word-wrap: break-word;
    font-size: 0.95rem;
}

.message.user .message-text {
    background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
    color: white;
    border-bottom-right-radius: 6px;
    box-shadow: 0 4px 15px rgba(168, 85, 247, 0.3);
}

.message.assistant .message-text {
    background: rgba(168, 85, 247, 0.08);
    color: var(--text-primary);
    border-bottom-left-radius: 6px;
    border: 1px solid rgba(168, 85, 247, 0.15);
}

.message-text :deep(code) {
    background: rgba(0, 0, 0, 0.3);
    color: var(--accent-purple);
    padding: 3px 8px;
    border-radius: 6px;
    font-family: 'JetBrains Mono', 'Consolas', monospace;
    font-size: 0.9em;
    border: 1px solid rgba(168, 85, 247, 0.2);
}

.message-text :deep(strong) {
    font-weight: 600;
}

.message-time {
    font-size: 0.7rem;
    color: var(--text-muted);
    margin-top: 6px;
}

/* 输入指示器 */
.typing-indicator {
    display: flex;
    gap: 6px;
    padding: 14px 18px;
    background: rgba(168, 85, 247, 0.08);
    border-radius: 16px;
    border-bottom-left-radius: 6px;
    border: 1px solid rgba(168, 85, 247, 0.15);
    width: fit-content;
}

.typing-indicator span {
    width: 8px;
    height: 8px;
    background: linear-gradient(135deg, #a855f7, #ec4899);
    border-radius: 50%;
    animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
    animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
    animation-delay: 0.4s;
}

@keyframes typing {

    0%,
    60%,
    100% {
        transform: translateY(0);
        opacity: 0.6;
    }

    30% {
        transform: translateY(-12px);
        opacity: 1;
    }
}

/* 输入区域 */
.chat-input-container {
    padding: 18px;
    border-top: 1px solid rgba(168, 85, 247, 0.15);
    display: flex;
    gap: 12px;
    background: rgba(26, 26, 37, 0.8);
    border-radius: 0 0 20px 20px;
}

.chat-input {
    flex: 1;
    background: rgba(10, 10, 15, 0.8);
    border: 1px solid rgba(168, 85, 247, 0.2);
    border-radius: 12px;
    padding: 12px 16px;
    color: var(--text-primary);
    font-size: 0.95rem;
    resize: none;
    outline: none;
    transition: all 0.3s;
    font-family: inherit;
    line-height: 1.4;
}

.chat-input:focus {
    border-color: var(--accent-purple);
    box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.1);
}

.chat-input::placeholder {
    color: var(--text-muted);
}

.send-button {
    width: 48px;
    height: 48px;
    background: linear-gradient(135deg, #a855f7 0%, #ec4899 100%);
    border: none;
    border-radius: 12px;
    color: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s;
    flex-shrink: 0;
    box-shadow: 0 4px 12px rgba(168, 85, 247, 0.3);
}

.send-button:hover:not(:disabled) {
    transform: scale(1.05);
    box-shadow: 0 6px 20px rgba(168, 85, 247, 0.4);
}

.send-button:active:not(:disabled) {
    transform: scale(0.98);
}

.send-button:disabled {
    opacity: 0.4;
    cursor: not-allowed;
    transform: none;
}

/* 响应式 */
@media (max-width: 480px) {
    .chat-widget {
        bottom: 20px;
        right: 20px;
    }

    .chat-window {
        width: calc(100vw - 40px);
        height: calc(100vh - 140px);
        bottom: 70px;
        border-radius: 16px;
    }

    .chat-header {
        padding: 20px;
        border-radius: 16px 16px 0 0;
    }

    .chat-input-container {
        border-radius: 0 0 16px 16px;
    }
}
</style>
