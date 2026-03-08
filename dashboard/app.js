class JanDashboard {
    constructor() {
        this.activePage = 'overview';
        this.brandId = 1; // Default
        this.init();
    }

    init() {
        this.navigate(this.activePage);
    }

    navigate(pageId) {
        this.activePage = pageId;
        
        // Update sidebar
        document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
        document.querySelector(`[data-page="${pageId}"]`)?.classList.add('active');
        
        // Update Title
        const titleMap = {
            'overview': 'Platform Overview',
            'intelligence': 'Intelligence Engine',
            'factory': 'Content Factory',
            'calendar': 'Editorial Calendar',
            'approvals': 'Approval Queue',
            'automation': 'Automation Center',
            'founder': 'Founder Assistant'
        };
        document.getElementById('page-title').innerText = titleMap[pageId] || 'Dashboard';

        // Load content
        const container = document.getElementById('page-container');
        const template = document.getElementById(`tpl-${pageId}`);
        
        if (template) {
            container.innerHTML = template.innerHTML;
        } else {
            container.innerHTML = `<div class="glass-panel"><h2><i class="fa-solid fa-person-digging"></i> Under Construction</h2><p>This module is part of the next Phase rollout.</p></div>`;
        }
        
        // Context specific loads
        if (pageId === 'approvals') {
            this.refreshQueue();
        }
    }

    switchBrand() {
        this.brandId = document.getElementById('brand-select').value;
        this.showToast(`Switched active workspace.`, 'success');
        this.navigate(this.activePage);
    }

    async startAutomation() {
        this.showToast("Starting autonomous pipeline...", "success");
        try {
            const res = await fetch(`http://localhost:8000/automation/start?brand_id=${this.brandId}`, {
                method: 'POST'
            });
            const data = await res.json();
            if(data.status === 'success') {
                this.showToast("Pipeline running in background.", "success");
            } else {
                this.showToast("Failed to start pipeline.", "error");
            }
        } catch (e) {
            this.showToast("Server error.", "error");
        }
    }

    async publishDraft(draftId) {
        this.showToast("Publishing draft...", "success");
        try {
            const res = await fetch(`http://localhost:8000/publish`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ draft_id: String(draftId), brand_id: Number(this.brandId) })
            });
            const data = await res.json();
            if(data.status === 'published') {
                this.showToast(`Draft published successfully!`, "success");
                // Remove element from DOM
                event.target.closest('.queue-item').style.display = 'none';
            }
        } catch(e) {
            this.showToast("Publish failed.", "error");
        }
    }

    async askFounder() {
        const input = document.getElementById('founder-query');
        const query = input.value;
        if (!query) return;

        const history = document.getElementById('chat-history');
        
        // Append user 
        history.innerHTML += `
            <div class="chat-msg user">
                <div class="msg-avatar"><i class="fa-solid fa-user"></i></div>
                <div class="msg-bubble">${query}</div>
            </div>`;
        
        input.value = '';
        history.scrollTop = history.scrollHeight;

        // Fetch
        try {
            const res = await fetch(`http://localhost:8000/assistant/chat?query=${encodeURIComponent(query)}&brand_id=${this.brandId}`);
            const data = await res.json();
            
            let advice = "I couldn't generate advice right now.";
            if (data.response && data.response.advice) {
                advice = data.response.advice;
            }

            history.innerHTML += `
                <div class="chat-msg ai">
                    <div class="msg-avatar"><i class="fa-solid fa-robot"></i></div>
                    <div class="msg-bubble">${advice}</div>
                </div>`;
            history.scrollTop = history.scrollHeight;

        } catch(e) {
             this.showToast("Failed to contact Founder Assistant.", "error");
        }
    }

    async refreshQueue() {
        // Mocked rendering for UX preview
        const list = document.getElementById('approval-queue-list');
        list.innerHTML = `
            <div class="queue-item">
                <div class="queue-meta">
                    <span class="platform-badge linkedin"><i class="fa-brands fa-linkedin"></i> LinkedIn</span>
                    <span class="topic-label">AI Scaling Architecture</span>
                </div>
                <div class="draft-content">How we scaled our AI pipeline from 10 to 10k requests/min. 🚀\n\nThe secret isn't more models, it's better routing. Here's a 3-step breakdown of our architecture...</div>
                <div class="queue-actions">
                    <button class="btn btn-success" onclick="app.publishDraft('d123')"><i class="fa-solid fa-check"></i> Approve & Publish</button>
                    <button class="btn btn-danger" onclick="this.closest('.queue-item').style.display='none';"><i class="fa-solid fa-xmark"></i> Reject</button>
                    <button class="btn btn-outline"><i class="fa-solid fa-pen"></i> Edit</button>
                </div>
            </div>`;
    }

    showToast(message, type = 'success') {
        const container = document.getElementById('notification-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = type === 'success' ? 'fa-circle-check' : 'fa-circle-exclamation';
        
        toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
}

const app = new JanDashboard();
