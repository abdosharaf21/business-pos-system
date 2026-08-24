import api from "../../shared/services/axios";

export const transferService = {
  getAll: (params) => api.get("/inventory/transfers", { params }),
  getById: (id) => api.get(`/inventory/transfers/${id}`),
  create: (data) => api.post("/inventory/transfers", data),
  complete: (id) => api.post(`/inventory/transfers/${id}/complete`),
  cancel: (id) => api.post(`/inventory/transfers/${id}/cancel`),
};

export const TRANSFER_STATUSES = ["pending", "completed", "cancelled"];
