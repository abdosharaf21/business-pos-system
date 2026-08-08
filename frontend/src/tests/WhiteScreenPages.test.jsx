import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import ProductsPage from "../modules/products/page";
import CustomersPage from "../modules/customers/page";
import CategoriesPage from "../modules/categories/page";
import SuppliersPage from "../modules/suppliers/page";

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

const getProductsMock = vi.fn();
const getCategoriesMock = vi.fn();
const getTreeMock = vi.fn();
const getCustomersMock = vi.fn();
const getSuppliersMock = vi.fn();

vi.mock("../modules/products/api", () => ({
  productService: {
    getAll: (...args) => getProductsMock(...args),
    getById: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
}));

vi.mock("../modules/categories/api", () => ({
  categoryService: {
    getAll: (...args) => getCategoriesMock(...args),
    getTree: (...args) => getTreeMock(...args),
    getById: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
}));

vi.mock("../modules/customers/api", () => ({
  customerService: {
    getAll: (...args) => getCustomersMock(...args),
    getById: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
}));

vi.mock("../modules/suppliers/api", () => ({
  supplierService: {
    getAll: (...args) => getSuppliersMock(...args),
    getById: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
  },
}));

function renderPage(ui) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>
  );
}

describe("White screen regression pages", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the Products page with the manage actions column", async () => {
    getProductsMock.mockResolvedValue({
      data: {
        data: [
          {
            id: 1,
            sku: "SKU-1",
            name: "Milk",
            barcode: "6291041500213",
            category_id: 1,
            category_name: "Dairy",
            purchase_price: 15,
            selling_price: 20,
            quantity: 10,
            minimum_stock: 2,
            expiration_status: "normal",
            status: "active",
          },
        ],
      },
    });
    getCategoriesMock.mockResolvedValue({ data: { data: [] } });

    renderPage(<ProductsPage />);

    expect(await screen.findByText("Milk")).toBeInTheDocument();
    expect(screen.getByTitle("products.delete")).toBeInTheDocument();
    expect(screen.getByTitle("products.edit")).toBeInTheDocument();
  });

  it("renders the Customers page with the manage actions column", async () => {
    getCustomersMock.mockResolvedValue({
      data: {
        data: [
          { id: 1, name: "Acme Corp", phone: "0123456789", email: "a@b.com", address: "Cairo" },
        ],
      },
    });

    renderPage(<CustomersPage />);

    expect(await screen.findByText("Acme Corp")).toBeInTheDocument();
    expect(screen.getByTitle("customers.delete")).toBeInTheDocument();
  });

  it("renders the Categories page with the manage actions column", async () => {
    getTreeMock.mockResolvedValue({
      data: {
        data: [
          {
            id: 1,
            name: "Beverages",
            description: "Drinks",
            children: [{ id: 2, name: "Juices", description: "", children: [] }],
          },
        ],
      },
    });

    renderPage(<CategoriesPage />);

    expect(await screen.findByText("Beverages")).toBeInTheDocument();
    expect(screen.getAllByTitle("categories.delete").length).toBeGreaterThan(0);
  });

  it("renders the Suppliers page with the manage actions column", async () => {
    getSuppliersMock.mockResolvedValue({
      data: {
        data: [
          { id: 1, name: "Nestle Egypt", phone: "0100000000", email: "n@n.com", address: "Giza" },
        ],
      },
    });

    renderPage(<SuppliersPage />);

    expect(await screen.findByText("Nestle Egypt")).toBeInTheDocument();
    expect(screen.getByTitle("suppliers.delete")).toBeInTheDocument();
  });
});
