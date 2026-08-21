import { useState } from "react";
import { Outlet } from "react-router-dom";
import TopNavigation from "./TopNavigation";
import Sidebar from "./Sidebar";

export default function ModuleLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="min-h-screen flex bg-surface-50 dark:bg-surface-900">
      <Sidebar
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <div className="flex-1 flex flex-col lg:ms-[260px] min-h-screen">
        <TopNavigation
          onOpenSidebar={() => setSidebarOpen(true)}
        />

        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-[1600px] w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
