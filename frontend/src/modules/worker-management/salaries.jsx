import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { salaryService, workerService, SALARY_STATUSES } from "./api";
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
  secondaryButtonClass, iconButtonClass, dangerIconButtonClass, amberIconButtonClass,
} from "../../shared/components/styles";
import {
  Plus, Pencil, Trash2, Wallet, Banknote, CheckCircle2,
} from "lucide-react";
import toast from "react-hot-toast";

const INPUT_CLASS = inputClass;
const LABEL_CLASS = labelClass;
const SELECT_CLASS = `${inputClass} appearance-none cursor-pointer`;

export default function SalariesPage() {
  const { t, i18n } = useTranslation();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const canManage = ["admin", "manager"].includes(user?.role);
  const locale = i18n.language === "ar" ? "ar-EG" : "en-US";
  const [workerFilter, setWorkerFilter] = useState("");
  const [period, setPeriod] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [payTarget, setPayTarget] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const { data: workers = [], isLoading: workersLoading } = useQuery({
    queryKey: ["worker-management", "workers"],
    queryFn: async () => {
      const res = await workerService.getAll({ status: "active" });
      return res.data.data;
    },
  });

  const { data: records = [], isLoading, error, refetch } = useQuery({
    queryKey: ["worker-management", "salaries", workerFilter, period, statusFilter],
    queryFn: async () => {
      const res = await salaryService.getAll({
        worker_id: workerFilter || undefined,
        period: period || undefined,
        status: statusFilter || undefined,
      });
      return res.data.data;
    },
  });

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["worker-management"] });
  };

  const createMutation = useMutation({
    mutationFn: (data) => salaryService.create(data),
    onSuccess: () => { invalidate(); toast.success(t("workerManagement.toast.salaryCreated")); setModalOpen(false); },
    onError: (err) => toast.error(err.response?.data?.message || t("workerManagement.toast.salaryCreateFailed")),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => salaryService.update(id, data),
    onSuccess: () => { invalidate(); toast.success(t("workerManagement.toast.salaryUpdated")); setModalOpen(false); setEditing(null); },
    onError: (err) => toast.error(err.response?.data?.message || t("workerManagement.toast.salaryUpdateFailed")),
  });

  const payMutation = useMutation({
    mutationFn: ({ id, paymentDate }) => salaryService.markPaid(id, paymentDate),
    onSuccess: () => { invalidate(); toast.success(t("workerManagement.toast.salaryPaid")); setPayTarget(null); },
    onError: (err) => toast.error(err.response?.data?.message || t("workerManagement.toast.salaryPayFailed")),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => salaryService.delete(id),
    onSuccess: () => { invalidate(); toast.success(t("workerManagement.toast.salaryDeleted")); setDeleteTarget(null); },
    onError: (err) => toast.error(err.response?.data?.message || t("workerManagement.toast.salaryDeleteFailed")),
  });

  const formatMoney = (value) => {
    const num = Number(value) || 0;
    return num.toLocaleString(locale, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  };

  const columns = [
    {
      key: "worker_name",
      label: t("workerManagement.salaries.columns.worker"),
      render: (val) => (
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center text-[11px] font-bold text-white shrink-0">
            {val?.charAt(0)?.toUpperCase() || "?"}
          </div>
          <span className="text-[13px] font-semibold text-surface-800 dark:text-surface-100 truncate">{val}</span>
        </div>
      ),
    },
    {
      key: "period",
      label: t("workerManagement.salaries.columns.period"),
      render: (val) => <span className="text-[13px] font-medium text-surface-600 dark:text-surface-300 tabular-nums">{val || "—"}</span>,
    },
    {
      key: "base_salary",
      label: t("workerManagement.salaries.columns.base"),
      render: (val) => <span className="text-[13px] text-surface-600 dark:text-surface-300 tabular-nums">{formatMoney(val)}</span>,
    },
    {
      key: "net_amount",
      label: t("workerManagement.salaries.columns.net"),
      render: (val) => <span className="text-[13px] font-bold text-surface-800 dark:text-surface-100 tabular-nums">{formatMoney(val)}</span>,
    },
    {
      key: "status",
      label: t("workerManagement.salaries.columns.status"),
      render: (val) => <Badge variant={val === "paid" ? "success" : val === "partial" ? "warning" : "info"}>{t(`workerManagement.statuses.${val}`)}</Badge>,
    },
    {
      key: "id",
      label: t("workerManagement.columns.actions"),
      render: (_, row) => (
        <div className="flex items-center gap-1">
          {canManage && (
            <>
              {row.status !== "paid" && (
                <button
                  onClick={() => setPayTarget(row)}
                  className={amberIconButtonClass}
                  title={t("workerManagement.salaries.markPaid")}
                  aria-label={t("workerManagement.salaries.markPaid")}
                >
                  <CheckCircle2 className="w-4 h-4" />
                </button>
              )}
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
        title={t("workerManagement.salaries.title")}
        description={t("workerManagement.salaries.subtitle")}
        actions={
          canManage && (
            <button onClick={() => { setEditing(null); setModalOpen(true); }} className={primaryButtonClass}>
              <Plus className="w-4 h-4" />
              {t("workerManagement.salaries.newSalary")}
            </button>
          )
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-[180px_1fr_1fr] gap-3 mb-6">
        <select
          value={workerFilter}
          onChange={(e) => setWorkerFilter(e.target.value)}
          className={SELECT_CLASS}
          aria-label={t("workerManagement.salaries.filterWorker")}
        >
          <option value="">{t("workerManagement.salaries.allWorkers")}</option>
          {workers.map((w) => (
            <option key={w.id} value={w.id}>{w.full_name}</option>
          ))}
        </select>
        <input
          type="month"
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
          className={INPUT_CLASS}
          aria-label={t("workerManagement.salaries.filterPeriod")}
        />
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className={SELECT_CLASS}
          aria-label={t("workerManagement.salaries.filterStatus")}
        >
          <option value="">{t("workerManagement.salaries.allStatuses")}</option>
          {SALARY_STATUSES.map((s) => (
            <option key={s} value={s}>{t(`workerManagement.statuses.${s}`)}</option>
          ))}
        </select>
      </div>

      {records.length === 0 ? (
        <EmptyState
          icon={Wallet}
          title={t("workerManagement.salaries.empty.title")}
          description={t("workerManagement.salaries.empty.description")}
          action={!workerFilter && !period && !statusFilter && canManage && (
            <button onClick={() => { setEditing(null); setModalOpen(true); }} className={primaryButtonClass}>
              {t("workerManagement.salaries.empty.addFirst")}
            </button>
          )}
        />
      ) : (
        <DataTable columns={columns} data={records} />
      )}

      <SalaryModal
        isOpen={modalOpen}
        onClose={() => { setModalOpen(false); setEditing(null); }}
        editing={editing}
        workers={workers}
        onSubmit={(data) => editing ? updateMutation.mutate({ id: editing.id, data }) : createMutation.mutate(data)}
        loading={createMutation.isPending || updateMutation.isPending}
      />

      <PayModal
        target={payTarget}
        onClose={() => setPayTarget(null)}
        onConfirm={(date) => payMutation.mutate({ id: payTarget.id, paymentDate: date })}
        loading={payMutation.isPending}
      />

      <ConfirmDialog
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => deleteMutation.mutate(deleteTarget.id)}
        title={t("workerManagement.salaries.confirmDelete.title")}
        message={t("workerManagement.salaries.confirmDelete.message", { worker: deleteTarget?.worker_name, period: deleteTarget?.period })}
        loading={deleteMutation.isPending}
      />
    </div>
  );
}

function SalaryModal({ isOpen, onClose, editing, workers, onSubmit, loading }) {
  const { t } = useTranslation();

  const schema = useMemo(() => z.object({
    worker_id: z.union([z.coerce.number().min(1, t("workerManagement.salaries.validation.workerRequired")), z.string().min(1, t("workerManagement.salaries.validation.workerRequired"))]),
    period: z.string().regex(/^\d{4}-\d{2}$/, t("workerManagement.salaries.validation.periodInvalid")),
    base_salary: z.coerce.number().min(0, t("workerManagement.salaries.validation.baseNegative")),
    bonuses: z.coerce.number().min(0, t("workerManagement.salaries.validation.bonusesNegative")).optional(),
    deductions: z.coerce.number().min(0, t("workerManagement.salaries.validation.deductionsNegative")).optional(),
    advances_deduction: z.coerce.number().min(0, t("workerManagement.salaries.validation.advancesNegative")).optional(),
    status: z.string().min(1),
    payment_date: z.string().optional(),
    notes: z.string().optional(),
  }), [t]);

  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
    values: editing ? {
      worker_id: String(editing.worker_id || ""),
      period: editing.period || "",
      base_salary: editing.base_salary ?? 0,
      bonuses: editing.bonuses ?? 0,
      deductions: editing.deductions ?? 0,
      advances_deduction: editing.advances_deduction ?? 0,
      status: editing.status || "pending",
      payment_date: editing.payment_date || "",
      notes: editing.notes || "",
    } : {
      worker_id: "",
      period: new Date().toISOString().slice(0, 7),
      base_salary: 0,
      bonuses: 0,
      deductions: 0,
      advances_deduction: 0,
      status: "pending",
      payment_date: "",
      notes: "",
    },
  });

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={editing ? t("workerManagement.salaries.form.titleEdit") : t("workerManagement.salaries.form.titleCreate")}>
      <form onSubmit={handleSubmit((data) => { onSubmit(data); reset(); })} className="space-y-5">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>{t("workerManagement.salaries.form.worker")}</label>
            <select {...register("worker_id")} className={SELECT_CLASS}>
              <option value="">{t("workerManagement.salaries.form.workerPlaceholder")}</option>
              {workers.map((w) => (
                <option key={w.id} value={w.id}>{w.full_name}</option>
              ))}
            </select>
            {errors.worker_id && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.worker_id.message}</p>}
          </div>
          <div>
            <label className={LABEL_CLASS}>{t("workerManagement.salaries.form.period")}</label>
            <input {...register("period")} type="month" className={INPUT_CLASS} />
            {errors.period && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.period.message}</p>}
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>{t("workerManagement.salaries.form.baseSalary")}</label>
            <input {...register("base_salary")} type="number" step="0.01" min="0" className={INPUT_CLASS} />
            {errors.base_salary && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.base_salary.message}</p>}
          </div>
          <div>
            <label className={LABEL_CLASS}>{t("workerManagement.salaries.form.bonuses")}</label>
            <input {...register("bonuses")} type="number" step="0.01" min="0" className={INPUT_CLASS} />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>{t("workerManagement.salaries.form.deductions")}</label>
            <input {...register("deductions")} type="number" step="0.01" min="0" className={INPUT_CLASS} />
          </div>
          <div>
            <label className={LABEL_CLASS}>{t("workerManagement.salaries.form.advancesDeduction")}</label>
            <input {...register("advances_deduction")} type="number" step="0.01" min="0" className={INPUT_CLASS} />
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>{t("workerManagement.salaries.form.status")}</label>
            <select {...register("status")} className={SELECT_CLASS}>
              {SALARY_STATUSES.map((s) => (
                <option key={s} value={s}>{t(`workerManagement.statuses.${s}`)}</option>
              ))}
            </select>
          </div>
          <div>
            <label className={LABEL_CLASS}>{t("workerManagement.salaries.form.paymentDate")}</label>
            <input {...register("payment_date")} type="date" className={INPUT_CLASS} />
          </div>
        </div>
        <div>
          <label className={LABEL_CLASS}>{t("workerManagement.salaries.form.notes")}</label>
          <input {...register("notes")} placeholder={t("workerManagement.salaries.form.notesPlaceholder")} className={INPUT_CLASS} />
        </div>
        <div className="bg-surface-50 dark:bg-surface-800/60 rounded-xl border border-surface-100 dark:border-surface-700/60 p-4 flex items-start gap-3">
          <Banknote className="w-4 h-4 text-primary-500 dark:text-primary-400 mt-0.5 shrink-0" />
          <p className="text-[12px] leading-relaxed text-surface-500 dark:text-surface-400">{t("workerManagement.salaries.form.netHint")}</p>
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

