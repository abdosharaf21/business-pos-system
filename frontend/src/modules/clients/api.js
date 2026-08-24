import { createCrudService } from "../../shared/services/crud";
import api from "../../shared/services/axios";

export const clientService = {
  ...createCrudService("/clients"),
  changeStatus: (id, status) => api.put(`/clients/${id}/status`, { status }),
};
