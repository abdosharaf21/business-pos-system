import api from "../../shared/services/axios";

export const dealService = {
  getAll: (search) => api.get("/deals/", { params: search ? { search } : {} }),
  getById: (id) => api.get(`/deals/${id}`),
  create: (data) => api.post("/deals/", data),
  update: (id, data) => api.put(`/deals/${id}`, data),
  delete: (id) => api.delete(`/deals/${id}`),
  changeStatus: (id, status) => api.put(`/deals/${id}/status`, { status }),
  changePaymentStatus: (id, status) => api.put(`/deals/${id}/payment-status`, { status }),
  getStatistics: () => api.get("/deals/statistics"),
  getByClient: (clientId) => api.get(`/deals/client/${clientId}`),
  getByService: (serviceId) => api.get(`/deals/service/${serviceId}`),
};
