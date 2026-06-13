document.addEventListener('DOMContentLoaded', () => {
    const grid = document.getElementById('requests-grid');
    const refreshBtn = document.getElementById('refresh-btn');
    const lastUpdatedLabel = document.getElementById('last-updated');
    const searchInput = document.getElementById('search-input');
    const sortFilter = document.getElementById('sort-filter');
    const themeToggle = document.getElementById('theme-toggle');
    const changeUaBtn = document.getElementById('change-ua-btn');
    const activeUaLabel = document.getElementById('active-ua');
    const htmlEl = document.documentElement;
    const aiStatusEl = document.getElementById('ai-status-value');

    // AI Modal Elements
    const aiModal = document.getElementById('ai-modal');
    const aiProposalText = document.getElementById('ai-proposal-text');
    const closeModalBtn = document.getElementById('modal-close-btn');
    const copyBtn = document.getElementById('copy-proposal');

    let allRequests = [];
    let ws;
    let wsReconnectTimer = null;

    // ─── Helpers ───────────────────────────────────────────────────────────────
    function formatRelativeTime(isoStr) {
        if (!isoStr) return 'غير محدد';
        const pubDate = new Date(isoStr);
        if (isNaN(pubDate.getTime())) return 'غير محدد';
        const diffSec = Math.floor((Date.now() - pubDate.getTime()) / 1000);
        if (diffSec < 60) return 'منذ لحظات';
        const mins = Math.floor(diffSec / 60);
        const hours = Math.floor(diffSec / 3600);
        const days = Math.floor(diffSec / 86400);
        if (days >= 1) return `منذ ${days} يوم`;
        if (hours >= 1) return `منذ ${hours} ساعة`;
        return `منذ ${mins} دقيقة`;
    }

    function escapeHtml(str) {
        if (!str || typeof str !== 'string') return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }

    // ─── Theme Management ──────────────────────────────────────────────────────
    const savedTheme = localStorage.getItem('theme') || 'dark';
    htmlEl.setAttribute('data-theme', savedTheme);
    themeToggle.addEventListener('click', () => {
        const newTheme = htmlEl.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
        htmlEl.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    });

    // ─── AI Status Check ───────────────────────────────────────────────────────
    async function checkStatus() {
        try {
            const res = await fetch('/api/status');
            if (!res.ok) return;
            const data = await res.json();

            if (aiStatusEl) {
                if (data.ai_available) {
                    aiStatusEl.textContent = 'Llama 3 متصل ✓';
                    aiStatusEl.style.color = '#4ade80';
                } else {
                    aiStatusEl.textContent = 'Ollama غير متصل ✗';
                    aiStatusEl.style.color = '#f87171';
                }
            }
        } catch (e) {
            if (aiStatusEl) {
                aiStatusEl.textContent = 'غير متاح';
                aiStatusEl.style.color = '#f87171';
            }
        }
    }

    // ─── WebSocket ─────────────────────────────────────────────────────────────
    function initWebSocket() {
        if (wsReconnectTimer) clearTimeout(wsReconnectTimer);

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('Connected to Khamsat Pro Real-time Engine');
            refreshBtn.classList.add('online');
        };

        ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                if (msg.type === 'new_item') {
                    handleNewItem(msg.data);
                } else if (msg.type === 'status') {
                    updateStatus(msg);
                }
            } catch (e) {
                console.error('WebSocket message parse error:', e);
            }
        };

        ws.onclose = () => {
            console.log('WebSocket disconnected. Retrying in 5s...');
            refreshBtn.classList.remove('online');
            wsReconnectTimer = setTimeout(initWebSocket, 5000);
        };

        ws.onerror = (err) => {
            console.error('WebSocket error:', err);
            ws.close();
        };
    }

    function handleNewItem(item) {
        if (!allRequests.find(r => r.url === item.url)) {
            allRequests.unshift(item);
            filterAndRender();

            if (item.ai_analysis?.match_score >= 80) {
                playNotification();
                showBrowserNotification(item);
            }
        }
    }

    function updateStatus(msg) {
        const span = refreshBtn.querySelector('span');
        if (!span) return;
        if (msg.msg && msg.msg.includes('started')) {
            refreshBtn.classList.add('loading-state');
            span.textContent = 'جاري البحث...';
        } else {
            refreshBtn.classList.remove('loading-state');
            span.textContent = 'تحديث لحظي';
            if (msg.last_updated) lastUpdatedLabel.textContent = msg.last_updated;
        }
    }

    function playNotification() {
        try {
            const ctx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.frequency.setValueAtTime(880, ctx.currentTime);
            gain.gain.setValueAtTime(0.3, ctx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.5);
            osc.start(ctx.currentTime);
            osc.stop(ctx.currentTime + 0.5);
        } catch (e) { /* silent fail */ }
    }

    function showBrowserNotification(item) {
        if (Notification.permission === 'granted') {
            new Notification('🔥 طلب جديد متوافق!', {
                body: item.title,
                icon: '/frontend/assets/favicon.ico',
            });
        }
    }

    // ─── Data Fetching ─────────────────────────────────────────────────────────
    const fetchRequests = async () => {
        try {
            const response = await fetch('/api/data');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();

            allRequests = data;
            filterAndRender();

            if (lastUpdatedLabel.textContent === '--:--') {
                lastUpdatedLabel.textContent = new Date().toLocaleTimeString('ar-EG');
            }
        } catch (error) {
            console.error('Error fetching data:', error);
            grid.innerHTML = '<div class="loading">⚠️ فشل الاتصال بالخادم. تأكد من تشغيل السيرفر.</div>';
        }
    };

    // ─── Filter & Render ───────────────────────────────────────────────────────
    const filterAndRender = () => {
        const query = searchInput.value.toLowerCase().trim();
        const sortVal = sortFilter.value;

        let filtered = allRequests.filter(req => {
            if (!query) return true;
            const title = (req.title || '').toLowerCase();
            const desc = (req.description || '').toLowerCase();
            return title.includes(query) || desc.includes(query);
        });

        if (sortVal === 'newest') {
            filtered.sort((a, b) => new Date(b.publish_time_iso || 0) - new Date(a.publish_time_iso || 0));
        } else if (sortVal === 'match') {
            filtered.sort((a, b) => (b.ai_analysis?.match_score || 0) - (a.ai_analysis?.match_score || 0));
        } else if (sortVal === 'least-comments') {
            filtered.sort((a, b) => (a.comments_count || 0) - (b.comments_count || 0));
        }

        renderRequests(filtered);
    };

    const renderRequests = (requests) => {
        grid.innerHTML = '';
        if (requests.length === 0) {
            grid.innerHTML = '<div class="loading">لا توجد طلبات تطابق بحثك.</div>';
            return;
        }

        const fragment = document.createDocumentFragment();

        requests.forEach((req) => {
            const ai = req.ai_analysis || {};
            const score = ai.match_score || 0;
            const isHighMatch = score >= 80;
            const publishTimeDisplay = formatRelativeTime(req.publish_time_iso);

            const item = document.createElement('div');
            item.className = `request-item${isHighMatch ? ' high-match' : ''}`;

            item.innerHTML = `
                <div class="item-main">
                    <div class="item-info">
                        <h3 class="item-title">${escapeHtml(req.title)}</h3>
                        <div class="item-meta">
                            <span class="m-badge">💰 ${escapeHtml(req.budget || 'N/A')}</span>
                            <span class="m-badge">💬 ${req.comments_count || 0}</span>
                            <span class="m-time">${publishTimeDisplay}</span>
                            ${score > 0 ? `<span class="score-badge ${score >= 80 ? 'green' : 'orange'}">${score}% توافق</span>` : ''}
                        </div>
                    </div>
                    <div class="item-actions">
                        <button class="view-btn" aria-label="عرض تفاصيل الطلب">عرض التفاصيل</button>
                    </div>
                </div>
            `;

            item.querySelector('.view-btn').addEventListener('click', () => openModal(req, ai));
            fragment.appendChild(item);
        });

        grid.appendChild(fragment);
    };

    // ─── Modal ─────────────────────────────────────────────────────────────────
    function openModal(req, ai) {
        const modalTitle = aiModal.querySelector('h3');
        if (modalTitle) modalTitle.textContent = req.title;

        aiProposalText.value = `[وصف الطلب]\n${req.description || 'لا يوجد وصف'}\n\n[العرض المقترح من الذكاء الاصطناعي]\n${ai.proposal || 'لم يتم توليد عرض بعد. تأكد من تشغيل Ollama.'}`;

        let link = aiModal.querySelector('.open-original');
        if (!link) {
            link = document.createElement('a');
            link.className = 'open-original primary-btn';
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            link.textContent = 'فتح الطلب في خمسات ↗';
            aiModal.querySelector('.modal-actions').appendChild(link);
        }
        link.href = req.url;

        aiModal.setAttribute('aria-hidden', 'false');
        aiModal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }

    function closeModal() {
        aiModal.style.display = 'none';
        aiModal.setAttribute('aria-hidden', 'true');
        document.body.style.overflow = '';
    }

    if (closeModalBtn) closeModalBtn.addEventListener('click', closeModal);
    window.addEventListener('click', (e) => { if (e.target === aiModal) closeModal(); });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeModal(); });

    // ─── Copy Button (using modern Clipboard API) ──────────────────────────────
    copyBtn.addEventListener('click', async () => {
        try {
            await navigator.clipboard.writeText(aiProposalText.value);
            copyBtn.textContent = '✓ تم النسخ!';
        } catch (e) {
            // Fallback for older browsers
            aiProposalText.select();
            document.execCommand('copy');
            copyBtn.textContent = '✓ تم النسخ!';
        }
        setTimeout(() => copyBtn.textContent = 'نسخ العرض', 2000);
    });

    // ─── Event Listeners ───────────────────────────────────────────────────────
    refreshBtn.addEventListener('click', async () => {
        refreshBtn.disabled = true;
        try {
            const res = await fetch('/api/scrape');
            const data = await res.json();
            if (data.status === 'busy') {
                const span = refreshBtn.querySelector('span');
                if (span) span.textContent = 'يعمل بالفعل...';
                setTimeout(() => { if (span) span.textContent = 'تحديث لحظي'; }, 2000);
            }
        } catch (e) {
            console.error(e);
        } finally {
            refreshBtn.disabled = false;
        }
    });

    changeUaBtn.addEventListener('click', async () => {
        changeUaBtn.disabled = true;
        activeUaLabel.textContent = 'جاري التغيير...';
        try {
            const res = await fetch('/api/change_identity');
            if (!res.ok) throw new Error('فشل في تغيير الهوية');
            const data = await res.json();
            activeUaLabel.textContent = data.new_identity || 'تم تحديث الهوية';
        } catch (e) {
            activeUaLabel.textContent = 'خطأ في التغيير';
        } finally {
            changeUaBtn.disabled = false;
        }
    });

    searchInput.addEventListener('input', filterAndRender);
    sortFilter.addEventListener('change', filterAndRender);

    // ─── Initial Load ──────────────────────────────────────────────────────────
    if (Notification.permission === 'default') Notification.requestPermission();
    fetchRequests();
    initWebSocket();
    checkStatus();
    // Refresh AI status every 60 seconds
    setInterval(checkStatus, 60000);
});
