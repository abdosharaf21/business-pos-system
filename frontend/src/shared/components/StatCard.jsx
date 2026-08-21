export function StatCard({ label, value, icon: Icon, color = "blue" }) {
  const colorStyles = {
    blue: {
      icon: "bg-primary-50 text-primary-600 ring-primary-100 dark:bg-primary-500/10 dark:text-primary-400 dark:ring-primary-500/20",
      value: "text-primary-600 dark:text-primary-400",
    },
    green: {
      icon: "bg-emerald-50 text-emerald-600 ring-emerald-100 dark:bg-emerald-500/10 dark:text-emerald-400 dark:ring-emerald-500/20",
      value: "text-emerald-600 dark:text-emerald-400",
    },
    purple: {
      icon: "bg-violet-50 text-violet-600 ring-violet-100 dark:bg-violet-500/10 dark:text-violet-400 dark:ring-violet-500/20",
      value: "text-violet-600 dark:text-violet-400",
    },
    orange: {
      icon: "bg-amber-50 text-amber-600 ring-amber-100 dark:bg-amber-500/10 dark:text-amber-400 dark:ring-amber-500/20",
      value: "text-amber-600 dark:text-amber-400",
    },
    red: {
      icon: "bg-red-50 text-red-600 ring-red-100 dark:bg-red-500/10 dark:text-red-400 dark:ring-red-500/20",
      value: "text-red-600 dark:text-red-400",
    },
  };

  const s = colorStyles[color] || colorStyles.blue;

  return (
    <div className="bg-white dark:bg-surface-800 rounded-xl border border-surface-200/80 dark:border-surface-700/60 p-5 flex items-center gap-4 shadow-card hover:shadow-card-hover transition-shadow duration-200">
      <div className={`w-11 h-11 rounded-lg flex items-center justify-center ring-1 ${s.icon}`}>
        <Icon className="w-5 h-5" strokeWidth={1.8} />
      </div>
      <div className="min-w-0">
        <p className="text-[12px] font-semibold text-surface-400 dark:text-surface-400 uppercase tracking-wide">{label}</p>
        <p className="numeric-value text-[22px] font-bold text-surface-900 dark:text-surface-100 tracking-tight mt-0.5 leading-snug">{value}</p>
      </div>
    </div>
  );
}
