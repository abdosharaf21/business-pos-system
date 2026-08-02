import api from "../../shared/services/axios";

export const reportService = {
  getDashboard: () => api.get("/reports/dashboard"),
  getSalesTrend: (params) => api.get("/reports/sales-trend", { params }),
  getProfit: (params) => api.get("/reports/profit", { params }),
  getProductsPerformance: () => api.get("/reports/products-performance"),
  getSuppliersPerformance: () => api.get("/reports/suppliers-performance"),
  getInventoryReport: () => api.get("/reports/inventory-report"),
  getMovementReport: (params) => api.get("/reports/movement", { params }),
  getMostTransferred: () => api.get("/reports/most-transferred"),
  getLowestStock: () => api.get("/reports/lowest-stock"),
  getExpensesDaily: (params) => api.get("/reports/expenses-daily", { params }),
  getExpensesCategory: (params) => api.get("/reports/expenses-category", { params }),
  getExpensesPaymentMethod: (params) => api.get("/reports/expenses-payment-method", { params }),
  getExpensesMonthlyComparison: (params) => api.get("/reports/expenses-monthly-comparison", { params }),
  getExpensesHighestCategories: (params) => api.get("/reports/expenses-highest-category", { params }),
  getInventoryAuditReport: () => api.get("/reports/inventory-audits"),
  getInventoryAuditsMonthly: (params) => api.get("/reports/inventory-audits-monthly", { params }),
  getInventoryAuditsYearly: (params) => api.get("/reports/inventory-audits-yearly", { params }),
};
