import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  Warehouse,
  Plus,
  Pencil,
  Trash2,
  Power,
  Search,
  MapPin,
  User,
} from "lucide-react";
import toast from "react-hot-toast";
import { warehouseService } from "./api";
import { PageHeader } from "../../shared/components/PageHeader";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
import { ConfirmDialog } from "../../shared/components/ConfirmDialog";
import { Modal } from "../../shared/components/Modal";
import { Badge } from "../../shared/components/Badge";
import {
  cardClassOverflowHidden,
  filterBarClass,
  inputClass,
  labelClass,
  primaryButtonClass,
  secondaryButtonClass,
  iconButtonClass,
  dangerIconButtonClass,
  tableHeadClass,
  tableBodyClass,
  tableRowClass,
  searchInputClass,
} from "../../shared/components/styles";

export default function WarehousesPage() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [confirmDelete, setConfirmDelete] = useState(null);
  const [confirmToggle, setConfirmToggle] = useState(null);
  const [viewStock, setViewStock] = useState(null);

  const listQuery = useQuery({
    queryKey: ["warehouses"],
    queryFn: async () => {
      const res = await warehouseService.getAll();
      return res.data.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: (data) => warehouseService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["warehouses"] });
      toast.success(t("warehouses.toast.created"));
      setShowForm(false);
    },
    onError: (err) => toast.error(err.response?.data?.message || t("common.error")),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => warehouseService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["warehouses"] });
      toast.success(t("warehouses.toast.updated"));
      setEditing(null);
    },
    onError: (err) => toast.error(err.response?.data?.message || t("common.error")),
  });

  const toggleMutation = useMutation({
    mutationFn: ({ id, status }) => warehouseService.toggleStatus(id, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["warehouses"] });
      toast.success(t("warehouses.toast.statusUpdated"));
      setConfirmToggle(null);
    },
    onError: (err) => toast.error(err.response?.data?.message || t("common.error")),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => warehouseService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["warehouses"] });
      toast.success(t("warehouses.toast.deleted"));
      setConfirmDelete(null);
    },
    onError: (err) => toast.error(err.response?.data?.message || t("common.error")),
  });

  if (listQuery.isLoading) return <LoadingSpinner />;
  if (listQuery.error) {
    return (
      <ErrorDisplay
        message={listQuery.error.response?.data?.message || listQuery.error.message}
        onRetry={() => listQuery.refetch()}
      />
    );
  }

  const warehouses = (listQuery.data || []).filter(
    (w) =>
      !search ||
      w.name.toLowerCase().includes(search.toLowerCase()) ||
      (w.code || "").toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <PageHeader
        title={t("warehouses.title")}
        description={t("warehouses.subtitle")}
        actions={
          <button
            onClick={() => { setEditing(null); setShowForm(true); }}
            className={primaryButtonClass}
          >
            <Plus className="w-4 h-4" />
            {t("warehouses.addWarehouse")}
          </button>
        }
      />

      <div className={filterBarClass}>
        <div className="relative max-w-sm">
          <Search className="absolute start-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={t("warehouses.searchPlaceholder")}
            className={searchInputClass}
          />
        </div>
      </div>

      {warehouses.length === 0 ? (
        <div className={cardClassOverflowHidden}>
          <EmptyState
            icon={Warehouse}
            title={t("warehouses.emptyTitle")}
            description={t("warehouses.emptyDescription")}
          />
        </div>
      ) : (
        <div className={cardClassOverflowHidden}>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className={tableHeadClass}>
                  <th className="px-5 py-3.5 text-start text-[12px] font-semibold text-surface-500 uppercase tracking-wide">{t("warehouses.columns.name")}</th>
                  <th className="px-5 py-3.5 text-start text-[12px] font-semibold text-surface-500 uppercase tracking-wide">{t("warehouses.columns.code")}</th>
                  <th className="px-5 py-3.5 text-start text-[12px] font-semibold text-surface-500 uppercase tracking-wide">{t("warehouses.columns.address")}</th>
                  <th className="px-5 py-3.5 text-start text-[12px] font-semibold text-surface-500 uppercase tracking-wide">{t("warehouses.columns.manager")}</th>
                  <th className="px-5 py-3.5 text-start text-[12px] font-semibold text-surface-500 uppercase tracking-wide">{t("warehouses.columns.stock")}</th>
                  <th className="px-5 py-3.5 text-start text-[12px] font-semibold text-surface-500 uppercase tracking-wide">{t("warehouses.columns.status")}</th>
                  <th className="px-5 py-3.5 text-end text-[12px] font-semibold text-surface-500 uppercase tracking-wide">{t("warehouses.columns.actions")}</th>
                </tr>
              </thead>
              <tbody className={tableBodyClass}>
                {warehouses.map((warehouse) => (
                  <tr key={warehouse.id} className={tableRowClass}>
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-lg bg-primary-50 dark:bg-primary-500/10 text-primary-600 flex items-center justify-center ring-1 ring-primary-100 dark:ring-primary-500/20 shrink-0">
                          <Warehouse className="w-4 h-4" strokeWidth={1.8} />
                        </div>
                        <span className="text-[13px] font-semibold text-surface-800 dark:text-surface-200">{warehouse.name}</span>
                      </div>
                    </td>
                    <td className="px-5 py-4">
                      <span className="text-[13px] font-mono text-surface-600 dark:text-surface-300">{warehouse.code || "—"}</span>
                    </td>
                    <td className="px-5 py-4">
                      <span className="text-[13px] text-surface-600 dark:text-surface-300 flex items-center gap-1.5">
                        {warehouse.address ? <MapPin className="w-3.5 h-3.5 text-surface-400 shrink-0" /> : null}
                        {warehouse.address || "—"}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <span className="text-[13px] text-surface-600 dark:text-surface-300 flex items-center gap-1.5">
                        {warehouse.manager_name ? <User className="w-3.5 h-3.5 text-surface-400 shrink-0" /> : null}
                        {warehouse.manager_name || "—"}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <button
                        onClick={() => setViewStock(warehouse)}
                        className="text-[13px] font-bold text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
                      >
                        {warehouse.stock_total ?? 0}
                      </button>
                    </td>
                    <td className="px-5 py-4">
                      <Badge variant={warehouse.status === "active" ? "success" : "danger"}>
                        {warehouse.status === "active" ? t("warehouses.status.active") : t("warehouses.status.inactive")}
                      </Badge>
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex items-center justify-end gap-1">
                        <button
                          onClick={() => { setEditing(warehouse); setShowForm(true); }}
                          className={iconButtonClass}
                          title={t("common.edit")}
                        >
                          <Pencil className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => setConfirmToggle(warehouse)}
                          className={warehouse.status === "active" ? dangerIconButtonClass : iconButtonClass}
                          title={warehouse.status === "active" ? t("warehouses.deactivate") : t("warehouses.activate")}
                        >
                          <Power className="w-4 h-4" />
                        </button>
                        {warehouse.stock_total === 0 && (
                          <button
                            onClick={() => setConfirmDelete(warehouse)}
                            className={dangerIconButtonClass}
                            title={t("common.delete")}
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {showForm && (
        <WarehouseForm
          isOpen={showForm}
          onClose={() => { setShowForm(false); setEditing(null); }}
          warehouse={editing}
          onSubmit={(data) => {
            if (editing) {
              updateMutation.mutate({ id: editing.id, data });
            } else {
              createMutation.mutate(data);
            }
          }}
          loading={createMutation.isPending || updateMutation.isPending}
        />
      )}

      {confirmToggle && (
        <ConfirmDialog
          isOpen={!!confirmToggle}
          onClose={() => setConfirmToggle(null)}
          onConfirm={() =>
            toggleMutation.mutate({
              id: confirmToggle.id,
              status: confirmToggle.status === "active" ? "inactive" : "active",
            })
          }
          title={confirmToggle.status === "active" ? t("warehouses.deactivateTitle") : t("warehouses.activateTitle")}
          message={confirmToggle.status === "active" ? t("warehouses.deactivateConfirm") : t("warehouses.activateConfirm")}
          confirmText={confirmToggle.status === "active" ? t("warehouses.deactivate") : t("warehouses.activate")}
          loading={toggleMutation.isPending}
        />
      )}

      {confirmDelete && (
        <ConfirmDialog
          isOpen={!!confirmDelete}
          onClose={() => setConfirmDelete(null)}
          onConfirm={() => deleteMutation.mutate(confirmDelete.id)}
          title={t("warehouses.deleteTitle")}
          message={t("warehouses.deleteConfirm", { name: confirmDelete.name })}
          confirmText={t("common.delete")}
          loading={deleteMutation.isPending}
        />
      )}

      {viewStock && (
        <WarehouseStockModal
          isOpen={!!viewStock}
          onClose={() => setViewStock(null)}
          warehouse={viewStock}
        />
      )}
    </div>
  );
}

function WarehouseForm({ isOpen, onClose, warehouse, onSubmit, loading }) {
  const { t } = useTranslation();
  const isEdit = !!warehouse;

  const schema = z.object({
    name: z.string().min(1, t("warehouses.validation.nameRequired")),
    code: z.string().min(1, t("warehouses.validation.codeRequired")),
    address: z.string().optional(),
    manager_name: z.string().optional(),
    phone: z.string().optional(),
  });

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(schema),
    defaultValues: {
      name: warehouse?.name || "",
      code: warehouse?.code || "",
      address: warehouse?.address || "",
      manager_name: warehouse?.manager_name || "",
      phone: warehouse?.phone || "",
    },
  });

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isEdit ? t("warehouses.editWarehouse") : t("warehouses.newWarehouse")}
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <div>
          <label className={labelClass}>{t("warehouses.form.name")} *</label>
          <input {...register("name")} className={inputClass} placeholder={t("warehouses.form.namePlaceholder")} />
          {errors.name && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.name.message}</p>}
        </div>
        <div>
          <label className={labelClass}>{t("warehouses.form.code")} *</label>
          <input {...register("code")} className={inputClass} placeholder={t("warehouses.form.codePlaceholder")} />
          {errors.code && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.code.message}</p>}
        </div>
        <div>
          <label className={labelClass}>{t("warehouses.form.address")}</label>
          <input {...register("address")} className={inputClass} placeholder={t("warehouses.form.addressPlaceholder")} />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelClass}>{t("warehouses.form.manager")}</label>
            <input {...register("manager_name")} className={inputClass} placeholder={t("warehouses.form.managerPlaceholder")} />
          </div>
          <div>
            <label className={labelClass}>{t("warehouses.form.phone")}</label>
            <input {...register("phone")} className={inputClass} placeholder={t("warehouses.form.phonePlaceholder")} />
          </div>
        </div>
        <div className="flex justify-end gap-3 pt-4 border-t border-surface-100 dark:border-surface-700/60">
          <button type="button" onClick={onClose} className={secondaryButtonClass}>{t("common.cancel")}</button>
          <button type="submit" disabled={loading} className={primaryButtonClass}>
            {loading ? t("common.saving") : isEdit ? t("common.update") : t("common.create")}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function WarehouseStockModal({ isOpen, onClose, warehouse }) {
  const { t } = useTranslation();
  const [search, setSearch] = useState("");

  const stockQuery = useQuery({
    queryKey: ["warehouse-stock", warehouse.id, search],
    queryFn: async () => {
      const res = await warehouseService.getStock(warehouse.id, search);
      return res.data.data;
    },
  });

  const items = stockQuery.data || [];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={t("warehouses.stockTitle", { name: warehouse.name })} maxWidth="max-w-2xl">
      <div className="space-y-4">
        <div className="relative">
          <Search className="absolute start-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={t("warehouses.stockSearchPlaceholder")}
            className={searchInputClass}
          />
        </div>
        {stockQuery.isLoading ? (
          <LoadingSpinner />
        ) : items.length === 0 ? (
          <EmptyState icon={Warehouse} title={t("warehouses.noStock")} />
        ) : (
          <div className="overflow-x-auto max-h-80 overflow-y-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className={tableHeadClass}>
                  <th className="px-4 py-3 text-start text-[12px] font-semibold text-surface-500 uppercase">{t("warehouses.stockColumns.product")}</th>
                  <th className="px-4 py-3 text-end text-[12px] font-semibold text-surface-500 uppercase">{t("warehouses.stockColumns.quantity")}</th>
                </tr>
              </thead>
              <tbody className={tableBodyClass}>
                {items.map((item) => (
                  <tr key={item.product_id || item.id} className={tableRowClass}>
                    <td className="px-4 py-3 text-[13px] font-medium text-surface-800 dark:text-surface-200">{item.name}</td>
                    <td className="px-4 py-3 text-[13px] font-bold text-surface-900 dark:text-surface-100 text-end">{item.quantity}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Modal>
  );
}
