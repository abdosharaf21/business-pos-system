import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { useState } from "react";
import { ClipboardList } from "lucide-react";
import { reportService } from "../reports/api";
import { PageHeader } from "../../shared/components/PageHeader";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { DataTable } from "../../shared/components/DataTable";
import { EmptyState } from "../../shared/components/EmptyState";
import { cardClass, ghostButtonClass } from "../../shared/components/styles";

const TABS = ["inventory", "mostTransferred", "lowestStock"];

export default function InventoryReportsPage() {
  const { t } = useTranslation();
  const [tab, setTab] = useState("inventory");

  const reportQuery = useQuery({
    queryKey: ["report-inventory-report"],
    queryFn: async () => (await reportService.getInventoryReport()).data.data,
  });

  const transferredQuery = useQuery({
    queryKey: ["report-most-transferred"],
    queryFn: async () => (await reportService.getMostTransferred()).data.data,
  });

  const lowestQuery = useQuery({
    queryKey: ["report-lowest-stock"],
    queryFn: async () => (await reportService.getLowestStock()).data.data,
  });

  if (reportQuery.isLoading || transferredQuery.isLoading || lowestQuery.isLoading)
    return <LoadingSpinner />;

  const queriesByTab = {
    inventory: reportQuery,
    mostTransferred: transferredQuery,
    lowestStock: lowestQuery,
  };
  const activeError = queriesByTab[tab].error;
  if (!activeError && (reportQuery.error || transferredQuery.error || lowestQuery.error)) {
    const failed = [reportQuery, transferredQuery, lowestQuery].find((q) => q.error);
    return (
      <ErrorDisplay
        message={failed.error.response?.data?.message || failed.error.message}
        onRetry={failed.refetch}
      />
    );
  }
  if (activeError)
    return (
      <ErrorDisplay
        message={activeError.response?.data?.message || activeError.message}
        onRetry={queriesByTab[tab].refetch}
      />
    );

  const inventoryReport = reportQuery.data || {};
  const mostTransferred = transferredQuery.data || [];
  const lowestStock = lowestQuery.data || [];

  const inventoryColumns = [
    {
      key: "category_name",
      label: t("inventory.reports.inventoryColumns.category"),
      render: (val) => (
        <span className="text-[13px] font-semibold text-surface-800 dark:text-surface-100">{val || "-"}</span>
      ),
    },
    {
      key: "products_count",
      label: t("inventory.reports.inventoryColumns.products"),
      render: (val) => (
        <span className="numeric-value text-[13px] text-surface-600 dark:text-surface-300">{val ?? 0}</span>
      ),
    },
    {
      key: "total_quantity",
      label: t("inventory.reports.inventoryColumns.quantity"),
      render: (val) => (
        <span className="numeric-value text-[13px] font-semibold text-surface-800 dark:text-surface-100">{val ?? 0}</span>
      ),
    },
    {
      key: "total_value",
      label: t("inventory.reports.inventoryColumns.value"),
      render: (val) => (
        <span className="numeric-value text-[13px] font-bold text-emerald-600 dark:text-emerald-400">
          {Number(val || 0).toFixed(2)}
        </span>
      ),
    },
  ];

  const transferredColumns = [
    {
      key: "product_name",
      label: t("inventory.reports.transferredColumns.product"),
      render: (val) => (
        <span className="text-[13px] font-semibold text-surface-800 dark:text-surface-100">{val}</span>
      ),
    },
    {
      key: "transfer_count",
      label: t("inventory.reports.transferredColumns.transfers"),
      render: (val) => (
        <span className="numeric-value text-[13px] font-bold text-primary-600 dark:text-primary-400">{val ?? 0}</span>
      ),
    },
    {
      key: "total_quantity",
      label: t("inventory.reports.transferredColumns.quantity"),
      render: (val) => (
        <span className="numeric-value text-[13px] text-surface-600 dark:text-surface-300">{val ?? 0}</span>
      ),
    },
  ];

  const lowestColumns = [
    {
      key: "name",
      label: t("inventory.reports.lowestColumns.product"),
      render: (val) => (
        <span className="text-[13px] font-semibold text-surface-800 dark:text-surface-100">{val}</span>
      ),
    },
    {
      key: "total",
      label: t("inventory.reports.lowestColumns.stock"),
      render: (val) => (
        <span className="numeric-value text-[13px] font-bold text-red-600 dark:text-red-400">{val ?? 0}</span>
      ),
    },
    {
      key: "minimum_stock",
      label: t("inventory.reports.lowestColumns.minimum"),
      render: (val) => (
        <span className="numeric-value text-[13px] text-surface-600 dark:text-surface-300">{val ?? 0}</span>
      ),
    },
  ];

  const tabLabels = {
    inventory: t("inventory.reports.tabs.inventory"),
    mostTransferred: t("inventory.reports.tabs.mostTransferred"),
    lowestStock: t("inventory.reports.tabs.lowestStock"),
  };

  return (
    <div>
      <PageHeader
        title={t("inventory.reports.title")}
        description={t("inventory.reports.description")}
      />

      <div className="flex items-center gap-2 mb-6">
        {TABS.map((key) => (
          <button
            key={key}
            type="button"
            onClick={() => setTab(key)}
            className={`${ghostButtonClass} ${
              tab === key
                ? "!bg-primary-50 !text-primary-700 dark:!bg-primary-500/10 dark:!text-primary-400"
                : ""
            }`}
          >
            {tabLabels[key]}
          </button>
        ))}
      </div>

      <div className={`${cardClass} p-5`}>
        <h2 className="text-[14px] font-bold text-surface-900 dark:text-surface-100 mb-4">
          {tabLabels[tab]}
        </h2>
        {tab === "inventory" && (
          <DataTable
            columns={inventoryColumns}
            data={
              Array.isArray(inventoryReport)
                ? inventoryReport
                : inventoryReport.by_category || inventoryReport.categories || []
            }
          />
        )}
        {tab === "mostTransferred" &&
          (mostTransferred.length === 0 ? (
            <EmptyState compact icon={ClipboardList} title={t("common.noDataAvailable")} />
          ) : (
            <DataTable columns={transferredColumns} data={mostTransferred} />
          ))}
        {tab === "lowestStock" &&
          (lowestStock.length === 0 ? (
            <EmptyState compact icon={ClipboardList} title={t("common.noDataAvailable")} />
          ) : (
            <DataTable columns={lowestColumns} data={lowestStock} />
          ))}
      </div>
    </div>
  );
}
