import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { customerService } from "./api";
import { useAuth } from "../../shared/context/AuthContext";
import { PageHeader } from "../../shared/components/PageHeader";
import { DataTable } from "../../shared/components/DataTable";
import { Modal } from "../../shared/components/Modal";
import { ConfirmDialog } from "../../shared/components/ConfirmDialog";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
import { inputClass, labelClass, searchInputClass, primaryButtonClass, secondaryButtonClass, iconButtonClass } from "../../shared/components/styles";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Plus, Pencil, Trash2, Search, Users } from "lucide-react";
import toast from "react-hot-toast";

const INPUT_CLASS = inputClass;
const LABEL_CLASS = labelClass;

export default function CustomersPage() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const canManage = ["admin", "manager"].includes(user?.role);
  const [search, setSearch] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const { data: customers = [], isLoading, error, refetch } = useQuery({
    queryKey: ["customers"],
    queryFn: async () => {
      const res = await customerService.getAll();
      return res.data.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: (data) => customerService.create(data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["customers"] }); toast.success(t("customers.toast.created")); setModalOpen(false); },
    onError: (err) => toast.error(err.response?.data?.message || t("customers.toast.createFailed")),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => customerService.update(id, data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["customers"] }); toast.success(t("customers.toast.updated")); setModalOpen(false); setEditing(null); },
    onError: (err) => toast.error(err.response?.data?.message || t("customers.toast.updateFailed")),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => customerService.delete(id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["customers"] }); toast.success(t("customers.toast.deleted")); setDeleteTarget(null); },
    onError: (err) => toast.error(err.response?.data?.message || t("customers.toast.deleteFailed")),
  });

  const filtered = customers.filter((c) => {
    const term = search.toLowerCase();
    return !search ||
      c.name?.toLowerCase().includes(term) ||
      c.phone?.toLowerCase().includes(term);
  });

  const columns = [
    {
      key: "name",
      label: t("customers.columns.name"),
      render: (val) => <span className="text-[13px] font-semibold text-surface-800 dark:text-surface-100">{val}</span>,
    },
    {
      key: "phone",
      label: t("customers.columns.phone"),
      render: (val) => <span className="text-[13px] text-surface-600 dark:text-surface-300">{val || "-"}</span>,
    },
    {
      key: "email",
      label: t("customers.columns.email"),
      render: (val) => <span className="text-[13px] text-surface-500 dark:text-surface-400">{val || "-"}</span>,
    },
    {
      key: "address",
      label: t("customers.columns.address"),
      render: (val) => <span className="text-[13px] text-surface-500 dark:text-surface-400 truncate max-w-[200px] inline-block">{val || "-"}</span>,
    },
    ...(canManage
      ? [
          {
            key: "id",
            label: t("customers.columns.actions"),
            render: (_, row) => (
              <div className="flex items-center gap-1">
                <button onClick={() => { setEditing(row); setModalOpen(true); }} className={iconButtonClass} title={t("customers.edit")}>
                  <Pencil className="w-4 h-4" />
                </button>
                <button onClick={() => setDeleteTarget(row)} className={dangerIconButtonClass} title={t("customers.delete")}>
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ),
          },
        ]
      : []),
  ];

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay message={error.response?.data?.message || error.message} onRetry={refetch} />;

  return (
    <div>
      <PageHeader
        title={t("customers.title")}
        description={t("customers.description")}
        actions={
          canManage && (
            <button onClick={() => { setEditing(null); setModalOpen(true); }} className={primaryButtonClass}>
              <Plus className="w-4 h-4" />
              {t("customers.newCustomer")}
            </button>
          )
        }
      />

      <div className="mb-6 relative">
        <Search className="w-4 h-4 absolute start-3.5 top-1/2 -translate-y-1/2 text-surface-400 dark:text-surface-500 pointer-events-none" />
        <input type="text" placeholder={t("customers.searchPlaceholder")} value={search} onChange={(e) => setSearch(e.target.value)} className={searchInputClass} aria-label={t("customers.searchAriaLabel")} />
      </div>

      {filtered.length === 0 ? (
        <EmptyState icon={Users} title={t("customers.empty.noResultsTitle")} description={search ? t("customers.empty.noResultsDescription") : t("customers.empty.noCustomersDescription")} action={!search && canManage && <button onClick={() => { setEditing(null); setModalOpen(true); }} className={primaryButtonClass}>{t("customers.empty.addCustomer")}</button>} />
      ) : (
        <DataTable columns={columns} data={filtered} />
      )}

      <CustomerModal isOpen={modalOpen} onClose={() => { setModalOpen(false); setEditing(null); }} editing={editing} onSubmit={(data) => editing ? updateMutation.mutate({ id: editing.id, data }) : createMutation.mutate(data)} loading={createMutation.isPending || updateMutation.isPending} />

      <ConfirmDialog isOpen={!!deleteTarget} onClose={() => setDeleteTarget(null)} onConfirm={() => deleteMutation.mutate(deleteTarget.id)} title={t("customers.confirmDelete.title")} message={t("customers.confirmDelete.message", { name: deleteTarget?.name })} loading={deleteMutation.isPending} />
    </div>
  );
}

function CustomerModal({ isOpen, onClose, editing, onSubmit, loading }) {
  const { t } = useTranslation();
  const customerSchema = useMemo(() => z.object({
    name: z.string().min(1, t("customers.validation.nameRequired")),
    phone: z.string().min(1, t("customers.validation.phoneRequired")),
    email: z.string().optional(),
    address: z.string().optional(),
  }), [t]);

  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: zodResolver(customerSchema),
    values: editing ? {
      name: editing.name || "",
      phone: editing.phone || "",
      email: editing.email || "",
      address: editing.address || "",
    } : {
      name: "",
      phone: "",
      email: "",
      address: "",
    },
  });

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={editing ? t("customers.form.titleEdit") : t("customers.form.titleCreate")}>
      <form onSubmit={handleSubmit((data) => { onSubmit(data); reset(); })} className="space-y-5">
        <div>
          <label className={LABEL_CLASS}>{t("customers.form.name")}</label>
          <input {...register("name")} placeholder={t("customers.form.namePlaceholder")} className={INPUT_CLASS} />
          {errors.name && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.name.message}</p>}
        </div>
        <div>
          <label className={LABEL_CLASS}>{t("customers.form.phone")}</label>
          <input {...register("phone")} placeholder={t("customers.form.phonePlaceholder")} className={INPUT_CLASS} />
          {errors.phone && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.phone.message}</p>}
        </div>
        <div>
          <label className={LABEL_CLASS}>{t("customers.form.email")}</label>
          <input {...register("email")} type="email" placeholder={t("customers.form.emailPlaceholder")} className={INPUT_CLASS} />
          {errors.email && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.email.message}</p>}
        </div>
        <div>
          <label className={LABEL_CLASS}>{t("customers.form.address")}</label>
          <textarea {...register("address")} rows={2} placeholder={t("customers.form.addressPlaceholder")} className={`${INPUT_CLASS} resize-none`} />
          {errors.address && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.address.message}</p>}
        </div>
        <div className="flex justify-end gap-3 pt-5 border-t border-surface-100 dark:border-surface-700/60">
          <button type="button" onClick={onClose} className={secondaryButtonClass}>{t("customers.form.cancel")}</button>
          <button type="submit" disabled={loading} className={primaryButtonClass}>{loading ? t("customers.form.saving") : editing ? t("customers.form.update") : t("customers.form.create")}</button>
        </div>
      </form>
    </Modal>
  );
}
