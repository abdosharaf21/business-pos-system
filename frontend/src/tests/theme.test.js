import { describe, it, expect, beforeEach, afterEach } from "vitest";
import {
  applyTheme,
  getActiveTheme,
  getStoredTheme,
  getSystemTheme,
  setTheme,
  toggleTheme,
  THEMES,
} from "../shared/utils/theme";

describe("theme", () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.classList.remove("dark");
    document.documentElement.style.colorScheme = "";
    window.matchMedia = undefined;
  });

  afterEach(() => {
    delete window.matchMedia;
  });

  it("falls back to light when nothing is stored and the system has no preference", () => {
    expect(getStoredTheme()).toBeNull();
    expect(getSystemTheme()).toBe(THEMES.LIGHT);
    expect(getActiveTheme()).toBe(THEMES.LIGHT);
    expect(document.documentElement.classList.contains("dark")).toBe(false);
  });

  it("follows the system dark preference when no user preference is stored", () => {
    window.matchMedia = (query) => ({
      matches: query === "(prefers-color-scheme: dark)",
      media: query,
    });
    expect(getSystemTheme()).toBe(THEMES.DARK);
    expect(getActiveTheme()).toBe(THEMES.DARK);
  });

  it("applies the dark class and color scheme to the document root", () => {
    applyTheme(THEMES.DARK);
    expect(document.documentElement.classList.contains("dark")).toBe(true);
    expect(document.documentElement.style.colorScheme).toBe(THEMES.DARK);

    applyTheme(THEMES.LIGHT);
    expect(document.documentElement.classList.contains("dark")).toBe(false);
    expect(document.documentElement.style.colorScheme).toBe(THEMES.LIGHT);
  });

  it("persists the selected theme", () => {
    expect(setTheme(THEMES.DARK)).toBe(THEMES.DARK);
    expect(getStoredTheme()).toBe(THEMES.DARK);

    expect(setTheme(THEMES.LIGHT)).toBe(THEMES.LIGHT);
    expect(getStoredTheme()).toBe(THEMES.LIGHT);
  });

  it("lets a stored preference override the system preference", () => {
    window.matchMedia = () => ({ matches: true, media: "(prefers-color-scheme: dark)" });
    localStorage.setItem("theme", THEMES.LIGHT);
    expect(getActiveTheme()).toBe(THEMES.LIGHT);
  });

  it("toggles between light and dark mode", () => {
    expect(toggleTheme()).toBe(THEMES.DARK);
    expect(document.documentElement.classList.contains("dark")).toBe(true);

    expect(toggleTheme()).toBe(THEMES.LIGHT);
    expect(document.documentElement.classList.contains("dark")).toBe(false);
    expect(localStorage.getItem("theme")).toBe(THEMES.LIGHT);
  });
});
