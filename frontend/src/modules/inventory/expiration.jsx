import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { CalendarClock, Search } from "lucide-react";
import { inventoryService } from "./api";
import { getCurrentLocale } from "../../shared/utils/format";
import { PageHeader } from "../../shared/components/PageHeader";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { DataTable } from "../../shared/components/DataTable";
import { EmptyState } from "../../shared/components/EmptyState";
import { Badge, statusBadge } from "../../shared/components/Badge";
import {
  searchInputClass,
  selectClass,
  secondaryButtonClass,
} from "../../shared/components/styles";

const EXPIRATION_STATUSES = ["normal", "expiring_soon", "expired"];

export default function InventoryExpirationPage() {
  const { t, i18n } = useTranslation();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  const { data: items = [], isLoading, error, refetch } = useQuery({
    queryKey: ["inventory-expiration", statusFilter],
    queryFn: async () =>
      (await inventoryService.getAll("", statusFilter || "", "")).data.data,
  });

  const withExpiration = items.filter((p) => p.expiration_status);
  const filtered = withExpiration.filter(
    (p) =>
      p.name?.toLowerCase().includes(search.toLowerCase()) ||
      (p.barcode || "").toLowerCase().includes(search.toLowerCase())
  );

  const columns = [
    {
      key: "name",
      label: t("inventory.expirationPage.columns.product"),
      render: (val, row) => (
        <div className="flex flex-col">
          <span className="text-[13px] font-semibold text-surface-800 dark:text-surface-100">{val}</span>
          <span className="text-[11px] text-surface-400 dark:text-surface-500">{row.barcode || "-"}</span>
        </div>
      ),
    },
    {
      key: "total",
      label: t("inventory.expirationPage.columns.stock"),
      render: (val) => (
        <span className="numeric-value text-[13px] font-semibold text-surface-800 dark:text-surface-100">{val}</span>
      ),
    },
    {
      key: "expiration_date",
      label: t("inventory.expirationPage.columns.expirationDate"),
      render: (val) => (
        <span className="numeric-value text-[13px] text-surface-600 dark:text-surface-300">
          {val
            ? new Date(val + "T00:00:00").toLocaleDateString(getCurrentLocale(i18n.language), {
                year: "numeric",
                month: "short",
                day: "numeric",
              })
            : "-"}
        </span>
      ),
    },
    {
      key: "expiration_status",
      label: t("inventory.expirationPage.columns.status"),
      render: (val) => (
        <Badge variant={statusBadge(val)}>{t(`inventory.expiration.statuses.${val}`)}</Badge>
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
        title={t("inventory.expirationPage.title")}
        description={t("inventory.expirationPage.description")}
      />

      <div className="mb-6 flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute start-3.5 top-1/2 -translate-y-1/2 text-surface-400 dark:text-surface-500 pointer-events-none" />
          <input
            type="text"
            placeholder={t("inventory.expirationPage.searchPlaceholder")}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className={searchInputClass}
            aria-label={t("inventory.expirationPage.searchPlaceholder")}
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className={`${selectClass} sm:w-48`}
          aria-label={t("inventory.expiration.filterLabel")}
        >
          <option value="">{t("inventory.expiration.all")}</option>
          {EXPIRATION_STATUSES.map((status) => (
            <option key={status} value={status}>
              {t(`inventory.expiration.statuses.${status}`)}
            </option>
          ))}
        </select>
        {(search || statusFilter) && (
          <button
            type="button"
            onClick={() => {
              setSearch("");
              setStatusFilter("");
            }}
            className={secondaryButtonClass}
          >
            {t("common.actions.clearFilters")}
          </button>
        )}
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          icon={CalendarClock}
          title={t("inventory.expirationPage.empty.title")}
          description={
            search || statusFilter
              ? t("inventory.expirationPage.empty.noResults")
              : t("inventory.expirationPage.empty.noTracked")
          }
        />
      ) : (
        <DataTable columns={columns} data={filtered} />
      )}
    </div>
  );
}
