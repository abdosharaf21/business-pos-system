import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { inventoryService } from "./api";
import { PageHeader } from "../../shared/components/PageHeader";
import { DataTable } from "../../shared/components/DataTable";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
import { Badge } from "../../shared/components/Badge";
import { Search, History, Filter } from "lucide-react";

const TYPE_COLORS = {
  transfer: "info",
  sale: "danger",
  purchase: "success",
  return: "info",
  damage: "warning",
  adjustment: "warning",
};

const TYPE_ORDER = ["transfer", "sale", "purchase", "return", "damage", "adjustment"];

export default function InventoryHistoryPage() {
  const { t } = useTranslation();
  const [productId, setProductId] = useState("");
  const [movementType, setMovementType] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [search, setSearch] = useState("");

  const { data: products = [], isLoading: productsLoading } = useQuery({
    queryKey: ["inventory-products"],
    queryFn: async () => {
      const res = await inventoryService.getAll("");
      return res.data.data;
    },
  });

  const params = {};
  if (productId) params.product_id = productId;
  if (movementType) params.movement_type = movementType;
  if (startDate) params.start_date = startDate;
  if (endDate) params.end_date = endDate;

  const { data: movements = [], isLoading, error, refetch } = useQuery({
    queryKey: ["inventory-movements-page", productId, movementType, startDate, endDate],
    queryFn: async () => {
      const res = await inventoryService.getMovements(params);
      return res.data.data;
    },
    keepPreviousData: true,
  });

  const filtered = movements.filter((m) =>
    !search ||
    m.product_name?.toLowerCase().includes(search.toLowerCase()) ||
    (m.reference || "").toLowerCase().includes(search.toLowerCase())
  );

  const clearFilters = () => {
    setProductId("");
    setMovementType("");
    setStartDate("");
    setEndDate("");
    setSearch("");
  };

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay message={error.response?.data?.message || error.message} onRetry={refetch} />;

  const columns = [
    {
      key: "product_name",
      label: t("inventory.historyPage.columns.product"),
      render: (val) => (
        <span className="text-[13px] font-semibold text-surface-800">{val}</span>
      ),
    },
    {
      key: "movement_type",
      label: t("inventory.historyPage.columns.type"),
      render: (val) => (
        <Badge variant={TYPE_COLORS[val] || "info"}>
          {t(`inventory.history.${val}`)}
        </Badge>
      ),
    },
    {
      key: "from_location",
      label: t("inventory.historyPage.columns.from"),
      render: (val) => (
        <span className="text-[12px] text-surface-500 capitalize">
          {val ? t(`inventory.history.${val}`) : "—"}
        </span>
      ),
    },
    {
      key: "to_location",
      label: t("inventory.historyPage.columns.to"),
      render: (val) => (
        <span className="text-[12px] text-surface-500 capitalize">
          {val ? t(`inventory.history.${val}`) : "—"}
        </span>
      ),
    },
    {
      key: "quantity",
      label: t("inventory.historyPage.columns.qty"),
      render: (val) => (
        <span className="text-[13px] font-bold text-surface-800">{val}</span>
      ),
    },
    {
      key: "reference",
      label: t("inventory.historyPage.columns.reference"),
      render: (val) => (
        <span className="text-[12px] text-surface-500">{val || "—"}</span>
      ),
    },
    {
      key: "created_at",
      label: t("inventory.historyPage.columns.date"),
      render: (val) => (
        <span className="text-[12px] text-surface-500">
          {val ? new Date(val).toLocaleString() : "—"}
        </span>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title={t("inventory.historyPage.title")}
        description={t("inventory.historyPage.subtitle")}
      />

      {/* Filters */}
      <div className="mb-6 p-4 bg-white rounded-2xl border border-surface-200/80 shadow-card space-y-4">
        <div className="flex items-center gap-2">
          <Filter className="w-5 h-5 text-surface-400 shrink-0" />
          <h2 className="text-[13px] font-semibold text-surface-700">
            {t("inventory.historyPage.filters")}
          </h2>
          <button
            onClick={clearFilters}
            className="ms-auto text-[12px] font-semibold text-primary-600 hover:text-primary-700"
          >
            {t("inventory.historyPage.clear")}
          </button>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-[12px] font-semibold text-surface-600 mb-1.5">
              {t("inventory.historyPage.filtersProduct")}
            </label>
            <select
              value={productId}
              onChange={(e) => setProductId(e.target.value)}
              disabled={productsLoading}
              className="w-full px-3.5 py-2.5 border border-surface-200 bg-surface-50 rounded-xl text-sm text-surface-800 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150"
            >
              <option value="">{t("inventory.historyPage.allProducts")}</option>
              {products.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-[12px] font-semibold text-surface-600 mb-1.5">
              {t("inventory.historyPage.filtersType")}
            </label>
            <select
              value={movementType}
              onChange={(e) => setMovementType(e.target.value)}
              className="w-full px-3.5 py-2.5 border border-surface-200 bg-surface-50 rounded-xl text-sm text-surface-800 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150"
            >
              <option value="">{t("inventory.historyPage.allTypes")}</option>
              {TYPE_ORDER.map((type) => (
                <option key={type} value={type}>
                  {t(`inventory.history.${type}`)}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-[12px] font-semibold text-surface-600 mb-1.5">
              {t("inventory.historyPage.fromDate")}
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-3.5 py-2.5 border border-surface-200 bg-surface-50 rounded-xl text-sm text-surface-800 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150"
            />
          </div>
          <div>
            <label className="block text-[12px] font-semibold text-surface-600 mb-1.5">
              {t("inventory.historyPage.toDate")}
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full px-3.5 py-2.5 border border-surface-200 bg-surface-50 rounded-xl text-sm text-surface-800 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150"
            />
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="mb-6 relative">
        <Search className="w-4 h-4 absolute start-3.5 top-1/2 -translate-y-1/2 text-surface-400 pointer-events-none" />
        <input
          type="text"
          placeholder={t("inventory.historyPage.searchPlaceholder")}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full ps-10 pe-4 py-2.5 border border-surface-200 bg-white rounded-xl text-sm text-surface-800 placeholder:text-surface-300 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150 shadow-card"
        />
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          icon={History}
          title={t("inventory.historyPage.noMovements")}
          description={t("inventory.historyPage.noMovementsHint")}
        />
      ) : (
        <DataTable columns={columns} data={filtered} emptyMessage={t("inventory.historyPage.noMovements")} />
      )}
    </div>
  );
}
