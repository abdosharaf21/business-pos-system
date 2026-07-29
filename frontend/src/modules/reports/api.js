import api from "../../shared/services/axios";

export const reportService = {
  getDashboard: () => api.get("/reports/dashboard"),
  getSalesTrend: (params) => api.get("/reports/sales-trend", { params }),
  getProfit: (params) => api.get("/reports/profit", { params }),
  getProductsPerformance: () => api.get("/reports/products-performance"),
  getSuppliersPerformance: () => api.get("/reports/suppliers-performance"),
};
