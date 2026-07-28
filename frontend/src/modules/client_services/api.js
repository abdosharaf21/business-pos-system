import api from "../../shared/services/axios";

export const clientServiceApi = {
  getByClient: (clientId) => api.get(`/client-services/client/${clientId}`),
  getByService: (serviceId) => api.get(`/client-services/service/${serviceId}`),
  assign: (clientId, serviceId, data) =>
    api.post(`/client-services/${clientId}/assign/${serviceId}`, data),
  update: (id, data) => api.put(`/client-services/${id}`, data),
  remove: (id) => api.delete(`/client-services/${id}`),
};
