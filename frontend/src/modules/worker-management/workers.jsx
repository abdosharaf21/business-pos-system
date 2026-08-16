import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { workerService, WORKER_STATUSES } from "./api";
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
  inputClass, labelClass, searchInputClass, primaryButtonClass,
  secondaryButtonClass, iconButtonClass, dangerIconButtonClass, amberIconButtonClass,
} from "../../shared/components/styles";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  Plus, Pencil, Trash2, Search, UsersRound,
  Power, Ban, Eye,
} from "lucide-react";
import toast from "react-hot-toast";

const INPUT_CLASS = inputClass;
const LABEL_CLASS = labelClass;
const SELECT_CLASS = `${inputClass} appearance-none cursor-pointer`;

export default function WorkersPage() {
  const { t, i18n } = useTranslation();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const canManage = ["admin", "manager"].includes(user?.role);
  const locale = i18n.language === "ar" ? "ar-EG" : "en-US";
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [viewTarget, setViewTarget] = useState(null);

  const { data: workers = [], isLoading, error, refetch } = useQuery({
    queryKey: ["worker-management", "workers", search, statusFilter],
    queryFn: async () => {
      const res = await workerService.getAll({
        search: search || undefined,
        status: statusFilter || undefined,
      });
      return res.data.data;
    },
  });

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["worker-management"] });
  };

  const createMutation = useMutation({
    mutationFn: (data) => workerService.create(data),
    onSuccess: () => { invalidate(); toast.success(t("workerManagement.toast.workerCreated")); setModalOpen(false); },
    onError: (err) => toast.error(err.response?.data?.message || t("workerManagement.toast.workerCreateFailed")),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => workerService.update(id, data),
    onSuccess: () => { invalidate(); toast.success(t("workerManagement.toast.workerUpdated")); setModalOpen(false); setEditing(null); },
    onError: (err) => toast.error(err.response?.data?.message || t("workerManagement.toast.workerUpdateFailed")),
  });

  const statusMutation = useMutation({
    mutationFn: ({ id, status }) => workerService.update(id, { status }),
    onSuccess: () => { invalidate(); toast.success(t("workerManagement.toast.workerStatusUpdated")); },
    onError: (err) => toast.error(err.response?.data?.message || t("workerManagement.toast.workerStatusFailed")),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => workerService.delete(id),
    onSuccess: () => { invalidate(); toast.success(t("workerManagement.toast.workerDeleted")); setDeleteTarget(null); },
    onError: (err) => toast.error(err.response?.data?.message || t("workerManagement.toast.workerDeleteFailed")),
  });

  const formatCurrency = (value) =>
    new Intl.NumberFormat(locale, { maximumFractionDigits: 2 }).format(value || 0);

  const columns = [
    {
      key: "full_name",
      label: t("workerManagement.workers.columns.worker"),
      render: (val, row) => (
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-[11px] font-bold text-white shrink-0">
            {val?.charAt(0)?.toUpperCase() || "?"}
          </div>
          <div className="min-w-0">
            <p className="text-[13px] font-semibold text-surface-800 dark:text-surface-100 truncate">{val}</p>
            <p className="text-[11px] text-surface-400 dark:text-surface-500 truncate">{row.phone || "—"}</p>
          </div>
        </div>
      ),
    },
    {
      key: "job_title",
      label: t("workerManagement.workers.columns.job"),
      render: (val, row) => (
        <span className="text-[12px] text-surface-600 dark:text-surface-300">
          {[val, row.department].filter(Boolean).join(" · ") || "—"}
        </span>
      ),
    },
    {
      key: "hire_date",
      label: t("workerManagement.workers.columns.hireDate"),
      render: (val) => {
        if (!val) return <span className="text-[12px] text-surface-400 dark:text-surface-500">—</span>;
        try {
          return (
            <span className="text-[12px] text-surface-500 dark:text-surface-400">
              {new Date(val).toLocaleDateString(locale, { year: "numeric", month: "short", day: "numeric" })}
            </span>
          );
        } catch {
          return <span className="text-[12px] text-surface-400 dark:text-surface-500">—</span>;
        }
      },
    },
    {
      key: "base_salary",
      label: t("workerManagement.workers.columns.salary"),
      render: (val) => (
        <span className="text-[13px] font-bold text-surface-800 dark:text-surface-100 tabular-nums">{formatCurrency(val)}</span>
      ),
    },
    {
      key: "status",
      label: t("workerManagement.workers.columns.status"),
      render: (val) => (
        <Badge variant={val === "active" ? "success" : "danger"}>
          {t(`workerManagement.statuses.${val}`)}
        </Badge>
      ),
    },
    {
      key: "id",
      label: t("workerManagement.columns.actions"),
      render: (_, row) => (
        <div className="flex items-center gap-1">
          <button
            onClick={() => setViewTarget(row)}
            className={iconButtonClass}
            title={t("workerManagement.workers.view")}
            aria-label={t("workerManagement.workers.view")}
          >
            <Eye className="w-4 h-4" />
          </button>
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
                onClick={() => statusMutation.mutate({ id: row.id, status: row.status === "active" ? "inactive" : "active" })}
                className={amberIconButtonClass}
                title={row.status === "active" ? t("workerManagement.workers.deactivate") : t("workerManagement.workers.activate")}
                aria-label={row.status === "active" ? t("workerManagement.workers.deactivate") : t("workerManagement.workers.activate")}
              >
                {row.status === "active" ? <Power className="w-4 h-4" /> : <Ban className="w-4 h-4" />}
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

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay message={error.response?.data?.message || error.message} onRetry={refetch} />;

  return (
    <div>
      <PageHeader
        title={t("workerManagement.workers.title")}
        description={t("workerManagement.workers.subtitle")}
        actions={
          canManage && (
            <button onClick={() => { setEditing(null); setModalOpen(true); }} className={primaryButtonClass}>
              <Plus className="w-4 h-4" />
              {t("workerManagement.workers.newWorker")}
            </button>
          )
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-[1fr_200px] gap-3 mb-6">
        <div className="relative">
          <Search className="w-4 h-4 absolute start-3.5 top-1/2 -translate-y-1/2 text-surface-400 dark:text-surface-500 pointer-events-none" />
          <input
            type="text"
            placeholder={t("workerManagement.workers.searchPlaceholder")}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className={searchInputClass}
            aria-label={t("workerManagement.workers.searchPlaceholder")}
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className={SELECT_CLASS}
          aria-label={t("workerManagement.workers.filterStatus")}
        >
          <option value="">{t("workerManagement.workers.allStatuses")}</option>
          {WORKER_STATUSES.map((s) => (
            <option key={s} value={s}>{t(`workerManagement.statuses.${s}`)}</option>
          ))}
        </select>
      </div>

      {workers.length === 0 ? (
        <EmptyState
          icon={UsersRound}
          title={t("workerManagement.workers.empty.title")}
          description={t("workerManagement.workers.empty.description")}
          action={!search && canManage && (
            <button onClick={() => { setEditing(null); setModalOpen(true); }} className={primaryButtonClass}>
              {t("workerManagement.workers.empty.addFirst")}
            </button>
          )}
        />
      ) : (
        <DataTable columns={columns} data={workers} />
      )}

      <WorkerModal
        isOpen={modalOpen}
        onClose={() => { setModalOpen(false); setEditing(null); }}
        editing={editing}
        onSubmit={(data) => editing ? updateMutation.mutate({ id: editing.id, data }) : createMutation.mutate(data)}
        loading={createMutation.isPending || updateMutation.isPending}
      />

      <WorkerDetailsModal worker={viewTarget} onClose={() => setViewTarget(null)} />

      <ConfirmDialog
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => deleteMutation.mutate(deleteTarget.id)}
        title={t("workerManagement.workers.confirmDelete.title")}
        message={t("workerManagement.workers.confirmDelete.message", { name: deleteTarget?.full_name })}
        loading={deleteMutation.isPending}
      />
    </div>
  );
}

function WorkerModal({ isOpen, onClose, editing, onSubmit, loading }) {
  const { t } = useTranslation();

  const schema = useMemo(() => z.object({
    full_name: z.string().min(1, t("workerManagement.workers.validation.nameRequired")),
    phone: z.string().min(1, t("workerManagement.workers.validation.phoneRequired")),
    email: z.string().email(t("workerManagement.workers.validation.emailInvalid")).optional().or(z.literal("")),
    job_title: z.string().optional(),
    department: z.string().optional(),
    hire_date: z.string().optional(),
    base_salary: z.union([
      z.coerce.number().min(0, t("workerManagement.workers.validation.salaryInvalid")),
      z.nan().refine(() => true),
    ]).optional().or(z.literal("")),
    status: z.string(),
    notes: z.string().optional(),
  }), [t]);

  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
    values: editing ? {
      full_name: editing.full_name || "",
      phone: editing.phone || "",
      email: editing.email || "",
      job_title: editing.job_title || "",
      department: editing.department || "",
      hire_date: editing.hire_date || "",
      base_salary: editing.base_salary ?? "",
      status: editing.status || "active",
      notes: editing.notes || "",
    } : {
      full_name: "",
      phone: "",
      email: "",
      job_title: "",
      department: "",
      hire_date: "",
      base_salary: "",
      status: "active",
      notes: "",
    },
  });

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={editing ? t("workerManagement.workers.form.titleEdit") : t("workerManagement.workers.form.titleCreate")} maxWidth="max-w-2xl">
      <form onSubmit={handleSubmit((data) => { onSubmit(data); reset(); })} className="space-y-5">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>{t("workerManagement.workers.form.fullName")}</label>
            <input {...register("full_name")} placeholder={t("workerManagement.workers.form.fullNamePlaceholder")} className={INPUT_CLASS} />
            {errors.full_name && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.full_name.message}</p>}
          </div>
          <div>
            <label className={LABEL_CLASS}>{t("workerManagement.workers.form.phone")}</label>
            <input {...register("phone")} placeholder={t("workerManagement.workers.form.phonePlaceholder")} className={INPUT_CLASS} />
            {errors.phone && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.phone.message}</p>}
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>{t("workerManagement.workers.form.email")}</label>
            <input {...register("email")} type="email" placeholder={t("workerManagement.workers.form.emailPlaceholder")} className={INPUT_CLASS} />
            {errors.email && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.email.message}</p>}
          </div>
          <div>
            <label className={LABEL_CLASS}>{t("workerManagement.workers.form.jobTitle")}</label>
            <input {...register("job_title")} placeholder={t("workerManagement.workers.form.jobTitlePlaceholder")} className={INPUT_CLASS} />
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>{t("workerManagement.workers.form.department")}</label>
            <input {...register("department")} placeholder={t("workerManagement.workers.form.departmentPlaceholder")} className={INPUT_CLASS} />
          </div>
          <div>
            <label className={LABEL_CLASS}>{t("workerManagement.workers.form.hireDate")}</label>
            <input {...register("hire_date")} type="date" className={INPUT_CLASS} />
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>{t("workerManagement.workers.form.baseSalary")}</label>
            <input {...register("base_salary")} type="number" min="0" step="0.01" placeholder={t("workerManagement.workers.form.baseSalaryPlaceholder")} className={INPUT_CLASS} />
            {errors.base_salary && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.base_salary.message}</p>}
          </div>
          <div>
            <label className={LABEL_CLASS}>{t("workerManagement.workers.form.status")}</label>
            <select {...register("status")} className={`${INPUT_CLASS} appearance-none cursor-pointer`}>
              {WORKER_STATUSES.map((s) => (
                <option key={s} value={s}>{t(`workerManagement.statuses.${s}`)}</option>
              ))}
            </select>
          </div>
        </div>
        <div>
          <label className={LABEL_CLASS}>{t("workerManagement.workers.form.notes")}</label>
          <textarea {...register("notes")} rows="2" placeholder={t("workerManagement.workers.form.notesPlaceholder")} className={INPUT_CLASS} />
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

