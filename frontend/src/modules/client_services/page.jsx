import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { clientServiceAssignmentService, ASSIGNMENT_STATUSES } from "./api";
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
  primaryButtonClass,
  secondaryButtonClass,
  iconButtonClass,
  dangerIconButtonClass,
  cardClass,
} from "../../shared/components/styles";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Plus, Pencil, Trash2, Link2 } from "lucide-react";
import toast from "react-hot-toast";

export default function ClientServicesPage() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const canManage = ["admin", "manager"].includes(user?.role);
  const [selectedClientId, setSelectedClientId] = useState("");
  const [assignOpen, setAssignOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const { data: clients = [], isLoading: clientsLoading } = useQuery({
    queryKey: ["clients"],
    queryFn: async () => (await clientService.getAll()).data.data,
  });

  const assignmentsQuery = useQuery({
    queryKey: ["client-services", selectedClientId],
    queryFn: async () =>
      (await clientServiceAssignmentService.getByClient(selectedClientId)).data.data,
    enabled: !!selectedClientId,
  });

  const deleteMutation = useMutation({
    mutationFn: (assignmentId) => clientServiceAssignmentService.delete(assignmentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["client-services"] });
      toast.success(t("business.clientServices.toast.deleted"));
      setDeleteTarget(null);
    },
    onError: (err) =>
      toast.error(err.response?.data?.message || t("business.clientServices.toast.deleteFailed")),
  });

  const assignments = assignmentsQuery.data || [];
  const selectedClient = clients.find((c) => c.id === Number(selectedClientId));

  const columns = [
    {
      key: "service_name",
      label: t("business.clientServices.columns.service"),
      render: (val) => (
        <span className="text-[13px] font-semibold text-surface-800 dark:text-surface-100">{val || "-"}</span>
      ),
    },
    {
      key: "price",
      label: t("business.clientServices.columns.price"),
      render: (val) => (
        <span className="numeric-value text-[13px] text-surface-600 dark:text-surface-300">
          {val != null ? Number(val).toFixed(2) : "-"}
        </span>
      ),
    },
    {
      key: "status",
      label: t("business.clientServices.columns.status"),
      render: (val) => (
        <Badge variant={statusBadge(val)}>{t(`business.assignmentStatus.${val}`)}</Badge>
      ),
    },
    {
      key: "notes",
      label: t("business.clientServices.columns.notes"),
      render: (val) => (
        <span className="text-[13px] text-surface-500 dark:text-surface-400 line-clamp-1 max-w-xs">{val || "-"}</span>
      ),
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
                    setAssignOpen(true);
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

  if (clientsLoading) return <LoadingSpinner />;

  return (
    <div>
      <PageHeader
        title={t("business.clientServices.title")}
        description={t("business.clientServices.description")}
        actions={
          canManage &&
          selectedClientId && (
            <button
              onClick={() => {
                setEditing(null);
                setAssignOpen(true);
              }}
              className={primaryButtonClass}
            >
              <Plus className="w-4 h-4" />
              {t("business.clientServices.assignNew")}
            </button>
          )
        }
      />

      <div className={`${cardClass} p-5 mb-6`}>
        <label className={labelClass}>{t("business.clientServices.selectClient")}</label>
        <select
          value={selectedClientId}
          onChange={(e) => setSelectedClientId(e.target.value)}
          className={`${selectClass} max-w-md`}
          aria-label={t("business.clientServices.selectClient")}
        >
          <option value="">{t("business.clientServices.chooseClient")}</option>
          {clients.map((c) => (
            <option key={c.id} value={c.id}>
              {c.company_name} — {c.contact_person}
            </option>
          ))}
        </select>
      </div>

      {!selectedClientId ? (
        <EmptyState
          icon={Link2}
          title={t("business.clientServices.empty.title")}
          description={t("business.clientServices.empty.pickClient")}
        />
      ) : assignmentsQuery.isLoading ? (
        <LoadingSpinner />
      ) : assignmentsQuery.error ? (
        <ErrorDisplay
          message={assignmentsQuery.error.response?.data?.message || assignmentsQuery.error.message}
          onRetry={assignmentsQuery.refetch}
        />
      ) : assignments.length === 0 ? (
        <EmptyState
          icon={Link2}
          compact
          title={t("business.clientServices.empty.noAssignments", {
            name: selectedClient?.company_name || "",
          })}
        />
      ) : (
        <DataTable columns={columns} data={assignments} />
      )}

      <AssignServiceModal
        isOpen={assignOpen}
        onClose={() => {
          setAssignOpen(false);
          setEditing(null);
        }}
        editing={editing}
        clientId={selectedClientId}
        onSubmit={(payload) => {
          if (editing) {
            return clientServiceAssignmentService.update(editing.id, payload);
          }
          return clientServiceAssignmentService.assign(
            selectedClientId,
            payload.service_id,
            payload
          );
        }}
      />

      <ConfirmDialog
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => deleteMutation.mutate(deleteTarget.id)}
        title={t("business.clientServices.confirmDelete.title")}
        message={t("business.clientServices.confirmDelete.message", {
          name: deleteTarget?.service_name || "",
        })}
        loading={deleteMutation.isPending}
      />
    </div>
  );
}

