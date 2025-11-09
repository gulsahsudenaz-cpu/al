// Admin Panel JavaScript - Full Live Implementation

// Get API Base URL - consistent across all pages
function getApiBaseUrl() {
    // Check if we're in a browser environment
    if (typeof window === 'undefined') return 'http://localhost:8000/v1';
    
    const origin = window.location.origin;
    
    // If opened via file:// protocol, use localhost
    if (origin === 'null' || origin === '' || origin.startsWith('file://')) {
        return 'http://localhost:8000/v1';
    }
    
    // If localhost or 127.0.0.1, use port 8000
    if (origin.includes('localhost') || origin.includes('127.0.0.1')) {
        // Replace port with 8000 if different
        return origin.replace(/:(\d+)/, ':8000') + '/v1';
    }
    
    // For production, use same origin
    return origin + '/v1';
}

const API_BASE_URL = getApiBaseUrl();

// Authentication
let authToken = localStorage.getItem('token');

// Update token when it changes
function updateAuthToken(token) {
    authToken = token;
    if (token) {
        localStorage.setItem('token', token);
    } else {
        localStorage.removeItem('token');
    }
}

// Check authentication (only if not on login page)
if (!authToken && !window.location.pathname.includes('login.html') && window.location.pathname !== '/') {
    // Allow root path to redirect to login
    const path = window.location.pathname;
    if (path && !path.includes('login.html')) {
        window.location.href = 'login.html';
    }
}

// HTML Escape function for XSS protection
function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}

