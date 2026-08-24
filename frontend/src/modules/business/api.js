import api from "../../shared/services/axios";

export const businessDevelopmentService = {
  getStatistics: () => api.get("/business-development/statistics"),
};
