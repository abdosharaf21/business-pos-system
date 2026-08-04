import api from "../../shared/services/axios";

export const storeSettingsService = {
  get: () => api.get("/store-settings/"),
  getPublic: () => api.get("/store-settings/public"),
  update: (data) => api.put("/store-settings/", data),
  updateWithFiles: (data, files = {}, removes = {}) => {
    const formData = new FormData();
    Object.entries(data).forEach(([key, value]) => {
      formData.append(key, value == null ? "" : String(value));
    });
    if (removes.logo) {
      formData.append("remove_logo", "1");
    }
    if (removes.loginBackground) {
      formData.append("remove_login_background", "1");
    }
    if (removes.loginLogo) {
      formData.append("remove_login_logo", "1");
    }
    if (files.logo) {
      formData.append("logo", files.logo);
    }
    if (files.loginBackground) {
      formData.append("login_background", files.loginBackground);
    }
    if (files.loginLogo) {
      formData.append("login_logo", files.loginLogo);
    }
    return api.put("/store-settings/", formData);
  },
};
