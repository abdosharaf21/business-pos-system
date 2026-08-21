import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm, useFieldArray } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  ArrowLeftRight,
  Plus,
  Search,
  CheckCircle2,
  XCircle,
  Eye,
  Trash2,
  Package,
} from "lucide-react";
import toast from "react-hot-toast";
import { transferService } from "./api";
import { warehouseService } from "../warehouses/api";
import { PageHeader } from "../../shared/components/PageHeader";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
import { ConfirmDialog } from "../../shared/components/ConfirmDialog";
import { Modal } from "../../shared/components/Modal";
import { Badge } from "../../shared/components/Badge";
import { formatCurrency } from "../../utils/formatCurrency";
import {
  cardClassOverflowHidden,
  filterBarClass,
  inputClass,
  selectClass,
  labelClass,
  primaryButtonClass,
  secondaryButtonClass,
  ghostButtonClass,
  iconButtonClass,
  dangerIconButtonClass,
  tableHeadClass,
  tableBodyClass,
  tableRowClass,
  searchInputClass,
} from "../../shared/components/styles";

const STATUS_VARIANT = {
  pending: "warning",
  completed: "success",
  cancelled: "danger",
};

export default function TransfersPage() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);
  const [showCreate, setShowCreate] = useState(false);
  const [viewTransfer, setViewTransfer] = useState(null);
  const [confirmComplete, setConfirmComplete] = useState(null);
  const [confirmCancel, setConfirmCancel] = useState(null);

  const perPage = 20;

  const listQuery = useQuery({
    queryKey: ["transfers", search, statusFilter, page],
    queryFn: async () => {
      const res = await transferService.getAll({
        search: search || undefined,
        status: statusFilter || undefined,
        page,
        per_page: perPage,
      });
      return res.data.data;
    },
  });

  const completeMutation = useMutation({
    mutationFn: (id) => transferService.complete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transfers"] });
      toast.success(t("transfers.toast.completed"));
      setConfirmComplete(null);
    },
    onError: (err) => toast.error(err.response?.data?.message || t("common.error")),
  });

  const cancelMutation = useMutation({
    mutationFn: (id) => transferService.cancel(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transfers"] });
      toast.success(t("transfers.toast.cancelled"));
      setConfirmCancel(null);
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

  const transfers = listQuery.data?.items || [];
  const totalPages = listQuery.data?.pages || 1;

  return (
    <div className="space-y-6">
      <PageHeader
        title={t("transfers.title")}
        description={t("transfers.subtitle")}
        actions={
          <button onClick={() => setShowCreate(true)} className={primaryButtonClass}>
            <Plus className="w-4 h-4" />
            {t("transfers.newTransfer")}
          </button>
        }
      />

      <div className={filterBarClass}>
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[200px] max-w-sm">
            <Search className="absolute start-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              placeholder={t("transfers.searchPlaceholder")}
              className={searchInputClass}
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
            className={`${selectClass} w-auto min-w-[140px]`}
          >
            <option value="">{t("transfers.allStatuses")}</option>
            <option value="pending">{t("transfers.status.pending")}</option>
            <option value="completed">{t("transfers.status.completed")}</option>
            <option value="cancelled">{t("transfers.status.cancelled")}</option>
          </select>
        </div>
      </div>

      {transfers.length === 0 ? (
        <div className={cardClassOverflowHidden}>
          <EmptyState
            icon={ArrowLeftRight}
            title={t("transfers.emptyTitle")}
            description={t("transfers.emptyDescription")}
          />
        </div>
      ) : (
        <div className={cardClassOverflowHidden}>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className={tableHeadClass}>
                  <th className="px-5 py-3.5 text-start text-[12px] font-semibold text-surface-500 uppercase tracking-wide">{t("transfers.columns.number")}</th>
                  <th className="px-5 py-3.5 text-start text-[12px] font-semibold text-surface-500 uppercase tracking-wide">{t("transfers.columns.from")}</th>
                  <th className="px-5 py-3.5 text-start text-[12px] font-semibold text-surface-500 uppercase tracking-wide">{t("transfers.columns.to")}</th>
                  <th className="px-5 py-3.5 text-start text-[12px] font-semibold text-surface-500 uppercase tracking-wide">{t("transfers.columns.items")}</th>
                  <th className="px-5 py-3.5 text-start text-[12px] font-semibold text-surface-500 uppercase tracking-wide">{t("transfers.columns.date")}</th>
                  <th className="px-5 py-3.5 text-start text-[12px] font-semibold text-surface-500 uppercase tracking-wide">{t("transfers.columns.status")}</th>
                  <th className="px-5 py-3.5 text-end text-[12px] font-semibold text-surface-500 uppercase tracking-wide">{t("transfers.columns.actions")}</th>
                </tr>
              </thead>
              <tbody className={tableBodyClass}>
                {transfers.map((transfer) => (
                  <tr key={transfer.id} className={tableRowClass}>
                    <td className="px-5 py-4">
                      <span className="text-[13px] font-bold text-surface-800 dark:text-surface-200 font-mono">
                        #{transfer.transfer_number || transfer.id}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <span className="text-[13px] text-surface-600 dark:text-surface-300">{transfer.source_warehouse_name || "—"}</span>
                    </td>
                    <td className="px-5 py-4">
                      <span className="text-[13px] text-surface-600 dark:text-surface-300">{transfer.destination_warehouse_name || "—"}</span>
                    </td>
                    <td className="px-5 py-4">
                      <span className="text-[13px] text-surface-600 dark:text-surface-300">{transfer.items?.length || 0}</span>
                    </td>
                    <td className="px-5 py-4">
                      <span className="text-[13px] text-surface-600 dark:text-surface-300">
                        {transfer.created_at ? new Date(transfer.created_at).toLocaleDateString() : "—"}
                      </span>
                    </td>
                    <td className="px-5 py-4">
                      <Badge variant={STATUS_VARIANT[transfer.status] || "default"}>
                        {t(`transfers.status.${transfer.status}`)}
                      </Badge>
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex items-center justify-end gap-1">
                        <button onClick={() => setViewTransfer(transfer)} className={iconButtonClass} title={t("common.view")}>
                          <Eye className="w-4 h-4" />
                        </button>
                        {transfer.status === "pending" && (
                          <>
                            <button onClick={() => setConfirmComplete(transfer)} className={iconButtonClass} title={t("transfers.complete")}>
                              <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                            </button>
                            <button onClick={() => setConfirmCancel(transfer)} className={dangerIconButtonClass} title={t("transfers.cancel")}>
                              <XCircle className="w-4 h-4" />
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-between px-5 py-3 border-t border-surface-100 dark:border-surface-700/60">
              <p className="text-[12px] text-surface-400">
                {t("common.pageOf", { page, total: totalPages })}
              </p>
              <div className="flex gap-2">
                <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page <= 1} className={ghostButtonClass}>{t("common.previous")}</button>
                <button onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page >= totalPages} className={ghostButtonClass}>{t("common.next")}</button>
              </div>
            </div>
          )}
        </div>
      )}

      {showCreate && (
        <CreateTransferModal
          isOpen={showCreate}
          onClose={() => setShowCreate(false)}
          onCreated={() => {
            queryClient.invalidateQueries({ queryKey: ["transfers"] });
            setShowCreate(false);
          }}
        />
      )}

      {viewTransfer && (
        <TransferDetailModal
          isOpen={!!viewTransfer}
          onClose={() => setViewTransfer(null)}
          transfer={viewTransfer}
        />
      )}

      {confirmComplete && (
        <ConfirmDialog
          isOpen={!!confirmComplete}
          onClose={() => setConfirmComplete(null)}
          onConfirm={() => completeMutation.mutate(confirmComplete.id)}
          title={t("transfers.completeTitle")}
          message={t("transfers.completeConfirm")}
          confirmText={t("transfers.complete")}
          loading={completeMutation.isPending}
        />
      )}

      {confirmCancel && (
        <ConfirmDialog
          isOpen={!!confirmCancel}
          onClose={() => setConfirmCancel(null)}
          onConfirm={() => cancelMutation.mutate(confirmCancel.id)}
          title={t("transfers.cancelTitle")}
          message={t("transfers.cancelConfirm")}
          confirmText={t("transfers.cancel")}
          loading={cancelMutation.isPending}
        />
      )}
    </div>
  );
}

function CreateTransferModal({ isOpen, onClose, onCreated }) {
  const { t } = useTranslation();

  const warehousesQuery = useQuery({
    queryKey: ["warehouses", "active"],
    queryFn: async () => {
      const res = await warehouseService.getAll(true);
      return res.data.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: (data) => transferService.create(data),
    onSuccess: () => {
      toast.success(t("transfers.toast.created"));
      onCreated();
    },
    onError: (err) => toast.error(err.response?.data?.message || t("common.error")),
  });

  const schema = z.object({
    source_warehouse_id: z.coerce.number().min(1, t("transfers.validation.sourceRequired")),
    destination_warehouse_id: z.coerce.number().min(1, t("transfers.validation.destinationRequired")),
    notes: z.string().max(500).optional(),
    items: z.array(z.object({
      product_id: z.coerce.number().min(1),
      quantity: z.coerce.number().int().min(1, t("transfers.validation.quantityMin")),
      cost_price: z.coerce.number().min(0).optional(),
    })).min(1, t("transfers.validation.itemsRequired")),
  });

  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(schema),
    defaultValues: {
      source_warehouse_id: 0,
      destination_warehouse_id: 0,
      notes: "",
      items: [{ product_id: 0, quantity: 1, cost_price: 0 }],
    },
  });

  const { fields, append, remove } = useFieldArray({ control, name: "items" });
  const warehouses = warehousesQuery.data || [];

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={t("transfers.createTitle")} maxWidth="max-w-2xl">
      <form onSubmit={handleSubmit((data) => createMutation.mutate(data))} className="space-y-5">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={labelClass}>{t("transfers.form.source")} *</label>
            <select {...register("source_warehouse_id")} className={selectClass}>
              <option value="0">{t("transfers.form.selectWarehouse")}</option>
              {warehouses.map((w) => (
                <option key={w.id} value={w.id}>{w.name}</option>
              ))}
            </select>
            {errors.source_warehouse_id && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.source_warehouse_id.message}</p>}
          </div>
          <div>
            <label className={labelClass}>{t("transfers.form.destination")} *</label>
            <select {...register("destination_warehouse_id")} className={selectClass}>
              <option value="0">{t("transfers.form.selectWarehouse")}</option>
              {warehouses.map((w) => (
                <option key={w.id} value={w.id}>{w.name}</option>
              ))}
            </select>
            {errors.destination_warehouse_id && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.destination_warehouse_id.message}</p>}
          </div>
        </div>

        <div>
          <label className={labelClass}>{t("transfers.form.notes")}</label>
          <textarea {...register("notes")} rows={2} className={inputClass} placeholder={t("transfers.form.notesPlaceholder")} />
        </div>

        <div>
          <div className="flex items-center justify-between mb-2">
            <label className={labelClass + " mb-0"}>{t("transfers.form.items")} *</label>
            <button type="button" onClick={() => append({ product_id: 0, quantity: 1, cost_price: 0 })} className={ghostButtonClass}>
              <Plus className="w-3.5 h-3.5" /> {t("transfers.form.addItem")}
            </button>
          </div>
          <div className="space-y-3">
            {fields.map((field, index) => (
              <div key={field.id} className="flex items-end gap-3">
                <div className="flex-1">
                  <label className="text-[11px] text-surface-400 font-medium">{t("transfers.form.productId")}</label>
                  <input type="number" {...register(`items.${index}.product_id`)} className={inputClass} placeholder="ID" />
                </div>
                <div className="w-24">
                  <label className="text-[11px] text-surface-400 font-medium">{t("transfers.form.quantity")}</label>
                  <input type="number" min="1" {...register(`items.${index}.quantity`)} className={inputClass} />
                </div>
                <div className="w-28">
                  <label className="text-[11px] text-surface-400 font-medium">{t("transfers.form.costPrice")}</label>
                  <input type="number" min="0" step="0.01" {...register(`items.${index}.cost_price`)} className={inputClass} />
                </div>
                {fields.length > 1 && (
                  <button type="button" onClick={() => remove(index)} className={dangerIconButtonClass}>
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            ))}
          </div>
          {errors.items && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.items.message}</p>}
        </div>

        <div className="flex justify-end gap-3 pt-4 border-t border-surface-100 dark:border-surface-700/60">
          <button type="button" onClick={onClose} className={secondaryButtonClass}>{t("common.cancel")}</button>
          <button type="submit" disabled={createMutation.isPending} className={primaryButtonClass}>
            {createMutation.isPending ? t("common.creating") : t("common.create")}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function TransferDetailModal({ isOpen, onClose, transfer }) {
  const { t } = useTranslation();

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={t("transfers.detailTitle", { number: transfer.transfer_number || transfer.id })} maxWidth="max-w-xl">
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4 text-[13px]">
          <div>
            <span className="text-surface-400">{t("transfers.form.source")}</span>
            <p className="font-semibold text-surface-800 dark:text-surface-200 mt-0.5">{transfer.source_warehouse_name || "—"}</p>
          </div>
          <div>
            <span className="text-surface-400">{t("transfers.form.destination")}</span>
            <p className="font-semibold text-surface-800 dark:text-surface-200 mt-0.5">{transfer.destination_warehouse_name || "—"}</p>
          </div>
          <div>
            <span className="text-surface-400">{t("transfers.columns.date")}</span>
            <p className="font-semibold text-surface-800 dark:text-surface-200 mt-0.5">
              {transfer.created_at ? new Date(transfer.created_at).toLocaleString() : "—"}
            </p>
          </div>
          <div>
            <span className="text-surface-400">{t("transfers.columns.status")}</span>
            <div className="mt-0.5">
              <Badge variant={STATUS_VARIANT[transfer.status] || "default"}>
                {t(`transfers.status.${transfer.status}`)}
              </Badge>
            </div>
          </div>
        </div>

        {transfer.notes && (
          <div>
            <span className="text-[12px] text-surface-400">{t("transfers.form.notes")}</span>
            <p className="text-[13px] text-surface-700 dark:text-surface-300 mt-0.5">{transfer.notes}</p>
          </div>
        )}

        <div>
          <h4 className="text-[13px] font-semibold text-surface-700 dark:text-surface-300 mb-2">{t("transfers.form.items")}</h4>
          {(transfer.items || []).length === 0 ? (
            <EmptyState icon={Package} title={t("transfers.noItems")} />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className={tableHeadClass}>
                    <th className="px-4 py-2.5 text-start text-[11px] font-semibold text-surface-500 uppercase">{t("transfers.form.productId")}</th>
                    <th className="px-4 py-2.5 text-end text-[11px] font-semibold text-surface-500 uppercase">{t("transfers.form.quantity")}</th>
                    <th className="px-4 py-2.5 text-end text-[11px] font-semibold text-surface-500 uppercase">{t("transfers.form.costPrice")}</th>
                  </tr>
                </thead>
                <tbody className={tableBodyClass}>
                  {transfer.items.map((item, i) => (
                    <tr key={i} className={tableRowClass}>
                      <td className="px-4 py-2.5 text-[13px] text-surface-800 dark:text-surface-200">{item.product_id}</td>
                      <td className="px-4 py-2.5 text-[13px] font-bold text-surface-900 dark:text-surface-100 text-end">{item.quantity}</td>
                      <td className="px-4 py-2.5 text-[13px] text-surface-600 dark:text-surface-300 text-end">{item.cost_price ? formatCurrency(item.cost_price) : "—"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </Modal>
  );
}
