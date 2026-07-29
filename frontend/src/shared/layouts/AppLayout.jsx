import { useState } from "react";
import { Outlet } from "react-router-dom";
import { useTranslation } from "react-i18next";
import Sidebar from "./Sidebar";
import { Menu, Bell } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import LanguageSwitcher from "../components/LanguageSwitcher";

export default function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { user } = useAuth();
  const { t } = useTranslation();

  return (
    <div className="min-h-screen flex bg-surface-50">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex-1 flex flex-col lg:ms-64 min-h-screen">
        {/* Mobile header */}
        <header className="sticky top-0 z-30 bg-white/80 backdrop-blur-xl border-b border-surface-200/60 px-4 py-3 flex items-center justify-between lg:hidden">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-2 text-surface-500 hover:bg-surface-100 rounded-xl transition-colors"
              aria-label={t("common.openMenu")}
            >
              <Menu className="w-5 h-5" />
            </button>
            <span className="text-[15px] font-bold text-surface-900 tracking-tight">{t("common.appName")}</span>
          </div>
          <div className="flex items-center gap-2">
            <LanguageSwitcher />
            <button
              className="p-2 text-surface-400 hover:text-surface-600 hover:bg-surface-100 rounded-xl transition-colors"
              aria-label={t("common.notifications")}
            >
              <Bell className="w-5 h-5" />
            </button>
            {user?.full_name && (
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-[10px] font-bold text-white shadow-sm shadow-primary-500/20">
                {user.full_name
                  .split(" ")
                  .map((n) => n[0])
                  .join("")
                  .toUpperCase()
                  .slice(0, 2)}
              </div>
            )}
          </div>
        </header>

        {/* Desktop header bar */}
        <header className="hidden lg:flex sticky top-0 z-30 bg-white/80 backdrop-blur-xl border-b border-surface-200/60 px-8 py-4 items-center justify-between">
          <div className="flex items-center gap-4">
            <LanguageSwitcher />
          </div>
          <div className="flex items-center gap-4">
            <button
              className="p-2.5 text-surface-400 hover:text-surface-600 hover:bg-surface-100 rounded-xl transition-colors relative"
              aria-label={t("common.notifications")}
            >
              <Bell className="w-5 h-5" />
              <span className="absolute top-2 end-2 w-2 h-2 bg-red-500 rounded-full ring-2 ring-white" />
            </button>
            <div className="h-6 w-px bg-surface-200" />
            {user?.full_name && (
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-[10px] font-bold text-white shadow-sm shadow-primary-500/20">
                  {user.full_name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")
                    .toUpperCase()
                    .slice(0, 2)}
                </div>
                <div className="text-end">
                  <p className="text-[13px] font-semibold text-surface-800 leading-tight">{user.full_name}</p>
                  <p className="text-[11px] text-surface-400 capitalize">{user.role}</p>
                </div>
              </div>
            )}
          </div>
        </header>

        {/* Main content */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-[1600px] w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
