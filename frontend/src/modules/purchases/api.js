import api from "../../shared/services/axios";
import { createCrudService } from "../../shared/services/crud";

export const purchaseService = {
  ...createCrudService("/purchases"),
  getInvoice: (id) => api.get(`/purchases/${id}/invoice`),
  searchProducts: (q) => api.get(`/purchases/products/search?q=${encodeURIComponent(q)}`),
};
