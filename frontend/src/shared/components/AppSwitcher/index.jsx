import { useState, useRef, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { ChevronDown, Check } from "lucide-react";
import { useAuth } from "../../context/AuthContext";
import {
  APPLICATIONS,
  getActiveApplication,
  getApplicationDefaultPath,
  getVisibleApplications,
} from "../../layouts/navigationConfig";

export default function AppSwitcher() {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const isRtl = i18n.language === "ar";

  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  const activeAppId = getActiveApplication(pathname);
  const activeApp = APPLICATIONS.find((a) => a.id === activeAppId) || APPLICATIONS[0];
  const apps = getVisibleApplications(user?.role);

  useEffect(() => {
    function handleClickOutside(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSwitch = (appId) => {
    setOpen(false);
    if (appId !== activeAppId) {
      navigate(getApplicationDefaultPath(appId));
    }
  };

  const ActiveIcon = activeApp.icon;

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-[13px] font-semibold bg-primary-50 text-primary-700 hover:bg-primary-100 transition-colors dark:bg-primary-500/10 dark:text-primary-300 dark:hover:bg-primary-500/20"
        aria-label={t("appSwitcher.label")}
        aria-expanded={open}
        aria-haspopup="listbox"
      >
        <ActiveIcon className="w-4 h-4" strokeWidth={2} />
        <span className="hidden sm:inline">{t(activeApp.labelKey)}</span>
        <ChevronDown
          className={`w-3.5 h-3.5 transition-transform duration-150 ${open ? "rotate-180" : ""}`}
          strokeWidth={2.5}
        />
      </button>

      {open && (
        <div
          className={`absolute top-full mt-2 z-50 min-w-[200px] bg-white dark:bg-surface-800 rounded-xl border border-surface-200/80 dark:border-surface-700/60 shadow-xl py-1.5 animate-in-fast ${
            isRtl ? "start-0" : "end-0"
          }`}
          role="listbox"
          aria-label={t("appSwitcher.selectApp")}
        >
          <p className="px-3 py-1.5 text-[10px] font-semibold text-surface-400 uppercase tracking-wider">
            {t("appSwitcher.applications")}
          </p>
          {apps.map((app) => {
            const Icon = app.icon;
            const isActive = app.id === activeAppId;
            return (
              <button
                key={app.id}
                onClick={() => handleSwitch(app.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 text-[13px] font-medium transition-colors ${
                  isActive
                    ? "bg-primary-50 text-primary-700 dark:bg-primary-500/10 dark:text-primary-300"
                    : "text-surface-600 hover:bg-surface-50 dark:text-surface-300 dark:hover:bg-surface-700/50"
                }`}
                role="option"
                aria-selected={isActive}
              >
                <Icon
                  className={`w-4 h-4 shrink-0 ${
                    isActive
                      ? "text-primary-600 dark:text-primary-400"
                      : "text-surface-400"
                  }`}
                  strokeWidth={1.8}
                />
                <span className="flex-1 text-start">{t(app.labelKey)}</span>
                {isActive && (
                  <Check className="w-4 h-4 text-primary-600 dark:text-primary-400 shrink-0" strokeWidth={2.5} />
                )}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
