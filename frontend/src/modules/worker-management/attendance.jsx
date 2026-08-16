import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { attendanceService, workerService, ATTENDANCE_STATUSES } from "./api";
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
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  Plus, Pencil, Trash2, CalendarCheck, Search,
} from "lucide-react";
import toast from "react-hot-toast";

const INPUT_CLASS = inputClass;
const LABEL_CLASS = labelClass;
const SELECT_CLASS = `${inputClass} appearance-none cursor-pointer`;

export default function AttendancePage() {
  const { t, i18n } = useTranslation();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const canManage = ["admin", "manager"].includes(user?.role);
  const locale = i18n.language === "ar" ? "ar-EG" : "en-US";
  const [workerFilter, setWorkerFilter] = useState("");
  const [month, setMonth] = useState("");
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
    queryKey: ["worker-management", "attendance", workerFilter, month],
    queryFn: async () => {
      const res = await attendanceService.getAll({
        worker_id: workerFilter || undefined,
        month: month || undefined,
      });
      return res.data.data;
    },
  });

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["worker-management"] });
  };

  const createMutation = useMutation({
    mutationFn: (data) => attendanceService.create(data),
    onSuccess: () => { invalidate(); toast.success(t("workerManagement.toast.attendanceCreated")); setModalOpen(false); },
    onError: (err) => toast.error(err.response?.data?.message || t("workerManagement.toast.attendanceCreateFailed")),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => attendanceService.update(id, data),
    onSuccess: () => { invalidate(); toast.success(t("workerManagement.toast.attendanceUpdated")); setModalOpen(false); setEditing(null); },
    onError: (err) => toast.error(err.response?.data?.message || t("workerManagement.toast.attendanceUpdateFailed")),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => attendanceService.delete(id),
    onSuccess: () => { invalidate(); toast.success(t("workerManagement.toast.attendanceDeleted")); setDeleteTarget(null); },
    onError: (err) => toast.error(err.response?.data?.message || t("workerManagement.toast.attendanceDeleteFailed")),
  });

  const formatDate = (value) => {
    if (!value) return "—";
    try {
      return new Date(value).toLocaleDateString(locale, { year: "numeric", month: "short", day: "numeric" });
    } catch {
      return "—";
    }
  };

  const columns = [
    {
      key: "worker_name",
      label: t("workerManagement.attendance.columns.worker"),
      render: (val) => (
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-[11px] font-bold text-white shrink-0">
            {val?.charAt(0)?.toUpperCase() || "?"}
          </div>
          <span className="text-[13px] font-semibold text-surface-800 dark:text-surface-100 truncate">{val}</span>
        </div>
      ),
    },
    {
      key: "attendance_date",
      label: t("workerManagement.attendance.columns.date"),
      render: (val) => <span className="text-[13px] text-surface-600 dark:text-surface-300">{formatDate(val)}</span>,
    },
    {
      key: "status",
      label: t("workerManagement.attendance.columns.status"),
      render: (val) => <Badge variant={val === "absent" ? "danger" : val === "late" ? "warning" : val === "leave" ? "info" : val === "half_day" ? "warning" : "success"}>{t(`workerManagement.statuses.${val}`)}</Badge>,
    },
    {
      key: "check_in",
      label: t("workerManagement.attendance.columns.checkIn"),
      render: (val) => <span className="text-[12px] text-surface-500 dark:text-surface-400 tabular-nums">{val ? val.slice(0, 5) : "—"}</span>,
    },
    {
      key: "check_out",
      label: t("workerManagement.attendance.columns.checkOut"),
      render: (val) => <span className="text-[12px] text-surface-500 dark:text-surface-400 tabular-nums">{val ? val.slice(0, 5) : "—"}</span>,
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
        title={t("workerManagement.attendance.title")}
        description={t("workerManagement.attendance.subtitle")}
        actions={
          canManage && (
            <button onClick={() => { setEditing(null); setModalOpen(true); }} className={primaryButtonClass}>
              <Plus className="w-4 h-4" />
              {t("workerManagement.attendance.newRecord")}
            </button>
          )
        }
      />

      <div className="grid grid-cols-1 md:grid-cols-[200px_1fr] gap-3 mb-6">
        <div>
          <select
            value={workerFilter}
            onChange={(e) => setWorkerFilter(e.target.value)}
            className={SELECT_CLASS}
            aria-label={t("workerManagement.attendance.filterWorker")}
          >
            <option value="">{t("workerManagement.attendance.allWorkers")}</option>
            {workers.map((w) => (
              <option key={w.id} value={w.id}>{w.full_name}</option>
            ))}
          </select>
        </div>
        <div className="relative">
          <Search className="w-4 h-4 absolute start-3.5 top-1/2 -translate-y-1/2 text-surface-400 dark:text-surface-500 pointer-events-none" />
          <input
            type="month"
            value={month}
            onChange={(e) => setMonth(e.target.value)}
            className={INPUT_CLASS}
            aria-label={t("workerManagement.attendance.filterMonth")}
          />
        </div>
      </div>

      {records.length === 0 ? (
        <EmptyState
          icon={CalendarCheck}
          title={t("workerManagement.attendance.empty.title")}
          description={t("workerManagement.attendance.empty.description")}
          action={!workerFilter && !month && canManage && (
            <button onClick={() => { setEditing(null); setModalOpen(true); }} className={primaryButtonClass}>
              {t("workerManagement.attendance.empty.addFirst")}
            </button>
          )}
        />
      ) : (
        <DataTable columns={columns} data={records} />
      )}

      <AttendanceModal
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
        title={t("workerManagement.attendance.confirmDelete.title")}
        message={t("workerManagement.attendance.confirmDelete.message", { worker: deleteTarget?.worker_name, date: formatDate(deleteTarget?.attendance_date) })}
        loading={deleteMutation.isPending}
      />
    </div>
  );
}

