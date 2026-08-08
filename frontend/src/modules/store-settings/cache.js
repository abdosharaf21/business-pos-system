import api from "../../shared/services/axios";
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
