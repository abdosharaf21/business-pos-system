import { useState, useEffect } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Menu, Building2, ChevronRight } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { useStoreSettings } from "../hooks/useStoreSettings";
import { getLogoUrl } from "../services/storeSettings";
import LanguageSwitcher from "../components/LanguageSwitcher";
import NotificationBell from "../components/NotificationBell";
import GlobalSearch from "../components/GlobalSearch";
import DarkModeToggle from "../components/DarkModeToggle";
import { getCurrentLocale } from "../utils/format";
import {
  getVisibleModules,
  getBreadcrumb,
} from "./navigationConfig";

function LiveClock() {
  const { t, i18n } = useTranslation();
  const [now, setNow] = useState(() => new Date());

  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 60_000);
    return () => clearInterval(id);
  }, []);

  const locale = getCurrentLocale(i18n.language);
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

export default function TopNavigation({ activeModuleId, onOpenSidebar }) {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const { data: settings } = useStoreSettings();
  const { pathname } = useLocation();
  const isRtl = i18n.language === "ar";

  const modules = getVisibleModules(user?.role);
  const { moduleLabelKey, sectionLabelKey } = getBreadcrumb(pathname);

  const storeName = settings?.store_name || t("common.appName");
  const logoUrl = getLogoUrl();

  return (
    <header className="sticky top-0 z-30 bg-white/80 backdrop-blur-xl border-b border-surface-200/60 dark:bg-surface-900 dark:border-surface-800">
      {/* Row 1 */}
      <div className="flex items-center gap-2 sm:gap-3 px-3 sm:px-5 lg:px-6 py-3">
        {/* Mobile menu trigger */}
        <button
          onClick={onOpenSidebar}
          className="lg:hidden p-2 -ms-1 text-surface-500 hover:bg-surface-100 rounded-xl transition-colors dark:text-surface-400 dark:hover:bg-surface-800"
          aria-label={t("common.openMenu")}
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Brand */}
        <div className="flex items-center gap-2.5 lg:pe-6 lg:me-2 lg:border-e lg:border-surface-200/60 lg:w-52 min-w-0">
          {logoUrl ? (
            <img
              src={logoUrl}
              alt=""
              className="w-9 h-9 rounded-xl object-cover shadow-sm ring-1 ring-surface-200/60 shrink-0"
            />
          ) : (
            <div className="w-9 h-9 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center shadow-sm shadow-primary-500/25 shrink-0">
              <Building2 className="w-5 h-5 text-white" strokeWidth={2.2} />
            </div>
          )}
          <div className="hidden sm:block min-w-0">
            <span className="block text-[15px] font-bold text-surface-900 tracking-tight leading-tight truncate dark:text-surface-100">
              {storeName}
            </span>
            <p className="text-[10px] text-surface-400 font-medium tracking-wide uppercase leading-tight">
              {t("common.appSubtitle")}
            </p>
          </div>
        </div>

        {/* Module title + breadcrumb */}
        <div className="hidden lg:block flex-1 min-w-0 px-4">
          <nav className="flex items-center gap-1.5 text-[11px] text-surface-400 mb-0.5" aria-label="Breadcrumb">
            <span className="font-medium">{t(moduleLabelKey)}</span>
            <ChevronRight className={`w-3 h-3 shrink-0 ${isRtl ? "rotate-180" : ""}`} />
            <span className="text-surface-600 font-semibold truncate dark:text-surface-300">{t(sectionLabelKey)}</span>
          </nav>
          <h1 className="text-[15px] font-bold text-surface-900 tracking-tight leading-tight truncate dark:text-surface-100">
            {t(sectionLabelKey)}
          </h1>
        </div>

        {/* Global actions */}
        <div className="ms-auto flex items-center gap-1.5 sm:gap-2.5">
          <GlobalSearch />
          <NotificationBell />
          <DarkModeToggle />
          <LanguageSwitcher />
          <LiveClock />
        </div>
      </div>

      {/* Row 2 - application switcher tabs */}
      <div className="hidden lg:flex items-center gap-3 px-3 sm:px-5 lg:px-6 py-2 border-t border-surface-100/70 dark:border-surface-800/70">
        <nav
          className="flex flex-1 items-center gap-1 overflow-x-auto scrollbar-thin"
          aria-label="Main modules"
        >
          {modules.map((module) => {
            const Icon = module.icon;
            const isActive = module.id === activeModuleId;
            return (
              <NavLink
                key={module.id}
                to={module.to}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[12px] font-medium transition-all duration-150 whitespace-nowrap ${
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
        </nav>
      </div>
    </header>
  );
}
