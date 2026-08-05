import { useNavigate } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { Zap } from "lucide-react";

const REFRESH_PREFIXES = {
  dashboard: ["dashboard"],
  inventory: ["inventory", "reports-"],
  purchases: ["purchases"],
  reports: ["reports-"],
  settings: ["store-settings", "users"],
};

function getDisabledHint(t, id) {
  if (id === "export") return t("header.quickActions.exportHint");
  if (id === "backup") return t("header.quickActions.backupHint");
  return t("header.quickActions.comingSoon");
}

export default function QuickActionBar({ actions, activeModuleId }) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  if (!actions || actions.length === 0) return null;

  const handleAction = (action) => {
    if (action.kind === "disabled") return;
    if (action.kind === "print") {
      window.print();
      return;
    }
    if (action.kind === "refresh") {
      const prefixes = REFRESH_PREFIXES[activeModuleId] || [];
      queryClient.refetchQueries({
        predicate: (query) =>
          prefixes.some((prefix) => String(query.queryKey[0] || "").startsWith(prefix)),
      });
      return;
    }
    if (action.to) navigate(action.to);
  };

  return (
    <div className="flex items-center gap-1.5 ms-auto">
      <span className="hidden md:flex items-center gap-1.5 px-1 text-[10px] font-semibold text-surface-400 uppercase tracking-wider">
        <Zap className="w-3 h-3" />
        {t("header.quickActions.label")}
      </span>
      {actions.map((action) => {
        const Icon = action.icon;
        const disabled = action.kind === "disabled";
        return (
          <button
            key={action.id}
            onClick={() => handleAction(action)}
            disabled={disabled}
            title={disabled ? getDisabledHint(t, action.id) : t(action.labelKey)}
            className={`inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-[12px] font-medium transition-all duration-150 whitespace-nowrap ${
              disabled
                ? "text-surface-300 cursor-not-allowed"
                : "text-surface-600 hover:bg-surface-100 hover:text-surface-800"
            }`}
          >
            <Icon className={`w-3.5 h-3.5 ${disabled ? "" : "text-surface-400"}`} strokeWidth={1.8} />
            <span className="hidden sm:inline">{t(action.labelKey)}</span>
            {disabled && (
              <span className="hidden sm:inline-flex px-1.5 py-0.5 rounded-md bg-surface-100 text-[9px] font-bold text-surface-400 uppercase tracking-wide">
                {t("header.quickActions.comingSoon")}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
