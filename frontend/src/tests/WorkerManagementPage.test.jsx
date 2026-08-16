import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import i18n from "../i18n";
import WorkerManagementPage from "../modules/worker-management/page";

const { mocks, adminUser } = vi.hoisted(() => {
  const fns = {};
  for (const k of ["getStatistics"]) {
    fns[k] = vi.fn();
  }
  return {
    mocks: fns,
    adminUser: { id: 1, role: "admin", full_name: "Admin" },
  };
});

vi.mock("react-i18next", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useTranslation: () => ({ t: (key) => key, i18n: { language: "en" } }),
  };
});

vi.mock("../shared/context/AuthContext", () => ({
  useAuth: () => ({ user: adminUser, logout: vi.fn() }),
}));

vi.mock("../modules/worker-management/api", () => ({
  workerManagementService: {
    getStatistics: (...args) => mocks.getStatistics(...args),
  },
}));

const statsPayload = {
  total_workers: 3,
  active_workers: 2,
  today_attendance: 1,
  outstanding_advances: 500,
  pending_salary_count: 1,
  pending_salary_total: 4800,
  total_salaries_paid: 2,
  attendance_by_status: { present: 1, absent: 1, late: 0, half_day: 0, leave: 0 },
  recent_workers: [
    { id: 1, full_name: "Ahmed Hassan", job_title: "Cashier", department: "Sales", status: "active", created_at: "2026-01-01T10:00:00" },
  ],
};

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <WorkerManagementPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe("WorkerManagementPage", () => {
  beforeEach(async () => {
    vi.clearAllMocks();
    mocks.getStatistics.mockResolvedValue({ data: { data: statsPayload } });
    await i18n.changeLanguage("en");
  });

  afterEach(() => {
    i18n.changeLanguage("en");
  });

  it("renders the real dashboard KPIs from the statistics API", async () => {
    renderPage();
    expect(await screen.findByText("workerManagement.kpis.totalWorkers")).toBeInTheDocument();
    expect(await screen.findByText("workerManagement.kpis.activeWorkers")).toBeInTheDocument();
    expect(await screen.findByText("workerManagement.kpis.todayAttendance")).toBeInTheDocument();
    expect(await screen.findByText("workerManagement.kpis.outstandingAdvances")).toBeInTheDocument();
    // Check KPI values exist in the document (they appear in StatCard components)
    // Use findAllByText to handle multiple matches and verify at least one exists
    expect(screen.getAllByText("3").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("2").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("1").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("500").length).toBeGreaterThanOrEqual(1);
    expect(mocks.getStatistics).toHaveBeenCalledTimes(1);
  });

  it("renders payroll, workforce, attendance breakdown, and quick access sections", async () => {
    renderPage();
    expect(await screen.findByText("workerManagement.payroll.title")).toBeInTheDocument();
    expect(screen.getByText("workerManagement.workforce.title")).toBeInTheDocument();
    expect(screen.getByText("workerManagement.breakdown.attendance")).toBeInTheDocument();
    expect(screen.getByText("workerManagement.quickAccess.title")).toBeInTheDocument();
  });

  it("links to the real worker management pages instead of coming soon placeholders", async () => {
    renderPage();
    expect(await screen.findByText("workerManagement.recent.workers")).toBeInTheDocument();
    expect(screen.queryAllByText("services.comingSoon").length).toBe(0);
    expect(screen.getByText("workerManagement.statuses.active")).toBeInTheDocument();
    expect(screen.getByText("Ahmed Hassan")).toBeInTheDocument();
  });

  it("shows an empty state when no workers exist", async () => {
    mocks.getStatistics.mockResolvedValue({
      data: { data: { ...statsPayload, total_workers: 0, active_workers: 0, recent_workers: [] } },
    });
    renderPage();
    expect(await screen.findByText("workerManagement.recent.noWorkers")).toBeInTheDocument();
    expect(screen.getByText("workerManagement.addFirstWorker")).toBeInTheDocument();
  });
});