function AttendanceModal({ isOpen, onClose, editing, workers, onSubmit, loading }) {
  const { t } = useTranslation();

  const schema = useMemo(() => z.object({
    worker_id: z.union([z.coerce.number().min(1, t("workerManagement.attendance.validation.workerRequired")), z.string().min(1, t("workerManagement.attendance.validation.workerRequired"))]),
    attendance_date: z.string().min(1, t("workerManagement.attendance.validation.dateRequired")),
    status: z.string().min(1),
    check_in: z.string().optional(),
    check_out: z.string().optional(),
    notes: z.string().optional(),
  }), [t]);

  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: zodResolver(schema),
    values: editing ? {
      worker_id: String(editing.worker_id || ""),
      attendance_date: editing.attendance_date || "",
      status: editing.status || "present",
      check_in: editing.check_in || "",
      check_out: editing.check_out || "",
      notes: editing.notes || "",
    } : {
      worker_id: "",
      attendance_date: new Date().toISOString().slice(0, 10),
      status: "present",
      check_in: "",
      check_out: "",
      notes: "",
    },
  });

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={editing ? t("workerManagement.attendance.form.titleEdit") : t("workerManagement.attendance.form.titleCreate")}>
      <form onSubmit={handleSubmit((data) => { onSubmit(data); reset(); })} className="space-y-5">
        <div>
          <label className={LABEL_CLASS}>{t("workerManagement.attendance.form.worker")}</label>
          <select {...register("worker_id")} className={SELECT_CLASS}>
            <option value="">{t("workerManagement.attendance.form.workerPlaceholder")}</option>
            {workers.map((w) => (
              <option key={w.id} value={w.id}>{w.full_name}</option>
            ))}
          </select>
          {errors.worker_id && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.worker_id.message}</p>}
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>{t("workerManagement.attendance.form.date")}</label>
            <input {...register("attendance_date")} type="date" className={INPUT_CLASS} />
            {errors.attendance_date && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.attendance_date.message}</p>}
          </div>
          <div>
            <label className={LABEL_CLASS}>{t("workerManagement.attendance.form.status")}</label>
            <select {...register("status")} className={SELECT_CLASS}>
              {ATTENDANCE_STATUSES.map((s) => (
                <option key={s} value={s}>{t(`workerManagement.statuses.${s}`)}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>{t("workerManagement.attendance.form.checkIn")}</label>
            <input {...register("check_in")} type="time" className={INPUT_CLASS} />
          </div>
          <div>
            <label className={LABEL_CLASS}>{t("workerManagement.attendance.form.checkOut")}</label>
            <input {...register("check_out")} type="time" className={INPUT_CLASS} />
          </div>
        </div>
        <div>
          <label className={LABEL_CLASS}>{t("workerManagement.attendance.form.notes")}</label>
          <input {...register("notes")} placeholder={t("workerManagement.attendance.form.notesPlaceholder")} className={INPUT_CLASS} />
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
