import api from "../../shared/services/axios";

export const notificationService = {
  getAll: (params) => api.get("/notifications/", { params }),
  getUnreadCount: () => api.get("/notifications/unread-count"),
  sync: () => api.post("/notifications/sync"),
  markAsRead: (notificationId) =>
    api.post(`/notifications/${notificationId}/read`),
  markAllAsRead: () => api.post("/notifications/read-all"),
};
