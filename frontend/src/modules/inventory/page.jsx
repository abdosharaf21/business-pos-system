import { formatCurrency } from "../../utils/formatCurrency";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import i18n from "../../i18n";
import { inventoryService } from "./api";
import { auditService } from "../inventory_audits/api";
import { useAuth } from "../../shared/context/AuthContext";
import { PageHeader } from "../../shared/components/PageHeader";
import { DataTable } from "../../shared/components/DataTable";
import { Modal } from "../../shared/components/Modal";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
import { Badge, statusBadge } from "../../shared/components/Badge";
import { StatCard } from "../../shared/components/StatCard";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  Package, Search, AlertTriangle, History, PackageOpen,
  ArrowUpDown, Warehouse, Store, ArrowLeftRight, ClipboardCheck,
} from "lucide-react";
import toast from "react-hot-toast";

const transferSchema = z.object({
  quantity: z.coerce
    .number()
    .int(() => i18n.t("inventory.validation.mustBeWhole"))
    .positive(() => i18n.t("inventory.validation.quantityPositive")),
});

const quickAuditSchema = z.object({
  counted_quantity: z
    .string()
    .min(1, () => i18n.t("inventory.validation.quantityRequired"))
    .refine((v) => Number.isInteger(Number(v)), () => i18n.t("inventory.validation.mustBeWhole"))
    .refine((v) => Number(v) >= 0, () => i18n.t("inventory.validation.quantityNonNegative")),
});

const INPUT_CLASS = "w-full px-3.5 py-2.5 border border-surface-200 bg-surface-50 rounded-xl text-sm text-surface-800 placeholder:text-surface-300 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150";
const LABEL_CLASS = "block text-[13px] font-semibold text-surface-700 mb-1.5";

