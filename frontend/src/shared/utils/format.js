/**
 * Shared formatting helpers.
 *
 * Generic, domain-independent formatting used across applications:
 * locale resolution, date/time formatting and API error message
 * extraction. Contains no business logic and no application-specific
 * imports.
 */

/** Locale used when the active language is Arabic. */
export const ARABIC_LOCALE = "ar-EG";

/** Locale used for every non-Arabic language. */
export const DEFAULT_LOCALE = "en-US";

/** Default options for formatDate (matches the common table cell format). */
export const SHORT_DATE_OPTIONS = {
  year: "numeric",
  month: "short",
  day: "numeric",
};

/**
 * Resolve the Intl locale for an i18n language code.
 *
 * Args:
 *     language: Active i18n language code (e.g. "ar", "en").
 *
 * Returns:
 *     The BCP-47 locale tag used for date/number formatting.
 */
export function getCurrentLocale(language) {
  return language === "ar" ? ARABIC_LOCALE : DEFAULT_LOCALE;
}

/**
 * Format a timestamp as a short localized date ("Jan 5, 2026").
 *
 * Args:
 *     value: Date-constructible value (Date, ISO string, number).
 *     locale: Locale tag; defaults to en-US.
 *     options: Optional toLocaleDateString options override.
 *
 * Returns:
 *     The formatted date string.
 */
export function formatDate(value, locale = DEFAULT_LOCALE, options = null) {
  return new Date(value).toLocaleDateString(
    locale,
    options || SHORT_DATE_OPTIONS
  );
}

/**
 * Format a timestamp as a short localized datetime ("Jan 5, 3:05 PM"),
 * returning an empty string for missing values or invalid dates.
 *
 * Args:
 *     value: Date-constructible value.
 *     locale: Locale tag; defaults to en-US.
 *
 * Returns:
 *     The formatted datetime string, or "" when value is falsy/invalid.
 */
export function formatTime(value, locale = DEFAULT_LOCALE) {
  if (!value) return "";
  try {
    return new Date(value).toLocaleString(locale, {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
    });
  } catch {
    return "";
  }
}

/**
 * Extract a human-readable message from an axios/API error.
 *
 * Mirrors the established inline pattern
 * ``error?.response?.data?.message || fallback`` so call sites keep
 * their exact behavior when migrated.
 *
 * Args:
 *     error: The caught error object.
 *     fallback: Message to use when the API returned no message.
 *
 * Returns:
 *     The best available error message.
 */
export function getApiErrorMessage(error, fallback = "") {
  return error?.response?.data?.message || fallback;
}
