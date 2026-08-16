import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { advanceService, workerService, ADVANCE_STATUSES } from "./api";
import { useAuth } from "../../shared/context/AuthContext";
import { PageHeader } from "../../shared/components/PageHeader";
import { DataTable } from "../../shared/components/DataTable";
import { Modal } from "../../shared/components/Modal";
import { ConfirmDialog } from "../../shared/components/ConfirmDialog";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
import { Badge } from "../../shared/components/Badge";
import {
  inputClass, labelClass, primaryButtonClass,
  secondaryButtonClass, iconButtonClass, dangerIconButtonClass,
} from "../../shared/components/styles";
import {
  Plus, Pencil, Trash2, HandCoins, CircleDollarSign,
} from "lucide-react";
import toast from "react-hot-toast";

const INPUT_CLASS = inputClass;
const LABEL_CLASS = labelClass;
const SELECT_CLASS = `${inputClass} appearance-none cursor-pointer`;

export default function AdvancesPage() {
  const { t, i18n } = useTranslation();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const canManage = ["admin", "manager"].includes(user?.role);
  const locale = i18n.language === "ar" ? "ar-EG" : "en-US";
  const [workerFilter, setWorkerFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const { data: workers = [], isLoading: workersLoading } = useQuery({
    queryKey: ["worker-management", "workers"],
    queryFn: async () => {
      const res = await workerService.getAll({ status: "active" });
      return res.data.data;
    },
  });

  const { data: records = [], isLoading, error, refetch } = useQuery({
    queryKey: ["worker-management", "advances", workerFilter, statusFilter],
    queryFn: async () => {
      const res = await advanceService.getAll({
        worker_id: workerFilter || undefined,
        status: statusFilter || undefined,
      });
      return res.data.data;
    },
  });

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["worker-management"] });
  };

  const createMutation = useMutation({
    mutationFn: (data) => advanceService.create(data),
    onSuccess: () => { invalidate(); toast.success(t("workerManagement.toast.advanceCreated")); setModalOpen(false); },
    onError: (err) => toast.error(err.response?.data?.message || t("workerManagement.toast.advanceCreateFailed")),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => advanceService.update(id, data),
    onSuccess: () => { invalidate(); toast.success(t("workerManagement.toast.advanceUpdated")); setModalOpen(false); setEditing(null); },
    onError: (err) => toast.error(err.response?.data?.message || t("workerManagement.toast.advanceUpdateFailed")),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => advanceService.delete(id),
    onSuccess: () => { invalidate(); toast.success(t("workerManagement.toast.advanceDeleted")); setDeleteTarget(null); },
    onError: (err) => toast.error(err.response?.data?.message || t("workerManagement.toast.advanceDeleteFailed")),
  });

  const formatMoney = (value) => {
    const num = Number(value) || 0;
    return num.toLocaleString(locale, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  };

  const columns = [
    {
      key: "worker_name",
      label: t("workerManagement.advances.columns.worker"),
      render: (val) => (
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-rose-500 to-pink-600 flex items-center justify-center text-[11px] font-bold text-white shrink-0">
            {val?.charAt(0)?.toUpperCase() || "?"}
          </div>
          <span className="text-[13px] font-semibold text-surface-800 dark:text-surface-100 truncate">{val}</span>
        </div>
      ),
    },
    {
      key: "amount",
      label: t("workerManagement.advances.columns.amount"),
      render: (val) => <span className="text-[13px] font-bold text-surface-800 dark:text-surface-100 tabular-nums">{formatMoney(val)}</span>,
    },
    {
      key: "advance_date",
      label: t("workerManagement.advances.columns.date"),
      render: (val) => {
        if (!val) return "—";
        try {
          return new Date(val).toLocaleDateString(locale, { year: "numeric", month: "short", day: "numeric" });
        } catch {
          return "—";
        }
      },
    },
    {
      key: "status",
      label: t("workerManagement.advances.columns.status"),
      render: (val) => <Badge variant={val === "paid" ? "success" : val === "settled" ? "info" : "warning"}>{t(`workerManagement.statuses.${val}`)}</Badge>,
    },
    {
      key: "notes",
      label: t("workerManagement.advances.columns.notes"),
      render: (val) => <span className="text-[12px] text-surface-500 dark:text-surface-400 truncate max-w-[200px]">{val || "—"}</span>,
    },
    {
      key: "id",
      label: t("workerManagement.columns.actions"),
      render: (_, row) => (
        <div className="flex items-center gap-1">
          {canManage && (
            <>
              <button
                onClick={() => { setEditing(row); setModalOpen(true); }}
                className={iconButtonClass}
                title={t("workerManagement.edit")}
                aria-label={t("workerManagement.edit")}
              >
                <Pencil className="w-4 h-4" />
              </button>
              <button
                onClick={() => setDeleteTarget(row)}
                className={dangerIconButtonClass}
                title={t("workerManagement.delete")}
                aria-label={t("workerManagement.delete")}
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </>
          )}
        </div>
      ),
    },
  ];

  if (isLoading || workersLoading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay message={error.response?.data?.message || error.message} onRetry={refetch} />;

  return (
    <div>
      <PageHeader
        title={t("workerManagement.advances.title")}
        description={t("workerManagement.advances.subtitle")}
        actions={
          canManage && (
            <button onClick={() => { setEditing(null); setModalOpen(true); }} className={primaryButtonClass}>
              <Plus className="w-4 h-4" />
              {t("workerManagement.advances.newAdvance")}
            </button>
          )
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-[1fr_1fr] gap-3 mb-6">
        <select
          value={workerFilter}
          onChange={(e) => setWorkerFilter(e.target.value)}
          className={SELECT_CLASS}
          aria-label={t("workerManagement.advances.filterWorker")}
        >
          <option value="">{t("workerManagement.advances.allWorkers")}</option>
          {workers.map((w) => (
            <option key={w.id} value={w.id}>{w.full_name}</option>
          ))}
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className={SELECT_CLASS}
          aria-label={t("workerManagement.advances.filterStatus")}
        >
          <option value="">{t("workerManagement.advances.allStatuses")}</option>
          {ADVANCE_STATUSES.map((s) => (
            <option key={s} value={s}>{t(`workerManagement.statuses.${s}`)}</option>
          ))}
        </select>
      </div>

      {records.length === 0 ? (
        <EmptyState
          icon={HandCoins}
          title={t("workerManagement.advances.empty.title")}
          description={t("workerManagement.advances.empty.description")}
          action={!workerFilter && !statusFilter && canManage && (
            <button onClick={() => { setEditing(null); setModalOpen(true); }} className={primaryButtonClass}>
              {t("workerManagement.advances.empty.addFirst")}
            </button>
          )}
        />
      ) : (
        <DataTable columns={columns} data={records} />
      )}

      <AdvanceModal
        isOpen={modalOpen}
        onClose={() => { setModalOpen(false); setEditing(null); }}
        editing={editing}
        workers={workers}
        onSubmit={(data) => editing ? updateMutation.mutate({ id: editing.id, data }) : createMutation.mutate(data)}
        loading={createMutation.isPending || updateMutation.isPending}
      />

      <ConfirmDialog
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => deleteMutation.mutate(deleteTarget.id)}
        title={t("workerManagement.advances.confirmDelete.title")}
        message={t("workerManagement.advances.confirmDelete.message", { worker: deleteTarget?.worker_name })}
        loading={deleteMutation.isPending}
      />
    </div>
  );
}

function AdvanceModal({ isOpen, onClose, editing, workers, onSubmit, loading }) {
  const { t } = useTranslation();

  const schema = useMemo(() => z.object({
    worker_id: z.union([z.coerce.number().min(1, t("workerManagement.advances.validation.workerRequired")), z.string().min(1, t("workerManagement.advances.validation.workerRequired"))]),
    amount: z.coerce.number().positive(t("workerManagement.advances.validation.amountPositive")),
    advance_date: z.string().min(1, t("workerManagement.advances.validation.dateRequired")),
    status: z.string().min(1),
    notes: z.string().optional(),
  }), [t]);

  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
    values: editing ? {
      worker_id: String(editing.worker_id || ""),
      amount: editing.amount ?? 0,
      advance_date: editing.advance_date || "",
      status: editing.status || "pending",
      notes: editing.notes || "",
    } : {
      worker_id: "",
      amount: 0,
      advance_date: new Date().toISOString().slice(0, 10),
      status: "pending",
      notes: "",
    },
  });

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={editing ? t("workerManagement.advances.form.titleEdit") : t("workerManagement.advances.form.titleCreate")}>
      <form onSubmit={handleSubmit((data) => { onSubmit(data); reset(); })} className="space-y-5">
        <div>
          <label className={LABEL_CLASS}>{t("workerManagement.advances.form.worker")}</label>
          <select {...register("worker_id")} className={SELECT_CLASS}>
            <option value="">{t("workerManagement.advances.form.workerPlaceholder")}</option>
            {workers.map((w) => (
              <option key={w.id} value={w.id}>{w.full_name}</option>
            ))}
          </select>
          {errors.worker_id && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.worker_id.message}</p>}
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>{t("workerManagement.advances.form.amount")}</label>
            <input {...register("amount")} type="number" step="0.01" min="0.01" className={INPUT_CLASS} />
            {errors.amount && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.amount.message}</p>}
          </div>
          <div>
            <label className={LABEL_CLASS}>{t("workerManagement.advances.form.date")}</label>
            <input {...register("advance_date")} type="date" className={INPUT_CLASS} />
            {errors.advance_date && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.advance_date.message}</p>}
          </div>
        </div>
        <div>
          <label className={LABEL_CLASS}>{t("workerManagement.advances.form.status")}</label>
          <select {...register("status")} className={SELECT_CLASS}>
            {ADVANCE_STATUSES.map((s) => (
              <option key={s} value={s}>{t(`workerManagement.statuses.${s}`)}</option>
            ))}
          </select>
        </div>
        <div>
          <label className={LABEL_CLASS}>{t("workerManagement.advances.form.notes")}</label>
          <input {...register("notes")} placeholder={t("workerManagement.advances.form.notesPlaceholder")} className={INPUT_CLASS} />
        </div>
        <div className="bg-rose-50 dark:bg-rose-500/10 rounded-xl border border-rose-100 dark:border-rose-500/20 p-4 flex items-start gap-3">
          <CircleDollarSign className="w-4 h-4 text-rose-500 dark:text-rose-400 mt-0.5 shrink-0" />
          <p className="text-[12px] leading-relaxed text-rose-600 dark:text-rose-300">{t("workerManagement.advances.form.deductionHint")}</p>
        </div>
        <div className="flex justify-end gap-3 pt-5 border-t border-surface-100 dark:border-surface-700/60">
          <button type="button" onClick={onClose} className={secondaryButtonClass}>{t("workerManagement.form.cancel")}</button>
          <button type="submit" disabled={loading} className={primaryButtonClass}>
            {loading ? t("workerManagement.form.saving") : editing ? t("workerManagement.form.update") : t("workerManagement.form.create")}
          </button>
        </div>
      </form>
    </Modal>
  );
}
