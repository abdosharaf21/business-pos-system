import api from "../../shared/services/axios";

export const dashboardService = {
  getStats: () => api.get("/dashboard/statistics"),
};
