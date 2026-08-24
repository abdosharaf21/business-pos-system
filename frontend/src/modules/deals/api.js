import { createCrudService } from "../../shared/services/crud";
import api from "../../shared/services/axios";

export const dealService = {
  ...createCrudService("/deals"),
  getStatistics: (params) => api.get("/deals/statistics", { params }),
  changeStatus: (id, dealStatus) =>
    api.put(`/deals/${id}/status`, { deal_status: dealStatus }),
  changePaymentStatus: (id, paymentStatus) =>
    api.put(`/deals/${id}/payment-status`, { payment_status: paymentStatus }),
  getByClient: (clientId) => api.get(`/deals/client/${clientId}`),
};

export const DEAL_STATUSES = ["draft", "confirmed", "delivered", "cancelled"];
export const PAYMENT_STATUSES = ["pending", "partial", "paid", "refunded"];
