import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { bdServiceService as serviceService } from "./api";
import { serviceCategoryService as serviceCategoriesService } from "../service_categories/api";
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
  searchInputClass,
  primaryButtonClass,
  secondaryButtonClass,
  iconButtonClass,
  dangerIconButtonClass,
} from "../../shared/components/styles";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Plus, Pencil, Trash2, Search, BriefcaseBusiness } from "lucide-react";
import toast from "react-hot-toast";

const SERVICE_STATUSES = ["active", "inactive"];

export default function ServicesPage() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const canManage = ["admin", "manager"].includes(user?.role);
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const { data: services = [], isLoading, error, refetch } = useQuery({
    queryKey: ["services"],
    queryFn: async () => (await serviceService.getAll()).data.data,
  });

  const { data: categories = [] } = useQuery({
    queryKey: ["service-categories"],
    queryFn: async () => (await serviceCategoriesService.getAll()).data.data,
  });

  const createMutation = useMutation({
    mutationFn: (data) => serviceService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["services"] });
      queryClient.invalidateQueries({ queryKey: ["business-development-statistics"] });
      toast.success(t("business.services.toast.created"));
      setModalOpen(false);
    },
    onError: (err) => toast.error(err.response?.data?.message || t("business.services.toast.createFailed")),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => serviceService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["services"] });
      toast.success(t("business.services.toast.updated"));
      setModalOpen(false);
      setEditing(null);
    },
    onError: (err) => toast.error(err.response?.data?.message || t("business.services.toast.updateFailed")),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => serviceService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["services"] });
      queryClient.invalidateQueries({ queryKey: ["business-development-statistics"] });
      toast.success(t("business.services.toast.deleted"));
      setDeleteTarget(null);
    },
    onError: (err) => toast.error(err.response?.data?.message || t("business.services.toast.deleteFailed")),
  });

  const filtered = services.filter((s) => {
    const term = search.toLowerCase();
    const matchesSearch =
      !search ||
      s.name?.toLowerCase().includes(term) ||
      s.description?.toLowerCase().includes(term);
    const matchesCategory = !categoryFilter || String(s.category_id) === categoryFilter;
    const matchesStatus = !statusFilter || s.status === statusFilter;
    return matchesSearch && matchesCategory && matchesStatus;
  });

  const categoryName = (id) => categories.find((c) => c.id === id)?.name;

  const columns = [
    {
      key: "name",
      label: t("business.services.columns.name"),
      render: (val, row) => (
        <div className="flex flex-col">
          <span className="text-[13px] font-semibold text-surface-800 dark:text-surface-100">{val}</span>
          {row.description && (
            <span className="text-[11px] text-surface-400 dark:text-surface-500 line-clamp-1 max-w-xs">
              {row.description}
            </span>
          )}
        </div>
      ),
    },
    {
      key: "category_id",
      label: t("business.services.columns.category"),
      render: (val) => (
        <span className="text-[13px] text-surface-600 dark:text-surface-300">
          {val ? categoryName(val) || "-" : t("common.none")}
        </span>
      ),
    },
    {
      key: "price",
      label: t("business.services.columns.price"),
      render: (val) => (
        <span className="numeric-value text-[13px] font-bold text-surface-800 dark:text-surface-100">
          {formatPrice(val)}
        </span>
      ),
    },
    {
      key: "duration_days",
      label: t("business.services.columns.duration"),
      render: (val) =>
        val != null ? (
          <span className="numeric-value text-[13px] text-surface-600 dark:text-surface-300">
            {t("business.services.durationDays", { count: val })}
          </span>
        ) : (
          <span className="text-[13px] text-surface-400">-</span>
        ),
    },
    {
      key: "status",
      label: t("business.services.columns.status"),
      render: (val) => (
        <Badge variant={statusBadge(val)}>{t(`business.serviceStatus.${val}`)}</Badge>
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
        title={t("business.services.title")}
        description={t("business.services.description")}
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
              {t("business.services.new")}
            </button>
          )
        }
      />

      <div className="mb-6 flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 absolute start-3.5 top-1/2 -translate-y-1/2 text-surface-400 dark:text-surface-500 pointer-events-none" />
          <input
            type="text"
            placeholder={t("business.services.searchPlaceholder")}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className={searchInputClass}
            aria-label={t("business.services.searchPlaceholder")}
          />
        </div>
        <select
          value={categoryFilter}
          onChange={(e) => setCategoryFilter(e.target.value)}
          className={`${selectClass} sm:w-48`}
          aria-label={t("business.services.filters.category")}
        >
          <option value="">{t("business.services.filters.allCategories")}</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className={`${selectClass} sm:w-44`}
          aria-label={t("business.services.filters.status")}
        >
          <option value="">{t("business.services.filters.allStatuses")}</option>
          {SERVICE_STATUSES.map((status) => (
            <option key={status} value={status}>
              {t(`business.serviceStatus.${status}`)}
            </option>
          ))}
        </select>
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          icon={BriefcaseBusiness}
          title={t("business.services.empty.title")}
          description={
            search || categoryFilter || statusFilter
              ? t("business.services.empty.noResults")
              : t("business.services.empty.noServices")
          }
        />
      ) : (
        <DataTable columns={columns} data={filtered} />
      )}

      <ServiceModal
        isOpen={modalOpen}
        onClose={() => {
          setModalOpen(false);
          setEditing(null);
        }}
        editing={editing}
        categories={categories}
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
        title={t("business.services.confirmDelete.title")}
        message={t("business.services.confirmDelete.message", { name: deleteTarget?.name })}
        loading={deleteMutation.isPending}
      />
    </div>
  );
}

