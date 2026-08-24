import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { ShoppingCart, Search } from "lucide-react";
import { useState } from "react";
import { inventoryService } from "./api";
import { PageHeader } from "../../shared/components/PageHeader";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { DataTable } from "../../shared/components/DataTable";
import { EmptyState } from "../../shared/components/EmptyState";
import { Badge } from "../../shared/components/Badge";
import { searchInputClass } from "../../shared/components/styles";

export default function InventoryReorderPage() {
  const { t } = useTranslation();
  const [search, setSearch] = useState("");

  const { data: lowStock = [], isLoading, error, refetch } = useQuery({
    queryKey: ["inventory-low-stock"],
    queryFn: async () => (await inventoryService.getLowStock()).data.data,
  });

  const filtered = lowStock.filter(
    (p) =>
      p.name?.toLowerCase().includes(search.toLowerCase()) ||
      (p.barcode || "").toLowerCase().includes(search.toLowerCase())
  );

  const columns = [
    {
      key: "name",
      label: t("inventory.reorder.columns.product"),
      render: (val, row) => (
        <div className="flex flex-col">
          <span className="text-[13px] font-semibold text-surface-800 dark:text-surface-100">{val}</span>
          <span className="text-[11px] text-surface-400 dark:text-surface-500">{row.category_name || "-"}</span>
        </div>
      ),
    },
    {
      key: "total",
      label: t("inventory.reorder.columns.current"),
      render: (val) => (
        <span className="numeric-value text-[13px] font-bold text-red-600 dark:text-red-400">{val}</span>
      ),
    },
    {
      key: "minimum_stock",
      label: t("inventory.reorder.columns.minimum"),
      render: (val) => (
        <span className="numeric-value text-[13px] text-surface-600 dark:text-surface-300">{val}</span>
      ),
    },
    {
      key: "suggested",
      label: t("inventory.reorder.columns.suggestedOrder"),
      render: (_, row) => {
        const suggested = Math.max(row.minimum_stock * 2 - row.total, row.minimum_stock);
        return (
          <Badge variant="warning">
            <span className="numeric-value">{suggested}</span>
          </Badge>
        );
      },
    },
    {
      key: "selling_price",
      label: t("inventory.reorder.columns.unitPrice"),
      render: (val) => (
        <span className="numeric-value text-[13px] text-surface-600 dark:text-surface-300">
          {val != null ? Number(val).toFixed(2) : "-"}
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
        title={t("inventory.reorder.title")}
        description={t("inventory.reorder.description")}
      />

      <div className="mb-6">
        <div className="relative">
          <Search className="w-4 h-4 absolute start-3.5 top-1/2 -translate-y-1/2 text-surface-400 dark:text-surface-500 pointer-events-none" />
          <input
            type="text"
            placeholder={t("inventory.reorder.searchPlaceholder")}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className={searchInputClass}
            aria-label={t("inventory.reorder.searchPlaceholder")}
          />
        </div>
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          icon={ShoppingCart}
          title={t("inventory.reorder.empty.title")}
          description={
            search ? t("inventory.reorder.empty.noResults") : t("inventory.reorder.empty.allStocked")
          }
        />
      ) : (
        <DataTable columns={columns} data={filtered} />
      )}
    </div>
  );
}
