import { AlertCircle, RefreshCw } from "lucide-react";

export function ErrorDisplay({ message, onRetry }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <div className="w-16 h-16 bg-red-50 rounded-2xl flex items-center justify-center mb-5 ring-1 ring-red-100">
        <AlertCircle className="w-7 h-7 text-red-400" strokeWidth={1.5} />
      </div>
      <h3 className="text-base font-bold text-surface-800 mb-1">Something went wrong</h3>
      <p className="text-sm text-surface-400 mb-6 max-w-sm leading-relaxed">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center gap-2 px-5 py-2.5 bg-surface-800 text-white rounded-xl hover:bg-surface-900 text-[13px] font-semibold transition-all duration-150 shadow-sm active:scale-[0.98]"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Try again
        </button>
      )}
    </div>
  );
}
