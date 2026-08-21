import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import AppSwitcher from "../shared/components/AppSwitcher";

vi.mock("react-i18next", async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useTranslation: () => ({
      t: (key) => key,
      i18n: { language: "en" },
    }),
  };
});

vi.mock("../shared/context/AuthContext", () => ({
  useAuth: () => ({
    user: { role: "admin", full_name: "Admin" },
    logout: vi.fn(),
  }),
}));

function renderSwitcher(route = "/dashboard") {
  return render(
    <MemoryRouter initialEntries={[route]}>
      <AppSwitcher />
    </MemoryRouter>
  );
}

describe("AppSwitcher", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders the current application name", () => {
    renderSwitcher("/dashboard");
    expect(screen.getByText("nav.pos")).toBeInTheDocument();
  });

  it("shows business development when on a business route", () => {
    renderSwitcher("/business/dashboard");
    expect(screen.getByText("nav.businessDevelopment")).toBeInTheDocument();
  });

  it("shows expenses when on the expenses route", () => {
    renderSwitcher("/expenses");
    expect(screen.getByText("nav.expenses")).toBeInTheDocument();
  });

  it("opens the dropdown when clicked", async () => {
    renderSwitcher();
    const button = screen.getByRole("button", { name: "appSwitcher.label" });
    await userEvent.click(button);
    expect(screen.getByRole("listbox")).toBeInTheDocument();
  });

  it("lists all applications in the dropdown", async () => {
    renderSwitcher();
    await userEvent.click(screen.getByRole("button", { name: "appSwitcher.label" }));
    expect(screen.getByRole("option", { name: "nav.pos" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "nav.businessDevelopment" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "nav.inventory" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "nav.expenses" })).toBeInTheDocument();
    expect(screen.queryByRole("option", { name: "nav.settings" })).not.toBeInTheDocument();
  });

  it("marks the current application as selected", async () => {
    renderSwitcher("/dashboard");
    await userEvent.click(screen.getByRole("button", { name: "appSwitcher.label" }));
    const posOption = screen.getByRole("option", { name: "nav.pos" });
    expect(posOption).toHaveAttribute("aria-selected", "true");
  });
});
