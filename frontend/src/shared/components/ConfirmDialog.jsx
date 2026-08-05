import { useTranslation } from "react-i18next";
import { AlertTriangle, Loader2 } from "lucide-react";

export function ConfirmDialog({ isOpen, onClose, onConfirm, title, message, confirmText, loadingText, loading = false }) {
  const { t } = useTranslation();

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" role="alertdialog" aria-modal="true" aria-label={title}>
      <div className="absolute inset-0 bg-surface-900/40 backdrop-blur-sm" onClick={onClose} aria-hidden="true" />
      <div className="relative bg-white dark:bg-surface-800 rounded-2xl shadow-xl w-full max-w-md animate-in-fast">
        <div className="p-6">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-red-50 dark:bg-red-500/10 rounded-xl flex items-center justify-center shrink-0 ring-1 ring-red-100 dark:ring-red-500/20">
              <AlertTriangle className="w-6 h-6 text-red-500" />
            </div>
            <div className="pt-0.5">
              <h3 className="text-[15px] font-bold text-surface-900 dark:text-surface-100">{title}</h3>
              <p className="text-sm text-surface-500 dark:text-surface-400 mt-1.5 leading-relaxed">{message}</p>
            </div>
          </div>
        </div>
        <div className="flex justify-end gap-3 px-6 py-4 bg-surface-50/50 dark:bg-surface-700/30 border-t border-surface-100 dark:border-surface-700/60 rounded-b-2xl">
          <button
            onClick={onClose}
            disabled={loading}
            className="px-4 py-2.5 text-[13px] font-semibold text-surface-600 dark:text-surface-300 bg-white dark:bg-surface-700/60 border border-surface-200 dark:border-surface-700 rounded-xl hover:bg-surface-50 dark:hover:bg-surface-700 disabled:opacity-50 transition-all duration-150"
          >
            {t("common.cancel")}
          </button>
          <button
            onClick={onConfirm}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2.5 text-[13px] font-semibold text-white bg-red-600 rounded-xl hover:bg-red-700 disabled:opacity-50 transition-all duration-150 shadow-sm shadow-red-600/25"
          >
            {loading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
            {loading ? (loadingText || confirmText || t("common.confirm")) : (confirmText || t("common.confirm"))}
          </button>
        </div>
      </div>
    </div>
  );
}
