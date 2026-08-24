const STORAGE_KEY = "theme";

export const THEMES = {
  LIGHT: "light",
  DARK: "dark",
};

/**
 * Read the theme persisted by the user, if any.
 *
 * @returns {string|null} "light", "dark" or null when nothing was stored.
 */
export function getStoredTheme() {
  try {
    return localStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

/**
 * Resolve the operating system colour-scheme preference.
 *
 * @returns {string} "dark" when the system prefers dark mode, otherwise "light".
 */
export function getSystemTheme() {
  if (typeof window === "undefined" || !window.matchMedia) return THEMES.LIGHT;
  return window.matchMedia("(prefers-color-scheme: dark)").matches
    ? THEMES.DARK
    : THEMES.LIGHT;
}

/**
 * Resolve the theme that should currently be applied.
 *
 * @returns {string} the stored user preference or the system preference.
 */
export function getActiveTheme() {
  const stored = getStoredTheme();
  if (stored === THEMES.LIGHT || stored === THEMES.DARK) return stored;
  return getSystemTheme();
}

/**
 * Apply a theme to the document root.
 *
 * @param {string} theme "light" or "dark".
 * @returns {string} the applied theme.
 */
export function applyTheme(theme) {
  const resolved = theme === THEMES.DARK ? THEMES.DARK : THEMES.LIGHT;
  document.documentElement.classList.toggle("dark", resolved === THEMES.DARK);
  document.documentElement.style.colorScheme = resolved;
  return resolved;
}

/**
 * Persist and apply a theme.
 *
 * @param {string} theme "light" or "dark".
 * @returns {string} the applied theme.
 */
export function setTheme(theme) {
  try {
    localStorage.setItem(STORAGE_KEY, theme);
  } catch {
    // Storage may be unavailable (private mode); still apply the theme.
  }
  return applyTheme(theme);
}

/**
 * Switch between light and dark mode.
 *
 * @returns {string} the newly applied theme.
 */
export function toggleTheme() {
  return setTheme(getActiveTheme() === THEMES.DARK ? THEMES.LIGHT : THEMES.DARK);
}
