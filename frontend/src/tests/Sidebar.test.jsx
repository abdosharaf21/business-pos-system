import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, within } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import Sidebar from "../shared/layouts/Sidebar";

let mockUser = { role: "admin", full_name: "Admin User", email: "admin@x.com" };

vi.mock("react-i18next", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useTranslation: () => ({ t: (key) => key, i18n: { language: "en" } }),
  };
});

vi.mock("../shared/hooks/useStoreSettings", () => ({
  useStoreSettings: () => ({ data: null }),
}));

vi.mock("../shared/services/storeSettings", () => ({
  getLogoUrl: () => null,
}));

vi.mock("../shared/context/AuthContext", () => ({
  useAuth: () => ({ user: mockUser, logout: vi.fn() }),
}));

function renderSidebar(pathname, activeModuleId = "dashboard") {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[pathname]}>
        <Sidebar
          isOpen={false}
          onClose={() => {}}
          activeModuleId={activeModuleId}
          pathname={pathname}
        />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe("Sidebar navigation (standalone)", () => {
  beforeEach(() => {
    mockUser = { role: "admin", full_name: "Admin User", email: "admin@x.com" };
  });

  it("shows the worker-management module navigation", () => {
    renderSidebar("/worker-management", "worker-management");
    const nav = screen.getByRole("navigation", { name: "Sidebar navigation" });
    expect(within(nav).queryAllByText("nav.dashboard").length).toBeGreaterThanOrEqual(1);
    expect(within(nav).getByText("nav.workers")).toBeInTheDocument();
    expect(within(nav).getByText("nav.attendance")).toBeInTheDocument();
    expect(within(nav).getByText("nav.salaries")).toBeInTheDocument();
    expect(within(nav).getByText("nav.advances")).toBeInTheDocument();
    expect(within(nav).getAllByText("nav.reports").length).toBeGreaterThanOrEqual(1);
    expect(within(nav).queryAllByText("services.comingSoon").length).toBe(0);
  });

  it("shows the expenses module navigation", () => {
    renderSidebar("/expenses", "expenses");
    const nav = screen.getByRole("navigation", { name: "Sidebar navigation" });
    // nav.expenses appears as both group label and nav item, use queryAllByText
    expect(within(nav).queryAllByText("nav.expenses").length).toBeGreaterThanOrEqual(1);
    expect(within(nav).getByText("nav.expenseCategories")).toBeInTheDocument();
    expect(within(nav).getAllByText("nav.reports").length).toBeGreaterThanOrEqual(1);
  });

  it("shows the dashboard module navigation", () => {
    renderSidebar("/dashboard");
    const nav = screen.getByRole("navigation", { name: "Sidebar navigation" });
    expect(within(nav).getByText("nav.dashboardOverview")).toBeInTheDocument();
  });

  it("shows the settings module navigation for admin", () => {
    renderSidebar("/store-settings", "settings");
    const nav = screen.getByRole("navigation", { name: "Sidebar navigation" });
    expect(within(nav).getByText("nav.storeSettings")).toBeInTheDocument();
    expect(within(nav).getByText("nav.users")).toBeInTheDocument();
  });

  it("hides the settings module navigation for employee", () => {
    mockUser = { role: "employee", full_name: "Employee User", email: "employee@x.com" };
    renderSidebar("/store-settings", "settings");
    const nav = screen.getByRole("navigation", { name: "Sidebar navigation" });
    expect(within(nav).queryByText("nav.storeSettings")).not.toBeInTheDocument();
    expect(within(nav).queryByText("nav.users")).not.toBeInTheDocument();
  });

  it("falls back to the business name in the brand", () => {
    renderSidebar("/dashboard");
    expect(screen.getByText("common.appName")).toBeInTheDocument();
    expect(screen.getByText("common.appSubtitle")).toBeInTheDocument();
  });
});