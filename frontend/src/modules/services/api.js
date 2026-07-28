import api from "../../shared/services/axios";

export const serviceService = {
  getAll: () => api.get("/services/"),
  getById: (id) => api.get(`/services/${id}`),
  getByCategory: (categoryId) => api.get(`/services/category/${categoryId}`),
  create: (data) => api.post("/services/", data),
  update: (id, data) => api.put(`/services/${id}`, data),
  delete: (id) => api.delete(`/services/${id}`),
};
