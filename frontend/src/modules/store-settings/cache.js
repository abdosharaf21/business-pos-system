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

export function getAssetUrl(route) {
  const base = (config.apiBaseUrl || "/api").replace(/\/+$/, "");
  return `${base}${route}`;
}

export function getLogoUrl() {
  if (!cachedSettings?.logo_path) return null;
  return getAssetUrl("/store-settings/logo");
}

export function getLoginBackgroundUrl() {
  if (!cachedSettings?.login_background_path) return null;
  return getAssetUrl("/store-settings/login-background");
}

export function getLoginLogoUrl() {
  if (!cachedSettings?.login_logo_path) return null;
  return getAssetUrl("/store-settings/login-logo");
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
