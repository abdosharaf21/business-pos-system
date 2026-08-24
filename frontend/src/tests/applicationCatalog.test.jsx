import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import ApplicationCatalogPage from "../modules/services/catalog";

const navigate = vi.fn();

vi.mock("react-router-dom", async (importOriginal) => ({
  ...(await importOriginal()),
  useNavigate: () => navigate,
}));

function renderCatalog() {
  return render(
    <MemoryRouter initialEntries={["/services"]}>
      <ApplicationCatalogPage />
    </MemoryRouter>
  );
}

describe("ApplicationCatalogPage", () => {
  beforeEach(() => {
    navigate.mockClear();
  });

  it("renders the catalog with every application card", () => {
    renderCatalog();

    expect(
      screen.getByRole("heading", { name: "Application Catalog" })
    ).toBeInTheDocument();

    for (const appName of [
      "Business Development",
      "POS",
      "Inventory",
      "Expenses",
    ]) {
      expect(screen.getByRole("button", { name: appName })).toBeInTheDocument();
    }
  });

  it("marks the current application context", () => {
    renderCatalog();

    const badges = screen.getAllByText("Current app");
    expect(badges).toHaveLength(1);
    expect(
      screen.getByRole("button", { name: "Business Development" })
    ).toContainElement(badges[0]);
  });

  it("launches an application onto its dashboard route", async () => {
    const user = userEvent.setup();
    renderCatalog();

    await user.click(screen.getByRole("button", { name: "POS" }));
    expect(navigate).toHaveBeenCalledWith("/dashboard");

    await user.click(screen.getByRole("button", { name: "Inventory" }));
    expect(navigate).toHaveBeenCalledWith("/inventory/overview");

    await user.click(screen.getByRole("button", { name: "Expenses" }));
    expect(navigate).toHaveBeenCalledWith("/expenses/dashboard");
  });

  it("links sellable service records separately from the applications", async () => {
    const user = userEvent.setup();
    renderCatalog();

    expect(screen.getByText("Service Records")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Manage service records" }));
    expect(navigate).toHaveBeenCalledWith("/business/services");
  });
});
