import { useState } from "react";
import { Outlet, useLocation } from "react-router-dom";
import TopNavigation from "./TopNavigation";
import Sidebar from "./Sidebar";
import { getActiveModule } from "./navigationConfig";

export default function ModuleLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { pathname } = useLocation();
  const activeModule = getActiveModule(pathname);

  return (
    <div className="min-h-screen flex bg-surface-50">
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        activeModuleId={activeModule}
      />

      <div className="flex-1 flex flex-col lg:ms-64 min-h-screen">
        <TopNavigation
          activeModuleId={activeModule}
          onOpenSidebar={() => setSidebarOpen(true)}
        />

        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-[1600px] w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
