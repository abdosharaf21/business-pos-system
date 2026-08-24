import api from "../../shared/services/axios";

export const warehouseService = {
  getAll: () => api.get("/inventory/warehouses"),
  getById: (id) => api.get(`/inventory/warehouses/${id}`),
  create: (data) => api.post("/inventory/warehouses", data),
  update: (id, data) => api.put(`/inventory/warehouses/${id}`, data),
  changeStatus: (id, status) =>
    api.patch(`/inventory/warehouses/${id}/status`, { status }),
  delete: (id) => api.delete(`/inventory/warehouses/${id}`),
  getStock: (id, params) =>
    api.get(`/inventory/warehouses/${id}/stock`, { params }),
};

export const WAREHOUSE_STATUSES = ["active", "inactive"];