export default function InventoryPage() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const { t } = useTranslation();
  const canManage = ["admin", "manager"].includes(user?.role);
  const [search, setSearch] = useState("");
  const [transferTarget, setTransferTarget] = useState(null);
  const [quickAuditTarget, setQuickAuditTarget] = useState(null);
  const [viewHistory, setViewHistory] = useState(null);
  const [tab, setTab] = useState("all");
  const [expirationFilter, setExpirationFilter] = useState("");
  const [sortBy, setSortBy] = useState("");

  const { data: inventory = [], isLoading, error, refetch } = useQuery({
    queryKey: ["inventory", search, expirationFilter, sortBy],
    queryFn: async () => {
      const res = await inventoryService.getAll(search, expirationFilter, sortBy);
      return res.data.data;
    },
  });

  const { data: summary } = useQuery({
    queryKey: ["inventory-summary"],
    queryFn: async () => {
      const res = await inventoryService.getSummary();
      return res.data.data;
    },
  });

  const { data: movements = [] } = useQuery({
    queryKey: ["inventory-movements", viewHistory],
    queryFn: async () => {
      const res = await inventoryService.getMovements({ product_id: viewHistory });
      return res.data.data;
    },
    enabled: !!viewHistory,
  });

  const invalidateInventory = () => {
    queryClient.invalidateQueries({ queryKey: ["inventory"] });
    queryClient.invalidateQueries({ queryKey: ["inventory-summary"] });
    queryClient.invalidateQueries({ queryKey: ["inventory-movements"] });
    queryClient.invalidateQueries({ queryKey: ["reports-dashboard"] });
    queryClient.invalidateQueries({ queryKey: ["dashboard"] });
  };

  const transferMutation = useMutation({
    mutationFn: (data) => inventoryService.transferStock(data),
    onSuccess: () => {
      invalidateInventory();
      toast.success(t("inventory.toast.transferred"));
      setTransferTarget(null);
    },
    onError: (err) => toast.error(err.response?.data?.message || t("inventory.toast.transferFailed")),
  });

  const quickAuditMutation = useMutation({
    mutationFn: async ({ product, location, counted_quantity, reason }) => {
      const name = `Quick Audit - ${product.name}`;
      const createRes = await auditService.create({ name, location });
      const auditId = createRes.data.data.id;
      await auditService.update(auditId, {
        items: [{ product_id: product.id, counted_quantity, notes: reason || null }],
      });
      const completeRes = await auditService.complete(auditId);
      return completeRes.data.data;
    },
    onSuccess: () => {
      invalidateInventory();
      toast.success(t("inventory.toast.quickAudited"));
      setQuickAuditTarget(null);
    },
    onError: (err) => toast.error(err.response?.data?.message || t("inventory.toast.quickAuditFailed")),
  });

  const lowStock = inventory.filter((p) => p.total <= p.minimum_stock);
  const displayData = tab === "low" ? lowStock : inventory;

  const filtered = displayData.filter(
    (p) =>
      p.name?.toLowerCase().includes(search.toLowerCase()) ||
      (p.barcode || "").toLowerCase().includes(search.toLowerCase())
  );

  const columns = [
    {
      key: "name",
      label: t("inventory.columns.product"),
      render: (val, row) => (
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-[11px] font-bold text-white shrink-0">
            {val?.charAt(0)?.toUpperCase() || "?"}
          </div>
          <div className="min-w-0">
            <p className="text-[13px] font-semibold text-surface-800 truncate">{val}</p>
            <p className="text-[11px] text-surface-400 truncate">{row.barcode || t("inventory.noBarcode")}</p>
          </div>
        </div>
      ),
    },
    {
      key: "category_name",
      label: t("inventory.columns.category"),
      render: (val) => (
        <span className="text-[12px] text-surface-500">{val || "-"}</span>
      ),
    },
    {
      key: "warehouse_qty",
      label: t("inventory.columns.warehouse"),
      render: (val) => (
        <span className="text-[13px] font-semibold text-surface-800 tabular-nums whitespace-nowrap">{val}</span>
      ),
    },
    {
      key: "store_qty",
      label: t("inventory.columns.store"),
      render: (val) => (
        <span className="text-[13px] font-semibold text-surface-800 tabular-nums whitespace-nowrap">{val}</span>
      ),
    },
    {
      key: "total",
      label: t("inventory.columns.total"),
      render: (val, row) => {
        const isLow = val <= row.minimum_stock;
        return (
          <div className="flex items-center gap-2">
            <span className={`text-[13px] font-bold tabular-nums whitespace-nowrap ${isLow ? "text-red-600" : "text-surface-800"}`}>
              {val}
            </span>
            {isLow && (
              <Badge variant="danger">{t("inventory.low")}</Badge>
            )}
          </div>
        );
      },
    },
    {
      key: "minimum_stock",
      label: t("inventory.columns.minStock"),
      render: (val) => <span className="text-[13px] text-surface-500 tabular-nums whitespace-nowrap">{val}</span>,
    },
    {
      key: "expiration_date",
      label: t("inventory.columns.expiration"),
      render: (val, row) => {
        const locale = i18n.language === "ar" ? "ar-EG" : "en-US";
        return (
          <div className="flex items-center gap-2">
            <span className="text-[13px] text-surface-600 whitespace-nowrap">
              {val ? new Date(val + "T00:00:00").toLocaleDateString(locale, { year: "numeric", month: "short", day: "numeric" }) : "—"}
            </span>
            {row.expiration_status && (
              <Badge variant={statusBadge(row.expiration_status)}>
                {t(`inventory.expiration.statuses.${row.expiration_status}`)}
              </Badge>
            )}
          </div>
        );
      },
    },
    {
      key: "status",
      label: t("inventory.columns.status"),
      render: (val) => <Badge variant={statusBadge(val)}>{val}</Badge>,
    },
    ...(canManage
      ? [
          {
            key: "id",
            label: t("inventory.columns.actions"),
            render: (_, row) => (
              <div className="flex items-center gap-1">
                <button
                  onClick={() => setTransferTarget(row)}
                  disabled={row.warehouse_qty < 1}
                  className="p-2 text-surface-400 hover:text-primary-600 hover:bg-primary-50 rounded-xl transition-all duration-150 disabled:opacity-40 disabled:hover:bg-transparent disabled:hover:text-surface-400"
                  title={t("inventory.transfer.title")}
                >
                  <ArrowLeftRight className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setQuickAuditTarget(row)}
                  className="p-2 text-surface-400 hover:text-primary-600 hover:bg-primary-50 rounded-xl transition-all duration-150"
                  title={t("inventory.quickAudit.button")}
                >
                  <ClipboardCheck className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewHistory(row.id)}
                  className="p-2 text-surface-400 hover:text-amber-600 hover:bg-amber-50 rounded-xl transition-all duration-150"
                  title={t("inventory.history.title", { name: "" }).trim()}
                >
                  <History className="w-4 h-4" />
                </button>
              </div>
            ),
          },
        ]
      : [
          {
            key: "id",
            label: t("inventory.columns.history"),
            render: (_, row) => (
              <button
                onClick={() => setViewHistory(row.id)}
                className="p-2 text-surface-400 hover:text-amber-600 hover:bg-amber-50 rounded-xl transition-all duration-150"
                title={t("inventory.history.title", { name: "" }).trim()}
              >
                <History className="w-4 h-4" />
              </button>
            ),
          },
        ]),
  ];

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay message={error.response?.data?.message || error.message} onRetry={refetch} />;

  return (
    <div>
      <PageHeader
        title={t("inventory.title")}
        description={t("inventory.subtitle")}
      />

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <StatCard label={t("inventory.totalProducts")} value={summary?.total_products ?? 0} icon={Package} color="blue" />
        <StatCard label={t("inventory.warehouseStock")} value={summary?.warehouse_total ?? 0} icon={Warehouse} color="green" />
        <StatCard label={t("inventory.storeStock")} value={summary?.store_total ?? 0} icon={Store} color="purple" />
        <StatCard label={t("inventory.lowStockItems")} value={summary?.low_stock_count ?? 0} icon={AlertTriangle} color="orange" />
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <StatCard label={t("inventory.totalStock")} value={summary?.total_quantity ?? 0} icon={PackageOpen} color="green" />
        <StatCard
          label={t("inventory.totalValue")}
          value={formatCurrency(summary?.total_value)}
          icon={ArrowUpDown}
          color="purple"
        />
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 p-1 bg-surface-100 rounded-xl w-fit">
        <button
          onClick={() => { setTab("all"); setSearch(""); }}
          className={`px-4 py-2 text-[13px] font-semibold rounded-xl transition-all duration-150 ${
            tab === "all" ? "bg-white text-surface-800 shadow-sm" : "text-surface-500 hover:text-surface-700"
          }`}
        >
          {t("inventory.allProducts")}
        </button>
        <button
          onClick={() => { setTab("low"); setSearch(""); }}
          className={`px-4 py-2 text-[13px] font-semibold rounded-xl transition-all duration-150 flex items-center gap-2 ${
            tab === "low" ? "bg-white text-surface-800 shadow-sm" : "text-surface-500 hover:text-surface-700"
          }`}
        >
          <AlertTriangle className="w-3.5 h-3.5" />
          {t("inventory.lowStock")}
          {summary?.low_stock_count > 0 && (
            <span className="inline-flex items-center justify-center w-5 h-5 text-[10px] font-bold text-white bg-red-500 rounded-full">
              {summary.low_stock_count}
            </span>
          )}
        </button>
      </div>

      {/* Search */}
      <div className="mb-6 relative">
        <Search className="w-4 h-4 absolute start-3.5 top-1/2 -translate-y-1/2 text-surface-400 pointer-events-none" />
        <input
          type="text"
          placeholder={t("inventory.searchPlaceholder")}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full ps-10 pe-4 py-2.5 border border-surface-200 bg-white rounded-xl text-sm text-surface-800 placeholder:text-surface-300 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150 shadow-card"
          aria-label={t("inventory.searchAriaLabel")}
        />
      </div>

      {/* Expiration filters */}
      <div className="flex flex-wrap items-center gap-3 mb-6">
        <div>
          <label className="block text-[11px] font-semibold text-surface-500 uppercase tracking-wider mb-1">
            {t("inventory.expiration.filterLabel")}
          </label>
          <select
            value={expirationFilter}
            onChange={(e) => setExpirationFilter(e.target.value)}
            className="px-3 py-2 border border-surface-200 bg-white rounded-xl text-[13px] text-surface-700 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150 appearance-none cursor-pointer"
          >
            <option value="">{t("inventory.expiration.all")}</option>
            <option value="expired">{t("inventory.expiration.statuses.expired")}</option>
            <option value="expiring_soon">{t("inventory.expiration.statuses.expiring_soon")}</option>
            <option value="normal">{t("inventory.expiration.statuses.normal")}</option>
          </select>
        </div>
        <div className="flex flex-col gap-1">
          <span className="text-[11px] font-semibold text-surface-500 uppercase tracking-wider">&nbsp;</span>
          <button
            onClick={() => setSortBy(sortBy === "expiration" ? "" : "expiration")}
            className={`inline-flex items-center gap-2 px-3 py-2 rounded-xl border text-[13px] font-semibold transition-all duration-150 ${
              sortBy === "expiration"
                ? "border-primary-200 bg-primary-50 text-primary-700"
                : "border-surface-200 bg-white text-surface-600 hover:bg-surface-50"
            }`}
          >
            <ArrowUpDown className="w-3.5 h-3.5" />
            {t("inventory.expiration.sortByExpiration")}
          </button>
        </div>
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          icon={Package}
          title={t("inventory.noProductsFound")}
          description={search ? t("inventory.tryDifferentSearch") : t("inventory.noProductsInInventory")}
        />
      ) : (
        <DataTable columns={columns} data={filtered} />
      )}

      {/* Transfer Modal */}
      <TransferModal
        isOpen={!!transferTarget}
        onClose={() => setTransferTarget(null)}
        product={transferTarget}
        onSubmit={(data) =>
          transferMutation.mutate({
            product_id: transferTarget.id,
            ...data,
          })
        }
        loading={transferMutation.isPending}
      />

      {/* Quick Audit Modal */}
      <QuickAuditModal
        isOpen={!!quickAuditTarget}
        onClose={() => setQuickAuditTarget(null)}
        product={quickAuditTarget}
        onSubmit={(data) =>
          quickAuditMutation.mutate({
            product: quickAuditTarget,
            ...data,
          })
        }
        loading={quickAuditMutation.isPending}
      />

      {/* Movement History Modal */}
      <MovementHistoryModal
        isOpen={!!viewHistory}
        onClose={() => setViewHistory(null)}
        movements={movements}
        product={inventory.find((p) => p.id === viewHistory)}
      />
    </div>
  );
}

