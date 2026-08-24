import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { PackageSearch, Boxes, Warehouse as WarehouseIcon, Store, AlertTriangle } from "lucide-react";
import { inventoryService } from "./api";
import { PageHeader } from "../../shared/components/PageHeader";
import { StatCard } from "../../shared/components/StatCard";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { DataTable } from "../../shared/components/DataTable";
import { EmptyState } from "../../shared/components/EmptyState";
import { cardClass } from "../../shared/components/styles";

export default function InventoryOverviewPage() {
  const { t } = useTranslation();

  const summaryQuery = useQuery({
    queryKey: ["inventory-summary"],
    queryFn: async () => (await inventoryService.getSummary()).data.data,
  });

  const movementsQuery = useQuery({
    queryKey: ["inventory-movements", "recent"],
    queryFn: async () => (await inventoryService.getMovements({ limit: 10 })).data.data.items || [],
  });

  if (summaryQuery.isLoading) return <LoadingSpinner />;
  if (summaryQuery.error)
    return (
      <ErrorDisplay
        message={summaryQuery.error.response?.data?.message || summaryQuery.error.message}
        onRetry={summaryQuery.refetch}
      />
    );

  const s = summaryQuery.data || {};
  const totalQty = s.total_quantity || 0;
  const warehousePct = totalQty > 0 ? Math.round(((s.warehouse_total || 0) / totalQty) * 100) : 0;
  const storePct = totalQty > 0 ? 100 - warehousePct : 0;
  const movements = movementsQuery.data || [];

  const movementColumns = [
    {
      key: "product_name",
      label: t("inventory.overview.movementColumns.product"),
      render: (val) => (
        <span className="text-[13px] font-semibold text-surface-800 dark:text-surface-100">{val}</span>
      ),
    },
    {
      key: "movement_type",
      label: t("inventory.overview.movementColumns.type"),
      render: (val) => (
        <span className="text-[12px] text-surface-500 dark:text-surface-400">{val}</span>
      ),
    },
    {
      key: "quantity",
      label: t("inventory.overview.movementColumns.quantity"),
      render: (val) => (
        <span className="numeric-value text-[13px] font-bold text-surface-800 dark:text-surface-100">
          {val > 0 ? `+${val}` : val}
        </span>
      ),
    },
    {
      key: "warehouse_name",
      label: t("inventory.overview.movementColumns.warehouse"),
      render: (val) => <span className="text-[12px] text-surface-500 dark:text-surface-400">{val || "-"}</span>,
    },
    {
      key: "user_name",
      label: t("inventory.overview.movementColumns.user"),
      render: (val) => <span className="text-[12px] text-surface-500 dark:text-surface-400">{val || "-"}</span>,
    },
  ];

  return (
    <div>
      <PageHeader
        title={t("inventory.overview.title")}
        description={t("inventory.overview.description")}
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
        <StatCard label={t("inventory.overview.kpi.products")} value={s.total_products ?? 0} icon={PackageSearch} color="blue" />
        <StatCard label={t("inventory.overview.kpi.totalQuantity")} value={totalQty} icon={Boxes} color="purple" />
        <StatCard
          label={t("inventory.overview.kpi.stockValue")}
          value={(Number(s.total_value) || 0).toFixed(2)}
          icon={Boxes}
          color="green"
        />
        <StatCard label={t("inventory.overview.kpi.lowStock")} value={s.low_stock_count ?? 0} icon={AlertTriangle} color="red" />
      </div>

      <div className={`${cardClass} p-5 mb-6`}>
        <h2 className="text-[14px] font-bold text-surface-900 dark:text-surface-100 mb-4">
          {t("inventory.overview.distribution.title")}
        </h2>
        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-2">
                <WarehouseIcon className="w-4 h-4 text-primary-600 dark:text-primary-400" />
                <span className="text-[13px] font-medium text-surface-700 dark:text-surface-200">
                  {t("inventory.overview.distribution.warehouse")}
                </span>
              </div>
              <span className="numeric-value text-[13px] font-bold text-surface-800 dark:text-surface-100">
                {s.warehouse_total ?? 0} ({warehousePct}%)
              </span>
            </div>
            <div className="h-2.5 bg-surface-100 dark:bg-surface-700/50 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-primary-500 to-primary-600 rounded-full transition-all duration-500"
                style={{ width: `${warehousePct}%` }}
              />
            </div>
          </div>
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <div className="flex items-center gap-2">
                <Store className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
                <span className="text-[13px] font-medium text-surface-700 dark:text-surface-200">
                  {t("inventory.overview.distribution.store")}
                </span>
              </div>
              <span className="numeric-value text-[13px] font-bold text-surface-800 dark:text-surface-100">
                {s.store_total ?? 0} ({storePct}%)
              </span>
            </div>
            <div className="h-2.5 bg-surface-100 dark:bg-surface-700/50 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-emerald-500 to-emerald-600 rounded-full transition-all duration-500"
                style={{ width: `${storePct}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      <div className={`${cardClass} p-5`}>
        <h2 className="text-[14px] font-bold text-surface-900 dark:text-surface-100 mb-4">
          {t("inventory.overview.recentMovements")}
        </h2>
        {movements.length === 0 ? (
          <EmptyState compact title={t("common.noDataAvailable")} />
        ) : (
          <DataTable columns={movementColumns} data={movements} />
        )}
      </div>
    </div>
  );
}
