// 全局状态
let currentTab = 'posts';
let currentPostId = null;

// DOM 元素
const tabs = document.querySelectorAll('.tab');
const postsTab = document.getElementById('posts-tab');
const visitsTab = document.getElementById('visits-tab');
const logoutBtn = document.getElementById('logout-btn');
const createPostBtn = document.getElementById('create-post-btn');
const refreshVisitsBtn = document.getElementById('refresh-visits-btn');
const postModal = document.getElementById('post-modal');
const modalTitle = document.getElementById('modal-title');
const modalClose = document.querySelector('.modal-close');
const modalCancel = document.querySelector('.modal-cancel');
const savePostBtn = document.getElementById('save-post-btn');
const postForm = document.getElementById('post-form');

// 标签切换
tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        const tabName = tab.dataset.tab;
        switchTab(tabName);
    });
});

function switchTab(tabName) {
    currentTab = tabName;

    tabs.forEach(t => t.classList.remove('active'));
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    if (tabName === 'posts') {
        postsTab.style.display = 'block';
        visitsTab.style.display = 'none';
        loadPosts();
    } else {
        postsTab.style.display = 'none';
        visitsTab.style.display = 'block';
        loadVisits();
    }
}

// 退出登录
logoutBtn.addEventListener('click', async () => {
    if (confirm('确定要退出登录吗？')) {
        try {
            await fetch('/admin/logout', { method: 'POST' });
            window.location.href = '/admin/login';
        } catch (error) {
            console.error('退出登录失败:', error);
        }
    }
});

// ============ 文章管理 ============

async function loadPosts() {
    const tbody = document.getElementById('posts-tbody');
    const loading = document.getElementById('posts-loading');
    const table = document.getElementById('posts-table');

    loading.style.display = 'block';
    table.style.display = 'none';

    try {
        const response = await fetch('/admin/posts');
        const data = await response.json();

        tbody.innerHTML = '';

        if (data.posts && data.posts.length > 0) {
            data.posts.forEach(post => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${post.id}</td>
                    <td>${escapeHtml(post.title)}</td>
                    <td>
                        <span class="badge badge-${post.status}">
                            ${post.status === 'published' ? '已发布' : '草稿'}
                        </span>
                    </td>
                    <td>${formatDateTime(post.created_at)}</td>
                    <td>${formatDateTime(post.updated_at)}</td>
                    <td>
                        <div class="action-buttons">
                            <button class="btn btn-secondary btn-sm" onclick="editPost(${post.id})">编辑</button>
                            <button class="btn btn-danger btn-sm" onclick="deletePost(${post.id})">删除</button>
                        </div>
                    </td>
                `;
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #9ca3af; padding: 40px;">暂无文章</td></tr>';
        }

        loading.style.display = 'none';
        table.style.display = 'table';

    } catch (error) {
        console.error('加载文章失败:', error);
        loading.innerHTML = '<span style="color: #dc2626;">加载失败</span>';
    }
}

// 打开新建文章模态框
createPostBtn.addEventListener('click', () => {
    currentPostId = null;
    modalTitle.textContent = '新建文章';
    document.getElementById('post-id').value = '';
    document.getElementById('post-title').value = '';
    document.getElementById('post-content').value = '';
    document.getElementById('post-status').value = 'published';
    document.getElementById('post-preview').innerHTML = '';
    postModal.classList.add('show');
});

// 编辑文章
window.editPost = async function(postId) {
    try {
        const response = await fetch(`/admin/posts/${postId}`);
        const data = await response.json();

        currentPostId = postId;
        modalTitle.textContent = '编辑文章';
        document.getElementById('post-id').value = data.id;
        document.getElementById('post-title').value = data.title;
        document.getElementById('post-content').value = data.content;
        document.getElementById('post-status').value = data.status;
        updatePreview();

        postModal.classList.add('show');

    } catch (error) {
        console.error('加载文章失败:', error);
        alert('加载文章失败');
    }
};

// 删除文章
window.deletePost = async function(postId) {
    if (!confirm('确定要删除这篇文章吗？删除后不可恢复！')) {
        return;
    }

    try {
        const response = await fetch(`/admin/posts/${postId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            alert('删除成功');
            loadPosts();
        } else {
            const data = await response.json();
            alert(data.error || '删除失败');
        }
    } catch (error) {
        console.error('删除文章失败:', error);
        alert('删除失败');
    }
};

// 保存文章
savePostBtn.addEventListener('click', async () => {
    const title = document.getElementById('post-title').value.trim();
    const content = document.getElementById('post-content').value.trim();
    const status = document.getElementById('post-status').value;

    if (!title || !content) {
        alert('标题和内容不能为空');
        return;
    }

    savePostBtn.disabled = true;
    savePostBtn.textContent = '保存中...';

    try {
        const url = currentPostId ? `/admin/posts/${currentPostId}` : '/admin/posts';
        const method = currentPostId ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title, content, status })
        });

        if (response.ok) {
            alert('保存成功');
            postModal.classList.remove('show');
            loadPosts();
        } else {
            const data = await response.json();
            alert(data.error || '保存失败');
        }
    } catch (error) {
        console.error('保存文章失败:', error);
        alert('保存失败');
    } finally {
        savePostBtn.disabled = false;
        savePostBtn.textContent = '保存';
    }
});

// 关闭模态框
modalClose.addEventListener('click', () => {
    postModal.classList.remove('show');
});

modalCancel.addEventListener('click', () => {
    postModal.classList.remove('show');
});

postModal.addEventListener('click', (e) => {
    if (e.target === postModal) {
        postModal.classList.remove('show');
    }
});

// Markdown 预览
const postContent = document.getElementById('post-content');
const postPreview = document.getElementById('post-preview');

function updatePreview() {
    const content = postContent.value;

    // 简单的 Markdown 渲染（生产环境建议使用 marked.js）
    let html = content
        // 标题
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        // 代码块
        .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
        // 行内代码
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        // 粗体
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        // 斜体
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        // 链接
        .replace(/\[([^\]]+)\]\(([^\)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
        // 段落
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');

    postPreview.innerHTML = `<p>${html}</p>`;
}

postContent.addEventListener('input', updatePreview);

// ============ 访问记录 ============

async function loadVisits() {
    const tbody = document.getElementById('visits-tbody');
    const loading = document.getElementById('visits-loading');
    const table = document.getElementById('visits-table');

    loading.style.display = 'block';
    table.style.display = 'none';

    try {
        const response = await fetch('/admin/visits');
        const data = await response.json();

        tbody.innerHTML = '';

        if (data.visits && data.visits.length > 0) {
            data.visits.forEach(visit => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${visit.id}</td>
                    <td>${visit.ip}</td>
                    <td>${escapeHtml(visit.path)}</td>
                    <td>${formatDateTime(visit.visited_at)}</td>
                `;
                tbody.appendChild(row);
            });
        } else {
            tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; color: #9ca3af; padding: 40px;">暂无访问记录</td></tr>';
        }

        loading.style.display = 'none';
        table.style.display = 'table';

    } catch (error) {
        console.error('加载访问记录失败:', error);
        loading.innerHTML = '<span style="color: #dc2626;">加载失败</span>';
    }
}

refreshVisitsBtn.addEventListener('click', loadVisits);

// ============ 工具函数 ============

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 页面加载时加载文章
loadPosts();
