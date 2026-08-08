import api from "../../shared/services/axios";

export const inventoryService = {
  getAll: (search, expirationStatus, sort) =>
    api.get("/inventory/", {
      params: {
        search: search || undefined,
        expiration_status: expirationStatus || undefined,
        sort: sort || undefined,
      },
    }),
  getSummary: () => api.get("/inventory/summary"),
  getLowStock: () => api.get("/inventory/low-stock"),
  getMovements: (params) => api.get("/inventory/movements", { params }),
  transferStock: (data) => api.post("/inventory/transfer", data),
  updateExpiration: (productId, expirationDate) =>
    api.put(`/inventory/${productId}/expiration`, { expiration_date: expirationDate }),
};
