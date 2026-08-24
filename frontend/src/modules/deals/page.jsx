import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { z } from "zod";
import { dealService, DEAL_STATUSES, PAYMENT_STATUSES } from "./api";
import { clientService } from "../clients/api";
import { bdServiceService as serviceService } from "../services/api";
import { useAuth } from "../../shared/context/AuthContext";
import { PageHeader } from "../../shared/components/PageHeader";
import { DataTable } from "../../shared/components/DataTable";
import { Modal } from "../../shared/components/Modal";
import { ConfirmDialog } from "../../shared/components/ConfirmDialog";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
import { Badge, statusBadge } from "../../shared/components/Badge";
import {
  inputClass,
  selectClass,
  labelClass,
  searchInputClass,
  primaryButtonClass,
  secondaryButtonClass,
  iconButtonClass,
  dangerIconButtonClass,
} from "../../shared/components/styles";
import { Plus, Pencil, Trash2, Search, Handshake } from "lucide-react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import toast from "react-hot-toast";

export default function DealsPage() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const canManage = ["admin", "manager"].includes(user?.role);
  const [search, setSearch] = useState("");
  const [dealStatusFilter, setDealStatusFilter] = useState("");
  const [paymentStatusFilter, setPaymentStatusFilter] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const { data: deals = [], isLoading, error, refetch } = useQuery({
    queryKey: ["deals"],
    queryFn: async () => (await dealService.getAll()).data.data,
  });

  const createMutation = useMutation({
    mutationFn: (data) => dealService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["deals"] });
      queryClient.invalidateQueries({ queryKey: ["deals-statistics"] });
      queryClient.invalidateQueries({ queryKey: ["business-development-statistics"] });
      toast.success(t("business.deals.toast.created"));
      setModalOpen(false);
    },
    onError: (err) => toast.error(err.response?.data?.message || t("business.deals.toast.createFailed")),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => dealService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["deals"] });
      queryClient.invalidateQueries({ queryKey: ["deals-statistics"] });
      toast.success(t("business.deals.toast.updated"));
      setModalOpen(false);
      setEditing(null);
    },
    onError: (err) => toast.error(err.response?.data?.message || t("business.deals.toast.updateFailed")),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => dealService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["deals"] });
      queryClient.invalidateQueries({ queryKey: ["deals-statistics"] });
      queryClient.invalidateQueries({ queryKey: ["business-development-statistics"] });
      toast.success(t("business.deals.toast.deleted"));
      setDeleteTarget(null);
    },
    onError: (err) => toast.error(err.response?.data?.message || t("business.deals.toast.deleteFailed")),
  });

  const filtered = deals.filter((d) => {
    const term = search.toLowerCase();
    const matchesSearch =
      !search ||
      d.deal_number?.toLowerCase().includes(term) ||
      d.client_name?.toLowerCase().includes(term) ||
      d.service_name?.toLowerCase().includes(term);
    const matchesDealStatus = !dealStatusFilter || d.deal_status === dealStatusFilter;
    const matchesPaymentStatus = !paymentStatusFilter || d.payment_status === paymentStatusFilter;
    return matchesSearch && matchesDealStatus && matchesPaymentStatus;
  });

  const columns = [
    {
      key: "deal_number",
      label: t("business.deals.columns.number"),
      render: (val) => (
        <span className="numeric-value text-[13px] font-semibold text-surface-800 dark:text-surface-100">{val}</span>
      ),
    },
    {
      key: "client_name",
      label: t("business.deals.columns.client"),
      render: (val) => (
        <span className="text-[13px] text-surface-600 dark:text-surface-300">{val || "-"}</span>
      ),
    },
    {
      key: "service_name",
      label: t("business.deals.columns.service"),
      render: (val) => (
        <span className="text-[13px] text-surface-600 dark:text-surface-300">{val || "-"}</span>
      ),
    },
    {
      key: "final_amount",
      label: t("business.deals.columns.finalAmount"),
      render: (val) => (
        <span className="numeric-value text-[13px] font-bold text-emerald-600 dark:text-emerald-400">
          {formatMoney(val)}
        </span>
      ),
    },
    {
      key: "payment_status",
      label: t("business.deals.columns.paymentStatus"),
      render: (val) => <Badge variant={statusBadge(val)}>{t(`business.paymentStatus.${val}`)}</Badge>,
    },
    {
      key: "deal_status",
      label: t("business.deals.columns.dealStatus"),
      render: (val) => <Badge variant={statusBadge(val)}>{t(`business.dealStatus.${val}`)}</Badge>,
    },
    ...(canManage
      ? [
          {
            key: "id",
            label: t("common.columns.actions"),
            render: (_, row) => (
              <div className="flex items-center gap-1">
                <button
                  onClick={() => {
                    setEditing(row);
                    setModalOpen(true);
                  }}
                  className={iconButtonClass}
                  title={t("common.actions.edit")}
                >
                  <Pencil className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setDeleteTarget(row)}
                  className={dangerIconButtonClass}
                  title={t("common.actions.delete")}
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ),
          },
        ]
      : []),
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
        title={t("business.deals.title")}
        description={t("business.deals.description")}
        actions={
          canManage && (
            <button
              onClick={() => {
                setEditing(null);
                setModalOpen(true);
              }}
              className={primaryButtonClass}
            >
              <Plus className="w-4 h-4" />
              {t("business.deals.new")}
            </button>
          )
        }
      />

      <div className="mb-6 flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute start-3.5 top-1/2 -translate-y-1/2 text-surface-400 dark:text-surface-500 pointer-events-none" />
          <input
            type="text"
            placeholder={t("business.deals.searchPlaceholder")}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className={searchInputClass}
            aria-label={t("business.deals.searchPlaceholder")}
          />
        </div>
        <select
          value={dealStatusFilter}
          onChange={(e) => setDealStatusFilter(e.target.value)}
          className={`${selectClass} sm:w-44`}
          aria-label={t("business.deals.filters.dealStatus")}
        >
          <option value="">{t("business.deals.filters.allDealStatuses")}</option>
          {DEAL_STATUSES.map((status) => (
            <option key={status} value={status}>
              {t(`business.dealStatus.${status}`)}
            </option>
          ))}
        </select>
        <select
          value={paymentStatusFilter}
          onChange={(e) => setPaymentStatusFilter(e.target.value)}
          className={`${selectClass} sm:w-44`}
          aria-label={t("business.deals.filters.paymentStatus")}
        >
          <option value="">{t("business.deals.filters.allPaymentStatuses")}</option>
          {PAYMENT_STATUSES.map((status) => (
            <option key={status} value={status}>
              {t(`business.paymentStatus.${status}`)}
            </option>
          ))}
        </select>
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          icon={Handshake}
          title={t("business.deals.empty.title")}
          description={
            search || dealStatusFilter || paymentStatusFilter
              ? t("business.deals.empty.noResults")
              : t("business.deals.empty.noDeals")
          }
        />
      ) : (
        <DataTable columns={columns} data={filtered} />
      )}

      <DealModal
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setEditing(null);
        }}
        editing={editing}
        onSubmit={(data) =>
          editing ? updateMutation.mutate({ id: editing.id, data }) : createMutation.mutate(data)
        }
        loading={createMutation.isPending || updateMutation.isPending}
      />

      <ConfirmDialog
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => deleteMutation.mutate(deleteTarget.id)}
        title={t("business.deals.confirmDelete.title")}
        message={t("business.deals.confirmDelete.message", { name: deleteTarget?.deal_number })}
        loading={deleteMutation.isPending}
      />
    </div>
  );
}