function AssignServiceModal({ isOpen, onClose, editing, clientId, onSubmit }) {
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const { data: services = [] } = useQuery({
    queryKey: ["services"],
    queryFn: async () => (await serviceService.getAll()).data.data,
    enabled: isOpen,
  });

  const schema = useMemo(
    () =>
      z.object({
        service_id:
          !editing && clientId
            ? z.string().min(1, t("business.clientServices.validation.serviceRequired"))
            : z.any(),
        price: z.coerce.number().min(0, t("business.clientServices.validation.priceInvalid")),
        status: z.enum(ASSIGNMENT_STATUSES),
        notes: z.string().optional(),
      }),
    [t, editing, clientId]
  );

  const defaults = useMemo(
    () =>
      editing
        ? {
            service_id: String(editing.service_id ?? ""),
            price: editing.price ?? "",
            status: editing.status || "pending",
            notes: editing.notes || "",
          }
        : { service_id: "", price: "", status: "pending", notes: "" },
    [editing]
  );

  const {
    register,
    handleSubmit,
    setValue,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(schema),
    values: defaults,
  });

  const mutation = useMutation({
    mutationFn: onSubmit,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["client-services"] });
      toast.success(
        editing
          ? t("business.clientServices.toast.updated")
          : t("business.clientServices.toast.assigned")
      );
      onClose();
    },
    onError: (err) =>
      toast.error(
        err.response?.data?.message ||
          (editing
            ? t("business.clientServices.toast.updateFailed")
            : t("business.clientServices.toast.assignFailed"))
      ),
  });

  const handleServiceChange = (event) => {
    const id = event.target.value;
    setValue("service_id", id, { shouldValidate: true });
    const svc = services.find((s) => s.id === Number(id));
    if (svc) setValue("price", svc.price ?? "");
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={
        editing
          ? t("business.clientServices.form.editTitle")
          : t("business.clientServices.form.assignTitle")
      }
    >
      <form onSubmit={handleSubmit((data) => mutation.mutate(data))} className="space-y-5">
        {editing ? (
          <div>
            <label className={labelClass}>{t("business.clientServices.form.service")}</label>
            <input
              readOnly
              value={
                services.find((s) => s.id === Number(defaults.service_id))?.name ||
                editing.service_name ||
                "-"
              }
              className={`${inputClass} opacity-70 cursor-not-allowed`}
            />
          </div>
        ) : (
          <div>
            <label className={labelClass}>{t("business.clientServices.form.service")}</label>
            <select
              {...register("service_id")}
              onChange={handleServiceChange}
              className={selectClass}
            >
              <option value="">{t("business.clientServices.form.chooseService")}</option>
              {services.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name} ({Number(s.price).toFixed(2)})
                </option>
              ))}
            </select>
            {errors.service_id && (
              <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.service_id.message}</p>
            )}
          </div>
        )}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className={labelClass}>{t("business.clientServices.form.price")}</label>
            <input {...register("price")} type="number" step="0.01" min="0" className={inputClass} />
            {errors.price && (
              <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.price.message}</p>
            )}
          </div>
          <div>
            <label className={labelClass}>{t("business.clientServices.form.status")}</label>
            <select {...register("status")} className={selectClass}>
              {ASSIGNMENT_STATUSES.map((status) => (
                <option key={status} value={status}>
                  {t(`business.assignmentStatus.${status}`)}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div>
          <label className={labelClass}>{t("business.clientServices.form.notes")}</label>
          <textarea {...register("notes")} rows={2} className={`${inputClass} resize-none`} />
        </div>
        <div className="flex justify-end gap-3 pt-5 border-t border-surface-100 dark:border-surface-700/60">
          <button type="button" onClick={onClose} className={secondaryButtonClass}>
            {t("common.actions.cancel")}
          </button>
          <button type="submit" disabled={mutation.isPending} className={primaryButtonClass}>
            {mutation.isPending
              ? t("common.actions.saving")
              : editing
                ? t("common.actions.update")
                : t("business.clientServices.form.assignAction")}
          </button>
        </div>
      </form>
    </Modal>
  );
}

