/**
 * Shared UI class tokens.
 *
 * Single source of truth for the ERP design language used across every
 * module page. Prevents duplicated inline styles and guarantees every
 * surface is dark-ready.
 */

export const cardClass =
  "bg-white dark:bg-surface-800/60 rounded-2xl border border-surface-200/80 dark:border-surface-700/60 shadow-card";

export const cardClassOverflowHidden =
  "bg-white dark:bg-surface-800/60 rounded-2xl border border-surface-200/80 dark:border-surface-700/60 overflow-hidden shadow-card";

export const filterBarClass =
  "p-4 bg-white dark:bg-surface-800/60 rounded-2xl border border-surface-200/80 dark:border-surface-700/60 shadow-card";

export const labelClass =
  "block text-[13px] font-semibold text-surface-700 dark:text-surface-300 mb-1.5";

export const inputClass =
  "w-full px-3.5 py-2.5 border border-surface-200 dark:border-surface-700/60 bg-surface-50 dark:bg-surface-700/40 rounded-xl text-sm text-surface-800 dark:text-surface-200 placeholder:text-surface-400 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150";

export const selectClass = `${inputClass} appearance-none cursor-pointer`;

export const searchInputClass =
  "w-full ps-10 pe-4 py-2.5 border border-surface-200 dark:border-surface-700/60 bg-white dark:bg-surface-700/40 rounded-xl text-sm text-surface-800 dark:text-surface-200 placeholder:text-surface-400 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150 shadow-card";

export const primaryButtonClass =
  "inline-flex items-center justify-center gap-2 px-4 py-2.5 text-[13px] font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 rounded-xl shadow-sm shadow-primary-600/20 transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed";

export const secondaryButtonClass =
  "inline-flex items-center justify-center gap-2 px-4 py-2.5 text-[13px] font-semibold text-surface-600 dark:text-surface-300 bg-white dark:bg-surface-700/60 border border-surface-200 dark:border-surface-700/60 rounded-xl hover:bg-surface-50 dark:hover:bg-surface-700 transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed";

export const ghostButtonClass =
  "inline-flex items-center gap-1.5 px-3 py-1.5 text-[12px] font-semibold text-surface-500 dark:text-surface-400 bg-surface-50 dark:bg-surface-700/40 hover:bg-surface-100 dark:hover:bg-surface-700/60 hover:text-surface-700 dark:hover:text-surface-200 rounded-lg transition-colors";

export const iconButtonClass =
  "p-2 text-surface-400 hover:text-primary-600 hover:bg-primary-50 dark:hover:bg-primary-500/10 rounded-xl transition-all duration-150";

export const dangerIconButtonClass =
  "p-2 text-surface-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-500/10 rounded-xl transition-all duration-150";

export const amberIconButtonClass =
  "p-2 text-surface-400 hover:text-amber-600 hover:bg-amber-50 dark:hover:bg-amber-500/10 rounded-xl transition-all duration-150";

export const paginationButtonClass =
  "inline-flex items-center gap-1 px-3 py-1.5 rounded-xl border border-surface-200 dark:border-surface-700/60 text-[12px] font-semibold text-surface-600 dark:text-surface-300 bg-white dark:bg-surface-700/40 hover:bg-surface-50 dark:hover:bg-surface-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors";

export const tableHeadClass =
  "border-b border-surface-100 dark:border-surface-700/60 bg-surface-50/60 dark:bg-surface-700/30";

export const tableBodyClass =
  "divide-y divide-surface-100 dark:divide-surface-700/60";

export const tableRowClass =
  "hover:bg-surface-50/50 dark:hover:bg-surface-700/30 transition-colors duration-100";

export const sectionTitleClass =
  "text-[15px] font-semibold text-surface-900 dark:text-surface-100";
