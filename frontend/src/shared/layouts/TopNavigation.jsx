import { useState, useEffect } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Menu, Building2 } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useStoreSettings } from "../hooks/useStoreSettings";
import { getLogoUrl } from "../services/storeSettings";
import LanguageSwitcher from "../components/LanguageSwitcher";
import DarkModeToggle from "../components/DarkModeToggle";
import NotificationBell from "../components/NotificationBell";
import GlobalSearch from "../components/GlobalSearch";
import QuickActionBar from "../components/QuickActionBar";
import {
  getActiveApplication,
  getAppTabs,
  getQuickActions,
  getBreadcrumb,
} from "./navigationConfig";

function LiveClock() {
  const { t, i18n } = useTranslation();
  const [now, setNow] = useState(() => new Date());

  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 60_000);
    return () => clearInterval(id);
  }, []);

  const locale = i18n.language === "ar" ? "ar-EG" : "en-US";
  const time = now.toLocaleTimeString(locale, { hour: "numeric", minute: "2-digit" });
  const date = now.toLocaleDateString(locale, { day: "numeric", month: "short" });

  return (
    <div
      className="hidden xl:flex flex-col items-end leading-tight pe-2"
      title={t("header.clock.now")}
    >
      <span className="text-[13px] font-semibold text-surface-700 tabular-nums dark:text-surface-100">{time}</span>
      <span className="text-[10px] font-medium text-surface-400">{date}</span>
    </div>
  );
}

export default function TopNavigation({ onOpenSidebar }) {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const { data: settings } = useStoreSettings();
  const { pathname } = useLocation();
  const isRtl = i18n.language === "ar";

  const activeAppId = getActiveApplication(pathname);
  const tabs = getAppTabs(activeAppId, user?.role);
  const quickActions = getQuickActions(activeAppId, user?.role);
  const { sectionLabelKey } = getBreadcrumb(pathname);

  const storeName = settings?.store_name || t("common.appName");
  const logoUrl = getLogoUrl();

  const showSecondRow = tabs.length > 0 || quickActions.length > 0;

  return (
    <header className="sticky top-0 z-30 bg-white/80 backdrop-blur-xl border-b border-surface-200/60 dark:bg-surface-900/80 dark:border-surface-800">
      {/* Row 1 */}
      <div className="flex items-center gap-2 sm:gap-3 px-3 sm:px-5 lg:px-6 py-3">
        {/* Mobile menu trigger */}
        <button
          onClick={onOpenSidebar}
          className="lg:hidden p-2 -ms-1 text-surface-500 hover:bg-surface-100 rounded-lg transition-colors dark:text-surface-400 dark:hover:bg-surface-800"
          aria-label={t("common.openMenu")}
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Brand */}
        <div className="flex items-center gap-2.5 lg:pe-4 lg:me-1 lg:border-e lg:border-surface-200/60 min-w-0">
          {logoUrl ? (
            <img
              src={logoUrl}
              alt=""
              className="w-9 h-9 rounded-lg object-cover shadow-sm ring-1 ring-surface-200/60 shrink-0"
            />
          ) : (
            <div className="w-9 h-9 bg-primary-700 rounded-lg flex items-center justify-center shadow-sm shrink-0">
              <Building2 className="w-5 h-5 text-white" strokeWidth={2.2} />
            </div>
          )}
          <div className="hidden sm:block min-w-0">
            <span className="block text-[15px] font-bold text-surface-900 tracking-tight leading-tight truncate dark:text-surface-100">
              {storeName}
            </span>
          </div>
        </div>

        {/* Breadcrumb */}
        <div className="hidden lg:flex items-center gap-2 flex-1 min-w-0 px-3">
          <span className="text-[13px] font-semibold text-surface-600 truncate dark:text-surface-300">
            {t(sectionLabelKey)}
          </span>
        </div>

        {/* Global actions */}
        <div className="ms-auto flex items-center gap-1 sm:gap-2">
          <GlobalSearch />
          <NotificationBell />
          <DarkModeToggle />
          <LanguageSwitcher />
          <LiveClock />
        </div>
      </div>

      {/* Row 2 - app-specific tabs + quick actions */}
      {showSecondRow && (
        <div
          className={`flex items-center gap-3 px-3 sm:px-5 lg:px-6 py-2 border-t border-surface-100/70 dark:border-surface-800/70 ${
            quickActions.length === 0 && tabs.length === 0 ? "max-lg:hidden" : ""
          }`}
        >
          <nav
            className="hidden lg:flex flex-1 items-center gap-1 overflow-x-auto scrollbar-thin"
            aria-label="Main navigation"
          >
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = pathname === tab.to || pathname.startsWith(`${tab.to}/`);
              return (
                <NavLink
                  key={tab.id}
                  to={tab.to}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[12px] font-medium transition-all duration-150 whitespace-nowrap ${
                    isActive
                      ? "bg-primary-50 text-primary-700 shadow-sm shadow-primary-500/5 dark:bg-primary-500/10 dark:text-primary-300"
                      : "text-surface-500 hover:bg-surface-50 hover:text-surface-800 dark:text-surface-400 dark:hover:bg-surface-700/50 dark:hover:text-surface-200"
                  }`}
                  aria-current={isActive ? "page" : undefined}
                >
                  <Icon
                    className={`w-4 h-4 ${isActive ? "text-primary-600 dark:text-primary-400" : "text-surface-400"}`}
                    strokeWidth={isActive ? 2.2 : 1.8}
                  />
                  {t(tab.labelKey)}
                </NavLink>
              );
            })}
          </nav>

          <QuickActionBar actions={quickActions} activeModuleId={activeAppId} />
        </div>
      )}
    </header>
  );
}
