import api from "../../shared/services/axios";

export const userService = {
  getAll: () => api.get("/users/"),
  getById: (id) => api.get(`/users/${id}`),
  create: (data) => api.post("/users/", data),
  update: (id, data) => api.put(`/users/${id}`, data),
  delete: (id) => api.delete(`/users/${id}`),
  changePassword: (id, newPassword) =>
    api.put(`/users/${id}/password`, { new_password: newPassword }),
  activate: (id) => api.put(`/users/${id}/activate`),
  deactivate: (id) => api.put(`/users/${id}/deactivate`),
};
