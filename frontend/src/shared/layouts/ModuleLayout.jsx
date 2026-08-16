import { useState } from "react";
import { Outlet, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import TopNavigation from "./TopNavigation";
import Sidebar from "./Sidebar";
import { getActiveModule } from "./navigationConfig";

export default function ModuleLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { pathname } = useLocation();
  const { t } = useTranslation();
  const activeModule = getActiveModule(pathname);

  return (
    <div className="min-h-screen flex bg-surface-50">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:fixed focus:top-3 focus:start-3 focus:z-[60] focus:px-4 focus:py-2 focus:rounded-xl focus:bg-primary-600 focus:text-white focus:text-[13px] focus:font-semibold focus:shadow-lg"
      >
        {t("common.skipToContent")}
      </a>
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        activeModuleId={activeModule}
        pathname={pathname}
      />

      <div className="flex-1 flex flex-col lg:ms-64 min-h-screen">
        <TopNavigation
          activeModuleId={activeModule}
          onOpenSidebar={() => setSidebarOpen(true)}
        />

        <main id="main-content" tabIndex={-1} className="flex-1 p-4 sm:p-6 lg:p-8 max-w-[1600px] w-full mx-auto focus:outline-none">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
