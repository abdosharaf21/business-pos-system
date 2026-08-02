import { useState, useMemo, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import toast from "react-hot-toast";
import { auditService, AUDIT_LOCATIONS, AUDIT_STATUSES } from "./api";
import { reportService } from "../reports/api";
import { useAuth } from "../../shared/context/AuthContext";
import { PageHeader } from "../../shared/components/PageHeader";
import { StatCard } from "../../shared/components/StatCard";
import { Badge, statusBadge } from "../../shared/components/Badge";
import { Modal } from "../../shared/components/Modal";
import { ConfirmDialog } from "../../shared/components/ConfirmDialog";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
import {
  Plus, Pencil, Trash2, Eye, Search, ClipboardList, ClipboardCheck,
  PackageCheck, CheckCircle2, ArrowUp, ArrowDown,
  ChevronLeft, ChevronRight, Filter, X, Ban, Save,
} from "lucide-react";

const INPUT_CLASS = "w-full px-3.5 py-2.5 border border-surface-200 bg-surface-50 rounded-xl text-sm text-surface-800 placeholder:text-surface-300 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150";
const LABEL_CLASS = "block text-[13px] font-semibold text-surface-700 mb-1.5";
const SELECT_CLASS = "w-full px-3.5 py-2.5 border border-surface-200 bg-surface-50 rounded-xl text-sm text-surface-800 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150 appearance-none cursor-pointer";

const SORT_COLUMNS = [
  { key: "name", labelKey: "inventoryAudits.columns.name" },
  { key: "location", labelKey: "inventoryAudits.columns.location" },
  { key: "status", labelKey: "inventoryAudits.columns.status" },
  { key: "total_items", labelKey: "inventoryAudits.columns.items" },
  { key: "counted_items", labelKey: "inventoryAudits.columns.counted" },
  { key: "started_at", labelKey: "inventoryAudits.columns.startedAt" },
  { key: "created_at", labelKey: "inventoryAudits.columns.createdAt" },
];

export default function InventoryAuditsPage() {
  const { t, i18n } = useTranslation();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const canManage = ["admin", "manager"].includes(user?.role);
  const locale = i18n.language === "ar" ? "ar-EG" : "en-US";

  const [search, setSearch] = useState("");
  const [location, setLocation] = useState("");
  const [status, setStatus] = useState("");
  const [sort, setSort] = useState("created_at");
  const [order, setOrder] = useState("desc");
  const [page, setPage] = useState(1);
  const perPage = 10;

  const [createOpen, setCreateOpen] = useState(false);
  const [counting, setCounting] = useState(null);
  const [details, setDetails] = useState(null);
  const [completeTarget, setCompleteTarget] = useState(null);
  const [cancelTarget, setCancelTarget] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const { data: metrics, isLoading: metricsLoading, error: metricsError, refetch: refetchMetrics } = useQuery({
    queryKey: ["inventory-audits-metrics"],
    queryFn: async () => {
      const res = await reportService.getInventoryAuditReport();
      return res.data.data.metrics;
    },
  });

  const { data: listData, isLoading, error, refetch } = useQuery({
    queryKey: ["inventory-audits", search, location, status, sort, order, page],
    queryFn: async () => {
      const res = await auditService.getAll({
        search: search || undefined,
        location: location || undefined,
        status: status || undefined,
        sort,
        order,
        page,
        per_page: perPage,
      });
      return res.data.data;
    },
    keepPreviousData: true,
  });

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["inventory-audits"] });
    queryClient.invalidateQueries({ queryKey: ["inventory-audits-metrics"] });
    queryClient.invalidateQueries({ queryKey: ["dashboard"] });
  };

  const createMutation = useMutation({
    mutationFn: (data) => auditService.create(data),
    onSuccess: () => { invalidate(); toast.success(t("inventoryAudits.toast.created")); setCreateOpen(false); },
    onError: (err) => toast.error(err.response?.data?.message || t("inventoryAudits.toast.createFailed")),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => auditService.update(id, data),
    onSuccess: () => { invalidate(); toast.success(t("inventoryAudits.toast.updated")); },
    onError: (err) => toast.error(err.response?.data?.message || t("inventoryAudits.toast.updateFailed")),
  });

  const completeMutation = useMutation({
    mutationFn: (id) => auditService.complete(id),
    onSuccess: () => {
      invalidate();
      toast.success(t("inventoryAudits.toast.completed"));
      setCompleteTarget(null);
    },
    onError: (err) => toast.error(err.response?.data?.message || t("inventoryAudits.toast.completeFailed")),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => auditService.delete(id),
    onSuccess: () => { invalidate(); toast.success(t("inventoryAudits.toast.deleted")); setDeleteTarget(null); },
    onError: (err) => toast.error(err.response?.data?.message || t("inventoryAudits.toast.deleteFailed")),
  });

  const clearFilters = () => {
    setSearch("");
    setLocation("");
    setStatus("");
    setPage(1);
  };

  const toggleSort = (key) => {
    if (sort === key) {
      setOrder((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSort(key);
      setOrder("asc");
    }
    setPage(1);
  };

  const hasFilters = search || location || status;

  const items = listData?.items || [];
  const total = listData?.total || 0;
  const pages = listData?.pages || 0;

  if (isLoading || metricsLoading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay message={error.response?.data?.message || error.message} onRetry={refetch} />;
  if (metricsError) return <ErrorDisplay message={metricsError.response?.data?.message || metricsError.message} onRetry={refetchMetrics} />;

  return (
    <div>
      <PageHeader
        title={t("inventoryAudits.title")}
        description={t("inventoryAudits.subtitle")}
        actions={
          canManage && (
            <button onClick={() => setCreateOpen(true)} className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white text-[13px] font-semibold rounded-xl hover:from-primary-700 hover:to-primary-800 transition-all duration-150 shadow-sm shadow-primary-600/20">
              <Plus className="w-4 h-4" />
              {t("inventoryAudits.newAudit")}
            </button>
          )
        }
      />

      {/* Summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <StatCard label={t("inventoryAudits.totalAudits")} value={metrics?.total_audits ?? 0} icon={ClipboardList} color="blue" />
        <StatCard label={t("inventoryAudits.openAudits")} value={metrics?.open_audits ?? 0} icon={ClipboardCheck} color="orange" />
        <StatCard label={t("inventoryAudits.completedAudits")} value={metrics?.completed_audits ?? 0} icon={PackageCheck} color="green" />
        <StatCard label={t("inventoryAudits.adjustedItems")} value={metrics?.adjusted_items ?? 0} icon={CheckCircle2} color="purple" />
      </div>

      {/* Filters */}
      <div className="p-4 bg-white rounded-2xl border border-surface-200/80 shadow-card mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 items-end">
          <div className="relative">
            <Search className="w-4 h-4 absolute start-3.5 top-1/2 -translate-y-1/2 text-surface-400 pointer-events-none" />
            <input type="text" placeholder={t("inventoryAudits.searchPlaceholder")} value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} className="w-full ps-10 pe-3.5 py-2.5 border border-surface-200 bg-surface-50 rounded-xl text-sm text-surface-800 placeholder:text-surface-300 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150" aria-label={t("inventoryAudits.searchPlaceholder")} />
          </div>
          <div>
            <select value={location} onChange={(e) => { setLocation(e.target.value); setPage(1); }} className={SELECT_CLASS}>
              <option value="">{t("inventoryAudits.allLocations")}</option>
              {AUDIT_LOCATIONS.map((l) => (
                <option key={l} value={l}>{t(`inventoryAudits.locations.${l}`)}</option>
              ))}
            </select>
          </div>
          <div>
            <select value={status} onChange={(e) => { setStatus(e.target.value); setPage(1); }} className={SELECT_CLASS}>
              <option value="">{t("inventoryAudits.allStatuses")}</option>
              {AUDIT_STATUSES.map((s) => (
                <option key={s} value={s}>{t(`inventoryAudits.statuses.${s}`)}</option>
              ))}
            </select>
          </div>
          <div className="flex items-center gap-2">
            <select value={sort} onChange={(e) => { setSort(e.target.value); setPage(1); }} className="flex-1 px-3 py-1.5 rounded-lg border border-surface-200 text-[12px] text-surface-700 bg-surface-50 focus:outline-none focus:ring-2 focus:ring-primary-500/20" aria-label={t("inventoryAudits.sortBy")}>
              {SORT_COLUMNS.map((col) => (
                <option key={col.key} value={col.key}>{t(col.labelKey)}</option>
              ))}
            </select>
            <button onClick={() => { setOrder((prev) => (prev === "asc" ? "desc" : "asc")); setPage(1); }} className="px-3 py-1.5 rounded-lg border border-surface-200 text-[12px] font-semibold text-surface-600 bg-surface-50 hover:bg-surface-100 transition-colors" title={order === "asc" ? t("inventoryAudits.sortAsc") : t("inventoryAudits.sortDesc")}>
              {order === "asc" ? <ArrowUp className="w-4 h-4" /> : <ArrowDown className="w-4 h-4" />}
            </button>
          </div>
        </div>
        <div className="flex items-center justify-between mt-3 pt-3 border-t border-surface-100">
          <div className="flex items-center gap-2 text-[12px] text-surface-400">
            <Filter className="w-4 h-4" />
            <span>{t("inventoryAudits.showing", { count: items.length, total })}</span>
          </div>
          {hasFilters && (
            <button onClick={clearFilters} className="flex items-center gap-1.5 px-3 py-1.5 text-[12px] font-semibold text-surface-500 bg-surface-50 hover:bg-surface-100 rounded-lg transition-colors">
              <X className="w-3.5 h-3.5" />
              {t("inventoryAudits.clear")}
            </button>
          )}
        </div>
      </div>

      {/* Table */}
      {items.length === 0 ? (
        <EmptyState
          icon={ClipboardList}
          title={t("inventoryAudits.noAudits")}
          description={t("inventoryAudits.noAuditsHint")}
          action={canManage && (
            <button onClick={() => setCreateOpen(true)} className="px-4 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white text-[13px] font-semibold rounded-xl hover:from-primary-700 hover:to-primary-800 shadow-sm shadow-primary-600/20">
              {t("inventoryAudits.newAudit")}
            </button>
          )}
        />
      ) : (
        <div className="bg-white rounded-2xl border border-surface-200/80 overflow-hidden shadow-card">
          <div className="overflow-x-auto">
            <table className="w-full text-sm" role="table">
              <thead>
                <tr className="border-b border-surface-100 bg-surface-50/60">
                  {[
                    { key: "name", labelKey: "inventoryAudits.columns.name" },
                    { key: "location", labelKey: "inventoryAudits.columns.location" },
                    { key: "status", labelKey: "inventoryAudits.columns.status" },
                    { key: "counted", labelKey: "inventoryAudits.columns.counted" },
                    { key: "difference", labelKey: "inventoryAudits.columns.difference" },
                    { key: "created_by_name", labelKey: "inventoryAudits.columns.createdBy" },
                    { key: "started_at", labelKey: "inventoryAudits.columns.startedAt" },
                  ].map((col) => (
                    <th key={col.key} className="px-5 py-3.5 text-start text-[11px] font-semibold text-surface-500 uppercase tracking-wider">
                      <button
                        onClick={() => toggleSort(col.key)}
                        className="inline-flex items-center gap-1 uppercase tracking-wider hover:text-primary-600 transition-colors"
                      >
                        {t(col.labelKey)}
                        {sort === col.key && (order === "asc" ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />)}
                      </button>
                    </th>
                  ))}
                  <th className="px-5 py-3.5 text-end text-[11px] font-semibold text-surface-500 uppercase tracking-wider">{t("inventoryAudits.columns.actions")}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-100">
                {items.map((audit) => (
                  <tr key={audit.id} className="hover:bg-surface-50/50 transition-colors duration-100">
                    <td className="px-5 py-3.5">
                      <button onClick={() => setDetails(audit)} className="text-[13px] font-semibold text-surface-800 hover:text-primary-600 text-start transition-colors">
                        {audit.name}
                      </button>
                    </td>
                    <td className="px-5 py-3.5 whitespace-nowrap text-[13px] text-surface-600">{t(`inventoryAudits.locations.${audit.location}`)}</td>
                    <td className="px-5 py-3.5 whitespace-nowrap">
                      <Badge variant={statusBadge(audit.status)}>{t(`inventoryAudits.statuses.${audit.status}`)}</Badge>
                    </td>
                    <td className="px-5 py-3.5 whitespace-nowrap text-[13px] text-surface-600">
                      {audit.counted_items}/{audit.total_items}
                    </td>
                    <td className="px-5 py-3.5 whitespace-nowrap">
                      {audit.total_difference !== 0 ? (
                        <span className={`text-[13px] font-bold ${audit.total_difference > 0 ? "text-emerald-600" : "text-red-600"}`}>
                          {audit.total_difference > 0 ? "+" : ""}{audit.total_difference}
                        </span>
                      ) : (
                        <span className="text-[13px] text-surface-400">0</span>
                      )}
                    </td>
                    <td className="px-5 py-3.5 whitespace-nowrap text-[13px] text-surface-500">{audit.created_by_name || "—"}</td>
                    <td className="px-5 py-3.5 whitespace-nowrap text-[13px] text-surface-500">
                      {new Date(audit.started_at).toLocaleDateString(locale, { year: "numeric", month: "short", day: "numeric" })}
                    </td>
                    <td className="px-5 py-3.5 whitespace-nowrap text-end">
                      <div className="inline-flex items-center gap-1">
                        <button onClick={() => setDetails(audit)} className="p-1.5 text-surface-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-all duration-150" title={t("inventoryAudits.details.title")}>
                          <Eye className="w-4 h-4" />
                        </button>
                        {canManage && audit.status === "open" && (
                          <>
                            <button onClick={() => setCounting(audit)} className="p-1.5 text-surface-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-all duration-150" title={t("inventoryAudits.form.countTitle")}>
                              <Pencil className="w-4 h-4" />
                            </button>
                            <button onClick={() => setCompleteTarget(audit)} className="p-1.5 text-surface-400 hover:text-emerald-600 hover:bg-emerald-50 rounded-lg transition-all duration-150" title={t("inventoryAudits.complete")}>
                              <CheckCircle2 className="w-4 h-4" />
                            </button>
                            <button onClick={() => setCancelTarget(audit)} className="p-1.5 text-surface-400 hover:text-amber-600 hover:bg-amber-50 rounded-lg transition-all duration-150" title={t("inventoryAudits.cancel")}>
                              <Ban className="w-4 h-4" />
                            </button>
                            <button onClick={() => setDeleteTarget(audit)} className="p-1.5 text-surface-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all duration-150" title={t("inventoryAudits.confirmDelete.title")}>
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </>
                        )}
                        {canManage && audit.status !== "open" && audit.status !== "completed" && (
                          <button onClick={() => setDeleteTarget(audit)} className="p-1.5 text-surface-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all duration-150" title={t("inventoryAudits.confirmDelete.title")}>
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {pages > 1 && (
            <div className="flex items-center justify-between px-5 py-3.5 border-t border-surface-100">
              <p className="text-[12px] text-surface-400">{t("inventoryAudits.pageOf", { page, pages })}</p>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page <= 1}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-lg border border-surface-200 text-[12px] font-semibold text-surface-600 hover:bg-surface-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  <ChevronLeft className="w-4 h-4" />
                  {t("inventoryAudits.previous")}
                </button>
                <button
                  onClick={() => setPage((p) => Math.min(pages, p + 1))}
                  disabled={page >= pages}
                  className="flex items-center gap-1 px-3 py-1.5 rounded-lg border border-surface-200 text-[12px] font-semibold text-surface-600 hover:bg-surface-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                >
                  {t("inventoryAudits.next")}
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      <AuditModal
        isOpen={createOpen}
        onClose={() => setCreateOpen(false)}
        onSubmit={(data) => createMutation.mutate(data)}
        loading={createMutation.isPending}
      />

      <CountModal
        audit={counting}
        onClose={() => setCounting(null)}
        onSubmit={(items) => updateMutation.mutate({ id: counting.id, data: { items } })}
        loading={updateMutation.isPending}
      />

      <AuditDetailsModal audit={details} onClose={() => setDetails(null)} onCount={canManage ? () => { setCounting(details); setDetails(null); } : null} />

      <ConfirmDialog
        isOpen={!!completeTarget}
        onClose={() => setCompleteTarget(null)}
        onConfirm={() => completeMutation.mutate(completeTarget.id)}
        title={t("inventoryAudits.confirmComplete.title")}
        message={t("inventoryAudits.confirmComplete.message", { name: completeTarget?.name })}
        confirmText={t("inventoryAudits.complete")}
        loadingText={t("inventoryAudits.completing")}
        loading={completeMutation.isPending}
      />

      <ConfirmDialog
        isOpen={!!cancelTarget}
        onClose={() => setCancelTarget(null)}
        onConfirm={() => updateMutation.mutate({ id: cancelTarget.id, data: { status: "cancelled" } })}
        title={t("inventoryAudits.confirmCancel.title")}
        message={t("inventoryAudits.confirmCancel.message", { name: cancelTarget?.name })}
        confirmText={t("inventoryAudits.cancel")}
        loadingText={t("inventoryAudits.cancelling")}
        loading={updateMutation.isPending}
      />

      <ConfirmDialog
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => deleteMutation.mutate(deleteTarget.id)}
        title={t("inventoryAudits.confirmDelete.title")}
        message={t("inventoryAudits.confirmDelete.message", { name: deleteTarget?.name })}
        confirmText={t("inventoryAudits.delete")}
        loadingText={t("inventoryAudits.deleting")}
        loading={deleteMutation.isPending}
      />
    </div>
  );
}

function AuditModal({ isOpen, onClose, onSubmit, loading }) {
  const { t } = useTranslation();

  const auditSchema = useMemo(() => z.object({
    name: z.string().min(1, t("inventoryAudits.validation.nameRequired")),
    location: z.string().min(1, t("inventoryAudits.validation.locationRequired")),
  }), [t]);

  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: zodResolver(auditSchema),
    values: {
      name: "",
      location: "warehouse",
    },
  });

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={t("inventoryAudits.form.title")}>
      <form onSubmit={handleSubmit((data) => { onSubmit(data); reset(); })} className="space-y-5">
        <div>
          <label className={LABEL_CLASS}>{t("inventoryAudits.form.nameLabel")}</label>
          <input {...register("name")} placeholder={t("inventoryAudits.form.namePlaceholder")} className={INPUT_CLASS} />
          {errors.name && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.name.message}</p>}
        </div>
        <div>
          <label className={LABEL_CLASS}>{t("inventoryAudits.form.locationLabel")}</label>
          <select {...register("location")} className={SELECT_CLASS}>
            {AUDIT_LOCATIONS.map((l) => (
              <option key={l} value={l}>{t(`inventoryAudits.locations.${l}`)}</option>
            ))}
          </select>
          {errors.location && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.location.message}</p>}
        </div>
        <div className="bg-surface-50 rounded-xl p-4 text-[13px] text-surface-600 leading-relaxed">
          {t("inventoryAudits.form.hint")}
        </div>
        <div className="flex justify-end gap-3 pt-5 border-t border-surface-100">
          <button type="button" onClick={onClose} className="px-4 py-2.5 text-[13px] font-semibold text-surface-600 bg-white border border-surface-200 rounded-xl hover:bg-surface-50 transition-all duration-150">{t("inventoryAudits.form.cancel")}</button>
          <button type="submit" disabled={loading} className="px-4 py-2.5 text-[13px] font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl hover:from-primary-700 hover:to-primary-800 disabled:opacity-50 transition-all duration-150 shadow-sm shadow-primary-600/20">{loading ? t("inventoryAudits.form.creating") : t("inventoryAudits.form.create")}</button>
        </div>
      </form>
    </Modal>
  );
}

function CountModal({ audit, onClose, onSubmit, loading }) {
  const { t } = useTranslation();
  const [rows, setRows] = useState([]);
  const [itemsLoading, setItemsLoading] = useState(false);
  const [itemsError, setItemsError] = useState(null);

  useEffect(() => {
    if (!audit) return;
    setRows([]);
    setItemsError(null);
    setItemsLoading(true);
    auditService.getItems(audit.id)
      .then((res) => setRows(res.data.data))
      .catch((err) => setItemsError(err.response?.data?.message || err.message))
      .finally(() => setItemsLoading(false));
  }, [audit]);

  if (!audit) return null;

  const updateRow = (productId, value) => {
    setRows((prev) => prev.map((r) => {
      if (r.product_id !== productId) return r;
      const counted = value === "" ? null : Number(value);
      const difference = counted === null ? 0 : counted - r.system_quantity;
      return { ...r, counted_quantity: counted, difference };
    }));
  };

  const handleSave = () => {
    const items = rows
      .filter((r) => r.counted_quantity !== null && r.counted_quantity !== undefined)
      .map((r) => ({
        product_id: r.product_id,
        counted_quantity: r.counted_quantity,
      }));
    onSubmit(items);
  };

  const entered = rows.filter((r) => r.counted_quantity !== null).length;

  return (
    <Modal isOpen={!!audit} onClose={onClose} title={t("inventoryAudits.form.countTitle")} maxWidth="max-w-3xl">
      <div className="space-y-4">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2">
            <span className="text-[12px] font-semibold text-surface-400 uppercase tracking-wide">{t("inventoryAudits.columns.name")}</span>
            <span className="text-[13px] font-bold text-surface-800">{audit.name}</span>
          </div>
          <span className="w-px h-4 bg-surface-200" />
          <div className="flex items-center gap-2">
            <span className="text-[12px] font-semibold text-surface-400 uppercase tracking-wide">{t("inventoryAudits.columns.location")}</span>
            <Badge variant="info">{t(`inventoryAudits.locations.${audit.location}`)}</Badge>
          </div>
          <span className="w-px h-4 bg-surface-200" />
          <span className="text-[12px] font-semibold text-surface-400">
            {t("inventoryAudits.entered", { entered, total: rows.length })}
          </span>
        </div>

        {itemsLoading ? (
          <LoadingSpinner />
        ) : itemsError ? (
          <ErrorDisplay message={itemsError} onRetry={() => {
            setItemsLoading(true);
            setItemsError(null);
            auditService.getItems(audit.id)
              .then((res) => setRows(res.data.data))
              .catch((err) => setItemsError(err.response?.data?.message || err.message))
              .finally(() => setItemsLoading(false));
          }} />
        ) : rows.length === 0 ? (
          <p className="text-center text-surface-400 py-10 text-[13px]">{t("inventoryAudits.noItems")}</p>
        ) : (
          <div className="max-h-[50vh] overflow-y-auto border border-surface-100 rounded-xl">
            <table className="w-full text-sm" role="table">
              <thead className="sticky top-0 bg-surface-50">
                <tr className="border-b border-surface-100">
                  <th className="px-4 py-3 text-start text-[11px] font-semibold text-surface-500 uppercase tracking-wider">{t("inventoryAudits.columns.product")}</th>
                  <th className="px-4 py-3 text-center text-[11px] font-semibold text-surface-500 uppercase tracking-wider">{t("inventoryAudits.columns.system")}</th>
                  <th className="px-4 py-3 text-center text-[11px] font-semibold text-surface-500 uppercase tracking-wider">{t("inventoryAudits.columns.counted")}</th>
                  <th className="px-4 py-3 text-center text-[11px] font-semibold text-surface-500 uppercase tracking-wider">{t("inventoryAudits.columns.difference")}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-100">
                {rows.map((row) => (
                  <tr key={row.product_id} className="hover:bg-surface-50/50">
                    <td className="px-4 py-2.5">
                      <p className="text-[13px] font-semibold text-surface-800">{row.product_name}</p>
                      {row.barcode && <p className="text-[11px] text-surface-400">{row.barcode}</p>}
                    </td>
                    <td className="px-4 py-2.5 text-center text-[13px] text-surface-600">{row.system_quantity}</td>
                    <td className="px-4 py-2.5 text-center">
                      <input
                        type="number"
                        min="0"
                        value={row.counted_quantity ?? ""}
                        placeholder={t("inventoryAudits.enterCount")}
                        onChange={(e) => updateRow(row.product_id, e.target.value)}
                        className="w-24 px-3 py-1.5 text-center border border-surface-200 bg-surface-50 rounded-lg text-sm text-surface-800 placeholder:text-surface-300 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150"
                      />
                    </td>
                    <td className="px-4 py-2.5 text-center">
                      {row.counted_quantity !== null && row.difference !== 0 ? (
                        <span className={`text-[13px] font-bold ${row.difference > 0 ? "text-emerald-600" : "text-red-600"}`}>
                          {row.difference > 0 ? "+" : ""}{row.difference}
                        </span>
                      ) : (
                        <span className="text-[13px] text-surface-300">0</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <p className="text-[12px] text-surface-400 leading-relaxed">{t("inventoryAudits.form.countHint")}</p>

        <div className="flex justify-end gap-3 pt-4 border-t border-surface-100">
          <button type="button" onClick={onClose} className="px-4 py-2.5 text-[13px] font-semibold text-surface-600 bg-white border border-surface-200 rounded-xl hover:bg-surface-50 transition-all duration-150">{t("inventoryAudits.form.cancel")}</button>
          <button type="button" onClick={handleSave} disabled={loading} className="flex items-center gap-2 px-4 py-2.5 text-[13px] font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl hover:from-primary-700 hover:to-primary-800 disabled:opacity-50 transition-all duration-150 shadow-sm shadow-primary-600/20">
            <Save className="w-4 h-4" />
            {loading ? t("inventoryAudits.form.saving") : t("inventoryAudits.form.save")}
          </button>
        </div>
      </div>
    </Modal>
  );
}

function AuditDetailsModal({ audit, onClose, onCount }) {
  const { t, i18n } = useTranslation();
  const locale = i18n.language === "ar" ? "ar-EG" : "en-US";
  const [items, setItems] = useState([]);
  const [itemsLoading, setItemsLoading] = useState(false);
  const [itemsError, setItemsError] = useState(null);

  useEffect(() => {
    if (!audit) return;
    setItems([]);
    setItemsError(null);
    setItemsLoading(true);
    auditService.getItems(audit.id)
      .then((res) => setItems(res.data.data))
      .catch((err) => setItemsError(err.response?.data?.message || err.message))
      .finally(() => setItemsLoading(false));
  }, [audit]);

  if (!audit) return null;

  const rows = [
    { label: t("inventoryAudits.columns.location"), value: t(`inventoryAudits.locations.${audit.location}`) },
    { label: t("inventoryAudits.columns.status"), value: t(`inventoryAudits.statuses.${audit.status}`) },
    { label: t("inventoryAudits.columns.createdBy"), value: audit.created_by_name || "—" },
    { label: t("inventoryAudits.columns.startedAt"), value: new Date(audit.started_at).toLocaleString(locale) },
    { label: t("inventoryAudits.columns.completedAt"), value: audit.completed_at ? new Date(audit.completed_at).toLocaleString(locale) : "—" },
  ];

  return (
    <Modal isOpen={!!audit} onClose={onClose} title={t("inventoryAudits.details.title")} maxWidth="max-w-3xl">
      <div className="space-y-5">
        <div className="bg-surface-50 rounded-xl p-4">
          <p className="text-[11px] font-semibold text-surface-400 uppercase tracking-wide mb-1">{t("inventoryAudits.columns.name")}</p>
          <p className="text-[15px] font-bold text-surface-900">{audit.name}</p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-1">
          {rows.map((row) => (
            <div key={row.label} className="flex items-center justify-between py-2 border-b border-surface-50">
              <span className="text-[13px] text-surface-500">{row.label}</span>
              <span className="text-[13px] font-semibold text-surface-800">{row.value}</span>
            </div>
          ))}
        </div>

        <div>
          <h3 className="text-[15px] font-semibold text-surface-900 mb-3">{t("inventoryAudits.details.items")}</h3>
          {itemsLoading ? (
            <LoadingSpinner />
          ) : itemsError ? (
            <ErrorDisplay message={itemsError} />
          ) : items.length === 0 ? (
            <p className="text-center text-surface-400 py-8 text-[13px]">{t("inventoryAudits.noItems")}</p>
          ) : (
            <div className="max-h-[40vh] overflow-y-auto border border-surface-100 rounded-xl">
              <table className="w-full text-sm" role="table">
                <thead className="sticky top-0 bg-surface-50">
                  <tr className="border-b border-surface-100">
                    <th className="px-4 py-3 text-start text-[11px] font-semibold text-surface-500 uppercase tracking-wider">{t("inventoryAudits.columns.product")}</th>
                    <th className="px-4 py-3 text-center text-[11px] font-semibold text-surface-500 uppercase tracking-wider">{t("inventoryAudits.columns.system")}</th>
                    <th className="px-4 py-3 text-center text-[11px] font-semibold text-surface-500 uppercase tracking-wider">{t("inventoryAudits.columns.counted")}</th>
                    <th className="px-4 py-3 text-center text-[11px] font-semibold text-surface-500 uppercase tracking-wider">{t("inventoryAudits.columns.difference")}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-surface-100">
                  {items.map((item) => (
                    <tr key={item.id} className="hover:bg-surface-50/50">
                      <td className="px-4 py-2.5">
                        <p className="text-[13px] font-semibold text-surface-800">{item.product_name}</p>
                        {item.barcode && <p className="text-[11px] text-surface-400">{item.barcode}</p>}
                      </td>
                      <td className="px-4 py-2.5 text-center text-[13px] text-surface-600">{item.system_quantity}</td>
                      <td className="px-4 py-2.5 text-center text-[13px] text-surface-600">
                        {item.counted_quantity === null ? "—" : item.counted_quantity}
                      </td>
                      <td className="px-4 py-2.5 text-center">
                        {item.difference !== 0 ? (
                          <span className={`text-[13px] font-bold ${item.difference > 0 ? "text-emerald-600" : "text-red-600"}`}>
                            {item.difference > 0 ? "+" : ""}{item.difference}
                          </span>
                        ) : (
                          <span className="text-[13px] text-surface-300">0</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="flex justify-end gap-3 pt-4 border-t border-surface-100">
          {onCount && audit.status === "open" && (
            <button onClick={onCount} className="flex items-center gap-2 px-4 py-2.5 text-[13px] font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl hover:from-primary-700 hover:to-primary-800 transition-all duration-150 shadow-sm shadow-primary-600/20">
              <Pencil className="w-4 h-4" />
              {t("inventoryAudits.form.countTitle")}
            </button>
          )}
          <button onClick={onClose} className="px-4 py-2.5 text-[13px] font-semibold text-surface-600 bg-white border border-surface-200 rounded-xl hover:bg-surface-50 transition-all duration-150">{t("inventoryAudits.details.close")}</button>
        </div>
      </div>
    </Modal>
  );
}
