// ==================== SIDEBAR TOGGLE ====================
document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.querySelector('.toggle-btn');
    const hamburgerBtn = document.querySelector('.hamburger-btn');
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const sidebar = document.querySelector('.sidebar');
    const mainContainer = document.querySelector('.main-container');
    
    // Load sidebar state from localStorage
    const sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
    if (sidebarCollapsed) {
        sidebar.classList.add('collapsed');
        mainContainer.classList.add('sidebar-collapsed');
    }
    
    // Desktop toggle sidebar (collapse/expand)
    if (toggleBtn) {
        toggleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            sidebar.classList.toggle('collapsed');
            mainContainer.classList.toggle('sidebar-collapsed');
            localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
        });
    }
    
    // Mobile hamburger menu toggle (show/hide)
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function(e) {
            e.preventDefault();
            sidebar.classList.toggle('show');
        });
    }
    
    // Close sidebar when clicking outside on mobile
    if (window.innerWidth <= 768) {
        document.addEventListener('click', function(e) {
            if (!sidebar.contains(e.target) && !mobileMenuBtn.contains(e.target)) {
                sidebar.classList.remove('show');
            }
        });
    }
    
});

// ==================== DELETE CONFIRMATION ====================
function confirmDelete(message = 'Apakah Anda yakin ingin menghapus data ini?') {
    return confirm(message);
}

// ==================== TOAST NOTIFICATION ====================
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type}`;
    toast.style.position = 'fixed';
    toast.style.top = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '5000';
    toast.style.minWidth = '300px';
    
    let icon = 'fa-info-circle';
    if (type === 'success') icon = 'fa-check-circle';
    else if (type === 'danger') icon = 'fa-exclamation-circle';
    else if (type === 'warning') icon = 'fa-exclamation-triangle';
    
    toast.innerHTML = `<i class="fas ${icon}"></i><span>${message}</span>`;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// ==================== FORM HELPERS ====================
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function getFormData(formElement) {
    const formData = new FormData(formElement);
    const data = {};
    formData.forEach((value, key) => {
        data[key] = value;
    });
    return data;
}

// ==================== TABLE ACTIONS ====================
function deleteItem(itemId, itemType, redirectUrl) {
    if (confirmDelete(`Hapus ${itemType} ini?`)) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = redirectUrl;
        document.body.appendChild(form);
        form.submit();
    }
}

// ==================== SENTIMENT BADGE ====================
function getSentimentBadgeClass(sentiment) {
    switch(sentiment) {
        case 'positive':
            return 'badge-positive';
        case 'negative':
            return 'badge-negative';
        case 'neutral':
            return 'badge-neutral';
        default:
            return 'badge-neutral';
    }
}

function getSentimentLabel(sentiment) {
    switch(sentiment) {
        case 'positive':
            return '😊 Positif';
        case 'negative':
            return '😞 Negatif';
        case 'neutral':
            return '😐 Netral';
        default:
            return 'Netral';
    }
}

// ==================== UTILITIES ====================
function truncateText(text, maxLength = 100) {
    if (text.length > maxLength) {
        return text.substring(0, maxLength) + '...';
    }
    return text;
}

function formatDate(dateString) {
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric', 
        hour: '2-digit', 
        minute: '2-digit' 
    };
    return new Date(dateString).toLocaleDateString('id-ID', options);
}

// ==================== MODAL ====================
function showModal(title, content, buttons = []) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5>${title}</h5>
                </div>
                <div class="modal-body">
                    ${content}
                </div>
                <div class="modal-footer">
                    ${buttons.map(btn => `<button class="${btn.class}">${btn.text}</button>`).join('')}
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    
    // Close modal logic
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.remove();
        }
    });
    
    return modal;
}

// ==================== CHARACTER COUNTER ====================
function setupCharacterCounter(textareaSelector, limitSelector, maxLength = 5000) {
    const textarea = document.querySelector(textareaSelector);
    const limitSpan = document.querySelector(limitSelector);
    
    if (textarea) {
        textarea.addEventListener('input', function() {
            const remaining = maxLength - this.value.length;
            if (limitSpan) {
                limitSpan.textContent = remaining;
                if (remaining < 500) {
                    limitSpan.parentElement?.classList.add('text-warning');
                } else {
                    limitSpan.parentElement?.classList.remove('text-warning');
                }
            }
        });
    }
}
