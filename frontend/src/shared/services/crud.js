import api from "./axios";

export function createCrudService(resource) {
  const base = resource.replace(/\/+$/, "");
  return {
    getAll: (params) => api.get(`${base}/`, { params }),
    getById: (id) => api.get(`${base}/${id}`),
    create: (data) => api.post(`${base}/`, data),
    update: (id, data) => api.put(`${base}/${id}`, data),
    delete: (id) => api.delete(`${base}/${id}`),
  };
}
