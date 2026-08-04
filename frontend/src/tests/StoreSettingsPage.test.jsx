import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import StoreSettingsPage from "../modules/store-settings/page";

vi.mock("react-i18next", () => ({
  useTranslation: () => ({ t: (key) => key, i18n: { language: "en" } }),
}));

vi.mock("react-hot-toast", () => ({
  default: { success: vi.fn(), error: vi.fn() },
}));

const getMock = vi.fn();
const updateMock = vi.fn();
vi.mock("../modules/store-settings/api", () => ({
  storeSettingsService: {
    get: (...args) => getMock(...args),
    update: (...args) => updateMock(...args),
    updateWithLogo: (...args) => updateMock(...args),
  },
}));

const sampleSettings = {
  store_name: "My Store",
  owner_name: "Ahmed",
  phone: "+1 555 000 0000",
  email: "contact@store.com",
  website: "",
  address: "",
  tax_number: "",
  currency: "EGP",
  receipt_footer: "Thank you!",
  logo_path: null,
};

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <StoreSettingsPage />
    </QueryClientProvider>
  );
}

describe("StoreSettingsPage", () => {
  beforeEach(() => {
    getMock.mockReset();
    updateMock.mockReset();
    getMock.mockResolvedValue({ data: { data: sampleSettings } });
    updateMock.mockResolvedValue({ data: { data: sampleSettings } });
  });

  it("renders the settings form with store name from the API", async () => {
    renderPage();
    expect(
      await screen.findByDisplayValue("My Store")
    ).toBeInTheDocument();
    expect(
      screen.getByDisplayValue("contact@store.com")
    ).toBeInTheDocument();
  });

  it("shows validation error when store name is empty", async () => {
    const user = userEvent.setup();
    renderPage();
    const nameInput = await screen.findByDisplayValue("My Store");
    await user.clear(nameInput);
    await user.click(screen.getByRole("button", { name: /storeSettings.save/ }));
    await waitFor(() => {
      expect(
        screen.getByText("storeSettings.validation.storeNameRequired")
      ).toBeInTheDocument();
    });
    expect(updateMock).not.toHaveBeenCalled();
  });

  it("saves updated settings on submit", async () => {
    const user = userEvent.setup();
    renderPage();
    const phoneInput = await screen.findByDisplayValue("+1 555 000 0000");
    await user.clear(phoneInput);
    await user.type(phoneInput, "+20 100 000 0000");
    await user.click(screen.getByRole("button", { name: /storeSettings.save/ }));
    await waitFor(() => {
      expect(updateMock).toHaveBeenCalledWith(
        expect.objectContaining({ phone: "+20 100 000 0000" })
      );
    });
  });

  it("shows an API error message when loading fails", async () => {
    getMock.mockRejectedValue({ response: { data: { message: "Server error" } } });
    renderPage();
    expect(
      await screen.findByText("Server error")
    ).toBeInTheDocument();
  });
});
