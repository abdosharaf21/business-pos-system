import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import LoginPage from "../shared/pages/LoginPage";

const mockLogin = vi.fn();
vi.mock("../shared/context/AuthContext", () => ({
  useAuth: () => ({ login: mockLogin }),
}));

vi.mock("../shared/hooks/useStoreSettings", () => ({
  useLoginBranding: () => ({ data: null }),
}));

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <LoginPage />
      </BrowserRouter>
    </QueryClientProvider>
  );
}

describe("LoginPage", () => {
  beforeEach(() => {
    mockLogin.mockReset();
  });

  it("renders login form", () => {
    renderPage();
    expect(screen.getByLabelText("Email address")).toBeInTheDocument();
    expect(screen.getByLabelText("Password")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Sign in/i })).toBeInTheDocument();
  });

  it("shows validation errors for empty fields", async () => {
    renderPage();
    await userEvent.click(screen.getByRole("button", { name: /Sign in/i }));
    await waitFor(() => {
      expect(screen.getByText("Email is required")).toBeInTheDocument();
    });
    expect(screen.getByText("Password is required")).toBeInTheDocument();
  });

  it("shows email format error", async () => {
    const user = userEvent.setup();
    renderPage();
    const emailInput = screen.getByLabelText("Email address");
    await user.type(emailInput, "bad-email");
    const form = screen.getByRole("button", { name: /Sign in/i }).closest("form");
    fireEvent.submit(form);
    expect(await screen.findByText("Invalid email address")).toBeInTheDocument();
  });

  it("calls login with email and password on valid submit", async () => {
    mockLogin.mockResolvedValue(undefined);
    renderPage();
    await userEvent.type(screen.getByLabelText("Email address"), "admin@test.com");
    await userEvent.type(screen.getByLabelText("Password"), "secret123");
    await userEvent.click(screen.getByRole("button", { name: /Sign in/i }));
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith("admin@test.com", "secret123");
    });
  });

  it("does not call login when fields are empty", async () => {
    renderPage();
    await userEvent.click(screen.getByRole("button", { name: /Sign in/i }));
    await waitFor(() => {
      expect(mockLogin).not.toHaveBeenCalled();
    });
  });
});
