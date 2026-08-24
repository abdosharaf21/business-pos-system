import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, useLocation } from "react-router-dom";
import TopNavigation from "../shared/layouts/TopNavigation";
import Sidebar from "../shared/layouts/Sidebar";
import DarkModeToggle from "../shared/components/DarkModeToggle";

const adminUser = {
  role: "admin",
  full_name: "Admin User",
  email: "admin@pos.com",
};

vi.mock("../shared/context/AuthContext", () => ({
  useAuth: () => ({ user: adminUser, logout: vi.fn() }),
}));

vi.mock("../shared/hooks/useStoreSettings", () => ({
  useStoreSettings: () => ({ data: null }),
}));

vi.mock("../shared/services/storeSettings", () => ({
  getLogoUrl: () => null,
}));

vi.mock("../shared/components/GlobalSearch", () => ({
  default: () => <div data-testid="global-search" />,
}));

vi.mock("../shared/components/NotificationBell", () => ({
  default: () => <div data-testid="notifications" />,
}));

vi.mock("../shared/components/LanguageSwitcher", () => ({
  default: () => <div data-testid="language-switcher" />,
}));

function renderWithRouter(ui, initialEntries) {
  return render(<MemoryRouter initialEntries={initialEntries}>{ui}</MemoryRouter>);
}

describe("TopNavigation chrome", () => {
  it("keeps global actions without a duplicate user menu", () => {
    renderWithRouter(
      <TopNavigation activeModuleId="business" onOpenSidebar={() => {}} />,
      ["/business"]
    );

    expect(screen.getByTestId("global-search")).toBeInTheDocument();
    expect(screen.getByTestId("notifications")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Toggle dark mode" })).toBeInTheDocument();
    expect(screen.queryByLabelText(adminUser.full_name)).not.toBeInTheDocument();
    expect(screen.queryByText("Sign out")).not.toBeInTheDocument();
    expect(screen.queryByText("Back to Services")).not.toBeInTheDocument();
  });

  it("shows the application switcher tabs", () => {
    renderWithRouter(
      <TopNavigation activeModuleId="pos" onOpenSidebar={() => {}} />,
      ["/dashboard"]
    );

    for (const tab of [
      "Business Development",
      "POS",
      "Inventory",
      "Expenses",
    ]) {
      expect(screen.getAllByRole("link", { name: tab }).length).toBeGreaterThan(0);
    }
  });
});

describe("Sidebar chrome", () => {
  function LocationProbe() {
    const { pathname } = useLocation();
    return <div data-testid="location">{pathname}</div>;
  }

  it("navigates back to the application catalog only inside real applications", async () => {
    const user = userEvent.setup();
    const { rerender } = render(
      <MemoryRouter initialEntries={["/products"]}>
        <Sidebar isOpen={false} onClose={() => {}} activeModuleId="pos" />
        <LocationProbe />
      </MemoryRouter>
    );

    expect(screen.getByTestId("location")).toHaveTextContent("/products");
    await user.click(screen.getByRole("button", { name: "Back to Services" }));
    expect(screen.getByTestId("location")).toHaveTextContent("/services");
    expect(
      screen.queryByRole("button", { name: "Back to Services" })
    ).not.toBeInTheDocument();

    rerender(
      <MemoryRouter initialEntries={["/business"]}>
        <Sidebar isOpen={false} onClose={() => {}} activeModuleId="business" />
        <LocationProbe />
      </MemoryRouter>
    );
    expect(
      screen.queryByRole("button", { name: "Back to Services" })
    ).not.toBeInTheDocument();
  });

  it("renders exactly one user menu with logout at the bottom of the sidebar", () => {
    renderWithRouter(
      <Sidebar isOpen={false} onClose={() => {}} activeModuleId="business" />,
      ["/business"]
    );

    expect(screen.getByText(adminUser.full_name)).toBeInTheDocument();
    expect(screen.getByText(adminUser.email)).toBeInTheDocument();
    expect(screen.getByText("admin")).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: "Sign out" })).toHaveLength(1);
  });

  it("lists both the application catalog and the service records under Business Development", () => {
    renderWithRouter(
      <Sidebar isOpen={false} onClose={() => {}} activeModuleId="business" />,
      ["/business"]
    );

    expect(screen.getByRole("link", { name: "Services" })).toHaveAttribute(
      "href",
      "/services"
    );
    expect(screen.getByRole("link", { name: "Service Records" })).toHaveAttribute(
      "href",
      "/business/services"
    );
  });
});

describe("DarkModeToggle", () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.classList.remove("dark");
  });

  it("toggles dark mode and persists the choice", async () => {
    const user = userEvent.setup();
    render(<DarkModeToggle />);

    const button = screen.getByRole("button", { name: "Toggle dark mode" });
    expect(button).toHaveAttribute("aria-pressed", "false");

    await user.click(button);
    expect(document.documentElement.classList.contains("dark")).toBe(true);
    expect(localStorage.getItem("theme")).toBe("dark");
    expect(button).toHaveAttribute("aria-pressed", "true");

    await user.click(button);
    expect(document.documentElement.classList.contains("dark")).toBe(false);
    expect(localStorage.getItem("theme")).toBe("light");
  });
});