function formatMoney(value) {
  const num = Number(value);
  return Number.isFinite(num) ? num.toFixed(2) : "-";
}

function DealModal({ isOpen, onClose, editing, onSubmit, loading }) {
  const { t } = useTranslation();

  const { data: clients = [] } = useQuery({
    queryKey: ["clients"],
    queryFn: async () => (await clientService.getAll()).data.data,
    enabled: isOpen,
  });

  const { data: services = [] } = useQuery({
    queryKey: ["services"],
    queryFn: async () => (await serviceService.getAll()).data.data,
    enabled: isOpen,
  });

  const schema = useMemo(
    () =>
      z.object({
        client_id: z.string().min(1, t("business.deals.validation.clientRequired")),
        service_id: z.string().min(1, t("business.deals.validation.serviceRequired")),
        price: z.coerce.number().min(0, t("business.deals.validation.priceInvalid")),
        discount: z.coerce.number().min(0),
        tax: z.coerce.number().min(0),
        deal_status: z.enum(DEAL_STATUSES),
        payment_status: z.enum(PAYMENT_STATUSES),
        notes: z.string().optional(),
      }),
    [t]
  );

  const defaults = useMemo(
    () =>
      editing
        ? {
            client_id: String(editing.client_id ?? ""),
            service_id: String(editing.service_id ?? ""),
            price: editing.price ?? "",
            discount: editing.discount ?? 0,
            tax: editing.tax ?? 0,
            deal_status: editing.deal_status || "draft",
            payment_status: editing.payment_status || "pending",
            notes: editing.notes || "",
          }
        : {
            client_id: "",
            service_id: "",
            price: "",
            discount: 0,
            tax: 0,
            deal_status: "draft",
            payment_status: "pending",
            notes: "",
          },
    [editing]
  );

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(schema),
    values: defaults,
  });

  const price = Number(watch("price")) || 0;
  const discount = Number(watch("discount")) || 0;
  const tax = Number(watch("tax")) || 0;
  const finalAmount = Math.max(price - discount + tax, 0);

  const handleServiceChange = (event) => {
    const svc = services.find((s) => s.id === Number(event.target.value));
    if (svc) setValue("price", svc.price ?? "");
  };

  const summaryRow = (label, value, strong = false) => (
    <div className="flex items-center justify-between text-[13px]">
      <span className="text-surface-500 dark:text-surface-400 font-medium">{label}</span>
      <span
        className={`numeric-value ${
          strong
            ? "font-bold text-emerald-600 dark:text-emerald-400"
            : "font-semibold text-surface-700 dark:text-surface-200"
        }`}
      >
        {value}
      </span>
    </div>
  );

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={editing ? t("business.deals.form.editTitle") : t("business.deals.form.createTitle")}
    >
      <form onSubmit={handleSubmit((data) => onSubmit(data))} className="space-y-5">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className={labelClass}>{t("business.deals.form.client")}</label>
            <select {...register("client_id")} className={selectClass}>
              <option value="">{t("business.deals.form.chooseClient")}</option>
              {clients.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.company_name}
                </option>
              ))}
            </select>
            {errors.client_id && (
              <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.client_id.message}</p>
            )}
          </div>
          <div>
            <label className={labelClass}>{t("business.deals.form.service")}</label>
            <select {...register("service_id")} onChange={handleServiceChange} className={selectClass}>
              <option value="">{t("business.deals.form.chooseService")}</option>
              {services.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
            {errors.service_id && (
              <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.service_id.message}</p>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className={labelClass}>{t("business.deals.form.price")}</label>
            <input {...register("price")} type="number" step="0.01" min="0" className={inputClass} />
            {errors.price && (
              <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.price.message}</p>
            )}
          </div>
          <div>
            <label className={labelClass}>{t("business.deals.form.discount")}</label>
            <input {...register("discount")} type="number" step="0.01" min="0" className={inputClass} />
          </div>
          <div>
            <label className={labelClass}>{t("business.deals.form.tax")}</label>
            <input {...register("tax")} type="number" step="0.01" min="0" className={inputClass} />
          </div>
        </div>

        <div className="bg-surface-50 dark:bg-surface-700/30 rounded-xl p-4 space-y-2">
          {summaryRow(t("business.deals.summary.price"), formatMoney(price))}
          {summaryRow(
            t("business.deals.summary.discount"),
            `- ${formatMoney(discount)}`
          )}
          {summaryRow(t("business.deals.summary.tax"), `+ ${formatMoney(tax)}`)}
          <div className="border-t border-surface-200/60 dark:border-surface-600/40 pt-2">
            {summaryRow(t("business.deals.summary.finalAmount"), formatMoney(finalAmount), true)}
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className={labelClass}>{t("business.deals.form.dealStatus")}</label>
            <select {...register("deal_status")} className={selectClass}>
              {DEAL_STATUSES.map((status) => (
                <option key={status} value={status}>
                  {t(`business.dealStatus.${status}`)}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelClass}>{t("business.deals.form.paymentStatus")}</label>
            <select {...register("payment_status")} className={selectClass}>
              {PAYMENT_STATUSES.map((status) => (
                <option key={status} value={status}>
                  {t(`business.paymentStatus.${status}`)}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className={labelClass}>{t("business.deals.form.notes")}</label>
          <textarea {...register("notes")} rows={2} className={`${inputClass} resize-none`} />
        </div>

        <div className="flex justify-end gap-3 pt-5 border-t border-surface-100 dark:border-surface-700/60">
          <button type="button" onClick={onClose} className={secondaryButtonClass}>
            {t("common.actions.cancel")}
          </button>
          <button type="submit" disabled={loading} className={primaryButtonClass}>
            {loading
              ? t("common.actions.saving")
              : editing
                ? t("common.actions.update")
                : t("common.actions.create")}
          </button>
        </div>
      </form>
    </Modal>
  );
}


