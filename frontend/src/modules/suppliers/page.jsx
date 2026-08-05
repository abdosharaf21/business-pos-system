import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { supplierService } from "./api";
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
import { Plus, Pencil, Trash2, Search, Truck } from "lucide-react";
import toast from "react-hot-toast";

const INPUT_CLASS = inputClass;
const LABEL_CLASS = labelClass;

export default function SuppliersPage() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const canManage = ["admin", "manager"].includes(user?.role);
  const [search, setSearch] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const { data: suppliers = [], isLoading, error, refetch } = useQuery({
    queryKey: ["suppliers"],
    queryFn: async () => {
      const res = await supplierService.getAll();
      return res.data.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: (data) => supplierService.create(data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["suppliers"] }); toast.success(t("suppliers.toast.created")); setModalOpen(false); },
    onError: (err) => toast.error(err.response?.data?.message || t("suppliers.toast.createFailed")),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => supplierService.update(id, data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["suppliers"] }); toast.success(t("suppliers.toast.updated")); setModalOpen(false); setEditing(null); },
    onError: (err) => toast.error(err.response?.data?.message || t("suppliers.toast.updateFailed")),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => supplierService.delete(id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["suppliers"] }); toast.success(t("suppliers.toast.deleted")); setDeleteTarget(null); },
    onError: (err) => toast.error(err.response?.data?.message || t("suppliers.toast.deleteFailed")),
  });

  const filtered = suppliers.filter((s) => {
    const term = search.toLowerCase();
    return !search ||
      s.name?.toLowerCase().includes(term) ||
      s.phone?.toLowerCase().includes(term);
  });

  const columns = [
    {
      key: "name",
      label: t("suppliers.columns.name"),
      render: (val) => <span className="text-[13px] font-semibold text-surface-800 dark:text-surface-100">{val}</span>,
    },
    {
      key: "phone",
      label: t("suppliers.columns.phone"),
      render: (val) => <span className="text-[13px] text-surface-600 dark:text-surface-300">{val || "-"}</span>,
    },
    {
      key: "email",
      label: t("suppliers.columns.email"),
      render: (val) => <span className="text-[13px] text-surface-500 dark:text-surface-400">{val || "-"}</span>,
    },
    {
      key: "address",
      label: t("suppliers.columns.address"),
      render: (val) => <span className="text-[13px] text-surface-500 dark:text-surface-400 truncate max-w-[200px] inline-block">{val || "-"}</span>,
    },
    ...(canManage
      ? [
          {
            key: "id",
            label: t("suppliers.columns.actions"),
            render: (_, row) => (
              <div className="flex items-center gap-1">
                <button onClick={() => { setEditing(row); setModalOpen(true); }} className={iconButtonClass} title={t("suppliers.edit")}>
                  <Pencil className="w-4 h-4" />
                </button>
                <button onClick={() => setDeleteTarget(row)} className={dangerIconButtonClass} title={t("suppliers.delete")}>
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
        title={t("suppliers.title")}
        description={t("suppliers.description")}
        actions={
          canManage && (
            <button onClick={() => { setEditing(null); setModalOpen(true); }} className={primaryButtonClass}>
              <Plus className="w-4 h-4" />
              {t("suppliers.newSupplier")}
            </button>
          )
        }
      />

      <div className="mb-6 relative">
        <Search className="w-4 h-4 absolute start-3.5 top-1/2 -translate-y-1/2 text-surface-400 dark:text-surface-500 pointer-events-none" />
        <input type="text" placeholder={t("suppliers.searchPlaceholder")} value={search} onChange={(e) => setSearch(e.target.value)} className={searchInputClass} aria-label={t("suppliers.searchAriaLabel")} />
      </div>

      {filtered.length === 0 ? (
        <EmptyState icon={Truck} title={t("suppliers.empty.noResultsTitle")} description={search ? t("suppliers.empty.noResultsDescription") : t("suppliers.empty.noSuppliersDescription")} action={!search && canManage && <button onClick={() => { setEditing(null); setModalOpen(true); }} className={primaryButtonClass}>{t("suppliers.empty.addSupplier")}</button>} />
      ) : (
        <DataTable columns={columns} data={filtered} />
      )}

      <SupplierModal isOpen={modalOpen} onClose={() => { setModalOpen(false); setEditing(null); }} editing={editing} onSubmit={(data) => editing ? updateMutation.mutate({ id: editing.id, data }) : createMutation.mutate(data)} loading={createMutation.isPending || updateMutation.isPending} />

      <ConfirmDialog isOpen={!!deleteTarget} onClose={() => setDeleteTarget(null)} onConfirm={() => deleteMutation.mutate(deleteTarget.id)} title={t("suppliers.confirmDelete.title")} message={t("suppliers.confirmDelete.message", { name: deleteTarget?.name })} loading={deleteMutation.isPending} />
    </div>
  );
}

function SupplierModal({ isOpen, onClose, editing, onSubmit, loading }) {
  const { t } = useTranslation();
  const supplierSchema = useMemo(() => z.object({
    name: z.string().min(1, t("suppliers.validation.nameRequired")),
    phone: z.string().min(1, t("suppliers.validation.phoneRequired")),
    email: z.string().optional(),
    address: z.string().optional(),
  }), [t]);

  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: zodResolver(supplierSchema),
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
    <Modal isOpen={isOpen} onClose={onClose} title={editing ? t("suppliers.form.titleEdit") : t("suppliers.form.titleCreate")}>
      <form onSubmit={handleSubmit((data) => { onSubmit(data); reset(); })} className="space-y-5">
        <div>
          <label className={LABEL_CLASS}>{t("suppliers.form.name")}</label>
          <input {...register("name")} placeholder={t("suppliers.form.namePlaceholder")} className={INPUT_CLASS} />
          {errors.name && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.name.message}</p>}
        </div>
        <div>
          <label className={LABEL_CLASS}>{t("suppliers.form.phone")}</label>
          <input {...register("phone")} placeholder={t("suppliers.form.phonePlaceholder")} className={INPUT_CLASS} />
          {errors.phone && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.phone.message}</p>}
        </div>
        <div>
          <label className={LABEL_CLASS}>{t("suppliers.form.email")}</label>
          <input {...register("email")} type="email" placeholder={t("suppliers.form.emailPlaceholder")} className={INPUT_CLASS} />
          {errors.email && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.email.message}</p>}
        </div>
        <div>
          <label className={LABEL_CLASS}>{t("suppliers.form.address")}</label>
          <textarea {...register("address")} rows={2} placeholder={t("suppliers.form.addressPlaceholder")} className={`${INPUT_CLASS} resize-none`} />
          {errors.address && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.address.message}</p>}
        </div>
        <div className="flex justify-end gap-3 pt-5 border-t border-surface-100 dark:border-surface-700/60">
          <button type="button" onClick={onClose} className={secondaryButtonClass}>{t("suppliers.form.cancel")}</button>
          <button type="submit" disabled={loading} className={primaryButtonClass}>{loading ? t("suppliers.form.saving") : editing ? t("suppliers.form.update") : t("suppliers.form.create")}</button>
        </div>
      </form>
    </Modal>
  );
}
