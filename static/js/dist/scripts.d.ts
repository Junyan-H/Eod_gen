declare global {
    interface Window {
        formatDuration: (minutes: number) => string;
        copyToClipboard: (text: string) => Promise<void>;
        showToast: (message: string, type?: ToastType) => void;
    }
}
type ToastType = 'info' | 'success' | 'error' | 'warning';
declare function formatDuration(minutes: number): string;
declare function copyToClipboard(text: string): Promise<void>;
declare function showToast(message: string, type?: ToastType): void;
export { formatDuration, copyToClipboard, showToast, ToastType };
//# sourceMappingURL=scripts.d.ts.map