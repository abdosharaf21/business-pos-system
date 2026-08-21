export function LoadingSpinner({ size = "md" }) {
  const sizes = { sm: "w-5 h-5 border-2", md: "w-8 h-8 border-[3px]", lg: "w-12 h-12 border-4" };
  return (
    <div className="flex items-center justify-center py-20">
      <div className="relative">
        <div className={`${sizes[size]} border-surface-200 dark:border-surface-700/60 border-t-primary-700 rounded-full animate-spin`} />
      </div>
    </div>
  );
}
