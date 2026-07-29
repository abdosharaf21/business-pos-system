import api from "../../shared/services/axios";

export const inventoryService = {
  getAll: () => api.get("/inventory/"),
  getSummary: () => api.get("/inventory/summary"),
  getLowStock: () => api.get("/inventory/low-stock"),
  getTransactions: (productId) => api.get(`/inventory/transactions${productId ? `?product_id=${productId}` : ""}`),
  adjustStock: (data) => api.post("/inventory/", data),
};
