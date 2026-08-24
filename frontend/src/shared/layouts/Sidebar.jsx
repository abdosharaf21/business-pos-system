import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useTranslation } from "react-i18next";
import { LogOut, X, Building2, ArrowLeft } from "lucide-react";
import { getVisibleModules, getVisibleSidebarGroups, getContextBack } from "./navigationConfig";

export default function Sidebar({ isOpen, onClose, activeModuleId }) {
  const { logout, user } = useAuth();
  const { t, i18n } = useTranslation();
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const isRtl = i18n.language === "ar";

  const modules = getVisibleModules(user?.role);
  const groups = getVisibleSidebarGroups(activeModuleId, user?.role);
  const contextBack = getContextBack(pathname);

  const handleLogout = async () => {
    await logout();
  };

  const initials = user?.full_name
    ? user.full_name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    : "?";

  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-surface-900/40 backdrop-blur-sm transition-opacity lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed top-0 start-0 z-50 h-full w-64 bg-white dark:bg-surface-900 border-e border-surface-200/80 dark:border-surface-800 flex flex-col transition-transform duration-300 ease-out
          lg:translate-x-0 ${isOpen ? "translate-x-0" : (isRtl ? "translate-x-full" : "-translate-x-full")}`}
        role="navigation"
        aria-label="Module navigation"
      >
        {/* Brand */}
        <div className="flex items-center justify-between px-5 py-5 border-b border-surface-100 dark:border-surface-800">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center shadow-sm shadow-primary-500/25">
              <Building2 className="w-5 h-5 text-white" strokeWidth={2.2} />
            </div>
            <div>
              <span className="text-[15px] font-bold text-surface-900 tracking-tight dark:text-surface-100">{t("common.appName")}</span>
              <p className="text-[10px] text-surface-400 font-medium -mt-0.5 tracking-wide uppercase">{t("common.appSubtitle")}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="lg:hidden text-surface-400 hover:text-surface-600 p-1.5 rounded-lg hover:bg-surface-100 dark:hover:bg-surface-800 dark:hover:text-surface-300 transition-colors"
            aria-label={t("common.closeSidebar")}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Mobile module switcher */}
        <div className="lg:hidden px-3 pt-4 pb-1 border-b border-surface-100 dark:border-surface-800">
          <div className="flex gap-1 overflow-x-auto scrollbar-thin">
            {modules.map((module) => {
              const Icon = module.icon;
              const isActive = module.id === activeModuleId;
              return (
                <NavLink
                  key={module.id}
                  to={module.to}
                  onClick={onClose}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-[12px] font-medium whitespace-nowrap transition-all duration-150 ${
                    isActive
                      ? "bg-primary-50 text-primary-700 shadow-sm shadow-primary-500/5 dark:bg-primary-500/10 dark:text-primary-300"
                      : "text-surface-500 hover:bg-surface-50 hover:text-surface-800 dark:text-surface-400 dark:hover:bg-surface-800 dark:hover:text-surface-200"
                  }`}
                  aria-current={isActive ? "page" : undefined}
                >
                  <Icon
                    className={`w-4 h-4 ${isActive ? "text-primary-600 dark:text-primary-400" : "text-surface-400"}`}
                    strokeWidth={isActive ? 2.2 : 1.8}
                  />
                  {t(module.labelKey)}
                </NavLink>
              );
            })}
          </div>
        </div>

        {/* Module navigation */}
        <nav className="flex-1 px-3 py-4 space-y-5 overflow-y-auto scrollbar-thin" aria-label="Sidebar navigation">
          {contextBack && (
            <button
              onClick={() => navigate(contextBack.to)}
              className="flex items-center gap-2 w-full px-3 py-2.5 rounded-xl text-[12px] font-semibold text-surface-500 dark:text-surface-400 bg-surface-50 dark:bg-surface-800 ring-1 ring-surface-200/70 dark:ring-surface-700 hover:text-primary-700 dark:hover:text-primary-300 hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors"
              aria-label={t(contextBack.labelKey)}
            >
              <ArrowLeft className={`w-4 h-4 shrink-0 ${isRtl ? "rotate-180" : ""}`} />
              {t(contextBack.labelKey)}
            </button>
          )}
          {groups.map((group) => (
            <div key={group.labelKey}>
              <p className="px-3 mb-2 text-[10px] font-semibold text-surface-400 uppercase tracking-wider">
                {t(group.labelKey)}
              </p>
              <div className="space-y-0.5">
                {group.items.map(({ to, labelKey, icon: Icon }) => (
                  <NavLink
                    key={to}
                    to={to}
                    onClick={onClose}
                    className={({ isActive }) =>
                      `relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-[13px] font-medium transition-all duration-150
                      ${
                        isActive
                          ? "bg-primary-50 text-primary-700 shadow-sm shadow-primary-500/5 dark:bg-primary-500/10 dark:text-primary-300"
                          : "text-surface-500 hover:bg-surface-50 hover:text-surface-800 dark:text-surface-400 dark:hover:bg-surface-800 dark:hover:text-surface-200"
                      }`
                    }
                  >
                    {({ isActive }) => (
                      <>
                        {isActive && (
                          <span className="absolute start-0 top-1/2 -translate-y-1/2 w-[3px] h-5 bg-primary-600 rounded-e-full" />
                        )}
                        <Icon
                          className={`w-[18px] h-[18px] shrink-0 ${
                            isActive ? "text-primary-600 dark:text-primary-400" : "text-surface-400"
                          }`}
                          strokeWidth={isActive ? 2.2 : 1.8}
                        />
                        {t(labelKey)}
                      </>
                    )}
                  </NavLink>
                ))}
              </div>
            </div>
          ))}
        </nav>

        {/* User Profile + Logout */}
        <div className="px-3 py-4 border-t border-surface-100 dark:border-surface-800">
          {user && (
            <div className="flex items-center gap-3 px-3 mb-3">
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-xs font-bold text-white shrink-0 shadow-sm shadow-primary-500/20">
                {initials}
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-[13px] font-semibold text-surface-800 truncate dark:text-surface-100">{user.full_name}</p>
                <p className="text-[11px] text-surface-400 truncate">{user.email}</p>
              </div>
            </div>
          )}
          {user?.role && (
            <div className="px-3 mb-3">
              <span className="inline-flex items-center text-[10px] font-semibold px-2.5 py-1 rounded-full bg-surface-100 text-surface-500 dark:bg-surface-800 dark:text-surface-400 uppercase tracking-wider capitalize">
                {user.role}
              </span>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-[13px] font-medium text-surface-500 dark:text-surface-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-500/10 dark:hover:text-red-400 transition-all duration-150"
            aria-label={t("common.signOut")}
          >
            <LogOut className={`w-[18px] h-[18px] ${isRtl ? "rotate-180" : ""}`} strokeWidth={1.8} />
            {t("common.signOut")}
          </button>
        </div>
      </aside>
    </>
  );
}
