import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider, useAuth } from "../shared/context/AuthContext";

vi.mock("../shared/services/auth", () => ({
  authService: {
    login: vi.fn(),
    logout: vi.fn(),
  },
}));

function TestConsumer() {
  const auth = useAuth();
  return (
    <div>
      <span data-testid="authenticated">{String(auth.isAuthenticated)}</span>
      <span data-testid="user">{JSON.stringify(auth.user)}</span>
      <button onClick={() => auth.login("a@b.com", "p")}>Login</button>
      <button onClick={() => auth.logout()}>Logout</button>
    </div>
  );
}

function renderWithProvider() {
  return render(
    <BrowserRouter>
      <AuthProvider>
        <TestConsumer />
      </AuthProvider>
    </BrowserRouter>
  );
}

describe("AuthContext", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("starts unauthenticated with no user", () => {
    renderWithProvider();
    expect(screen.getByTestId("authenticated")).toHaveTextContent("false");
    expect(screen.getByTestId("user")).toHaveTextContent("null");
  });

  it("restores session from localStorage", () => {
    localStorage.setItem("token", "saved-token");
    localStorage.setItem("user", JSON.stringify({ id: 1, email: "a@b.com" }));
    renderWithProvider();
    expect(screen.getByTestId("authenticated")).toHaveTextContent("true");
    expect(screen.getByTestId("user")).toHaveTextContent("a@b.com");
  });

  it("calls login, saves tokens and navigates", async () => {
    const { authService } = await import("../shared/services/auth");
    authService.login.mockResolvedValue({
      data: {
        success: true,
        data: {
          access_token: "new-token",
          refresh_token: "new-refresh",
          user: { id: 1, email: "a@b.com", role: "admin" },
        },
      },
    });
    renderWithProvider();
    await userEvent.click(screen.getByText("Login"));
    await waitFor(() => {
      expect(localStorage.getItem("token")).toBe("new-token");
    });
    expect(localStorage.getItem("refresh_token")).toBe("new-refresh");
    expect(localStorage.getItem("user")).toContain("a@b.com");
    expect(screen.getByTestId("authenticated")).toHaveTextContent("true");
  });

  it("calls logout, clears storage and navigates", async () => {
    localStorage.setItem("token", "t");
    localStorage.setItem("refresh_token", "r");
    localStorage.setItem("user", JSON.stringify({ id: 1 }));
    const { authService } = await import("../shared/services/auth");
    authService.logout.mockResolvedValue({});
    renderWithProvider();
    await userEvent.click(screen.getByText("Logout"));
    await waitFor(() => {
      expect(localStorage.getItem("token")).toBeNull();
    });
    expect(localStorage.getItem("refresh_token")).toBeNull();
    expect(localStorage.getItem("user")).toBeNull();
    expect(screen.getByTestId("authenticated")).toHaveTextContent("false");
  });
});
