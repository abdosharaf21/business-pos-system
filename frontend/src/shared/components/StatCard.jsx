export function StatCard({ label, value, icon: Icon, color = "blue" }) {
  const colorStyles = {
    blue: {
      icon: "bg-primary-50 text-primary-600 ring-primary-100",
      value: "text-primary-600",
      accent: "from-primary-500/5 to-transparent",
    },
    green: {
      icon: "bg-emerald-50 text-emerald-600 ring-emerald-100",
      value: "text-emerald-600",
      accent: "from-emerald-500/5 to-transparent",
    },
    purple: {
      icon: "bg-violet-50 text-violet-600 ring-violet-100",
      value: "text-violet-600",
      accent: "from-violet-500/5 to-transparent",
    },
    orange: {
      icon: "bg-amber-50 text-amber-600 ring-amber-100",
      value: "text-amber-600",
      accent: "from-amber-500/5 to-transparent",
    },
    red: {
      icon: "bg-red-50 text-red-600 ring-red-100",
      value: "text-red-600",
      accent: "from-red-500/5 to-transparent",
    },
  };

  const s = colorStyles[color] || colorStyles.blue;

  return (
    <div className="bg-white rounded-2xl border border-surface-200/80 p-6 flex items-center gap-4 shadow-card hover:shadow-card-hover transition-shadow duration-200 relative overflow-hidden group">
      <div className={`absolute inset-0 bg-gradient-to-br ${s.accent} opacity-0 group-hover:opacity-100 transition-opacity duration-300`} />
      <div className={`relative w-12 h-12 rounded-xl flex items-center justify-center ring-1 ${s.icon}`}>
        <Icon className="w-[22px] h-[22px]" strokeWidth={1.8} />
      </div>
      <div className="relative min-w-0">
        <p className="text-[12px] font-semibold text-surface-400 uppercase tracking-wide">{label}</p>
        <p className="numeric-value text-2xl font-bold text-surface-900 tracking-tight mt-0.5 leading-snug">{value}</p>
      </div>
    </div>
  );
}
