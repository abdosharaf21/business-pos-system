import { Inbox } from "lucide-react";

/**
 * Shared empty-state placeholder.
 *
 * Renders a centered icon + title (+ optional description/action).
 * Use `compact` for dense surfaces like dashboard panels; the default
 * size suits full-page empty states.
 */
export function EmptyState({
  icon: Icon = Inbox,
  title,
  description,
  action,
  compact = false,
}) {
  const containerClass = compact
    ? "flex flex-col items-center justify-center py-10 text-center px-4"
    : "flex flex-col items-center justify-center py-20 text-center";
  const iconWrapperClass = compact
    ? "w-12 h-12 bg-surface-100 dark:bg-surface-700/50 rounded-xl flex items-center justify-center mb-3 ring-1 ring-surface-200/60"
    : "w-16 h-16 bg-surface-100 dark:bg-surface-700/50 rounded-2xl flex items-center justify-center mb-5 ring-1 ring-surface-200/60 dark:ring-surface-600/50";
  const iconClass = compact
    ? "w-6 h-6 text-surface-400"
    : "w-7 h-7 text-surface-400";
  const titleClass = compact
    ? "text-[13px] font-semibold text-surface-600 dark:text-surface-300"
    : "text-base font-bold text-surface-800 dark:text-surface-100 mb-1";
  const descriptionClass = compact
    ? "text-[12px] text-surface-400 mt-1 max-w-xs leading-relaxed"
    : "text-sm text-surface-400 mb-6 max-w-sm leading-relaxed";

  return (
    <div className={containerClass}>
      <div className={iconWrapperClass}>
        <Icon className={iconClass} strokeWidth={1.5} />
      </div>
      {compact ? (
        <p className={titleClass}>{title}</p>
      ) : (
        <h3 className={titleClass}>{title}</h3>
      )}
      {description && (
        <p className={descriptionClass}>{description}</p>
      )}
      {action && <div>{action}</div>}
    </div>
  );
}
