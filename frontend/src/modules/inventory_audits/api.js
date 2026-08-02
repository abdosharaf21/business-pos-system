import api from "../../shared/services/axios";

export const auditService = {
  getAll: (params) => api.get("/inventory-audits/", { params }),
  getById: (id) => api.get(`/inventory-audits/${id}`),
  getItems: (id) => api.get(`/inventory-audits/${id}/items`),
  create: (data) => api.post("/inventory-audits/", data),
  update: (id, data) => api.put(`/inventory-audits/${id}`, data),
  complete: (id) => api.post(`/inventory-audits/${id}/complete`),
  delete: (id) => api.delete(`/inventory-audits/${id}`),
};

export const AUDIT_LOCATIONS = ["warehouse", "store"];
export const AUDIT_STATUSES = ["open", "completed", "cancelled"];
