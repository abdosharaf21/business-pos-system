import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { FolderOpen } from "lucide-react";
import { expenseService } from "./api";
import { PageHeader } from "../../shared/components/PageHeader";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { DataTable } from "../../shared/components/DataTable";
import { EmptyState } from "../../shared/components/EmptyState";

export default function ExpenseCategoriesPage() {
  const { t } = useTranslation();

  const { data: categories = [], isLoading, error, refetch } = useQuery({
    queryKey: ["expense-categories"],
    queryFn: async () => (await expenseService.getCategories()).data.data,
  });

  const columns = [
    {
      key: "name",
      label: t("expenses.categoriesPage.columns.name"),
      render: (val) => (
        <span className="text-[13px] font-semibold text-surface-800 dark:text-surface-100">{val}</span>
      ),
    },
    {
      key: "description",
      label: t("expenses.categoriesPage.columns.description"),
      render: (val) => (
        <span className="text-[13px] text-surface-500 dark:text-surface-400 line-clamp-1 max-w-md">
          {val || "-"}
        </span>
      ),
    },
  ];

  if (isLoading) return <LoadingSpinner />;
  if (error)
    return (
      <ErrorDisplay
        message={error.response?.data?.message || error.message}
        onRetry={refetch}
      />
    );

  return (
    <div>
      <PageHeader
        title={t("expenses.categoriesPage.title")}
        description={t("expenses.categoriesPage.description")}
      />

      {categories.length === 0 ? (
        <EmptyState
          icon={FolderOpen}
          title={t("expenses.categoriesPage.empty.title")}
          description={t("expenses.categoriesPage.empty.noCategories")}
        />
      ) : (
        <DataTable columns={columns} data={categories} />
      )}
    </div>
  );
}
