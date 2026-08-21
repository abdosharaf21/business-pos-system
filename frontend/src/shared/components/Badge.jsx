export function Badge({ children, variant = "default" }) {
  const variants = {
    default: "bg-surface-100 text-surface-600 ring-surface-200 dark:bg-surface-700/50 dark:text-surface-300 dark:ring-surface-600/50",
    success: "bg-emerald-50 text-emerald-700 ring-emerald-200/60 dark:bg-emerald-500/10 dark:text-emerald-400 dark:ring-emerald-500/20",
    warning: "bg-amber-50 text-amber-700 ring-amber-200/60 dark:bg-amber-500/10 dark:text-amber-400 dark:ring-amber-500/20",
    danger: "bg-red-50 text-red-700 ring-red-200/60 dark:bg-red-500/10 dark:text-red-400 dark:ring-red-500/20",
    info: "bg-sky-50 text-sky-700 ring-sky-200/60 dark:bg-sky-500/10 dark:text-sky-400 dark:ring-sky-500/20",
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-semibold ring-1 ring-inset ${variants[variant]}`}
    >
      {children}
    </span>
  );
}

export function statusBadge(status) {
  const map = {
    active: "success",
    inactive: "danger",
    lead: "info",
    prospect: "warning",
    customer: "success",
    pending: "warning",
    in_progress: "info",
    completed: "success",
    cancelled: "danger",
    archived: "default",
    expired: "danger",
    expiring_soon: "warning",
    normal: "success",
  };
  return map[status] || "default";
}
