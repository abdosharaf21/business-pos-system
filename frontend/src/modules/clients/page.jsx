import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { clientService } from "./api";
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
  labelClass,
  searchInputClass,
  primaryButtonClass,
  secondaryButtonClass,
  iconButtonClass,
  dangerIconButtonClass,
} from "../../shared/components/styles";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Plus, Pencil, Trash2, Search, Contact2 } from "lucide-react";
import toast from "react-hot-toast";

const CLIENT_STATUSES = ["lead", "prospect", "customer"];

export default function ClientsPage() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const canManage = ["admin", "manager"].includes(user?.role);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const { data: clients = [], isLoading, error, refetch } = useQuery({
    queryKey: ["clients"],
    queryFn: async () => (await clientService.getAll()).data.data,
  });

  const createMutation = useMutation({
    mutationFn: (data) => clientService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      queryClient.invalidateQueries({ queryKey: ["business-development-statistics"] });
      toast.success(t("business.clients.toast.created"));
      setModalOpen(false);
    },
    onError: (err) => toast.error(err.response?.data?.message || t("business.clients.toast.createFailed")),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => clientService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      toast.success(t("business.clients.toast.updated"));
      setModalOpen(false);
      setEditing(null);
    },
    onError: (err) => toast.error(err.response?.data?.message || t("business.clients.toast.updateFailed")),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => clientService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["clients"] });
      queryClient.invalidateQueries({ queryKey: ["business-development-statistics"] });
      toast.success(t("business.clients.toast.deleted"));
      setDeleteTarget(null);
    },
    onError: (err) => toast.error(err.response?.data?.message || t("business.clients.toast.deleteFailed")),
  });

  const filtered = clients.filter((c) => {
    const term = search.toLowerCase();
    const matchesSearch =
      !search ||
      c.company_name?.toLowerCase().includes(term) ||
      c.contact_person?.toLowerCase().includes(term) ||
      c.email?.toLowerCase().includes(term) ||
      c.phone?.toLowerCase().includes(term);
    const matchesStatus = !statusFilter || c.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const columns = [
    {
      key: "company_name",
      label: t("business.clients.columns.company"),
      render: (val) => (
        <span className="text-[13px] font-semibold text-surface-800 dark:text-surface-100">{val}</span>
      ),
    },
    {
      key: "contact_person",
      label: t("business.clients.columns.contactPerson"),
      render: (val) => <span className="text-[13px] text-surface-600 dark:text-surface-300">{val}</span>,
    },
    {
      key: "phone",
      label: t("business.clients.columns.phone"),
      render: (val) => <span className="text-[13px] text-surface-500 dark:text-surface-400">{val || "-"}</span>,
    },
    {
      key: "email",
      label: t("business.clients.columns.email"),
      render: (val) => <span className="text-[13px] text-surface-500 dark:text-surface-400">{val || "-"}</span>,
    },
    {
      key: "industry",
      label: t("business.clients.columns.industry"),
      render: (val) => <span className="text-[13px] text-surface-500 dark:text-surface-400">{val || "-"}</span>,
    },
    {
      key: "status",
      label: t("business.clients.columns.status"),
      render: (val) => (
        <Badge variant={statusBadge(val)}>{t(`business.clientStatus.${val}`)}</Badge>
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
        title={t("business.clients.title")}
        description={t("business.clients.description")}
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
              {t("business.clients.new")}
            </button>
          )
        }
      />

      <div className="mb-6 flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute start-3.5 top-1/2 -translate-y-1/2 text-surface-400 dark:text-surface-500 pointer-events-none" />
          <input
            type="text"
            placeholder={t("business.clients.searchPlaceholder")}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className={searchInputClass}
            aria-label={t("business.clients.searchPlaceholder")}
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className={`${inputClass} sm:w-44`}
          aria-label={t("business.clients.filters.status")}
        >
          <option value="">{t("business.clients.filters.allStatuses")}</option>
          {CLIENT_STATUSES.map((status) => (
            <option key={status} value={status}>
              {t(`business.clientStatus.${status}`)}
            </option>
          ))}
        </select>
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          icon={Contact2}
          title={t("business.clients.empty.title")}
          description={
            search || statusFilter
              ? t("business.clients.empty.noResults")
              : t("business.clients.empty.noClients")
          }
        />
      ) : (
        <DataTable columns={columns} data={filtered} />
      )}

      <ClientModal
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setEditing(null);
        }}
        editing={editing}
        onSubmit={(data) =>
          editing
            ? updateMutation.mutate({ id: editing.id, data })
            : createMutation.mutate(data)
        }
        loading={createMutation.isPending || updateMutation.isPending}
      />

      <ConfirmDialog
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => deleteMutation.mutate(deleteTarget.id)}
        title={t("business.clients.confirmDelete.title")}
        message={t("business.clients.confirmDelete.message", {
          name: deleteTarget?.company_name,
        })}
        loading={deleteMutation.isPending}
      />
    </div>
  );
}

function ClientModal({ isOpen, onClose, editing, onSubmit, loading }) {
  const { t } = useTranslation();
  const clientSchema = useMemo(
    () =>
      z.object({
        company_name: z.string().min(1, t("business.clients.validation.companyRequired")),
        contact_person: z.string().min(1, t("business.clients.validation.contactRequired")),
        phone: z.string().optional(),
        email: z.string().optional(),
        address: z.string().optional(),
        industry: z.string().optional(),
      }),
    [t]
  );

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(clientSchema),
    values: editing
      ? {
          company_name: editing.company_name || "",
          contact_person: editing.contact_person || "",
          phone: editing.phone || "",
          email: editing.email || "",
          address: editing.address || "",
          industry: editing.industry || "",
        }
      : { company_name: "", contact_person: "", phone: "", email: "", address: "", industry: "" },
  });

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={editing ? t("business.clients.form.editTitle") : t("business.clients.form.createTitle")}
    >
      <form
        onSubmit={handleSubmit((data) => onSubmit(data))}
        className="space-y-5"
      >
        <div>
          <label className={labelClass}>{t("business.clients.form.company")}</label>
          <input {...register("company_name")} className={inputClass} />
          {errors.company_name && (
            <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.company_name.message}</p>
          )}
        </div>
        <div>
          <label className={labelClass}>{t("business.clients.form.contactPerson")}</label>
          <input {...register("contact_person")} className={inputClass} />
          {errors.contact_person && (
            <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.contact_person.message}</p>
          )}
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className={labelClass}>{t("business.clients.form.phone")}</label>
            <input {...register("phone")} className={inputClass} />
          </div>
          <div>
            <label className={labelClass}>{t("business.clients.form.email")}</label>
            <input {...register("email")} type="email" className={inputClass} />
          </div>
        </div>
        <div>
          <label className={labelClass}>{t("business.clients.form.industry")}</label>
          <input {...register("industry")} className={inputClass} />
        </div>
        <div>
          <label className={labelClass}>{t("business.clients.form.address")}</label>
          <textarea {...register("address")} rows={2} className={`${inputClass} resize-none`} />
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
