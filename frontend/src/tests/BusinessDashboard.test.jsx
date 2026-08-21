import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import BusinessDashboardPage from "../modules/business/dashboard/page";

const getStatisticsMock = vi.fn();

vi.mock("react-i18next", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useTranslation: () => ({
      t: (key, fallback) => fallback || key,
      i18n: { language: "en" },
    }),
  };
});

vi.mock("../shared/context/AuthContext", () => ({
  useAuth: () => ({ user: { role: "admin", full_name: "Admin" }, logout: vi.fn() }),
}));

vi.mock("../modules/business/dashboard/api", () => ({
  bdDashboardService: {
    getStatistics: (...args) => getStatisticsMock(...args),
  },
}));

const getDealStatisticsMock = vi.fn();
vi.mock("../modules/deals/api", () => ({
  dealService: {
    getStatistics: (...args) => getDealStatisticsMock(...args),
  },
}));

vi.mock("../shared/hooks/useStoreSettings", () => ({
  useStoreSettings: () => ({ data: { store_name: "Test Store" } }),
}));

vi.mock("../shared/services/storeSettings", () => ({
  getLogoUrl: () => null,
}));

vi.mock("../shared/components/DarkModeToggle", () => ({
  default: () => null,
}));

vi.mock("../shared/components/LanguageSwitcher", () => ({
  default: () => null,
}));

vi.mock("../shared/components/NotificationBell", () => ({
  default: () => null,
}));

vi.mock("../shared/components/GlobalSearch", () => ({
  default: () => null,
}));

vi.mock("../shared/components/UserMenu", () => ({
  default: () => null,
}));

vi.mock("../shared/components/QuickActionBar", () => ({
  default: () => null,
}));

const mockStats = {
  total_clients: 12,
  active_clients: 8,
  total_services: 5,
  active_services: 4,
  total_client_services: 15,
  active_client_services: 10,
  clients_by_status: { customer: 8, lead: 3, prospect: 1 },
  services_by_status: { active: 4, inactive: 1 },
  client_services_by_status: { in_progress: 10, completed: 5 },
  recent_clients: [
    { id: 1, company_name: "Acme Corp", contact_person: "John", status: "customer" },
    { id: 2, company_name: "Beta Ltd", contact_person: "Jane", status: "lead" },
  ],
  recent_client_services: [
    { id: 1, company_name: "Acme Corp", service_name: "POS System", status: "in_progress" },
    { id: 2, company_name: "Beta Ltd", service_name: "Inventory", status: "completed" },
  ],
};

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <BusinessDashboardPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe("BusinessDashboardPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders page title and description", async () => {
    getStatisticsMock.mockResolvedValue({ data: { data: mockStats } });
    getDealStatisticsMock.mockResolvedValue({ data: { data: { total_deals: 0, total_revenue: 0, monthly_revenue: 0, recent_deals: [], best_services: [] } } });
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Business Development")).toBeInTheDocument();
    });
    expect(screen.getByText("Overview of your business development activities")).toBeInTheDocument();
  });

  it("renders KPI cards with correct values", async () => {
    getStatisticsMock.mockResolvedValue({ data: { data: mockStats } });
    getDealStatisticsMock.mockResolvedValue({ data: { data: { total_deals: 5, total_revenue: 1000, monthly_revenue: 500 } } });
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Total Clients")).toBeInTheDocument();
    });
    expect(screen.getByText("Active Clients")).toBeInTheDocument();
    expect(screen.getByText("Total Services")).toBeInTheDocument();
    expect(screen.getByText("Total Deals")).toBeInTheDocument();
    expect(screen.getByText("Total Assignments")).toBeInTheDocument();
    expect(screen.getByText("Active Assignments")).toBeInTheDocument();
  });

  it("derives service KPIs from API statistics", async () => {
    getStatisticsMock.mockResolvedValue({ data: { data: mockStats } });
    getDealStatisticsMock.mockResolvedValue({ data: { data: { total_deals: 0, total_revenue: 0, monthly_revenue: 0 } } });
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Total Services")).toBeInTheDocument();
    });

    const totalLabel = screen.getByText("Total Services");
    const totalValue = totalLabel.parentElement.querySelector(".numeric-value");
    expect(totalValue).toHaveTextContent(String(mockStats.total_services));
  });

  it("renders recent clients", async () => {
    getStatisticsMock.mockResolvedValue({ data: { data: mockStats } });
    getDealStatisticsMock.mockResolvedValue({ data: { data: { total_deals: 0, total_revenue: 0, monthly_revenue: 0, recent_deals: [], best_services: [] } } });
    renderPage();
    await waitFor(() => {
      expect(screen.getAllByText("Acme Corp").length).toBeGreaterThanOrEqual(1);
    });
    expect(screen.getAllByText("Beta Ltd").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText("John")).toBeInTheDocument();
  });

  it("renders recent assignments", async () => {
    getStatisticsMock.mockResolvedValue({ data: { data: mockStats } });
    getDealStatisticsMock.mockResolvedValue({ data: { data: { total_deals: 0, total_revenue: 0, monthly_revenue: 0, recent_deals: [], best_services: [] } } });
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("POS System")).toBeInTheDocument();
    });
    expect(screen.getByText("Inventory")).toBeInTheDocument();
  });

  it("renders quick access section", async () => {
    getStatisticsMock.mockResolvedValue({ data: { data: mockStats } });
    getDealStatisticsMock.mockResolvedValue({ data: { data: { total_deals: 0, total_revenue: 0, monthly_revenue: 0, recent_deals: [], best_services: [] } } });
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Quick Access")).toBeInTheDocument();
    });
  });

  it("shows empty state when no data", async () => {
    getStatisticsMock.mockResolvedValue({
      data: {
        data: {
          total_clients: 0,
          active_clients: 0,
          total_services: 0,
          active_services: 0,
          total_client_services: 0,
          active_client_services: 0,
          clients_by_status: {},
          services_by_status: {},
          client_services_by_status: {},
          recent_clients: [],
          recent_client_services: [],
        },
      },
    });
    getDealStatisticsMock.mockResolvedValue({ data: { data: { total_deals: 0, total_revenue: 0, monthly_revenue: 0, recent_deals: [], best_services: [] } } });
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("No Business Development Data")).toBeInTheDocument();
    });
  });

  it("shows error state on API failure", async () => {
    getStatisticsMock.mockRejectedValue(new Error("Network error"));
    getDealStatisticsMock.mockResolvedValue({ data: { data: {} } });
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Network error")).toBeInTheDocument();
    });
  });
});
