import api from "../../shared/services/axios";

export const clientServiceAssignmentService = {
  getByClient: (clientId) => api.get(`/client-services/client/${clientId}`),
  getByService: (serviceId) => api.get(`/client-services/service/${serviceId}`),
  assign: (clientId, serviceId, data) =>
    api.post(`/client-services/${clientId}/assign/${serviceId}`, data),
  update: (assignmentId, data) =>
    api.put(`/client-services/${assignmentId}`, data),
  delete: (assignmentId) => api.delete(`/client-services/${assignmentId}`),
};

export const ASSIGNMENT_STATUSES = [
  "pending",
  "in_progress",
  "completed",
  "cancelled",
];
