import api from "../../shared/services/axios";
import { createCrudService } from "../../shared/services/crud";

export const userService = {
  ...createCrudService("/users"),
  changePassword: (id, newPassword) =>
    api.put(`/users/${id}/password`, { new_password: newPassword }),
  activate: (id) => api.put(`/users/${id}/activate`),
  deactivate: (id) => api.put(`/users/${id}/deactivate`),
};
