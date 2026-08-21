import api from "../../shared/services/axios";

export const clientService = {
  getAll: () => api.get("/clients/"),
  getById: (id) => api.get(`/clients/${id}`),
  create: (data) => api.post("/clients/", data),
  update: (id, data) => api.put(`/clients/${id}`, data),
  delete: (id) => api.delete(`/clients/${id}`),
  changeStatus: (id, status) => api.put(`/clients/${id}/status`, { status }),
};
