import api from "../../shared/services/axios";
import { createCrudService } from "../../shared/services/crud";

export const categoryService = {
  ...createCrudService("/categories"),
  getTree: () => api.get("/categories/tree"),
};
