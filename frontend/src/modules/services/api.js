import { createCrudService } from "../../shared/services/crud";
import api from "../../shared/services/axios";

export const bdServiceService = {
  ...createCrudService("/services"),
  getByCategory: (categoryId) => api.get(`/services/category/${categoryId}`),
};
