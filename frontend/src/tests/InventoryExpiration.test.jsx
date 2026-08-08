import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor, within } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import InventoryPage from "../modules/inventory/page";

const { toast, adminUser } = vi.hoisted(() => ({
  toast: { error: vi.fn(), success: vi.fn() },
  adminUser: { role: "admin", full_name: "Admin" },
}));

vi.mock("react-i18next", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useTranslation: () => ({ t: (key) => key }),
  };
});

vi.mock("react-hot-toast", () => ({
  default: toast,
}));

vi.mock("../shared/context/AuthContext", () => ({
  useAuth: () => ({ user: adminUser, logout: vi.fn() }),
}));

const getAllMock = vi.fn();
const getSummaryMock = vi.fn();
const getMovementsMock = vi.fn();
const updateExpirationMock = vi.fn();

vi.mock("../modules/inventory/api", () => ({
  inventoryService: {
    getAll: (...args) => getAllMock(...args),
    getSummary: (...args) => getSummaryMock(...args),
    getLowStock: vi.fn(),
    getMovements: (...args) => getMovementsMock(...args),
    transferStock: vi.fn(),
    updateExpiration: (...args) => updateExpirationMock(...args),
  },
}));

vi.mock("../modules/inventory_audits/api", () => ({
  auditService: {
    create: vi.fn(),
    update: vi.fn(),
    complete: vi.fn(),
  },
}));

const products = [
  {
    id: 1,
    name: "Milk",
    barcode: "B1",
    category_name: "Dairy",
    warehouse_qty: 5,
    store_qty: 5,
    total: 10,
    minimum_stock: 2,
    expiration_date: "2026-08-15",
    expiration_status: "normal",
    status: "active",
  },
  {
    id: 2,
    name: "Water",
    barcode: "B2",
    category_name: "Drinks",
    warehouse_qty: 0,
    store_qty: 5,
    total: 5,
    minimum_stock: 1,
    expiration_date: "2025-01-01",
    expiration_status: "expired",
    status: "active",
  },
  {
    id: 3,
    name: "Juice",
    barcode: "B3",
    category_name: "Drinks",
    warehouse_qty: 3,
    store_qty: 0,
    total: 3,
    minimum_stock: 1,
    expiration_date: "2026-12-31",
    expiration_status: "expiring_soon",
    status: "active",
  },
  {
    id: 4,
    name: "Sugar",
    barcode: "B4",
    category_name: "Pantry",
    warehouse_qty: 8,
    store_qty: 2,
    total: 10,
    minimum_stock: 3,
    expiration_date: null,
    expiration_status: null,
    status: "active",
  },
];