// API Helper
async function apiCall(endpoint, options = {}) {
    // Prepare body if it exists
    const body = options.body;
    if (body && typeof body === 'object' && !(body instanceof FormData)) {
        options.body = JSON.stringify(body);
    }
    
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authToken}`
        }
    };
    
    // Merge headers properly
    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...(options.headers || {})
        }
    };
    
    // Remove Content-Type for FormData
    if (options.body instanceof FormData) {
        delete mergedOptions.headers['Content-Type'];
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, mergedOptions);
        
        if (response.status === 401) {
            // Unauthorized - redirect to login
            updateAuthToken(null);
            localStorage.removeItem('username');
            window.location.href = 'login.html';
            return null;
        }
        
        if (!response.ok) {
            let errorDetail = `HTTP ${response.status}`;
            try {
                const errorData = await response.json();
                errorDetail = errorData.detail || errorData.message || errorDetail;
            } catch (e) {
                // If response is not JSON, use status text
                errorDetail = response.statusText || errorDetail;
            }
            throw new Error(errorDetail);
        }
        
        return await response.json();
    } catch (error) {
        // Network errors
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            throw new Error('Backend bağlantı hatası! API\'nin çalıştığından emin olun.');
        }
        console.error('API call error:', error);
        throw error;
    }
}

// Sidebar Toggle
if (document.getElementById('toggleSidebar')) {
    document.getElementById('toggleSidebar').addEventListener('click', () => {
        document.getElementById('sidebar').classList.toggle('show');
    });
}

// Navigation
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            // Don't prevent default for actual links
            const href = link.getAttribute('href');
            if (href && href !== '#') {
                // Let browser handle navigation for same-origin links
                if (href.startsWith('http') || href.startsWith('//')) {
                    // External link
                } else {
                    // Internal link - let browser navigate
                    // Remove active class from all links
                    navLinks.forEach(l => l.classList.remove('active'));
                    // Add active class to clicked link
                    link.classList.add('active');
                }
            }
        });
    });
    
    // Set active nav item based on current page
    const path = window.location.pathname;
    const fileName = path.split('/').pop() || 'index.html';
    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === fileName || (fileName === '' && href === 'index.html')) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// Logout
function setupLogout() {
    const logoutLinks = document.querySelectorAll('.logout-link');
    logoutLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('token');
            localStorage.removeItem('username');
            window.location.href = 'login.html';
        });
    });
}

// Load Dashboard Data
let dashboardChart = null;

async function loadDashboard() {
    try {
        showLoading('dashboard');
        
        // Load dashboard stats
        const stats = await apiCall('/admin/dashboard');
        if (!stats) return;
        
        updateDashboardStats(stats);
        
        // Load RAG metrics for chart
        const ragMetrics = await apiCall('/admin/metrics/rag?days=7&limit=100');
        if (ragMetrics) {
            updateRAGChart(ragMetrics);
        }
        
        // Load recent chats
        const chats = await apiCall('/admin/chats?limit=5');
        if (chats) {
            updateRecentChats(chats);
        }
        
        // Load recent activities
        loadRecentActivities();
        
        hideLoading('dashboard');
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showError('Dashboard yüklenirken hata oluştu: ' + error.message);
        hideLoading('dashboard');
    }
}

function updateDashboardStats(stats) {
    // Update today chats
    const todayChatsEl = document.getElementById('todayChats');
    if (todayChatsEl) {
        todayChatsEl.textContent = stats.today_chats || 0;
    }
    
    // Update average response time
    const avgResponseTimeEl = document.getElementById('avgResponseTime');
    if (avgResponseTimeEl) {
        avgResponseTimeEl.textContent = (stats.avg_response_time_seconds || 0).toFixed(1) + 's';
    }
    
    // Update unresolved
    const unresolvedEl = document.getElementById('unresolved');
    if (unresolvedEl) {
        unresolvedEl.textContent = stats.unresolved || 0;
    }
    
    // Update RAG hit rate
    const ragHitRateEl = document.getElementById('ragHitRate');
    if (ragHitRateEl) {
        ragHitRateEl.textContent = (stats.rag_hit_rate || 0).toFixed(1) + '%';
    }
    
    // Update active chats
    const activeChatsEl = document.getElementById('activeChats');
    if (activeChatsEl) {
        activeChatsEl.textContent = stats.active_chats || 0;
    }
    
    // Update LLM cost
    const llmCostEl = document.getElementById('llmCost');
    if (llmCostEl) {
        llmCostEl.textContent = '$' + (stats.llm_cost_today || 0).toFixed(4);
    }
}

function updateRAGChart(ragMetrics) {
    const ctx = document.getElementById('aiChart');
    if (!ctx) return;
    
    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded');
        ctx.parentElement.innerHTML = '<div class="text-center text-muted py-3">Chart.js yüklenemedi. Sayfayı yenileyin.</div>';
        return;
    }
    
    try {
        const chartCtx = ctx.getContext('2d');
        
        // Destroy existing chart
        if (dashboardChart) {
            dashboardChart.destroy();
            dashboardChart = null;
        }
        
        // Prepare data
        const labels = [];
        const hitRates = ragMetrics.daily_hit_rates || [];
        
        // Ensure we have 7 days of data
        while (hitRates.length < 7) {
            hitRates.push(0);
        }
        
        // Generate labels for last 7 days
        const dayNames = ['Paz', 'Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt'];
        for (let i = 6; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            labels.push(dayNames[date.getDay()]);
        }
        
        // Create chart
        dashboardChart = new Chart(chartCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'RAG Hit Rate %',
                    data: hitRates.slice(0, 7),
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                return 'Hit Rate: ' + context.parsed.y.toFixed(1) + '%';
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: 'rgba(255, 255, 255, 0.7)'
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Chart error:', error);
        // Show error message in chart area
        ctx.parentElement.innerHTML = '<div class="text-center text-muted py-3">Grafik yüklenirken hata oluştu</div>';
    }
}

function updateRecentChats(chats) {
    const liveChatEl = document.getElementById('liveChat');
    if (!liveChatEl) return;
    
    // Clear existing messages
    liveChatEl.innerHTML = '';
    
    if (!chats || chats.length === 0) {
        liveChatEl.innerHTML = '<div class="text-muted text-center py-3"><i class="fas fa-comments fa-2x mb-2 d-block"></i>Henüz sohbet yok</div>';
        return;
    }
    
    // Show recent chat messages
    const recentChats = chats.slice(0, 5).filter(chat => chat.last_message);
    
    if (recentChats.length === 0) {
        liveChatEl.innerHTML = '<div class="text-muted text-center py-3">Mesaj içeren sohbet yok</div>';
        return;
    }
    
    recentChats.forEach(chat => {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'msg-user mb-2';
        msgDiv.innerHTML = `
            <small class="d-block text-muted mb-1 fw-bold">${escapeHtml(chat.tenant || 'Bilinmeyen')}</small>
            <div class="small">${escapeHtml(chat.last_message || '')}</div>
            <small class="text-muted">${formatTime(chat.last_message_at || chat.created_at)}</small>
        `;
        liveChatEl.appendChild(msgDiv);
    });
}

function loadRecentActivities() {
    const activitiesEl = document.getElementById('recentActivities');
    if (!activitiesEl) return;
    
    // Clear existing activities
    activitiesEl.innerHTML = '';
    
    const activities = [
        { icon: 'check', color: 'success', text: 'Sistem başlatıldı', time: 'Az önce' },
        { icon: 'robot', color: 'primary', text: 'AI modeli aktif', time: '2 dk önce' },
        { icon: 'database', color: 'info', text: 'Veritabanı bağlantısı kuruldu', time: '5 dk önce' }
    ];
    
    activities.forEach(activity => {
        const li = document.createElement('li');
        li.className = 'd-flex align-items-center py-2 border-bottom border-secondary';
        li.innerHTML = `
            <div class="bg-${activity.color} rounded-circle p-2 me-3">
                <i class="fas fa-${activity.icon} text-white" style="font-size:0.8rem"></i>
            </div>
            <div>
                <small class="d-block fw-medium text-white">${activity.text}</small>
                <small class="text-muted">${activity.time}</small>
            </div>
        `;
        activitiesEl.appendChild(li);
    });
}

// Load Chats Page
async function loadChats() {
    try {
        showLoading('chats');
        
        const chats = await apiCall('/admin/chats?limit=50');
        if (!chats) return;
        
        displayChats(chats);
        hideLoading('chats');
    } catch (error) {
        console.error('Error loading chats:', error);
        showError('Sohbetler yüklenirken hata oluştu: ' + error.message);
        hideLoading('chats');
    }
}

function displayChats(chats) {
    const chatsContainer = document.getElementById('chatsContainer');
    if (!chatsContainer) return;
    
    if (!chats || chats.length === 0) {
        chatsContainer.innerHTML = '<div class="text-center py-5 text-muted"><i class="fas fa-comments fa-3x mb-3 d-block"></i>Henüz sohbet yok</div>';
        return;
    }
    
    chatsContainer.innerHTML = chats.map(chat => `
        <div class="ai-card mb-3 chat-item" data-chat-id="${chat.id}">
            <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                    <h6 class="text-white mb-1">${escapeHtml(chat.tenant || 'Bilinmeyen')}</h6>
                    <p class="text-muted mb-2 small">${escapeHtml(chat.last_message || 'Mesaj yok')}</p>
                    <div class="d-flex gap-3 small text-muted">
                        <span><i class="fas fa-comments me-1"></i>${chat.message_count || 0} mesaj</span>
                        <span><i class="fas fa-clock me-1"></i>${formatTime(chat.last_message_at || chat.created_at)}</span>
                    </div>
                </div>
                <div>
                    <span class="badge bg-${getStatusColor(chat.status)}">${escapeHtml(chat.status)}</span>
                </div>
            </div>
            <div class="mt-3">
                <button class="btn btn-sm btn-outline-primary view-chat" data-chat-id="${chat.id}">
                    <i class="fas fa-eye me-1"></i>Görüntüle
                </button>
            </div>
        </div>
    `).join('');
    
    // Add event listeners (use event delegation for better performance)
    chatsContainer.addEventListener('click', (e) => {
        const viewBtn = e.target.closest('.view-chat');
        if (viewBtn) {
            const chatId = viewBtn.dataset.chatId;
            viewChatMessages(chatId);
        }
    });
}

function getStatusColor(status) {
    const colors = {
        'active': 'success',
        'closed': 'secondary',
        'waiting': 'warning',
        'assigned': 'info'
    };
    return colors[status] || 'secondary';
}

async function viewChatMessages(chatId) {
    try {
        const messages = await apiCall(`/admin/chats/${chatId}/messages?limit=100`);
        if (!messages) return;
        
        // Show messages in modal or dedicated page
        showChatModal(chatId, messages);
    } catch (error) {
        console.error('Error loading chat messages:', error);
        showError('Mesajlar yüklenirken hata oluştu: ' + error.message);
    }
}

function showChatModal(chatId, messages) {
    // Remove existing modal if any
    const existingModal = document.querySelector('.chat-modal-container');
    if (existingModal) {
        existingModal.remove();
    }
    
    const modal = document.createElement('div');
    modal.className = 'modal fade chat-modal-container';
    modal.setAttribute('tabindex', '-1');
    modal.setAttribute('aria-labelledby', 'chatModalLabel');
    modal.setAttribute('aria-hidden', 'true');
    
    if (!messages || messages.length === 0) {
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content bg-dark text-light">
                    <div class="modal-header">
                        <h5 class="modal-title">Sohbet Mesajları</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center py-5 text-muted">
                        Bu sohbette henüz mesaj yok
                    </div>
                </div>
            </div>
        `;
    } else {
        modal.innerHTML = `
            <div class="modal-dialog modal-lg modal-dialog-scrollable">
                <div class="modal-content bg-dark text-light">
                    <div class="modal-header">
                        <h5 class="modal-title">Sohbet Mesajları (${messages.length})</h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body" style="max-height: 600px; overflow-y: auto;">
                        ${messages.map(msg => `
                            <div class="mb-3 ${msg.role === 'user' ? 'text-end' : ''}">
                                <div class="d-inline-block p-3 rounded ${msg.role === 'user' ? 'bg-primary' : 'bg-secondary'}" style="max-width: 75%; word-wrap: break-word;">
                                    <small class="d-block text-muted mb-2 fw-bold">${escapeHtml(msg.role === 'user' ? 'Kullanıcı' : 'Asistan')}</small>
                                    <div class="mb-2">${escapeHtml(msg.text || '')}</div>
                                    <small class="text-muted">${formatTime(msg.created_at)}</small>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }
    
    document.body.appendChild(modal);
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
    
    // Auto-scroll to bottom
    const modalBody = modal.querySelector('.modal-body');
    if (modalBody) {
        modalBody.scrollTop = modalBody.scrollHeight;
    }
    
    // Cleanup on close
    modal.addEventListener('hidden.bs.modal', () => {
        modal.remove();
    });
}

