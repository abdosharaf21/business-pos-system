import api from "../../shared/services/axios";

export const expenseService = {
  getAll: (params) => api.get("/expenses/", { params }),
  getById: (id) => api.get(`/expenses/${id}`),
  getCategories: () => api.get("/expenses/categories"),
  create: (data) => api.post("/expenses/", data),
  update: (id, data) => api.put(`/expenses/${id}`, data),
  delete: (id) => api.delete(`/expenses/${id}`),
  getSummary: () => api.get("/expenses/summary"),
  getMonthly: (params) => api.get("/expenses/monthly", { params }),
  getYearly: (params) => api.get("/expenses/yearly", { params }),
  getByCategory: (params) => api.get("/expenses/by-category", { params }),
  getByPayment: (params) => api.get("/expenses/by-payment", { params }),
};

export const PAYMENT_METHODS = ["Cash", "Bank", "Visa", "Other"];