const summary = {
  total_products: 4,
  warehouse_total: 16,
  store_total: 12,
  low_stock_count: 0,
  total_quantity: 28,
  total_value: 500,
};

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <InventoryPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe("Inventory expiration date feature", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getAllMock.mockResolvedValue({ data: { data: products } });
    getSummaryMock.mockResolvedValue({ data: { data: summary } });
    getMovementsMock.mockResolvedValue({ data: { data: [] } });
  });

  it("shows the formatted expiration date for a product with a date", async () => {
    renderPage();
    expect(await screen.findByText("Milk")).toBeInTheDocument();
    expect(screen.getByText("Aug 15, 2026")).toBeInTheDocument();
  });

  it("shows an em dash for a product without an expiration date", async () => {
    renderPage();
    expect(await screen.findByText("Sugar")).toBeInTheDocument();
    expect(screen.getByText("—")).toBeInTheDocument();
  });

  it("shows a red badge for an expired product", async () => {
    renderPage();
    await screen.findByText("Water");
    const badge = screen
      .getAllByText("inventory.expiration.statuses.expired")
      .find((el) => el.tagName === "SPAN");
    expect(badge).toBeTruthy();
    expect(badge.className).toContain("bg-red-50");
  });

  it("shows a warning badge for an expiring-soon product", async () => {
    renderPage();
    await screen.findByText("Juice");
    const badge = screen
      .getAllByText("inventory.expiration.statuses.expiring_soon")
      .find((el) => el.tagName === "SPAN");
    expect(badge).toBeTruthy();
    expect(badge.className).toContain("bg-amber-50");
  });

  it("shows a success badge for a normal product", async () => {
    renderPage();
    await screen.findByText("Milk");
    const badge = screen
      .getAllByText("inventory.expiration.statuses.normal")
      .find((el) => el.tagName === "SPAN");
    expect(badge).toBeTruthy();
    expect(badge.className).toContain("bg-emerald-50");
  });

  it("exposes All / Normal / Expiring Soon / Expired filter options", async () => {
    renderPage();
    await screen.findByText("Milk");
    const select = screen.getByRole("combobox");
    const options = Array.from(select.querySelectorAll("option")).map((o) => o.value);
    expect(options).toEqual(["", "normal", "expiring_soon", "expired"]);
  });

  it("refetches with expiration sort when the sort button is clicked", async () => {
    renderPage();
    await screen.findByText("Milk");
    expect(getAllMock).toHaveBeenCalledWith("", "", "");
    fireEvent.click(screen.getByText("inventory.expiration.sortByExpiration"));
    await waitFor(() => {
      expect(getAllMock).toHaveBeenLastCalledWith("", "", "expiration");
    });
  });

  it("opens the expiration modal for undated stock and submits the new date", async () => {
    updateExpirationMock.mockResolvedValue({
      data: { data: { updated_rows: 3, expiration_date: "2027-03-15" } },
    });

    renderPage();
    await screen.findByText("Sugar");

    const sugarRow = screen.getByText("Sugar").closest("tr");
    fireEvent.click(within(sugarRow).getByRole("button", { name: "inventory.expiration.editButton" }));

    expect(screen.getByText("inventory.expiration.editTitle")).toBeInTheDocument();
    expect(screen.getByText("inventory.expiration.none")).toBeInTheDocument();

    fireEvent.change(screen.getByLabelText("inventory.expiration.dateLabel"), {
      target: { value: "2027-03-15" },
    });
    fireEvent.click(screen.getByRole("button", { name: "inventory.expiration.save" }));

    await waitFor(() => {
      expect(updateExpirationMock).toHaveBeenCalledWith(4, "2027-03-15");
    });
    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("inventory.expiration.toast.updated");
    });
  });

  it("shows the new expiration date and status after the update refetches", async () => {
    let call = 0;
    getAllMock.mockImplementation(() => {
      call += 1;
      const data =
        call > 1
          ? products.map((p) =>
              p.id === 4
                ? { ...p, expiration_date: "2027-03-15", expiration_status: "normal" }
                : p
            )
          : products;
      return Promise.resolve({ data: { data } });
    });
    updateExpirationMock.mockResolvedValue({
      data: { data: { updated_rows: 3, expiration_date: "2027-03-15" } },
    });

    renderPage();
    await screen.findByText("Sugar");
    expect(screen.getByText("—")).toBeInTheDocument();

    const sugarRow = screen.getByText("Sugar").closest("tr");
    fireEvent.click(within(sugarRow).getByRole("button", { name: "inventory.expiration.editButton" }));
    fireEvent.change(screen.getByLabelText("inventory.expiration.dateLabel"), {
      target: { value: "2027-03-15" },
    });
    fireEvent.click(screen.getByRole("button", { name: "inventory.expiration.save" }));

    await waitFor(() => {
      expect(screen.getByText("Mar 15, 2027")).toBeInTheDocument();
    });
    const updatedRow = screen.getByText("Sugar").closest("tr");
    const normalBadge = within(updatedRow)
      .getAllByText("inventory.expiration.statuses.normal")
      .find((el) => el.tagName === "SPAN");
    expect(normalBadge).toBeTruthy();
    expect(normalBadge.className).toContain("bg-emerald-50");
  });

  it("requires a date before saving the expiration update", async () => {
    renderPage();
    await screen.findByText("Sugar");

    const sugarRow = screen.getByText("Sugar").closest("tr");
    fireEvent.click(within(sugarRow).getByRole("button", { name: "inventory.expiration.editButton" }));
    fireEvent.click(screen.getByRole("button", { name: "inventory.expiration.save" }));

    await waitFor(() => {
      expect(screen.getByText("inventory.expiration.validation.dateRequired")).toBeInTheDocument();
    });
    expect(updateExpirationMock).not.toHaveBeenCalled();
  });

  it("shows an error toast when the expiration update fails", async () => {
    updateExpirationMock.mockRejectedValue({
      response: { data: { message: "Expiration date is required" } },
    });

    renderPage();
    await screen.findByText("Sugar");

    const sugarRow = screen.getByText("Sugar").closest("tr");
    fireEvent.click(within(sugarRow).getByRole("button", { name: "inventory.expiration.editButton" }));
    fireEvent.change(screen.getByLabelText("inventory.expiration.dateLabel"), {
      target: { value: "2027-03-15" },
    });
    fireEvent.click(screen.getByRole("button", { name: "inventory.expiration.save" }));

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith("Expiration date is required");
    });
  });
});
