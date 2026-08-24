/**
 * Shared notification API service.
 *
 * Thin axios wrapper for the notifications endpoints, consumed by the
 * shared NotificationBell and re-exported by the notifications module.
 */

import api from "./axios";

export const notificationService = {
  getAll: (params) => api.get("/notifications/", { params }),
  getUnreadCount: () => api.get("/notifications/unread-count"),
  sync: () => api.post("/notifications/sync"),
  markAsRead: (notificationId) =>
    api.post(`/notifications/${notificationId}/read`),
  markAllAsRead: () => api.post("/notifications/read-all"),
};
