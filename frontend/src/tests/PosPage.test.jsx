import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import PosPage from "../modules/pos/page";

const { toast } = vi.hoisted(() => ({ toast: { error: vi.fn(), success: vi.fn() } }));

vi.mock("react-i18next", () => ({
  useTranslation: () => ({ t: (key) => key, i18n: { language: "en" } }),
}));

vi.mock("react-hot-toast", () => ({
  default: toast,
}));

const getProductsMock = vi.fn();
const getCategoriesMock = vi.fn();
vi.mock("../modules/pos/api", () => ({
  posService: {
    getProducts: (...args) => getProductsMock(...args),
    getCategories: (...args) => getCategoriesMock(...args),
    checkout: vi.fn(),
    searchCustomers: vi.fn(),
    getInvoice: vi.fn(),
  },
}));

const milk = {
  id: 1,
  barcode: "6291041500213",
  name: "Milk",
  category: "Dairy",
  selling_price: 20,
  quantity: 10,
  minimum_stock: 2,
};
const water = {
  id: 2,
  barcode: "6223009990000",
  name: "Water",
  category: "Drinks",
  selling_price: 5,
  quantity: 5,
  minimum_stock: 1,
};
const unknown = {
  id: 3,
  barcode: "1111111111111",
  name: "Unknown",
  category: "Other",
  selling_price: 1,
  quantity: 0,
  minimum_stock: 1,
};

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <PosPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

function scan(code) {
  for (const ch of code) {
    fireEvent.keyDown(document.body, { key: ch });
  }
  fireEvent.keyDown(document.body, { key: "Enter" });
}

describe("PosPage barcode scanner", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getProductsMock.mockResolvedValue({ data: { data: [milk, water, unknown] } });
    getCategoriesMock.mockResolvedValue({ data: { data: [] } });
  });

  it("adds a scanned product to the cart", async () => {
    renderPage();
    await screen.findByText("Milk");

    scan(milk.barcode);

    await waitFor(() => {
      expect(screen.getAllByText("Milk")).toHaveLength(2);
    });
    expect(screen.getByTestId("cart-count")).toHaveTextContent("1");
  });

  it("increases quantity on duplicate scans without duplicate rows", async () => {
    renderPage();
    await screen.findByText("Milk");

    scan(milk.barcode);
    scan(milk.barcode);
    scan(milk.barcode);

    await waitFor(() => {
      expect(screen.getAllByText("Milk")).toHaveLength(2);
    });
    expect(screen.getByTestId("cart-count")).toHaveTextContent("3");
  });

  it("shows an error toast for an unknown barcode", async () => {
    renderPage();
    await screen.findByText("Milk");

    scan("0000000000000");

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith("pos.productNotFound");
    });
    expect(screen.queryByTestId("cart-count")).not.toBeInTheDocument();
  });

  it("refuses to add an out-of-stock product", async () => {
    renderPage();
    await screen.findByText("Milk");

    scan(unknown.barcode);

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith("pos.outOfStock");
    });
    expect(screen.queryByTestId("cart-count")).not.toBeInTheDocument();
  });

  it("keeps manual search working", async () => {
    renderPage();
    await screen.findByText("Milk");

    fireEvent.change(screen.getByPlaceholderText("pos.searchPlaceholder"), {
      target: { value: "water" },
    });

    await waitFor(() => {
      expect(screen.getByText("Water")).toBeInTheDocument();
    });
    expect(screen.queryByText("Milk")).not.toBeInTheDocument();
  });

  it("returns focus to the barcode input after a scan", async () => {
    renderPage();
    await screen.findByText("Milk");

    const barcodeInput = screen.getByTestId("barcode-input");
    barcodeInput.blur();
    expect(document.activeElement).not.toBe(barcodeInput);

    scan(milk.barcode);

    await waitFor(() => {
      expect(document.activeElement).toBe(barcodeInput);
    });
  });
});
