import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { serviceCategoryService as serviceCategoriesService } from "./api";
import { useAuth } from "../../shared/context/AuthContext";
import { PageHeader } from "../../shared/components/PageHeader";
import { DataTable } from "../../shared/components/DataTable";
import { Modal } from "../../shared/components/Modal";
import { ConfirmDialog } from "../../shared/components/ConfirmDialog";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
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
import { Plus, Pencil, Trash2, Search, FolderTree } from "lucide-react";
import toast from "react-hot-toast";

export default function ServiceCategoriesPage() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const canManage = ["admin", "manager"].includes(user?.role);
  const [search, setSearch] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const { data: categories = [], isLoading, error, refetch } = useQuery({
    queryKey: ["service-categories"],
    queryFn: async () => (await serviceCategoriesService.getAll()).data.data,
  });

  const createMutation = useMutation({
    mutationFn: (data) => serviceCategoriesService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["service-categories"] });
      queryClient.invalidateQueries({ queryKey: ["services"] });
      toast.success(t("business.serviceCategories.toast.created"));
      setModalOpen(false);
    },
    onError: (err) =>
      toast.error(err.response?.data?.message || t("business.serviceCategories.toast.createFailed")),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => serviceCategoriesService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["service-categories"] });
      queryClient.invalidateQueries({ queryKey: ["services"] });
      toast.success(t("business.serviceCategories.toast.updated"));
      setModalOpen(false);
      setEditing(null);
    },
    onError: (err) =>
      toast.error(err.response?.data?.message || t("business.serviceCategories.toast.updateFailed")),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => serviceCategoriesService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["service-categories"] });
      queryClient.invalidateQueries({ queryKey: ["services"] });
      toast.success(t("business.serviceCategories.toast.deleted"));
      setDeleteTarget(null);
    },
    onError: (err) =>
      toast.error(err.response?.data?.message || t("business.serviceCategories.toast.deleteFailed")),
  });

  const filtered = categories.filter((c) => {
    const term = search.toLowerCase();
    return (
      !search ||
      c.name?.toLowerCase().includes(term) ||
      c.description?.toLowerCase().includes(term)
    );
  });

  const columns = [
    {
      key: "name",
      label: t("business.serviceCategories.columns.name"),
      render: (val) => (
        <span className="text-[13px] font-semibold text-surface-800 dark:text-surface-100">{val}</span>
      ),
    },
    {
      key: "description",
      label: t("business.serviceCategories.columns.description"),
      render: (val) => (
        <span className="text-[13px] text-surface-500 dark:text-surface-400 line-clamp-1 max-w-md">{val || "-"}</span>
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
        title={t("business.serviceCategories.title")}
        description={t("business.serviceCategories.description")}
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
              {t("business.serviceCategories.new")}
            </button>
          )
        }
      />

      <div className="mb-6">
        <div className="relative">
          <Search className="w-4 h-4 absolute start-3.5 top-1/2 -translate-y-1/2 text-surface-400 dark:text-surface-500 pointer-events-none" />
          <input
            type="text"
            placeholder={t("business.serviceCategories.searchPlaceholder")}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className={searchInputClass}
            aria-label={t("business.serviceCategories.searchPlaceholder")}
          />
        </div>
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          icon={FolderTree}
          title={t("business.serviceCategories.empty.title")}
          description={
            search ? t("business.serviceCategories.empty.noResults") : t("business.serviceCategories.empty.noCategories")
          }
        />
      ) : (
        <DataTable columns={columns} data={filtered} />
      )}

      <CategoryModal
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
        title={t("business.serviceCategories.confirmDelete.title")}
        message={t("business.serviceCategories.confirmDelete.message", { name: deleteTarget?.name })}
        loading={deleteMutation.isPending}
      />
    </div>
  );
}

function CategoryModal({ isOpen, onClose, editing, onSubmit, loading }) {
  const { t } = useTranslation();
  const schema = useMemo(
    () =>
      z.object({
        name: z.string().min(1, t("business.serviceCategories.validation.nameRequired")),
        description: z.string().optional(),
      }),
    [t]
  );

  const defaults = useMemo(
    () =>
      editing
        ? { name: editing.name || "", description: editing.description || "" }
        : { name: "", description: "" },
    [editing]
  );

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(schema),
    values: defaults,
  });

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      maxWidth="max-w-md"
      title={
        editing
          ? t("business.serviceCategories.form.editTitle")
          : t("business.serviceCategories.form.createTitle")
      }
    >
      <form onSubmit={handleSubmit((data) => onSubmit(data))} className="space-y-5">
        <div>
          <label className={labelClass}>{t("business.serviceCategories.form.name")}</label>
          <input {...register("name")} className={inputClass} />
          {errors.name && (
            <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.name.message}</p>
          )}
        </div>
        <div>
          <label className={labelClass}>{t("business.serviceCategories.form.description")}</label>
          <textarea {...register("description")} rows={2} className={`${inputClass} resize-none`} />
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

