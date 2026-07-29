import api from "../../shared/services/axios";

export const productService = {
  getAll: () => api.get("/products/"),
  getById: (id) => api.get(`/products/${id}`),
  create: (data) => api.post("/products/", data),
  update: (id, data) => api.put(`/products/${id}`, data),
  delete: (id) => api.delete(`/products/${id}`),
};
