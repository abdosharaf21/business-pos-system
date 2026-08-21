import api from "../../../shared/services/axios";

export const bdDashboardService = {
  getStatistics: () => api.get("/business-development/statistics"),
};
