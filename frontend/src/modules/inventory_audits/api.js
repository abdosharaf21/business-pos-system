import api from "../../shared/services/axios";
import { createCrudService } from "../../shared/services/crud";

export const auditService = {
  ...createCrudService("/inventory-audits"),
  getItems: (id) => api.get(`/inventory-audits/${id}/items`),
  complete: (id) => api.post(`/inventory-audits/${id}/complete`),
};

export const AUDIT_LOCATIONS = ["warehouse", "store"];
export const AUDIT_STATUSES = ["open", "completed", "cancelled"];
