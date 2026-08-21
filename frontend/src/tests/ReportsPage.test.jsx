import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";

vi.mock("react-i18next", () => ({
  useTranslation: () => ({ t: (key) => key, i18n: { language: "en" } }),
}));

const getDashboardMock = vi.fn();
const getSalesTrendMock = vi.fn();
const getProfitMock = vi.fn();
const getProductsPerformanceMock = vi.fn();
const getSuppliersPerformanceMock = vi.fn();
const getInventoryReportMock = vi.fn();
const getMovementReportMock = vi.fn();
const getMostTransferredMock = vi.fn();
const getLowestStockMock = vi.fn();
const getExpensesDailyMock = vi.fn();
const getExpensesCategoryMock = vi.fn();
const getExpensesPaymentMethodMock = vi.fn();
const getExpensesMonthlyComparisonMock = vi.fn();
const getExpensesHighestCategoriesMock = vi.fn();
const getInventoryAuditReportMock = vi.fn();
const getInventoryAuditsMonthlyMock = vi.fn();
const getInventoryAuditsYearlyMock = vi.fn();

vi.mock("../modules/reports/api", () => ({
  reportService: {
    getDashboard: (...args) => getDashboardMock(...args),
    getSalesTrend: (...args) => getSalesTrendMock(...args),
    getProfit: (...args) => getProfitMock(...args),
    getProductsPerformance: (...args) => getProductsPerformanceMock(...args),
    getSuppliersPerformance: (...args) => getSuppliersPerformanceMock(...args),
    getInventoryReport: (...args) => getInventoryReportMock(...args),
    getMovementReport: (...args) => getMovementReportMock(...args),
    getMostTransferred: (...args) => getMostTransferredMock(...args),
    getLowestStock: (...args) => getLowestStockMock(...args),
    getExpensesDaily: (...args) => getExpensesDailyMock(...args),
    getExpensesCategory: (...args) => getExpensesCategoryMock(...args),
    getExpensesPaymentMethod: (...args) => getExpensesPaymentMethodMock(...args),
    getExpensesMonthlyComparison: (...args) => getExpensesMonthlyComparisonMock(...args),
    getExpensesHighestCategories: (...args) => getExpensesHighestCategoriesMock(...args),
    getInventoryAuditReport: (...args) => getInventoryAuditReportMock(...args),
    getInventoryAuditsMonthly: (...args) => getInventoryAuditsMonthlyMock(...args),
    getInventoryAuditsYearly: (...args) => getInventoryAuditsYearlyMock(...args),
  },
}));

const dashboardData = {
  sales: { today_sales: 100, monthly_sales: 5000, total_invoices: 10, average_invoice_value: 500 },
  purchases: { today_purchases: 50, monthly_purchases: 2000 },
  inventory: { inventory_value: 15000, low_stock_count: 3 },
  top_selling_products: [],
  recent_sales: [],
};

const profitData = {
  total_revenue: 10000,
  total_purchase_cost: 6000,
  gross_profit: 4000,
  profit_margin: 40,
};

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return ({ children }) => (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={["/reports"]}>
        {children}
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe("ReportsPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getDashboardMock.mockResolvedValue({ data: { data: dashboardData } });
    getSalesTrendMock.mockResolvedValue({ data: { data: { data: [] } } });
    getProfitMock.mockResolvedValue({ data: { data: profitData } });
    getProductsPerformanceMock.mockResolvedValue({ data: { data: { top_products: [], slow_products: [] } } });
    getSuppliersPerformanceMock.mockResolvedValue({ data: { data: { suppliers: [] } } });
    getInventoryReportMock.mockResolvedValue({ data: { data: { inventory: [] } } });
    getMovementReportMock.mockResolvedValue({ data: { data: { data: [] } } });
    getMostTransferredMock.mockResolvedValue({ data: { data: { most_transferred: [] } } });
    getLowestStockMock.mockResolvedValue({ data: { data: { lowest_stock: [] } } });
    getExpensesDailyMock.mockResolvedValue({ data: { data: { total_expenses: 0, data: [] } } });
    getExpensesCategoryMock.mockResolvedValue({ data: { data: { data: [] } } });
    getExpensesPaymentMethodMock.mockResolvedValue({ data: { data: { data: [] } } });
    getExpensesMonthlyComparisonMock.mockResolvedValue({ data: { data: { data: [] } } });
    getExpensesHighestCategoriesMock.mockResolvedValue({ data: { data: { highest_categories: [] } } });
    getInventoryAuditReportMock.mockResolvedValue({ data: { data: { metrics: {}, largest_shortages: [], largest_overages: [] } } });
    getInventoryAuditsMonthlyMock.mockResolvedValue({ data: { data: { data: [] } } });
    getInventoryAuditsYearlyMock.mockResolvedValue({ data: { data: { data: [] } } });
  });

  it("sends custom period with dates to the profit endpoint", async () => {
    const ReportsPage = (await import("../modules/reports/page")).default;
    render(<ReportsPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(getProfitMock).toHaveBeenCalled();
    });

    const profitCall = getProfitMock.mock.calls[0][0];
    expect(profitCall.period).toBe("custom");
    expect(profitCall.start_date).toBeDefined();
    expect(profitCall.end_date).toBeDefined();
    expect(profitCall.start_date).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    expect(profitCall.end_date).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });

  it("does not send last_30_days to the profit endpoint", async () => {
    const ReportsPage = (await import("../modules/reports/page")).default;
    render(<ReportsPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(getProfitMock).toHaveBeenCalled();
    });

    const profitCall = getProfitMock.mock.calls[0][0];
    expect(profitCall.period).not.toBe("last_30_days");
  });

  it("renders the reports page title", async () => {
    const ReportsPage = (await import("../modules/reports/page")).default;
    render(<ReportsPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText("reports.title")).toBeInTheDocument();
    });
  });

  it("renders profit analytics section", async () => {
    const ReportsPage = (await import("../modules/reports/page")).default;
    render(<ReportsPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText("reports.profitAnalytics")).toBeInTheDocument();
    });
  });

  it("renders expenses reports section", async () => {
    const ReportsPage = (await import("../modules/reports/page")).default;
    render(<ReportsPage />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText("reports.expenses.title")).toBeInTheDocument();
    });
  });
});