function PayModal({ target, onClose, onConfirm, loading }) {
  const { t } = useTranslation();
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(z.object({
      payment_date: z.string().min(1, t("workerManagement.salaries.validation.paymentDateRequired")),
    })),
    defaultValues: { payment_date: new Date().toISOString().slice(0, 10) },
  });

  return (
    <Modal isOpen={!!target} onClose={onClose} title={t("workerManagement.salaries.payModal.title")}>
      {target && (
        <form onSubmit={handleSubmit((data) => { onConfirm(data.payment_date); })} className="space-y-5">
          <p className="text-[13px] text-surface-600 dark:text-surface-300 leading-relaxed">
            {t("workerManagement.salaries.payModal.message", { worker: target.worker_name, period: target.period })}
          </p>
          <div>
            <label className={LABEL_CLASS}>{t("workerManagement.salaries.payModal.paymentDate")}</label>
            <input {...register("payment_date")} type="date" className={INPUT_CLASS} />
            {errors.payment_date && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.payment_date.message}</p>}
          </div>
          <div className="flex justify-end gap-3 pt-5 border-t border-surface-100 dark:border-surface-700/60">
            <button type="button" onClick={onClose} className={secondaryButtonClass}>{t("workerManagement.form.cancel")}</button>
            <button type="submit" disabled={loading} className={primaryButtonClass}>
              {loading ? t("workerManagement.form.saving") : t("workerManagement.salaries.payModal.confirm")}
            </button>
          </div>
        </form>
      )}
    </Modal>
  );
}
