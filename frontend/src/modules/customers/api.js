import api from "../../shared/services/axios";

export const customerService = {
  getAll: () => api.get("/customers/"),
  getById: (id) => api.get(`/customers/${id}`),
  create: (data) => api.post("/customers/", data),
  update: (id, data) => api.put(`/customers/${id}`, data),
  delete: (id) => api.delete(`/customers/${id}`),
};