function TransferModal({ isOpen, onClose, product, onSubmit, loading }) {
  const { t } = useTranslation();
  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(transferSchema),
    defaultValues: { quantity: 0 },
  });

  const quantity = Number(watch("quantity", 0)) || 0;
  const remaining = product ? Number(product.warehouse_qty) - quantity : 0;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={t("inventory.transfer.title", { name: product?.name || "" })}>
      <form
        onSubmit={handleSubmit((data) => {
          onSubmit(data);
          reset();
        })}
        className="space-y-5"
      >
        <div className="bg-surface-50 rounded-xl p-4 space-y-2">
          <div className="flex justify-between text-[13px]">
            <span className="text-surface-500">{t("inventory.transfer.from")}</span>
            <span className="font-bold text-surface-800">{t("inventory.warehouse")}</span>
          </div>
          <div className="flex justify-between text-[13px]">
            <span className="text-surface-500">{t("inventory.transfer.to")}</span>
            <span className="font-bold text-surface-800">{t("inventory.store")}</span>
          </div>
          <div className="flex justify-between text-[13px] pt-2 border-t border-surface-200">
            <span className="text-surface-500">{t("inventory.transfer.currentWarehouse")}</span>
            <span className="font-bold text-surface-800">{product?.warehouse_qty ?? 0}</span>
          </div>
          <div className="flex justify-between text-[13px]">
            <span className="text-surface-500">{t("inventory.transfer.afterTransfer")}</span>
            <span className={`font-bold ${remaining < 0 ? "text-red-600" : "text-surface-800"}`}>
              {remaining}
            </span>
          </div>
        </div>

        <div>
          <label className={LABEL_CLASS}>{t("inventory.transfer.quantity")}</label>
          <input
            type="number"
            min="1"
            {...register("quantity")}
            className={`${INPUT_CLASS} numeric-grow min-w-14`}
            placeholder={t("inventory.transfer.quantityPlaceholder")}
          />
          {errors.quantity && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.quantity.message}</p>}
        </div>

        <div className="flex justify-end gap-3 pt-5 border-t border-surface-100">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2.5 text-[13px] font-semibold text-surface-600 bg-white border border-surface-200 rounded-xl hover:bg-surface-50 transition-all duration-150"
          >
            {t("common.cancel")}
          </button>
          <button
            type="submit"
            disabled={loading || remaining < 0}
            className="px-4 py-2.5 text-[13px] font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl hover:from-primary-700 hover:to-primary-800 disabled:opacity-50 transition-all duration-150 shadow-sm shadow-primary-600/20"
          >
            {loading ? t("inventory.transfer.transferring") : t("inventory.transfer.transfer")}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function QuickAuditModal({ isOpen, onClose, product, onSubmit, loading }) {
  const { t } = useTranslation();
  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(quickAuditSchema),
    defaultValues: { location: "store", counted_quantity: "", reason: "" },
  });

  const location = watch("location", "store");
  const currentQty = product
    ? (location === "warehouse" ? Number(product.warehouse_qty) : Number(product.store_qty))
    : 0;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={t("inventory.quickAudit.title", { name: product?.name || "" })}>
      <form
        onSubmit={handleSubmit((data) => {
          onSubmit({ ...data, counted_quantity: Number(data.counted_quantity) });
          reset();
        })}
        className="space-y-5"
      >
        <div className="bg-surface-50 rounded-xl p-4 flex justify-between text-[13px]">
          <span className="text-surface-500">{t("inventory.quickAudit.location")}</span>
          <select {...register("location")} className="px-2 py-1 border border-surface-200 bg-white rounded-lg text-[13px] text-surface-700 focus:outline-none focus:ring-2 focus:ring-primary-500/20 cursor-pointer">
            <option value="store">{t("inventory.store")}</option>
            <option value="warehouse">{t("inventory.warehouse")}</option>
          </select>
        </div>

        <div className="bg-surface-50 rounded-xl p-4 flex justify-between text-[13px]">
          <span className="text-surface-500">{t("inventory.quickAudit.currentQuantity")}</span>
          <span className="font-bold text-surface-800 tabular-nums">{currentQty}</span>
        </div>

        <div>
          <label className={LABEL_CLASS}>{t("inventory.quickAudit.countedQuantity")}</label>
          <input
            type="number"
            min="0"
            step="1"
            {...register("counted_quantity")}
            className={`${INPUT_CLASS} numeric-grow min-w-14`}
            placeholder="0"
          />
          {errors.counted_quantity && (
            <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.counted_quantity.message}</p>
          )}
        </div>

        <div>
          <label className={LABEL_CLASS}>{t("inventory.quickAudit.reason")}</label>
          <input
            type="text"
            maxLength={255}
            {...register("reason")}
            className={INPUT_CLASS}
            placeholder={t("inventory.quickAudit.reasonPlaceholder")}
          />
        </div>

        <p className="text-[11px] text-surface-400 -mt-2">{t("inventory.quickAudit.hint")}</p>

        <div className="flex justify-end gap-3 pt-5 border-t border-surface-100">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2.5 text-[13px] font-semibold text-surface-600 bg-white border border-surface-200 rounded-xl hover:bg-surface-50 transition-all duration-150"
          >
            {t("inventory.quickAudit.cancel")}
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2.5 text-[13px] font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl hover:from-primary-700 hover:to-primary-800 disabled:opacity-50 transition-all duration-150 shadow-sm shadow-primary-600/20"
          >
            {loading ? t("inventory.quickAudit.applying") : t("inventory.quickAudit.apply")}
          </button>
        </div>
      </form>
    </Modal>
  );
}

