import api from "../../shared/services/axios";

export const inventoryService = {
  getAll: (search) =>
    api.get("/inventory/", { params: { search: search || undefined } }),
  getSummary: () => api.get("/inventory/summary"),
  getLowStock: () => api.get("/inventory/low-stock"),
  getMovements: (params) => api.get("/inventory/movements", { params }),
  transferStock: (data) => api.post("/inventory/transfer", data),
  adjustStock: (data) => api.post("/inventory/adjust", data),
};
