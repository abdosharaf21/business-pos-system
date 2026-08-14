import api from "./axios";
import config from "../../config";

let cachedSettings = null;

export function setStoreSettings(settings) {
  cachedSettings = settings;
}

export function getStoreSettings() {
  return cachedSettings;
}

export async function loadStoreSettings() {
  if (cachedSettings) return cachedSettings;
  try {
    const res = await api.get("/store-settings/");
    cachedSettings = res.data.data;
  } catch {
    cachedSettings = null;
  }
  return cachedSettings;
}

export function getAssetUrl(route, version) {
  const base = (config.apiBaseUrl || "/api").replace(/\/+$/, "");
  const url = `${base}${route}`;
  if (!version) return url;
  return `${url}?v=${encodeURIComponent(version)}`;
}

export function getLogoUrl() {
  if (!cachedSettings?.logo_path) return null;
  return getAssetUrl("/store-settings/logo", cachedSettings.logo_path);
}

export function getLoginBackgroundUrl() {
  if (!cachedSettings?.login_background_path) return null;
  return getAssetUrl(
    "/store-settings/login-background",
    cachedSettings.login_background_path
  );
}

export function getLoginLogoUrl() {
  if (!cachedSettings?.login_logo_path) return null;
  return getAssetUrl(
    "/store-settings/login-logo",
    cachedSettings.login_logo_path
  );
}

const CURRENCY_SYMBOLS = {
  EGP: "ج.م",
  USD: "$",
  EUR: "€",
  GBP: "£",
  SAR: "ر.س",
  AED: "د.إ",
  KWD: "د.ك",
  QAR: "ر.ق",
  JOD: "د.أ",
  TRY: "₺",
  LBP: "ل.ل",
  MAD: "د.م.",
};

export function getCurrencySymbol() {
  const currency = cachedSettings?.currency;
  if (!currency) return "ج.م";
  return CURRENCY_SYMBOLS[currency.toUpperCase()] || currency;
}

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
