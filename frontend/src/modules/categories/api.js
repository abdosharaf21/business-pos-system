import api from "../../shared/services/axios";

export const categoryService = {
  getAll: () => api.get("/categories/"),
  getById: (id) => api.get(`/categories/${id}`),
  create: (data) => api.post("/categories/", data),
  update: (id, data) => api.put(`/categories/${id}`, data),
  delete: (id) => api.delete(`/categories/${id}`),
};
