import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { categoryService } from "./api";
import { useAuth } from "../../shared/context/AuthContext";
import { useTranslation } from "react-i18next";
import { PageHeader } from "../../shared/components/PageHeader";
import { DataTable } from "../../shared/components/DataTable";
import { Modal } from "../../shared/components/Modal";
import { ConfirmDialog } from "../../shared/components/ConfirmDialog";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Plus, Pencil, Trash2, Search, FolderOpen } from "lucide-react";
import toast from "react-hot-toast";

const INPUT_CLASS = "w-full px-3.5 py-2.5 border border-surface-200 bg-surface-50 rounded-xl text-sm text-surface-800 placeholder:text-surface-300 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150";
const LABEL_CLASS = "block text-[13px] font-semibold text-surface-700 mb-1.5";

export default function CategoriesPage() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const canManage = ["admin", "manager"].includes(user?.role);
  const [search, setSearch] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const { data: categories = [], isLoading, error, refetch } = useQuery({
    queryKey: ["categories"],
    queryFn: async () => {
      const res = await categoryService.getAll();
      return res.data.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: (data) => categoryService.create(data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["categories"] }); toast.success(t("categories.toast.created")); setModalOpen(false); },
    onError: (err) => toast.error(err.response?.data?.message || t("categories.toast.createFailed")),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => categoryService.update(id, data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["categories"] }); toast.success(t("categories.toast.updated")); setModalOpen(false); setEditing(null); },
    onError: (err) => toast.error(err.response?.data?.message || t("categories.toast.updateFailed")),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => categoryService.delete(id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["categories"] }); toast.success(t("categories.toast.deleted")); setDeleteTarget(null); },
    onError: (err) => toast.error(err.response?.data?.message || t("categories.toast.deleteFailed")),
  });

  const filtered = categories.filter(
    (c) => c.name?.toLowerCase().includes(search.toLowerCase()) || c.description?.toLowerCase().includes(search.toLowerCase())
  );

  const columns = [
    {
      key: "name",
      label: t("categories.columns.name"),
      render: (val) => (
        <span className="text-[13px] font-semibold text-surface-800">{val}</span>
      ),
    },
    {
      key: "description",
      label: t("categories.columns.description"),
      render: (val) => <span className="text-surface-500">{val || "-"}</span>,
    },
    ...(canManage
      ? [
          {
            key: "id",
            label: t("categories.columns.actions"),
            render: (_, row) => (
              <div className="flex items-center gap-1">
                <button onClick={() => { setEditing(row); setModalOpen(true); }} className="p-2 text-surface-400 hover:text-primary-600 hover:bg-primary-50 rounded-xl transition-all duration-150" title={t("categories.edit")}>
                  <Pencil className="w-4 h-4" />
                </button>
                <button onClick={() => setDeleteTarget(row)} className="p-2 text-surface-400 hover:text-red-600 hover:bg-red-50 rounded-xl transition-all duration-150" title={t("categories.delete")}>
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
        title={t("categories.title")}
        description={t("categories.description")}
        actions={
          canManage && (
            <button onClick={() => { setEditing(null); setModalOpen(true); }} className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white text-[13px] font-semibold rounded-xl hover:from-primary-700 hover:to-primary-800 transition-all duration-150 shadow-sm shadow-primary-600/20">
              <Plus className="w-4 h-4" />
              {t("categories.newCategory")}
            </button>
          )
        }
      />

      <div className="mb-6 relative">
        <Search className="w-4 h-4 absolute start-3.5 top-1/2 -translate-y-1/2 text-surface-400 pointer-events-none" />
        <input type="text" placeholder={t("categories.searchPlaceholder")} value={search} onChange={(e) => setSearch(e.target.value)} className="w-full ps-10 pe-4 py-2.5 border border-surface-200 bg-white rounded-xl text-sm text-surface-800 placeholder:text-surface-300 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150 shadow-card" aria-label={t("categories.searchAriaLabel")} />
      </div>

      {filtered.length === 0 ? (
        <EmptyState icon={FolderOpen} title={t("categories.empty.noResultsTitle")} description={search ? t("categories.empty.noResultsDescription") : t("categories.empty.noCategoriesDescription")} action={!search && canManage && <button onClick={() => { setEditing(null); setModalOpen(true); }} className="px-4 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white text-[13px] font-semibold rounded-xl hover:from-primary-700 hover:to-primary-800 shadow-sm shadow-primary-600/20">{t("categories.empty.addCategory")}</button>} />
      ) : (
        <DataTable columns={columns} data={filtered} />
      )}

      <CategoryModal isOpen={modalOpen} onClose={() => { setModalOpen(false); setEditing(null); }} editing={editing} onSubmit={(data) => editing ? updateMutation.mutate({ id: editing.id, data }) : createMutation.mutate(data)} loading={createMutation.isPending || updateMutation.isPending} />

      <ConfirmDialog isOpen={!!deleteTarget} onClose={() => setDeleteTarget(null)} onConfirm={() => deleteMutation.mutate(deleteTarget.id)} title={t("categories.confirmDelete.title")} message={t("categories.confirmDelete.message", { name: deleteTarget?.name })} loading={deleteMutation.isPending} />
    </div>
  );
}

function CategoryModal({ isOpen, onClose, editing, onSubmit, loading }) {
  const { t } = useTranslation();

  const categorySchema = useMemo(() => z.object({
    name: z.string().min(1, t("categories.validation.nameRequired")),
    description: z.string().optional(),
  }), [t]);

  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: zodResolver(categorySchema),
    values: editing ? { name: editing.name, description: editing.description || "" } : { name: "", description: "" },
  });

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={editing ? t("categories.form.titleEdit") : t("categories.form.titleCreate")}>
      <form onSubmit={handleSubmit((data) => { onSubmit(data); reset(); })} className="space-y-5">
        <div>
          <label className={LABEL_CLASS}>{t("categories.form.name")}</label>
          <input {...register("name")} placeholder={t("categories.form.namePlaceholder")} className={INPUT_CLASS} />
          {errors.name && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.name.message}</p>}
        </div>
        <div>
          <label className={LABEL_CLASS}>{t("categories.form.description")}</label>
          <textarea {...register("description")} rows={3} placeholder={t("categories.form.descriptionPlaceholder")} className={`${INPUT_CLASS} resize-none`} />
          {errors.description && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.description.message}</p>}
        </div>
        <div className="flex justify-end gap-3 pt-5 border-t border-surface-100">
          <button type="button" onClick={onClose} className="px-4 py-2.5 text-[13px] font-semibold text-surface-600 bg-white border border-surface-200 rounded-xl hover:bg-surface-50 transition-all duration-150">{t("categories.form.cancel")}</button>
          <button type="submit" disabled={loading} className="px-4 py-2.5 text-[13px] font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl hover:from-primary-700 hover:to-primary-800 disabled:opacity-50 transition-all duration-150 shadow-sm shadow-primary-600/20">{loading ? t("categories.form.saving") : editing ? t("categories.form.update") : t("categories.form.create")}</button>
        </div>
      </form>
    </Modal>
  );
}
