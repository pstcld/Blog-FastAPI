const API = '/api/v1';
let token = localStorage.getItem('token') || null;
let currentUser = null;
let categoriesMap = {};
let locationsMap = {};

// Состояние текущего экрана: 'all' | 'user-posts' | 'user-likes'
let currentViewMode = 'all';
let viewedUserId = null;

// Плоская векторная иконка сердца без бликов
const HEART_SVG = `
<svg class="heart-icon" viewBox="0 0 24 24">
    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
</svg>`;

document.addEventListener('DOMContentLoaded', async () => {
    await checkAuth();
    await loadTaxonomies();
    await loadPosts();
});

function authHeaders(isJson = true) {
    const headers = {};
    if (isJson) headers['Content-Type'] = 'application/json';
    if (token) headers['Authorization'] = `Bearer ${token}`;
    return headers;
}

// --- АВТОРИЗАЦИЯ ---
async function checkAuth() {
    if (!token) {
        updateNavUI();
        return;
    }
    try {
        const res = await fetch(`${API}/users/me`, { headers: authHeaders(false) });
        if (res.ok) {
            currentUser = await res.json();
        } else {
            localStorage.removeItem('token');
            token = null;
            currentUser = null;
        }
    } catch (e) {
        console.error(e);
    }
    updateNavUI();
}