function formatPrice(value) {
  const num = Number(value);
  return Number.isFinite(num) ? num.toFixed(2) : "-";
}

function ServiceModal({ isOpen, onClose, editing, categories, onSubmit, loading }) {
  const { t } = useTranslation();
  const schema = useMemo(
    () =>
      z.object({
        name: z.string().min(1, t("business.services.validation.nameRequired")),
        price: z.coerce.number().min(0, t("business.services.validation.priceInvalid")),
        duration_days: z.coerce.number().int().min(0).optional(),
      }),
    [t]
  );

  const defaults = useMemo(
    () =>
      editing
        ? {
            name: editing.name || "",
            description: editing.description || "",
            category_id: editing.category_id ?? "",
            price: editing.price ?? "",
            duration_days: editing.duration_days ?? "",
            status: editing.status || "active",
          }
        : { name: "", description: "", category_id: "", price: "", duration_days: "", status: "active" },
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
      title={editing ? t("business.services.form.editTitle") : t("business.services.form.createTitle")}
    >
      <form onSubmit={handleSubmit((data) => onSubmit(data))} className="space-y-5">
        <div>
          <label className={labelClass}>{t("business.services.form.name")}</label>
          <input {...register("name")} className={inputClass} />
          {errors.name && (
            <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.name.message}</p>
          )}
        </div>
        <div>
          <label className={labelClass}>{t("business.services.form.description")}</label>
          <textarea {...register("description")} rows={2} className={`${inputClass} resize-none`} />
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className={labelClass}>{t("business.services.form.category")}</label>
            <select {...register("category_id")} className={selectClass}>
              <option value="">{t("business.services.form.noCategory")}</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelClass}>{t("business.services.form.status")}</label>
            <select {...register("status")} className={selectClass}>
              {SERVICE_STATUSES.map((status) => (
                <option key={status} value={status}>
                  {t(`business.serviceStatus.${status}`)}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className={labelClass}>{t("business.services.form.price")}</label>
            <input {...register("price")} type="number" step="0.01" min="0" className={inputClass} />
            {errors.price && (
              <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.price.message}</p>
            )}
          </div>
          <div>
            <label className={labelClass}>{t("business.services.form.duration")}</label>
            <input {...register("duration_days")} type="number" step="1" min="0" className={inputClass} />
          </div>
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

