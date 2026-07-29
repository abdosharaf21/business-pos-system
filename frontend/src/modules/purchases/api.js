import api from "../../shared/services/axios";

export const purchaseService = {
  getAll: () => api.get("/purchases/"),
  getById: (id) => api.get(`/purchases/${id}`),
  create: (data) => api.post("/purchases/", data),
  getInvoice: (id) => api.get(`/purchases/${id}/invoice`),
  searchProducts: (q) => api.get(`/purchases/products/search?q=${encodeURIComponent(q)}`),
};

export const supplierService = {
  getAll: () => api.get("/suppliers/"),
  create: (data) => api.post("/suppliers/", data),
};
