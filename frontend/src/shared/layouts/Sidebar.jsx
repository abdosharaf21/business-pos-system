import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useTranslation } from "react-i18next";
import { LogOut, X, Building2, ArrowLeft } from "lucide-react";
import { getActiveApplication, getAppTabs, getAppSidebarGroups, getBackRoute } from "./navigationConfig";
import { getLogoUrl } from "../services/storeSettings";


export default function Sidebar({ isOpen, onClose }) {
  const { logout, user } = useAuth();
  const { t, i18n } = useTranslation();
  const { pathname } = useLocation();
  const navigate = useNavigate();
  const isRtl = i18n.language === "ar";

  const activeAppId = getActiveApplication(pathname);
  const tabs = getAppTabs(activeAppId, user?.role);
  const groups = getAppSidebarGroups(activeAppId, user?.role);
  const logoUrl = getLogoUrl();

  const handleLogout = async () => {
    await logout();
  };

  const backRoute = getBackRoute(pathname);

  const handleBack = () => {
    navigate(backRoute);
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
        className={`fixed top-0 start-0 z-50 h-full w-[260px] bg-primary-800 flex flex-col transition-transform duration-300 ease-out
          lg:translate-x-0 ${isOpen ? "translate-x-0" : (isRtl ? "translate-x-full" : "-translate-x-full")}`}
        role="navigation"
        aria-label="Module navigation"
      >
        {/* Brand */}
        <div className="flex items-center justify-between px-5 py-5 border-b border-primary-700/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/15 rounded-xl flex items-center justify-center backdrop-blur-sm">
              {logoUrl ? (
                <img src={logoUrl} alt="" className="w-6 h-6 object-contain" />
              ) : (
                <Building2 className="w-5 h-5 text-white" strokeWidth={2.2} />
              )}
            </div>
            <div>
              <span className="text-[15px] font-bold text-white tracking-tight">{t("common.appName")}</span>
              <p className="text-[10px] text-primary-300 font-medium -mt-0.5 tracking-wide uppercase">{t("common.appSubtitle")}</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="lg:hidden text-primary-300 hover:text-white p-1.5 rounded-lg hover:bg-white/10 transition-colors"
            aria-label={t("common.closeSidebar")}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Mobile tab switcher */}
        <div className="lg:hidden px-3 pt-4 pb-1 border-b border-primary-700/50">
          <div className="flex gap-1 overflow-x-auto scrollbar-thin">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = pathname === tab.to || pathname.startsWith(`${tab.to}/`);
              return (
                <NavLink
                  key={tab.id}
                  to={tab.to}
                  onClick={onClose}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-[12px] font-medium whitespace-nowrap transition-all duration-150 ${
                    isActive
                      ? "bg-white/15 text-white"
                      : "text-primary-300 hover:bg-white/10 hover:text-white"
                  }`}
                  aria-current={isActive ? "page" : undefined}
                >
                  <Icon
                    className={`w-4 h-4 ${isActive ? "text-white" : "text-primary-400"}`}
                    strokeWidth={isActive ? 2.2 : 1.8}
                  />
                  {t(tab.labelKey)}
                </NavLink>
              );
            })}
          </div>
        </div>

        {/* Back button — above app-specific navigation */}
        {backRoute && (
          <div className="px-3 pt-3">
            <button
              onClick={handleBack}
              className="flex items-center gap-2 w-full px-3 py-2 rounded-lg text-[13px] font-medium text-primary-200 hover:bg-white/10 hover:text-white transition-all duration-150"
            >
              <ArrowLeft className={`w-4 h-4 ${isRtl ? "rotate-180" : ""}`} strokeWidth={1.8} />
              {t("common.back", "Back")}
            </button>
          </div>
        )}

        {/* App-specific sidebar navigation */}
        <nav className="flex-1 px-3 py-4 space-y-5 overflow-y-auto scrollbar-thin" aria-label="Sidebar navigation">
          {groups.map((group) => (
            <div key={group.labelKey}>
              <p className="px-3 mb-2 text-[10px] font-semibold text-primary-400 uppercase tracking-wider">
                {t(group.labelKey)}
              </p>
              <div className="space-y-0.5">
                {group.items.map(({ to, labelKey, icon: Icon }) => (
                  <NavLink
                    key={`${to}-${labelKey}`}
                    to={to}
                    onClick={onClose}
                    className={({ isActive }) =>
                      `relative flex items-center gap-3 px-3 py-2.5 rounded-lg text-[14px] font-medium transition-all duration-150
                      ${
                        isActive
                          ? "bg-white/15 text-white"
                          : "text-primary-200 hover:bg-white/10 hover:text-white"
                      }`
                    }
                  >
                    {({ isActive }) => (
                      <>
                        {isActive && (
                          <span className="absolute start-0 top-1/2 -translate-y-1/2 w-[3px] h-5 bg-white rounded-e-full" />
                        )}
                        <Icon
                          className={`w-5 h-5 shrink-0 ${
                            isActive ? "text-white" : "text-primary-400"
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
        <div className="px-3 py-4 border-t border-primary-700/50">
          {user && (
            <div className="flex items-center gap-3 px-3 mb-3">
              <div className="w-9 h-9 rounded-full bg-white/15 flex items-center justify-center text-xs font-bold text-white shrink-0">
                {initials}
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-[13px] font-semibold text-white truncate">{user.full_name}</p>
                <p className="text-[11px] text-primary-300 truncate">{user.email}</p>
              </div>
            </div>
          )}
          {user?.role && (
            <div className="px-3 mb-3">
              <span className="inline-flex items-center text-[10px] font-semibold px-2.5 py-1 rounded-full bg-white/10 text-primary-200 uppercase tracking-wider capitalize">
                {user.role}
              </span>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-[13px] font-medium text-primary-300 hover:bg-white/10 hover:text-white transition-all duration-150"
            aria-label={t("common.signOut")}
          >
            <LogOut className={`w-5 h-5 ${isRtl ? "rotate-180" : ""}`} strokeWidth={1.8} />
            {t("common.signOut")}
          </button>
        </div>
      </aside>
    </>
  );
}
