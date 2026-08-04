import { describe, it, expect, beforeEach, vi } from "vitest";

vi.mock("../shared/services/axios", () => ({
  default: { get: vi.fn() },
}));

import {
  setStoreSettings,
  getStoreSettings,
  loadStoreSettings,
  getCurrencySymbol,
  getLogoUrl,
} from "../modules/store-settings/cache";

describe("storeSettingsCache", () => {
  beforeEach(() => {
    setStoreSettings(null);
    vi.clearAllMocks();
  });

  it("defaults to EGP symbol when no settings cached", () => {
    setStoreSettings(null);
    expect(getCurrencySymbol()).toBe("ج.م");
  });

  it("uses the configured currency symbol", () => {
    setStoreSettings({ currency: "USD" });
    expect(getCurrencySymbol()).toBe("$");
  });

  it("falls back to the currency code for unknown currencies", () => {
    setStoreSettings({ currency: "XYZ" });
    expect(getCurrencySymbol()).toBe("XYZ");
  });

  it("returns null logo URL when no logo is set", () => {
    setStoreSettings({ logo_path: null });
    expect(getLogoUrl()).toBeNull();
  });

  it("returns the logo URL when a logo exists", () => {
    setStoreSettings({ logo_path: "logo.png" });
    expect(getLogoUrl()).toBe("/api/store-settings/logo");
  });

  it("loads settings from the API and caches them", async () => {
    const api = (await import("../shared/services/axios")).default;
    api.get.mockResolvedValue({ data: { data: { store_name: "My Store" } } });
    const settings = await loadStoreSettings();
    expect(settings.store_name).toBe("My Store");
    expect(api.get).toHaveBeenCalledWith("/store-settings/");
    expect(getStoreSettings()).toEqual({ store_name: "My Store" });
  });

  it("does not re-fetch when settings are already cached", async () => {
    const api = (await import("../shared/services/axios")).default;
    setStoreSettings({ store_name: "Cached Store" });
    const settings = await loadStoreSettings();
    expect(settings.store_name).toBe("Cached Store");
    expect(api.get).not.toHaveBeenCalled();
  });

  it("returns null and does not throw on API error", async () => {
    const api = (await import("../shared/services/axios")).default;
    api.get.mockRejectedValue(new Error("network"));
    const settings = await loadStoreSettings();
    expect(settings).toBeNull();
  });
});