function WorkerDetailsModal({ worker, onClose }) {
  const { t, i18n } = useTranslation();
  const locale = i18n.language === "ar" ? "ar-EG" : "en-US";

  if (!worker) return null;

  const formatCurrency = (value) =>
    new Intl.NumberFormat(locale, { maximumFractionDigits: 2 }).format(value || 0);

  const formatDate = (value) => {
    if (!value) return "—";
    try {
      return new Date(value).toLocaleDateString(locale, { year: "numeric", month: "short", day: "numeric" });
    } catch {
      return "—";
    }
  };

  const rows = [
    { label: t("workerManagement.workers.form.phone"), value: worker.phone || "—" },
    { label: t("workerManagement.workers.form.email"), value: worker.email || "—" },
    { label: t("workerManagement.workers.form.jobTitle"), value: worker.job_title || "—" },
    { label: t("workerManagement.workers.form.department"), value: worker.department || "—" },
    { label: t("workerManagement.workers.form.hireDate"), value: formatDate(worker.hire_date) },
    { label: t("workerManagement.workers.form.baseSalary"), value: formatCurrency(worker.base_salary) },
    { label: t("workerManagement.workers.columns.status"), value: t(`workerManagement.statuses.${worker.status}`) },
  ];

  return (
    <Modal isOpen={!!worker} onClose={onClose} title={t("workerManagement.workers.details.title")} maxWidth="max-w-lg">
      <div className="space-y-5">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-xl font-bold text-white shrink-0">
            {worker.full_name?.charAt(0)?.toUpperCase() || "?"}
          </div>
          <div className="min-w-0">
            <h3 className="text-[15px] font-bold text-surface-900 dark:text-surface-100 truncate">{worker.full_name}</h3>
            <Badge variant={worker.status === "active" ? "success" : "danger"}>{t(`workerManagement.statuses.${worker.status}`)}</Badge>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-1">
          {rows.map((row) => (
            <div key={row.label} className="flex items-center justify-between py-2 border-b border-surface-50">
              <span className="text-[13px] text-surface-500 dark:text-surface-400">{row.label}</span>
              <span className="text-[13px] font-semibold text-surface-800 dark:text-surface-100">{row.value}</span>
            </div>
          ))}
        </div>
        {worker.notes && (
          <div className="bg-surface-50 dark:bg-surface-700/40 rounded-xl p-4">
            <p className="text-[11px] font-semibold text-surface-400 dark:text-surface-500 uppercase tracking-wide mb-1">{t("workerManagement.workers.form.notes")}</p>
            <p className="text-[13px] text-surface-700 dark:text-surface-200 leading-relaxed">{worker.notes}</p>
          </div>
        )}
        <div className="flex justify-end pt-4 border-t border-surface-100 dark:border-surface-700/60">
          <button onClick={onClose} className={secondaryButtonClass}>{t("workerManagement.detailsClose")}</button>
        </div>
      </div>
    </Modal>
  );
}
