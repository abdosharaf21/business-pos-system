import api from "../../shared/services/axios";

export const posService = {
  getProducts: (params) => api.get("/pos/products", { params }),
  getCategories: () => api.get("/pos/categories"),
  checkout: (data) => api.post("/pos/checkout", data),
  searchCustomers: (q) => api.get("/pos/customers/search", { params: { q } }),
  getInvoice: (saleId) => api.get(`/pos/invoice/${saleId}`),
};
