import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import i18n from "../i18n";

vi.mock("../shared/services/notifications", () => ({
  notificationService: {
    getAll: vi.fn(),
    getUnreadCount: vi.fn(),
    markAllAsRead: vi.fn(),
    markAsRead: vi.fn(),
    sync: vi.fn(),
  },
}));

import NotificationBell from "../shared/components/NotificationBell/NotificationBell";
import { notificationService } from "../modules/notifications/api";

function renderBell() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <NotificationBell />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

const UNREAD = {
  data: { data: { unread_count: 0 } },
};

describe("NotificationBell", () => {
  beforeEach(() => {
    i18n.changeLanguage("en");
    vi.clearAllMocks();
    notificationService.getUnreadCount.mockResolvedValue(UNREAD);
  });

  it("renders a bell button", () => {
    renderBell();
    expect(
      screen.getByRole("button", { name: "Notifications" })
    ).toBeInTheDocument();
  });

  it("shows the unread count badge", async () => {
    notificationService.getUnreadCount.mockResolvedValue({
      data: { data: { unread_count: 3 } },
    });
    renderBell();
    expect(await screen.findByText("3")).toBeInTheDocument();
  });

  it("hides the badge when there are no unread notifications", async () => {
    renderBell();
    await waitFor(() => {
      expect(screen.queryByText(/99\+|^\d+$/)).not.toBeInTheDocument();
    });
  });

  it("opens the panel and lists notifications", async () => {
    notificationService.getAll.mockResolvedValue({
      data: {
        data: [
          {
            id: 1,
            product_id: 10,
            notification_type: "low_stock",
            priority: "warning",
            is_read: false,
            product_name: "Keyboard",
            quantity: 2,
            created_at: "2026-08-01T10:00:00",
          },
        ],
      },
    });
    const user = userEvent.setup();
    renderBell();
    await user.click(screen.getByRole("button", { name: "Notifications" }));
    expect(await screen.findByText("Keyboard")).toBeInTheDocument();
    expect(screen.getByText("Low stock")).toBeInTheDocument();
  });

  it("shows the empty state when there are no notifications", async () => {
    notificationService.getAll.mockResolvedValue({ data: { data: [] } });
    const user = userEvent.setup();
    renderBell();
    await user.click(screen.getByRole("button", { name: "Notifications" }));
    expect(
      await screen.findByText("You're all caught up")
    ).toBeInTheDocument();
  });

  it("marks all notifications as read", async () => {
    notificationService.getUnreadCount.mockResolvedValue({
      data: { data: { unread_count: 1 } },
    });
    notificationService.getAll.mockResolvedValue({
      data: {
        data: [
          {
            id: 1,
            product_id: 10,
            notification_type: "expired",
            priority: "critical",
            is_read: false,
            product_name: "Milk",
            created_at: "2026-08-01T10:00:00",
          },
        ],
      },
    });
    notificationService.markAllAsRead.mockResolvedValue({
      data: { data: { updated: 1 } },
    });
    const user = userEvent.setup();
    renderBell();
    await user.click(screen.getByRole("button", { name: "Notifications" }));
    await user.click(screen.getByRole("button", { name: /Mark all as read/i }));
    await waitFor(() => {
      expect(notificationService.markAllAsRead).toHaveBeenCalled();
    });
  });

  it("navigates to the product and marks it read on click", async () => {
    notificationService.getAll.mockResolvedValue({
      data: {
        data: [
          {
            id: 7,
            product_id: 10,
            notification_type: "out_of_stock",
            priority: "critical",
            is_read: false,
            product_name: "Mouse",
            created_at: "2026-08-01T10:00:00",
          },
        ],
      },
    });
    notificationService.markAsRead.mockResolvedValue({
      data: { data: { id: 7, is_read: true } },
    });
    const user = userEvent.setup();
    renderBell();
    await user.click(screen.getByRole("button", { name: "Notifications" }));
    await user.click(await screen.findByText("Mouse"));
    await waitFor(() => {
      expect(notificationService.markAsRead).toHaveBeenCalledWith(7);
    });
  });
});
