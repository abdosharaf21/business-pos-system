import api from "../../shared/services/axios";

export const warehouseService = {
  getAll: (activeOnly) =>
    api.get("/inventory/warehouses", {
      params: { active_only: activeOnly ? "true" : undefined },
    }),
  getById: (id) => api.get(`/inventory/warehouses/${id}`),
  create: (data) => api.post("/inventory/warehouses", data),
  update: (id, data) => api.put(`/inventory/warehouses/${id}`, data),
  toggleStatus: (id, status) =>
    api.patch(`/inventory/warehouses/${id}/status`, { status }),
  delete: (id) => api.delete(`/inventory/warehouses/${id}`),
  getStock: (id, search) =>
    api.get(`/inventory/warehouses/${id}/stock`, {
      params: { search: search || undefined },
    }),
};
