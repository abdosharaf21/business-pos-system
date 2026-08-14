import api from "../../shared/services/axios";
import { createCrudService } from "../../shared/services/crud";

export const expenseService = {
  ...createCrudService("/expenses"),
  getCategories: () => api.get("/expenses/categories"),
  getSummary: () => api.get("/expenses/summary"),
  getMonthly: (params) => api.get("/expenses/monthly", { params }),
  getYearly: (params) => api.get("/expenses/yearly", { params }),
  getByCategory: (params) => api.get("/expenses/by-category", { params }),
  getByPayment: (params) => api.get("/expenses/by-payment", { params }),
};

export const PAYMENT_METHODS = ["Cash", "Bank", "Visa", "Other"];