const TYPE_ICONS = {
  transfer: ArrowLeftRight,
  sale: Package,
  purchase: Package,
  return: PackageOpen,
  damage: AlertTriangle,
  adjustment: ClipboardCheck,
};

function MovementHistoryModal({ isOpen, onClose, movements, product }) {
  const { t } = useTranslation();

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={t("inventory.history.title", { name: product?.name || "" })}>
      <div className="space-y-4">
        {movements.length === 0 ? (
          <p className="text-center text-surface-400 py-8 text-[13px]">{t("inventory.history.noTransactions")}</p>
        ) : (
          <div className="divide-y divide-surface-100 max-h-96 overflow-y-auto">
            {movements.map((m) => {
              const Icon = TYPE_ICONS[m.movement_type] || Package;
              return (
                <div key={m.id} className="flex items-center justify-between py-3">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-surface-100 flex items-center justify-center text-[11px] font-bold text-surface-500 shrink-0">
                      <Icon className="w-4 h-4" />
                    </div>
                    <div>
                      <p className="text-[13px] font-semibold text-surface-800 capitalize">
                        {t(`inventory.history.${m.movement_type}`)}
                      </p>
                      <p className="text-[11px] text-surface-400">
                        {m.from_location ? t(`inventory.history.${m.from_location}`) : "—"}
                        {" → "}
                        {m.to_location ? t(`inventory.history.${m.to_location}`) : "—"}
                        {" · "}
                        {new Date(m.created_at).toLocaleString()}
                      </p>
                      {m.notes && (
                        <p className="text-[11px] text-surface-400 mt-0.5">
                          {t("inventory.history.source")}: {m.notes}
                        </p>
                      )}
                    </div>
                  </div>
                  <span className="text-[13px] font-bold text-surface-800 tabular-nums whitespace-nowrap">
                    {m.quantity} {t("inventory.history.units")}
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </Modal>
  );
}
