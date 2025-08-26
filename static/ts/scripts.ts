// EOD Generator TypeScript functionality

// Global declarations (must be at module level)
declare global {
    interface Window {
        formatDuration: (minutes: number) => string;
        copyToClipboard: (text: string) => Promise<void>;
        showToast: (message: string, type?: ToastType) => void;
    }
}

// Type definitions
type ToastType = 'info' | 'success' | 'error' | 'warning';

interface SubmitButtonState {
    disabled: boolean;
    innerHTML: string;
    originalText?: string;
}

// Utility type guards
const isHTMLElement = (element: Element | null): element is HTMLElement => {
    return element instanceof HTMLElement;
};

const isHTMLInputElement = (element: Element): element is HTMLInputElement => {
    return element instanceof HTMLInputElement;
};

const isHTMLTextAreaElement = (element: Element): element is HTMLTextAreaElement => {
    return element instanceof HTMLTextAreaElement;
};

const isHTMLSelectElement = (element: Element): element is HTMLSelectElement => {
    return element instanceof HTMLSelectElement;
};

const isHTMLFormElement = (element: Element | null): element is HTMLFormElement => {
    return element instanceof HTMLFormElement;
};

const isHTMLButtonElement = (element: Element | null): element is HTMLButtonElement => {
    return element instanceof HTMLButtonElement;
};

// Main initialization
document.addEventListener('DOMContentLoaded', (): void => {
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
function initializeAlertDismissal(): void {
    const alerts: NodeListOf<Element> = document.querySelectorAll('.alert-dismissible');
    
    alerts.forEach((alert: Element): void => {
        setTimeout((): void => {
            const closeButton: Element | null = alert.querySelector('.btn-close');
            if (isHTMLElement(closeButton)) {
                closeButton.click();
            }
        }, 5000);
    });
}

// Confirm form submission for dangerous actions
function initializeDangerousFormConfirmation(): void {
    const dangerousForms: NodeListOf<Element> = document.querySelectorAll('form[data-confirm]');
    
    dangerousForms.forEach((form: Element): void => {
        if (isHTMLFormElement(form)) {
            form.addEventListener('submit', function(this: HTMLFormElement, e: Event): void {
                const message: string = this.getAttribute('data-confirm') ?? 'Are you sure?';
                if (!confirm(message)) {
                    e.preventDefault();
                }
            });
        }
    });
}

// Auto-focus on first input field
function initializeAutoFocus(): void {
    const firstInput: Element | null = document.querySelector('input[type="text"]:not([readonly])');
    if (firstInput && isHTMLInputElement(firstInput)) {
        firstInput.focus();
    }
}

// Auto-resize textareas
function initializeAutoResize(): void {
    const textareas: NodeListOf<Element> = document.querySelectorAll('textarea');
    
    textareas.forEach((textarea: Element): void => {
        if (isHTMLTextAreaElement(textarea)) {
            textarea.addEventListener('input', function(this: HTMLTextAreaElement): void {
                this.style.height = 'auto';
                this.style.height = `${this.scrollHeight}px`;
            });
        }
    });
}

// Live time updates for active blockers
function initializeActiveTimers(): void {
    updateActiveTimes();
    setInterval(updateActiveTimes, 60000); // Update every minute
}

function updateActiveTimes(): void {
    const activeTimers: NodeListOf<Element> = document.querySelectorAll('[data-start-time]');
    
    activeTimers.forEach((timer: Element): void => {
        const startTimeAttr: string | null = timer.getAttribute('data-start-time');
        if (!startTimeAttr) return;
        
        const startTime: Date = new Date(startTimeAttr);
        const now: Date = new Date();
        const diff: number = Math.floor((now.getTime() - startTime.getTime()) / (1000 * 60)); // minutes
        
        const hours: number = Math.floor(diff / 60);
        const minutes: number = diff % 60;
        
        timer.textContent = `${hours}h ${minutes}m`;
    });
}

// Form validation improvements
function initializeFormValidation(): void {
    const forms: NodeListOf<Element> = document.querySelectorAll('form');
    
    forms.forEach((form: Element): void => {
        if (isHTMLFormElement(form)) {
            form.addEventListener('submit', function(this: HTMLFormElement, e: Event): void {
                const submitButton: Element | null = this.querySelector('button[type="submit"]');
                if (isHTMLButtonElement(submitButton)) {
                    const originalText: string = submitButton.innerHTML;
                    submitButton.disabled = true;
                    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Processing...';
                    
                    // Re-enable after a delay in case of errors
                    setTimeout((): void => {
                        if (isHTMLButtonElement(submitButton)) {
                            submitButton.disabled = false;
                            const dataOriginalText: string | null = submitButton.getAttribute('data-original-text');
                            submitButton.innerHTML = dataOriginalText ?? originalText.replace('<i class="fas fa-spinner fa-spin me-1"></i>Processing...', submitButton.textContent ?? '');
                        }
                    }, 3000);
                }
            });
        }
    });
}

// Keyboard shortcuts
function initializeKeyboardShortcuts(): void {
    document.addEventListener('keydown', (e: KeyboardEvent): void => {
        // Ctrl/Cmd + Enter to submit forms
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            const activeElement: Element | null = document.activeElement;
            if (activeElement) {
                const form: Element | null = activeElement.closest('form');
                if (isHTMLFormElement(form)) {
                    const submitButton: Element | null = form.querySelector('button[type="submit"]');
                    if (isHTMLButtonElement(submitButton) && !submitButton.disabled) {
                        submitButton.click();
                    }
                }
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const modals: NodeListOf<Element> = document.querySelectorAll('.modal.show');
            modals.forEach((modal: Element): void => {
                const closeButton: Element | null = modal.querySelector('.btn-close');
                if (isHTMLElement(closeButton)) {
                    closeButton.click();
                }
            });
        }
    });
}

// Utility functions
function formatDuration(minutes: number): string {
    const hours: number = Math.floor(minutes / 60);
    const mins: number = minutes % 60;
    return `${hours}h ${mins}m`;
}

function copyToClipboard(text: string): Promise<void> {
    return navigator.clipboard.writeText(text)
        .then((): void => {
            showToast('Copied to clipboard!', 'success');
        })
        .catch((err: Error): void => {
            console.error('Could not copy text: ', err);
            showToast('Failed to copy to clipboard', 'error');
        });
}

function showToast(message: string, type: ToastType = 'info'): void {
    // Create toast element
    const toast: HTMLDivElement = document.createElement('div');
    const alertType: string = type === 'error' ? 'danger' : type;
    
    toast.className = `alert alert-${alertType} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove after 3 seconds
    setTimeout((): void => {
        if (toast.parentNode) {
            toast.parentNode.removeChild(toast);
        }
    }, 3000);
}

// Enhanced form handling for better UX
function enhanceFormInputs(): void {
    // Add input validation feedback
    const inputs: NodeListOf<Element> = document.querySelectorAll('input, textarea, select');
    
    inputs.forEach((input: Element): void => {
        if (isHTMLInputElement(input) || isHTMLTextAreaElement(input) || isHTMLSelectElement(input)) {
            input.addEventListener('blur', function(this: HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement): void {
                if (this.checkValidity()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            });
            
            input.addEventListener('input', function(this: HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement): void {
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
export { formatDuration, copyToClipboard, showToast, ToastType };