function updateNavUI() {
    const guestNav = document.getElementById('guest-nav');
    const userNav = document.getElementById('user-nav');
    const taxPanel = document.getElementById('taxonomy-panel');

    if (currentUser) {
        guestNav.classList.add('hidden');
        userNav.classList.remove('hidden');
        taxPanel.classList.remove('hidden');
        document.getElementById('nav-username').textContent = `@${currentUser.username}`;
        const badge = document.getElementById('nav-admin-badge');
        if (currentUser.is_admin) badge.classList.remove('hidden');
        else badge.classList.add('hidden');
    } else {
        guestNav.classList.remove('hidden');
        userNav.classList.add('hidden');
        taxPanel.classList.add('hidden');
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const errEl = document.getElementById('login-error');
    errEl.classList.add('hidden');

    const formData = new URLSearchParams();
    formData.append('username', document.getElementById('login-username').value);
    formData.append('password', document.getElementById('login-password').value);

    const res = await fetch(`${API}/users/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
    });

    if (res.ok) {
        const data = await res.json();
        token = data.access_token;
        localStorage.setItem('token', token);
        closeModal('login-modal');
        e.target.reset();
        await checkAuth();
        await loadPosts();
    } else {
        errEl.textContent = 'Неверный логин или пароль';
        errEl.classList.remove('hidden');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const errEl = document.getElementById('reg-error');
    errEl.classList.add('hidden');

    const payload = {
        username: document.getElementById('reg-username').value,
        email: document.getElementById('reg-email').value,
        password: document.getElementById('reg-password').value
    };

    const res = await fetch(`${API}/users/`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify(payload)
    });

    if (res.ok) {
        closeModal('register-modal');
        document.getElementById('login-username').value = payload.username;
        document.getElementById('login-password').value = payload.password;
        await handleLogin(new Event('submit'));
        e.target.reset();
    } else {
        const err = await res.json();
        errEl.textContent = err.detail ? JSON.stringify(err.detail) : 'Ошибка регистрации';
        errEl.classList.remove('hidden');
    }
}

function logout() {
    localStorage.removeItem('token');
    token = null;
    currentUser = null;
    updateNavUI();
    showAllFeed();
}

// --- ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ И РЕЖИМЫ ЛЕНТЫ ---
function openMyProfile() {
    if (!currentUser) return;
    openUserProfile(currentUser.id);
}

async function openUserProfile(userId) {
    closeModal('likers-modal');
    viewedUserId = userId;
    currentViewMode = 'user-posts';

    const profileHeader = document.getElementById('profile-header');
    profileHeader.classList.remove('hidden');

    // Получаем данные о пользователе
    const res = await fetch(`${API}/users/${userId}`);
    if (res.ok) {
        const user = await res.json();
        document.getElementById('profile-username').textContent = `@${user.username}`;
        document.getElementById('profile-email').textContent = user.email || '';
    }

    updateProfileTabsUI();
    await loadPosts();
}

function switchProfileTab(tab) {
    currentViewMode = tab === 'likes' ? 'user-likes' : 'user-posts';
    updateProfileTabsUI();
    loadPosts();
}

function updateProfileTabsUI() {
    const tabPosts = document.getElementById('tab-user-posts');
    const tabLikes = document.getElementById('tab-user-likes');
    tabPosts.classList.toggle('active', currentViewMode === 'user-posts');
    tabLikes.classList.toggle('active', currentViewMode === 'user-likes');
}

function showAllFeed() {
    currentViewMode = 'all';
    viewedUserId = null;
    document.getElementById('profile-header').classList.add('hidden');
    document.getElementById('filter-category').value = '';
    document.getElementById('filter-location').value = '';
    loadPosts();
}

function onFilterChange() {
    // При выборе фильтра категории или локации возвращаемся в общую ленту
    currentViewMode = 'all';
    viewedUserId = null;
    document.getElementById('profile-header').classList.add('hidden');
    loadPosts();
}

// --- КАТЕГОРИИ И ЛОКАЦИИ ---
async function loadTaxonomies() {
    const [catRes, locRes] = await Promise.all([
        fetch(`${API}/categories/`),
        fetch(`${API}/locations/`)
    ]);
    const categories = catRes.ok ? await catRes.json() : [];
    const locations = locRes.ok ? await locRes.json() : [];

    categoriesMap = Object.fromEntries(categories.map(c => [c.id, c]));
    locationsMap = Object.fromEntries(locations.map(l => [l.id, l]));

    const filterCat = document.getElementById('filter-category');
    const postCat = document.getElementById('post-category');
    filterCat.innerHTML = '<option value="">Все категории</option>';
    postCat.innerHTML = '<option value="">Без категории</option>';
    categories.forEach(c => {
        filterCat.innerHTML += `<option value="${c.id}">${escapeHtml(c.title)}</option>`;
        postCat.innerHTML += `<option value="${c.id}">${escapeHtml(c.title)}</option>`;
    });

    const filterLoc = document.getElementById('filter-location');
    const postLoc = document.getElementById('post-location');
    filterLoc.innerHTML = '<option value="">Все локации</option>';
    postLoc.innerHTML = '<option value="">Без локации</option>';
    locations.forEach(l => {
        filterLoc.innerHTML += `<option value="${l.id}">${escapeHtml(l.name)}</option>`;
        postLoc.innerHTML += `<option value="${l.id}">${escapeHtml(l.name)}</option>`;
    });
}

async function createCategory(e) {
    e.preventDefault();
    const title = document.getElementById('new-cat-title').value;
    const slug = document.getElementById('new-cat-slug').value;
    const res = await fetch(`${API}/categories/`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ title, slug, is_published: true })
    });
    if (res.ok) {
        e.target.reset();
        await loadTaxonomies();
    } else {
        alert('Ошибка создания категории');
    }
}

async function createLocation(e) {
    e.preventDefault();
    const name = document.getElementById('new-loc-name').value;
    const res = await fetch(`${API}/locations/`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ name, is_published: true })
    });
    if (res.ok) {
        e.target.reset();
        await loadTaxonomies();
    } else {
        alert('Ошибка создания локации');
    }
}

// --- ПОСТЫ ---
async function loadPosts() {
    const container = document.getElementById('posts-container');
    let url = `${API}/posts/`;

    if (currentViewMode === 'user-posts' && viewedUserId) {
        url = `${API}/users/${viewedUserId}/posts`;
    } else if (currentViewMode === 'user-likes' && viewedUserId) {
        url = `${API}/users/${viewedUserId}/likes/posts`;
    } else {
        const catId = document.getElementById('filter-category').value;
        const locId = document.getElementById('filter-location').value;
        const params = new URLSearchParams();
        if (catId) params.append('category_id', catId);
        if (locId) params.append('location_id', locId);
        url = `${API}/posts/?${params.toString()}`;
    }

    const res = await fetch(url);
    if (!res.ok) {
        container.innerHTML = '<div class="empty-state">Ошибка при загрузке публикаций</div>';
        return;
    }
    const posts = await res.json();
    if (posts.length === 0) {
        container.innerHTML = '<div class="empty-state">Публикаций пока нет</div>';
        return;
    }

    container.innerHTML = posts.map(post => renderPostCard(post)).join('');
    // Подгружаем количество лайков и комментариев для каждого поста
    posts.forEach(p => {
        loadPostLikes(p.id);
        loadPostCommentsCount(p.id);
    });
}

function renderPostCard(post) {
    const catName = post.category_id && categoriesMap[post.category_id] ? categoriesMap[post.category_id].title : null;
    const locName = post.location_id && locationsMap[post.location_id] ? locationsMap[post.location_id].name : null;
    const canEdit = currentUser && (currentUser.id === post.author_id || currentUser.is_admin);
    const dateStr = new Date(post.created_at).toLocaleString('ru-RU', {
        day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit'
    });

    return `
    <article class="post-card">
        ${post.image ? `<img src="${post.image}" alt="${escapeHtml(post.title)}" class="post-image">` : ''}
        <div class="post-body">
            <div class="post-meta">
                <div>
                    <strong class="user-link" onclick="openUserProfile(${post.author.id})" title="Профиль автора">@${escapeHtml(post.author.username)}</strong> • <span>${dateStr}</span>
                </div>
                <div class="post-tags">
                    ${catName ? `<span class="badge badge-cat">${escapeHtml(catName)}</span>` : ''}
                    ${locName ? `<span class="badge badge-loc">📍 ${escapeHtml(locName)}</span>` : ''}
                </div>
            </div>

            <h2 class="post-title">${escapeHtml(post.title)}</h2>
            <p class="post-text">${escapeHtml(post.text)}</p>

            <div class="post-footer">
                <div class="post-actions">
                    <div class="like-group">
                        <button class="like-toggle-btn" id="like-btn-${post.id}" onclick="togglePostLike(${post.id})" title="Поставить / убрать лайк">
                            ${HEART_SVG}
                        </button>
                        <button class="like-count-btn" id="like-count-${post.id}" onclick="showPostLikers(${post.id})" title="Кто оценил этот пост">0</button>
                    </div>

                    <button class="action-btn" onclick="toggleComments(${post.id})">
                        <span>💬 Комментарии</span>
                        <span id="comment-count-${post.id}">(0)</span>
                    </button>
                </div>

                ${canEdit ? `
                <div class="post-actions">
                    ${post.image ? `<button class="btn-link" onclick="deletePostImage(${post.id})">Удалить фото</button>` : ''}
                    <button class="btn-link" onclick='openPostModal(${JSON.stringify(post).replace(/'/g, "&#39;")})'>Изменить</button>
                    <button class="btn-link btn-danger" onclick="deletePost(${post.id})">Удалить</button>
                </div>
                ` : ''}
            </div>
        </div>

        <div id="comments-section-${post.id}" class="comments-section hidden">
            <div id="comments-list-${post.id}"></div>
            ${currentUser ? `
            <form class="comment-form" onsubmit="submitComment(event, ${post.id})">
                <input type="text" id="comment-input-${post.id}" placeholder="Написать комментарий..." required>
                <button type="submit" class="btn btn-primary">Отправить</button>
            </form>
            ` : `<div style="font-size:0.8rem; color:#868e96;">Войдите, чтобы оставить комментарий</div>`}
        </div>
    </article>`;
}

// --- ЛАЙКИ ПОСТОВ И МОДАЛКА ОЦЕНИВШИХ ---
async function loadPostLikes(postId) {
    const res = await fetch(`${API}/posts/${postId}/likes`);
    if (!res.ok) return;
    const likers = await res.json();
    const countEl = document.getElementById(`like-count-${postId}`);
    const btnEl = document.getElementById(`like-btn-${postId}`);
    if (countEl) countEl.textContent = likers.length;
    if (btnEl && currentUser) {
        const likedByMe = likers.some(u => u.id === currentUser.id);
        btnEl.classList.toggle('liked', likedByMe);
    }
}

async function togglePostLike(postId) {
    if (!currentUser) return openModal('login-modal');
    const res = await fetch(`${API}/posts/${postId}/like`, {
        method: 'POST',
        headers: authHeaders()
    });
    if (res.ok) {
        await loadPostLikes(postId);
        // Если мы находимся во вкладке "Понравившиеся посты", обновим список
        if (currentViewMode === 'user-likes') loadPosts();
    }
}

async function showPostLikers(postId) {
    const res = await fetch(`${API}/posts/${postId}/likes`);
    if (!res.ok) return;
    const likers = await res.json();
    renderLikersModal('Оценили публикацию', likers);
}

async function showCommentLikers(commentId) {
    const res = await fetch(`${API}/comments/${commentId}/likes`);
    if (!res.ok) return;
    const likers = await res.json();
    renderLikersModal('Оценили комментарий', likers);
}

function renderLikersModal(title, users) {
    document.getElementById('likers-modal-title').textContent = `${title} (${users.length})`;
    const listEl = document.getElementById('likers-list');
    if (users.length === 0) {
        listEl.innerHTML = '<div style="font-size:0.85rem; color:#868e96; text-align:center; padding:12px 0;">Пока никто не оценил</div>';
    } else {
        listEl.innerHTML = users.map(u => `
            <div class="liker-item">
                <strong class="user-link" onclick="openUserProfile(${u.id})">@${escapeHtml(u.username)}</strong>
                <button class="btn-link" onclick="openUserProfile(${u.id})">Профиль →</button>
            </div>
        `).join('');
    }
    openModal('likers-modal');
}

// --- СОЗДАНИЕ / РЕДАКТИРОВАНИЕ ПОСТА ---
function openPostModal(post = null) {
    document.getElementById('post-error').classList.add('hidden');
    document.getElementById('post-image-file').value = '';
    if (post) {
        document.getElementById('post-modal-title').textContent = 'Редактировать пост';
        document.getElementById('post-id').value = post.id;
        document.getElementById('post-title').value = post.title;
        document.getElementById('post-text').value = post.text;
        document.getElementById('post-category').value = post.category_id || '';
        document.getElementById('post-location').value = post.location_id || '';
    } else {
        document.getElementById('post-modal-title').textContent = 'Новый пост';
        document.getElementById('post-id').value = '';
        document.getElementById('post-title').value = '';
        document.getElementById('post-text').value = '';
        document.getElementById('post-category').value = '';
        document.getElementById('post-location').value = '';
    }
    openModal('post-modal');
}

async function handleSavePost(e) {
    e.preventDefault();
    const postId = document.getElementById('post-id').value;
    const catVal = document.getElementById('post-category').value;
    const locVal = document.getElementById('post-location').value;
    const fileInput = document.getElementById('post-image-file');

    const payload = {
        title: document.getElementById('post-title').value,
        text: document.getElementById('post-text').value,
        category_id: catVal ? parseInt(catVal) : null,
        location_id: locVal ? parseInt(locVal) : null,
        is_published: true
    };

    const url = postId ? `${API}/posts/${postId}` : `${API}/posts/`;
    const method = postId ? 'PUT' : 'POST';

    const res = await fetch(url, {
        method,
        headers: authHeaders(),
        body: JSON.stringify(payload)
    });

    if (!res.ok) {
        const err = await res.json();
        const errEl = document.getElementById('post-error');
        errEl.textContent = err.detail ? JSON.stringify(err.detail) : 'Ошибка сохранения';
        errEl.classList.remove('hidden');
        return;
    }

    const savedPost = await res.json();

    if (fileInput.files.length > 0) {
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);
        await fetch(`${API}/posts/${savedPost.id}/image`, {
            method: 'POST',
            headers: authHeaders(false),
            body: formData
        });
    }

    closeModal('post-modal');
    await loadPosts();
}

async function deletePost(postId) {
    if (!confirm('Удалить эту публикацию?')) return;
    const res = await fetch(`${API}/posts/${postId}`, {
        method: 'DELETE',
        headers: authHeaders()
    });
    if (res.ok) loadPosts();
}

async function deletePostImage(postId) {
    if (!confirm('Удалить изображение поста?')) return;
    const res = await fetch(`${API}/posts/${postId}/image`, {
        method: 'DELETE',
        headers: authHeaders()
    });
    if (res.ok) loadPosts();
}

// --- КОММЕНТАРИИ И ИХ ЛАЙКИ ---
async function loadPostCommentsCount(postId) {
    const res = await fetch(`${API}/posts/${postId}/comments/`);
    if (!res.ok) return;
    const comments = await res.json();
    const countEl = document.getElementById(`comment-count-${postId}`);
    if (countEl) countEl.textContent = `(${comments.length})`;
}

async function toggleComments(postId) {
    const sec = document.getElementById(`comments-section-${postId}`);
    const isHidden = sec.classList.contains('hidden');
    if (isHidden) {
        sec.classList.remove('hidden');
        await loadComments(postId);
    } else {
        sec.classList.add('hidden');
    }
}

async function loadComments(postId) {
    const listEl = document.getElementById(`comments-list-${postId}`);
    const res = await fetch(`${API}/posts/${postId}/comments/`);
    if (!res.ok) return;
    const comments = await res.json();

    // Обновляем счетчик комментариев на кнопке поста
    const countEl = document.getElementById(`comment-count-${postId}`);
    if (countEl) countEl.textContent = `(${comments.length})`;

    if (comments.length === 0) {
        listEl.innerHTML = '<div style="font-size:0.8rem; color:#868e96; margin-bottom:8px;">Комментариев пока нет</div>';
        return;
    }

    listEl.innerHTML = comments.map(c => {
        const canDel = currentUser && (currentUser.id === c.author_id || currentUser.is_admin);
        return `
        <div class="comment-item">
            <div>
                <strong class="user-link" onclick="openUserProfile(${c.author.id})">@${escapeHtml(c.author.username)}:</strong>
                <span>${escapeHtml(c.text)}</span>
            </div>
            <div class="post-actions">
                <div class="like-group">
                    <button class="like-toggle-btn" id="comment-like-btn-${c.id}" onclick="toggleCommentLike(${c.id})" title="Оценить комментарий">
                        ${HEART_SVG}
                    </button>
                    <button class="like-count-btn" id="comment-like-count-${c.id}" onclick="showCommentLikers(${c.id})" title="Кто оценил комментарий">0</button>
                </div>
                ${canDel ? `<button class="btn-link btn-danger" onclick="deleteComment(${c.id}, ${postId})" title="Удалить">&times;</button>` : ''}
            </div>
        </div>`;
    }).join('');

    comments.forEach(c => loadCommentLikes(c.id));
}

async function loadCommentLikes(commentId) {
    const res = await fetch(`${API}/comments/${commentId}/likes`);
    if (!res.ok) return;
    const likers = await res.json();
    const countEl = document.getElementById(`comment-like-count-${commentId}`);
    const btnEl = document.getElementById(`comment-like-btn-${commentId}`);
    if (countEl) countEl.textContent = likers.length;
    if (btnEl && currentUser) {
        const likedByMe = likers.some(u => u.id === currentUser.id);
        btnEl.classList.toggle('liked', likedByMe);
    }
}

async function submitComment(e, postId) {
    e.preventDefault();
    const input = document.getElementById(`comment-input-${postId}`);
    const res = await fetch(`${API}/posts/${postId}/comments/`, {
        method: 'POST',
        headers: authHeaders(),
        body: JSON.stringify({ text: input.value })
    });
    if (res.ok) {
        input.value = '';
        await loadComments(postId);
    }
}

async function deleteComment(commentId, postId) {
    const res = await fetch(`${API}/comments/${commentId}`, {
        method: 'DELETE',
        headers: authHeaders()
    });
    if (res.ok) loadComments(postId);
}

async function toggleCommentLike(commentId) {
    if (!currentUser) return openModal('login-modal');
    const res = await fetch(`${API}/comments/${commentId}/like`, {
        method: 'POST',
        headers: authHeaders()
    });
    if (res.ok) loadCommentLikes(commentId);
}

// --- УТИЛИТЫ ---
function openModal(id) {
    document.getElementById(id).classList.remove('hidden');
}

function closeModal(id) {
    document.getElementById(id).classList.add('hidden');
}

function escapeHtml(str) {
    return String(str).replace(/[&<>"']/g, m => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[m]));
}