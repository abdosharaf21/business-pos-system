import { describe, it, expect, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import ProtectedRoute from "../router/ProtectedRoute";

vi.mock("../shared/context/AuthContext", () => ({
  useAuth: vi.fn(),
}));

describe("ProtectedRoute", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders children when authenticated", async () => {
    const { useAuth } = await import("../shared/context/AuthContext");
    useAuth.mockReturnValue({ isAuthenticated: true });
    render(
      <MemoryRouter>
        <ProtectedRoute>
          <div data-testid="protected-content">Secret</div>
        </ProtectedRoute>
      </MemoryRouter>
    );
    expect(screen.getByTestId("protected-content")).toHaveTextContent("Secret");
  });

  it("redirects to /login when not authenticated", async () => {
    const { useAuth } = await import("../shared/context/AuthContext");
    useAuth.mockReturnValue({ isAuthenticated: false });
    render(
      <MemoryRouter initialEntries={["/dashboard"]}>
        <ProtectedRoute>
          <div>Secret</div>
        </ProtectedRoute>
      </MemoryRouter>
    );
    expect(screen.queryByText("Secret")).not.toBeInTheDocument();
  });
});
