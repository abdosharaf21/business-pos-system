import api from "../../shared/services/axios";

export const supplierService = {
  getAll: () => api.get("/suppliers/"),
  getById: (id) => api.get(`/suppliers/${id}`),
  create: (data) => api.post("/suppliers/", data),
  update: (id, data) => api.put(`/suppliers/${id}`, data),
  delete: (id) => api.delete(`/suppliers/${id}`),
};