// Load Analytics Page
async function loadAnalytics() {
    try {
        showLoading('analytics');
        
        // Load RAG metrics
        const ragMetrics = await apiCall('/admin/metrics/rag?days=7&limit=100');
        if (ragMetrics) {
            displayRAGMetrics(ragMetrics);
        }
        
        // Load LLM metrics
        const llmMetrics = await apiCall('/admin/metrics/llm?days=7&limit=100');
        if (llmMetrics) {
            displayLLMMetrics(llmMetrics);
        }
        
        hideLoading('analytics');
    } catch (error) {
        console.error('Error loading analytics:', error);
        showError('Analitik veriler yüklenirken hata oluştu: ' + error.message);
        hideLoading('analytics');
    }
}

function displayRAGMetrics(metrics) {
    const container = document.getElementById('ragMetrics');
    if (!container) return;
    
    if (!metrics || !metrics.metrics) {
        container.innerHTML = '<div class="alert alert-warning">RAG metrikleri yüklenemedi</div>';
        return;
    }
    
    const avgHitRate = (metrics.avg_hit_rate || 0).toFixed(1);
    const avgResponseTime = (metrics.avg_response_time_ms || 0).toFixed(0);
    const totalQueries = metrics.total_queries || 0;
    const metricsList = metrics.metrics || [];
    
    container.innerHTML = `
        <div class="row g-3">
            <div class="col-md-4">
                <div class="ai-card text-center">
                    <h3 class="text-primary">${avgHitRate}%</h3>
                    <p class="text-muted mb-0">Ortalama Hit Rate</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="ai-card text-center">
                    <h3 class="text-info">${avgResponseTime}ms</h3>
                    <p class="text-muted mb-0">Ortalama Yanıt Süresi</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="ai-card text-center">
                    <h3 class="text-success">${totalQueries}</h3>
                    <p class="text-muted mb-0">Toplam Sorgu</p>
                </div>
            </div>
        </div>
        <div class="mt-4">
            <h6 class="text-white mb-3">Son Sorgular</h6>
            ${metricsList.length === 0 ? 
                '<div class="text-center text-muted py-4">Henüz sorgu yok</div>' :
                `<div class="table-responsive">
                    <table class="table table-dark table-striped">
                        <thead>
                            <tr>
                                <th>Sorgu</th>
                                <th>Döküman Sayısı</th>
                                <th>Hit Rate</th>
                                <th>Yanıt Süresi</th>
                                <th>Tarih</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${metricsList.slice(0, 10).map(m => `
                                <tr>
                                    <td>${escapeHtml(m.query_text || '')}</td>
                                    <td>${m.retrieved_documents || 0}</td>
                                    <td><span class="badge bg-${m.hit_rate ? 'success' : 'danger'}">${m.hit_rate ? 'Hit' : 'Miss'}</span></td>
                                    <td>${(m.response_time_ms || 0).toFixed(0)}ms</td>
                                    <td>${formatTime(m.created_at)}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>`
            }
        </div>
    `;
}

function displayLLMMetrics(metrics) {
    const container = document.getElementById('llmMetrics');
    if (!container) return;
    
    if (!metrics || !metrics.usage) {
        container.innerHTML = '<div class="alert alert-warning">LLM metrikleri yüklenemedi</div>';
        return;
    }
    
    const totals = metrics.totals || {};
    const today = metrics.today || {};
    const usage = metrics.usage || [];
    
    container.innerHTML = `
        <div class="row g-3 mb-4">
            <div class="col-md-3">
                <div class="ai-card text-center">
                    <h3 class="text-warning">$${(totals.total_cost_usd || 0).toFixed(4)}</h3>
                    <p class="text-muted mb-0">Toplam Maliyet</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="ai-card text-center">
                    <h3 class="text-info">${(totals.total_tokens || 0).toLocaleString()}</h3>
                    <p class="text-muted mb-0">Toplam Token</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="ai-card text-center">
                    <h3 class="text-success">${(totals.avg_latency_ms || 0).toFixed(0)}ms</h3>
                    <p class="text-muted mb-0">Ortalama Gecikme</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="ai-card text-center">
                    <h3 class="text-primary">${totals.total_calls || 0}</h3>
                    <p class="text-muted mb-0">Toplam Çağrı</p>
                </div>
            </div>
        </div>
        <div class="mt-4">
            <h6 class="text-white mb-3">Bugün: $${(today.cost_usd || 0).toFixed(4)} (${today.calls || 0} çağrı)</h6>
            ${usage.length === 0 ? 
                '<div class="text-center text-muted py-4">Henüz LLM kullanımı yok</div>' :
                `<div class="table-responsive">
                    <table class="table table-dark table-striped">
                        <thead>
                            <tr>
                                <th>Model</th>
                                <th>Token</th>
                                <th>Maliyet</th>
                                <th>Gecikme</th>
                                <th>Tarih</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${usage.slice(0, 10).map(u => `
                                <tr>
                                    <td>${escapeHtml(u.model || '')}</td>
                                    <td>${u.total_tokens || 0}</td>
                                    <td>$${(u.cost_usd || 0).toFixed(4)}</td>
                                    <td>${(u.latency_ms || 0).toFixed(0)}ms</td>
                                    <td>${formatTime(u.created_at)}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>`
            }
        </div>
    `;
}

// Load Documents Page
async function loadDocuments() {
    try {
        showLoading('documents');
        
        const documents = await apiCall('/rag/documents?limit=100');
        if (!documents) return;
        
        displayDocuments(documents);
        hideLoading('documents');
    } catch (error) {
        console.error('Error loading documents:', error);
        showError('Dökümanlar yüklenirken hata oluştu: ' + error.message);
        hideLoading('documents');
    }
}

function displayDocuments(documents) {
    const container = document.getElementById('documentsContainer');
    if (!container) return;
    
    if (!documents || documents.length === 0) {
        container.innerHTML = '<div class="text-center py-5 text-muted"><i class="fas fa-file-alt fa-3x mb-3 d-block"></i>Henüz döküman yok<br><small class="text-muted">Yeni döküman eklemek için yukarıdaki butonu kullanın</small></div>';
        return;
    }
    
    container.innerHTML = documents.map(doc => `
        <div class="ai-card mb-3">
            <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                    <h6 class="text-white mb-1">${escapeHtml(doc.name || 'İsimsiz')}</h6>
                    <p class="text-muted mb-2 small">${escapeHtml(doc.source || 'Kaynak yok')}</p>
                    <small class="text-muted"><i class="fas fa-clock me-1"></i>${formatTime(doc.created_at)}</small>
                </div>
                <div class="ms-3">
                    <span class="badge bg-${getDocumentStatusColor(doc.status)}">${escapeHtml(doc.status)}</span>
                </div>
            </div>
        </div>
    `).join('');
}

function getDocumentStatusColor(status) {
    const colors = {
        'indexed': 'success',
        'pending': 'warning',
        'failed': 'danger'
    };
    return colors[status] || 'secondary';
}

// Utility Functions
function formatTime(isoString) {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);
    
    if (diffMins < 1) return 'Az önce';
    if (diffMins < 60) return `${diffMins} dk önce`;
    if (diffHours < 24) return `${diffHours} saat önce`;
    if (diffDays < 7) return `${diffDays} gün önce`;
    
    return date.toLocaleDateString('tr-TR');
}

function showLoading(page) {
    const containers = document.querySelectorAll(`#${page}Container, #${page}`);
    containers.forEach(container => {
        if (container) {
            container.innerHTML = '<div class="text-center py-5"><div class="spinner-border text-primary" role="status"></div></div>';
        }
    });
}

function hideLoading(page) {
    // Loading will be replaced by actual content
}

// Toast notification system
function showError(message, duration = 5000) {
    console.error(message);
    
    // Remove existing toasts
    const existingToasts = document.querySelectorAll('.toast-notification');
    existingToasts.forEach(toast => toast.remove());
    
    // Create toast
    const toast = document.createElement('div');
    toast.className = 'toast-notification alert alert-danger alert-dismissible fade show';
    toast.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; min-width: 300px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);';
    toast.innerHTML = `
        <strong>Hata!</strong> ${escapeHtml(message)}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, duration);
}

function showSuccess(message, duration = 3000) {
    const toast = document.createElement('div');
    toast.className = 'toast-notification alert alert-success alert-dismissible fade show';
    toast.style.cssText = 'position: fixed; top: 20px; right: 20px; z-index: 9999; min-width: 300px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);';
    toast.innerHTML = `
        <strong>Başarılı!</strong> ${escapeHtml(message)}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, duration);
}

