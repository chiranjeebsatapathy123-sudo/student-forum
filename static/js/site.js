document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts with [data-autodismiss]
    (function autoDismissAlerts() {
        const alerts = document.querySelectorAll('.alert[data-autodismiss="true"]');
        alerts.forEach(alertEl => {
            const delay = 5000; // 5s
            setTimeout(() => {
                try {
                    const bsAlert = bootstrap.Alert.getOrCreateInstance(alertEl);
                    bsAlert.close();
                } catch (e) { /* ignore */ }
            }, delay);
        });
    })();

    // Bootstrap-style client-side validation helper
    (function formValidation() {
        const forms = document.querySelectorAll('.needs-validation');
        Array.prototype.slice.call(forms).forEach(function(form) {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                    form.classList.add('was-validated');
                    // focus first invalid control
                    const firstInvalid = form.querySelector(':invalid');
                    if (firstInvalid) firstInvalid.focus();
                }
            }, false);
        });
    })();

    // Small enhancement: add accessible descriptions for form feedback
    const invalidFeedbacks = document.querySelectorAll('.invalid-feedback');
    invalidFeedbacks.forEach((fb, idx) => {
        const input = fb.closest('.mb-3')?.querySelector('input,textarea,select');
        if (input && !input.getAttribute('aria-describedby')) {
            const id = fb.id || ('invalid-feedback-' + idx);
            fb.id = id;
            input.setAttribute('aria-describedby', id);
        }
    });

    // Toast System
    window.showToast = function(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) return;
        
        const icons = {
            'success': 'fa-check-circle text-success',
            'error': 'fa-exclamation-circle text-danger',
            'warning': 'fa-exclamation-triangle text-warning',
            'info': 'fa-info-circle text-primary'
        };
        
        const toastId = 'toast-' + Date.now();
        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center border-0 mb-2" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body d-flex align-items-center fw-medium">
                        <i class="fas ${icons[type] || icons['info']} me-2 fs-5"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;
        
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        const toastElement = document.getElementById(toastId);
        const bsToast = new bootstrap.Toast(toastElement, { delay: 4000 });
        bsToast.show();
        
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    };

    // Command Palette (Ctrl+K)
    const cmdPaletteModal = document.getElementById('commandPalette');
    let bsCmdPalette = null;
    if (cmdPaletteModal) {
        bsCmdPalette = new bootstrap.Modal(cmdPaletteModal);
        
        document.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                bsCmdPalette.toggle();
            }
        });
        
        cmdPaletteModal.addEventListener('shown.bs.modal', function () {
            document.getElementById('cmd-input').focus();
        });
    }

    // Markdown Rendering & Syntax Highlighting
    if (typeof marked !== 'undefined') {
        marked.setOptions({
            breaks: true,
            gfm: true
        });
        
        const mdElements = document.querySelectorAll('.post-content, .comment-content');
        mdElements.forEach(el => {
            // Sanitize and render
            const rawContent = el.textContent;
            const dirtyHtml = marked.parse(rawContent);
            
            if (typeof DOMPurify !== 'undefined') {
                el.innerHTML = DOMPurify.sanitize(dirtyHtml);
            } else {
                el.innerHTML = dirtyHtml; // fallback if DOMPurify not loaded
            }
            
            el.classList.add('markdown-body');
            
            // Add copy buttons to code blocks
            el.querySelectorAll('pre').forEach(pre => {
                const btn = document.createElement('button');
                btn.className = 'copy-btn';
                btn.innerHTML = '<i class="far fa-copy"></i> Copy';
                pre.appendChild(btn);
                
                btn.addEventListener('click', () => {
                    const code = pre.querySelector('code');
                    if (code) {
                        navigator.clipboard.writeText(code.innerText).then(() => {
                            btn.innerHTML = '<i class="fas fa-check"></i> Copied';
                            setTimeout(() => {
                                btn.innerHTML = '<i class="far fa-copy"></i> Copy';
                            }, 2000);
                        });
                    }
                });
            });
            
            // Apply highlight.js
            if (typeof hljs !== 'undefined') {
                el.querySelectorAll('pre code').forEach((block) => {
                    hljs.highlightElement(block);
                });
            }
        });
    }

    // Unsaved changes warning
    let formChanged = false;
    document.querySelectorAll('.track-changes input, .track-changes textarea, .track-changes select').forEach(el => {
        el.addEventListener('change', () => formChanged = true);
        el.addEventListener('keyup', () => formChanged = true);
    });
    
    document.querySelectorAll('.track-changes').forEach(form => {
        form.addEventListener('submit', () => formChanged = false);
    });

    window.addEventListener('beforeunload', function (e) {
        if (formChanged) {
            e.preventDefault();
            e.returnValue = '';
        }
    });
});