import { Inbox } from "lucide-react";

export function EmptyState({ icon: Icon = Inbox, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center py-20 text-center">
      <div className="w-16 h-16 bg-surface-100 rounded-2xl flex items-center justify-center mb-5 ring-1 ring-surface-200/60">
        <Icon className="w-7 h-7 text-surface-400" strokeWidth={1.5} />
      </div>
      <h3 className="text-base font-bold text-surface-800 mb-1">{title}</h3>
      {description && (
        <p className="text-sm text-surface-400 mb-6 max-w-sm leading-relaxed">{description}</p>
      )}
      {action && <div>{action}</div>}
    </div>
  );
}
