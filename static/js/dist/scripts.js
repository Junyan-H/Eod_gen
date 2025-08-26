// EOD Generator TypeScript functionality
// Utility type guards
const isHTMLElement = (element) => {
    return element instanceof HTMLElement;
};
const isHTMLInputElement = (element) => {
    return element instanceof HTMLInputElement;
};
const isHTMLTextAreaElement = (element) => {
    return element instanceof HTMLTextAreaElement;
};
const isHTMLSelectElement = (element) => {
    return element instanceof HTMLSelectElement;
};
const isHTMLFormElement = (element) => {
    return element instanceof HTMLFormElement;
};
const isHTMLButtonElement = (element) => {
    return element instanceof HTMLButtonElement;
};
// Main initialization
document.addEventListener('DOMContentLoaded', () => {
    initializeAlertDismissal();
    initializeDangerousFormConfirmation();
    initializeAutoFocus();
    initializeAutoResize();
    initializeActiveTimers();
    initializeFormValidation();
    initializeKeyboardShortcuts();
    enhanceFormInputs();
});
// Auto-dismiss alerts after 5 seconds
function initializeAlertDismissal() {
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach((alert) => {
        setTimeout(() => {
            const closeButton = alert.querySelector('.btn-close');
            if (isHTMLElement(closeButton)) {
                closeButton.click();
            }
        }, 5000);
    });
}
// Confirm form submission for dangerous actions
function initializeDangerousFormConfirmation() {
    const dangerousForms = document.querySelectorAll('form[data-confirm]');
    dangerousForms.forEach((form) => {
        if (isHTMLFormElement(form)) {
            form.addEventListener('submit', function (e) {
                const message = this.getAttribute('data-confirm') ?? 'Are you sure?';
                if (!confirm(message)) {
                    e.preventDefault();
                }
            });
        }
    });
}
// Auto-focus on first input field
function initializeAutoFocus() {
    const firstInput = document.querySelector('input[type="text"]:not([readonly])');
    if (firstInput && isHTMLInputElement(firstInput)) {
        firstInput.focus();
    }
}
// Auto-resize textareas
function initializeAutoResize() {
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach((textarea) => {
        if (isHTMLTextAreaElement(textarea)) {
            textarea.addEventListener('input', function () {
                this.style.height = 'auto';
                this.style.height = `${this.scrollHeight}px`;
            });
        }
    });
}
// Live time updates for active blockers
function initializeActiveTimers() {
    updateActiveTimes();
    setInterval(updateActiveTimes, 60000); // Update every minute
}
function updateActiveTimes() {
    const activeTimers = document.querySelectorAll('[data-start-time]');
    activeTimers.forEach((timer) => {
        const startTimeAttr = timer.getAttribute('data-start-time');
        if (!startTimeAttr)
            return;
        const startTime = new Date(startTimeAttr);
        const now = new Date();
        const diff = Math.floor((now.getTime() - startTime.getTime()) / (1000 * 60)); // minutes
        const hours = Math.floor(diff / 60);
        const minutes = diff % 60;
        timer.textContent = `${hours}h ${minutes}m`;
    });
}
// Form validation improvements
function initializeFormValidation() {
    const forms = document.querySelectorAll('form');
    forms.forEach((form) => {
        if (isHTMLFormElement(form)) {
            form.addEventListener('submit', function (e) {
                const submitButton = this.querySelector('button[type="submit"]');
                if (isHTMLButtonElement(submitButton)) {
                    const originalText = submitButton.innerHTML;
                    submitButton.disabled = true;
                    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Processing...';
                    // Re-enable after a delay in case of errors
                    setTimeout(() => {
                        if (isHTMLButtonElement(submitButton)) {
                            submitButton.disabled = false;
                            const dataOriginalText = submitButton.getAttribute('data-original-text');
                            submitButton.innerHTML = dataOriginalText ?? originalText.replace('<i class="fas fa-spinner fa-spin me-1"></i>Processing...', submitButton.textContent ?? '');
                        }
                    }, 3000);
                }
            });
        }
    });
}
// Keyboard shortcuts
function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + Enter to submit forms
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const activeElement = document.activeElement;
            if (activeElement) {
                const form = activeElement.closest('form');
                if (isHTMLFormElement(form)) {
                    const submitButton = form.querySelector('button[type="submit"]');
                    if (isHTMLButtonElement(submitButton) && !submitButton.disabled) {
                        submitButton.click();
                    }
                }
            }
        }
        // Escape to close modals
        if (e.key === 'Escape') {
            const modals = document.querySelectorAll('.modal.show');
            modals.forEach((modal) => {
                const closeButton = modal.querySelector('.btn-close');
                if (isHTMLElement(closeButton)) {
                    closeButton.click();
                }
            });
        }
    });
}
// Utility functions
function formatDuration(minutes) {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
}
function copyToClipboard(text) {
    return navigator.clipboard.writeText(text)
        .then(() => {
        showToast('Copied to clipboard!', 'success');
    })
        .catch((err) => {
        console.error('Could not copy text: ', err);
        showToast('Failed to copy to clipboard', 'error');
    });
}
function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    const alertType = type === 'error' ? 'danger' : type;
    toast.className = `alert alert-${alertType} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(toast);
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 3000);
}
// Enhanced form handling for better UX
function enhanceFormInputs() {
    // Add input validation feedback
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach((input) => {
        if (isHTMLInputElement(input) || isHTMLTextAreaElement(input) || isHTMLSelectElement(input)) {
            input.addEventListener('blur', function () {
                if (this.checkValidity()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                }
                else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            });
            input.addEventListener('input', function () {
                this.classList.remove('is-invalid', 'is-valid');
            });
        }
    });
}
// Make functions available globally
window.formatDuration = formatDuration;
window.copyToClipboard = copyToClipboard;
window.showToast = showToast;
// Export for module usage
export { formatDuration, copyToClipboard, showToast };
//# sourceMappingURL=scripts.js.map