import api from "../../shared/services/axios";

export const categoryService = {
  getAll: () => api.get("/service-categories/"),
  getById: (id) => api.get(`/service-categories/${id}`),
  create: (data) => api.post("/service-categories/", data),
  update: (id, data) => api.put(`/service-categories/${id}`, data),
  delete: (id) => api.delete(`/service-categories/${id}`),
};
