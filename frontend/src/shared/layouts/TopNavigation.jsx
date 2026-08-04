import { NavLink } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Menu, Building2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import LanguageSwitcher from "../components/LanguageSwitcher";
import NotificationBell from "../components/NotificationBell";
import { getVisibleModules } from "./navigationConfig";

export default function TopNavigation({ activeModuleId, onOpenSidebar }) {
  const { t } = useTranslation();
  const { user } = useAuth();
  const modules = getVisibleModules(user?.role);

  const initials = user?.full_name
    ? user.full_name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    : "?";

  return (
    <header className="sticky top-0 z-30 bg-white/80 backdrop-blur-xl border-b border-surface-200/60">
      <div className="flex items-center gap-2 sm:gap-3 px-3 sm:px-5 lg:px-6 py-3">
        {/* Mobile menu trigger */}
        <button
          onClick={onOpenSidebar}
          className="lg:hidden p-2 -ms-1 text-surface-500 hover:bg-surface-100 rounded-xl transition-colors"
          aria-label={t("common.openMenu")}
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Brand */}
        <div className="flex items-center gap-2.5 lg:pe-6 lg:me-2 lg:border-e lg:border-surface-200/60 lg:w-52">
          <div className="w-9 h-9 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center shadow-sm shadow-primary-500/25 shrink-0">
            <Building2 className="w-5 h-5 text-white" strokeWidth={2.2} />
          </div>
          <div className="hidden sm:block min-w-0">
            <span className="block text-[15px] font-bold text-surface-900 tracking-tight leading-tight truncate">
              {t("common.appName")}
            </span>
            <p className="text-[10px] text-surface-400 font-medium tracking-wide uppercase leading-tight">
              {t("common.appSubtitle")}
            </p>
          </div>
        </div>

        {/* Module navigation */}
        <nav
          className="hidden lg:flex flex-1 items-center gap-1 overflow-x-auto scrollbar-thin"
          aria-label="Main modules"
        >
          {modules.map((module) => {
            const Icon = module.icon;
            const isActive = module.id === activeModuleId;
            return (
              <NavLink
                key={module.id}
                to={module.to}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-[13px] font-medium transition-all duration-150 whitespace-nowrap ${
                  isActive
                    ? "bg-primary-50 text-primary-700 shadow-sm shadow-primary-500/5"
                    : "text-surface-500 hover:bg-surface-50 hover:text-surface-800"
                }`}
                aria-current={isActive ? "page" : undefined}
              >
                <Icon
                  className={`w-[18px] h-[18px] ${
                    isActive ? "text-primary-600" : "text-surface-400"
                  }`}
                  strokeWidth={isActive ? 2.2 : 1.8}
                />
                {t(module.labelKey)}
              </NavLink>
            );
          })}
        </nav>

        {/* Actions */}
        <div className="ms-auto flex items-center gap-2">
          <LanguageSwitcher />
          <NotificationBell />
          <div className="hidden sm:block h-6 w-px bg-surface-200" />
          {user?.full_name && (
            <div className="hidden sm:flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-[10px] font-bold text-white shadow-sm shadow-primary-500/20 shrink-0">
                {initials}
              </div>
              <div className="hidden xl:block text-end min-w-0">
                <p className="text-[13px] font-semibold text-surface-800 leading-tight truncate">
                  {user.full_name}
                </p>
                <p className="text-[11px] text-surface-400 capitalize leading-tight">{user.role}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
