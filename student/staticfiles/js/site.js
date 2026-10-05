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
        const input = fb.closest('.mb-3') ? .querySelector('input,textarea,select');
        if (input && !input.getAttribute('aria-describedby')) {
            const id = fb.id || ('invalid-feedback-' + idx);
            fb.id = id;
            input.setAttribute('aria-describedby', id);
        }
    });
});