import { ChevronLeft, ChevronRight } from "lucide-react";
import { paginationButtonClass } from "./styles";

export function Pagination({
  page,
  pages,
  onPageChange,
  disabled = false,
  pageText,
  prevText,
  nextText,
  variant = "footer",
}) {
  const goPrev = () => onPageChange(Math.max(1, page - 1));
  const goNext = () => onPageChange(Math.min(pages, page + 1));
  const canPrev = page > 1 && !disabled;
  const canNext = page < pages && !disabled;

  const prevButton = (
    <button
      type="button"
      onClick={goPrev}
      disabled={!canPrev}
      className={paginationButtonClass}
      aria-label={prevText}
    >
      <ChevronLeft className="w-4 h-4 rtl:rotate-180" />
      {prevText}
    </button>
  );

  const nextButton = (
    <button
      type="button"
      onClick={goNext}
      disabled={!canNext}
      className={paginationButtonClass}
      aria-label={nextText}
    >
      {nextText}
      <ChevronRight className="w-4 h-4 rtl:rotate-180" />
    </button>
  );

  if (variant === "center") {
    return (
      <div className="mt-6 flex items-center justify-center gap-3">
        {prevButton}
        <span className="text-[13px] font-semibold text-surface-600 dark:text-surface-300">
          {pageText}
        </span>
        {nextButton}
      </div>
    );
  }

  return (
    <div className="flex items-center justify-between px-5 py-3.5 border-t border-surface-100 dark:border-surface-700/60">
      <p className="text-[12px] text-surface-400 dark:text-surface-500">{pageText}</p>
      <div className="flex items-center gap-2">
        {prevButton}
        {nextButton}
      </div>
    </div>
  );
}
