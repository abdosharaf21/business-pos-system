import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { warehouseService, WAREHOUSE_STATUSES } from "./api";
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
import { Plus, Pencil, Trash2, Search, Warehouse as WarehouseIcon } from "lucide-react";
import toast from "react-hot-toast";

export default function WarehousesPage() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const canManage = ["admin", "manager"].includes(user?.role);
  const [search, setSearch] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const { data: warehouses = [], isLoading, error, refetch } = useQuery({
    queryKey: ["warehouses"],
    queryFn: async () => (await warehouseService.getAll()).data.data,
  });

  const createMutation = useMutation({
    mutationFn: (data) => warehouseService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["warehouses"] });
      toast.success(t("inventory.warehouses.toast.created"));
      setModalOpen(false);
    },
    onError: (err) =>
      toast.error(err.response?.data?.message || t("inventory.warehouses.toast.createFailed")),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => warehouseService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["warehouses"] });
      toast.success(t("inventory.warehouses.toast.updated"));
      setModalOpen(false);
      setEditing(null);
    },
    onError: (err) =>
      toast.error(err.response?.data?.message || t("inventory.warehouses.toast.updateFailed")),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => warehouseService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["warehouses"] });
      toast.success(t("inventory.warehouses.toast.deleted"));
      setDeleteTarget(null);
    },
    onError: (err) =>
      toast.error(err.response?.data?.message || t("inventory.warehouses.toast.deleteFailed")),
  });

  const filtered = warehouses.filter((w) => {
    const term = search.toLowerCase();
    return !search || w.name?.toLowerCase().includes(term) || w.location?.toLowerCase().includes(term);
  });

  const columns = [
    {
      key: "name",
      label: t("inventory.warehouses.columns.name"),
      render: (val) => (
        <span className="text-[13px] font-semibold text-surface-800 dark:text-surface-100">{val}</span>
      ),
    },
    {
      key: "location",
      label: t("inventory.warehouses.columns.location"),
      render: (val) => (
        <span className="text-[13px] text-surface-500 dark:text-surface-400">{val || "-"}</span>
      ),
    },
    {
      key: "status",
      label: t("inventory.warehouses.columns.status"),
      render: (val) => (
        <Badge variant={statusBadge(val)}>{t(`inventory.warehouses.statuses.${val}`)}</Badge>
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
        title={t("inventory.warehouses.title")}
        description={t("inventory.warehouses.description")}
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
              {t("inventory.warehouses.new")}
            </button>
          )
        }
      />

      <div className="mb-6">
        <div className="relative">
          <Search className="w-4 h-4 absolute start-3.5 top-1/2 -translate-y-1/2 text-surface-400 dark:text-surface-500 pointer-events-none" />
          <input
            type="text"
            placeholder={t("inventory.warehouses.searchPlaceholder")}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className={searchInputClass}
            aria-label={t("inventory.warehouses.searchPlaceholder")}
          />
        </div>
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          icon={WarehouseIcon}
          title={t("inventory.warehouses.empty.title")}
          description={
            search ? t("inventory.warehouses.empty.noResults") : t("inventory.warehouses.empty.noWarehouses")
          }
        />
      ) : (
        <DataTable columns={columns} data={filtered} />
      )}

      <WarehouseModal
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setEditing(null);
        }}
        editing={editing}
        onSubmit={(data) =>
          editing ? updateMutation.mutate({ id: editing.id, data }) : createMutation.mutate(data)
        }
        loading={createMutation.isPending || updateMutation.isPending}
      />

      <ConfirmDialog
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => deleteMutation.mutate(deleteTarget.id)}
        title={t("inventory.warehouses.confirmDelete.title")}
        message={t("inventory.warehouses.confirmDelete.message", { name: deleteTarget?.name })}
        loading={deleteMutation.isPending}
      />
    </div>
  );
}

function WarehouseModal({ isOpen, onClose, editing, onSubmit, loading }) {
  const { t } = useTranslation();
  const schema = useMemo(
    () =>
      z.object({
        name: z.string().min(1, t("inventory.warehouses.validation.nameRequired")),
        location: z.string().optional(),
        status: z.enum(WAREHOUSE_STATUSES),
      }),
    [t]
  );

  const defaults = useMemo(
    () =>
      editing
        ? { name: editing.name || "", location: editing.location || "", status: editing.status || "active" }
        : { name: "", location: "", status: "active" },
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
        editing ? t("inventory.warehouses.form.editTitle") : t("inventory.warehouses.form.createTitle")
      }
    >
      <form onSubmit={handleSubmit((data) => onSubmit(data))} className="space-y-5">
        <div>
          <label className={labelClass}>{t("inventory.warehouses.form.name")}</label>
          <input {...register("name")} className={inputClass} />
          {errors.name && (
            <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.name.message}</p>
          )}
        </div>
        <div>
          <label className={labelClass}>{t("inventory.warehouses.form.location")}</label>
          <input {...register("location")} className={inputClass} />
        </div>
        <div>
          <label className={labelClass}>{t("inventory.warehouses.form.status")}</label>
          <select {...register("status")} className={`${inputClass} appearance-none cursor-pointer`}>
            {WAREHOUSE_STATUSES.map((status) => (
              <option key={status} value={status}>
                {t(`inventory.warehouses.statuses.${status}`)}
              </option>
            ))}
          </select>
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

