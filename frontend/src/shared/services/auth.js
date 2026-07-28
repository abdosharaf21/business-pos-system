import api from "./axios";

export const authService = {
  login: (email, password) =>
    api.post("/auth/login", { email, password }),

  logout: (refreshToken) =>
    api.post("/auth/logout", { refresh_token: refreshToken }),

  refresh: (refreshToken) =>
    api.post("/auth/refresh", { refresh_token: refreshToken }),

  me: () => api.get("/auth/me"),

  changePassword: (currentPassword, newPassword) =>
    api.put("/auth/change-password", {
      current_password: currentPassword,
      new_password: newPassword,
    }),
};