// Auto-refresh dashboard every 30 seconds
let dashboardInterval = null;

function startAutoRefresh() {
    if (dashboardInterval) clearInterval(dashboardInterval);
    
    dashboardInterval = setInterval(() => {
        if (window.location.pathname.includes('index.html') || window.location.pathname.endsWith('/')) {
            loadDashboard();
        }
    }, 30000); // 30 seconds
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if not on login page
    if (!window.location.pathname.includes('login.html')) {
        setupNavigation();
        setupLogout();
        
        // Update username in UI
        const username = localStorage.getItem('username');
        if (username) {
            const usernameElements = document.querySelectorAll('.username-display');
            usernameElements.forEach(el => {
                el.textContent = escapeHtml(username);
            });
        }
        
        // Load initial page data based on current page
        const path = window.location.pathname;
        const fileName = path.split('/').pop() || 'index.html';
        
        if (fileName === 'index.html' || fileName === '' || path.endsWith('/admin/') || path.endsWith('/admin')) {
            loadDashboard();
            startAutoRefresh();
        } else if (fileName === 'chats.html' || path.includes('chats')) {
            loadChats();
        } else if (fileName === 'analytics.html' || path.includes('analytics')) {
            loadAnalytics();
        } else if (fileName === 'documents.html' || path.includes('documents')) {
            loadDocuments();
        }
    }
});

// Handle page visibility change (pause refresh when tab is hidden)
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        if (dashboardInterval) {
            clearInterval(dashboardInterval);
            dashboardInterval = null;
        }
    } else {
        const path = window.location.pathname;
        if (path.includes('index.html') || path.endsWith('/') || path.endsWith('/admin/')) {
            loadDashboard();
            startAutoRefresh();
        }
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (dashboardInterval) {
        clearInterval(dashboardInterval);
    }
});
