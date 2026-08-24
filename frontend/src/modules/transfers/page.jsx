import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { transferService, TRANSFER_STATUSES } from "./api";
import { warehouseService } from "../warehouses/api";
import { productService } from "../products/api";
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
  ghostButtonClass,
  iconButtonClass,
} from "../../shared/components/styles";
import { ArrowLeftRight, Eye, CheckCircle2, XCircle, Plus, Trash2 } from "lucide-react";
import toast from "react-hot-toast";

export default function TransfersPage() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const canManage = ["admin", "manager"].includes(user?.role);
  const [statusFilter, setStatusFilter] = useState("");
  const [createOpen, setCreateOpen] = useState(false);
  const [detailsTarget, setDetailsTarget] = useState(null);
  const [completeTarget, setCompleteTarget] = useState(null);
  const [cancelTarget, setCancelTarget] = useState(null);

  const { data: transfers = [], isLoading, error, refetch } = useQuery({
    queryKey: ["transfers", statusFilter],
    queryFn: async () => {
      const res = await transferService.getAll(statusFilter ? { status: statusFilter } : {});
      return res.data.data.items || [];
    },
  });

  const completeMutation = useMutation({
    mutationFn: (id) => transferService.complete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transfers"] });
      queryClient.invalidateQueries({ queryKey: ["inventory"] });
      toast.success(t("inventory.transfers.toast.completed"));
      setCompleteTarget(null);
    },
    onError: (err) =>
      toast.error(err.response?.data?.message || t("inventory.transfers.toast.completeFailed")),
  });

  const cancelMutation = useMutation({
    mutationFn: (id) => transferService.cancel(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transfers"] });
      toast.success(t("inventory.transfers.toast.cancelled"));
      setCancelTarget(null);
    },
    onError: (err) =>
      toast.error(err.response?.data?.message || t("inventory.transfers.toast.cancelFailed")),
  });

  const columns = [
    {
      key: "transfer_number",
      label: t("inventory.transfers.columns.number"),
      render: (val) => (
        <span className="numeric-value text-[13px] font-semibold text-surface-800 dark:text-surface-100">
          {val || "-"}
        </span>
      ),
    },
    {
      key: "source_warehouse_name",
      label: t("inventory.transfers.columns.source"),
      render: (val) => <span className="text-[13px] text-surface-600 dark:text-surface-300">{val || "-"}</span>,
    },
    {
      key: "destination_warehouse_name",
      label: t("inventory.transfers.columns.destination"),
      render: (val) => <span className="text-[13px] text-surface-600 dark:text-surface-300">{val || "-"}</span>,
    },
    {
      key: "items_count",
      label: t("inventory.transfers.columns.itemsCount"),
      render: (val, row) => (
        <span className="numeric-value text-[13px] text-surface-600 dark:text-surface-300">
          {row.items?.length ?? val ?? 0}
        </span>
      ),
    },
    {
      key: "status",
      label: t("inventory.transfers.columns.status"),
      render: (val) => (
        <Badge variant={statusBadge(val)}>{t(`inventory.transfers.statuses.${val}`)}</Badge>
      ),
    },
    {
      key: "id",
      label: t("common.columns.actions"),
      render: (_, row) => (
        <div className="flex items-center gap-1">
          <button
            onClick={() => setDetailsTarget(row)}
            className={iconButtonClass}
            title={t("inventory.transfers.actions.viewDetails")}
          >
            <Eye className="w-4 h-4" />
          </button>
          {canManage && row.status === "pending" && (
            <>
              <button
                onClick={() => setCompleteTarget(row)}
                className={iconButtonClass}
                title={t("inventory.transfers.actions.complete")}
              >
                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
              </button>
              <button
                onClick={() => setCancelTarget(row)}
                className={iconButtonClass}
                title={t("inventory.transfers.actions.cancel")}
              >
                <XCircle className="w-4 h-4 text-red-500" />
              </button>
            </>
          )}
        </div>
      ),
    },
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
        title={t("inventory.transfers.title")}
        description={t("inventory.transfers.description")}
        actions={
          canManage && (
            <button onClick={() => setCreateOpen(true)} className={primaryButtonClass}>
              <Plus className="w-4 h-4" />
              {t("inventory.transfers.new")}
            </button>
          )
        }
      />

      <div className="mb-6 flex flex-col sm:flex-row gap-3 sm:w-auto">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className={`${selectClass} sm:w-48`}
          aria-label={t("inventory.transfers.filters.status")}
        >
          <option value="">{t("inventory.transfers.filters.allStatuses")}</option>
          {TRANSFER_STATUSES.map((status) => (
            <option key={status} value={status}>
              {t(`inventory.transfers.statuses.${status}`)}
            </option>
          ))}
        </select>
      </div>

      {transfers.length === 0 ? (
        <EmptyState
          icon={ArrowLeftRight}
          title={t("inventory.transfers.empty.title")}
          description={
            statusFilter ? t("inventory.transfers.empty.noResults") : t("inventory.transfers.empty.noTransfers")
          }
        />
      ) : (
        <DataTable columns={columns} data={transfers} />
      )}

      <CreateTransferModal isOpen={createOpen} onClose={() => setCreateOpen(false)} />

      <TransferDetailsModal
        transfer={detailsTarget}
        onClose={() => setDetailsTarget(null)}
      />

      <ConfirmDialog
        isOpen={!!completeTarget}
        onClose={() => setCompleteTarget(null)}
        onConfirm={() => completeMutation.mutate(completeTarget.id)}
        title={t("inventory.transfers.confirmComplete.title")}
        message={t("inventory.transfers.confirmComplete.message", {
          name: completeTarget?.transfer_number || "",
        })}
        confirmText={t("inventory.transfers.actions.complete")}
        loadingText={t("inventory.transfers.actions.completing")}
        loading={completeMutation.isPending}
      />

      <ConfirmDialog
        isOpen={!!cancelTarget}
        onClose={() => setCancelTarget(null)}
        onConfirm={() => cancelMutation.mutate(cancelTarget.id)}
        title={t("inventory.transfers.confirmCancel.title")}
        message={t("inventory.transfers.confirmCancel.message", {
          name: cancelTarget?.transfer_number || "",
        })}
        confirmText={t("inventory.transfers.actions.cancel")}
        loadingText={t("inventory.transfers.actions.cancelling")}
        loading={cancelMutation.isPending}
      />
    </div>
  );
}

function TransferDetailsModal({ transfer, onClose }) {
  const { t } = useTranslation();

  if (!transfer) return null;

  return (
    <Modal
      isOpen={!!transfer}
      onClose={onClose}
      maxWidth="max-w-2xl"
      title={t("inventory.transfers.details.title", { name: transfer.transfer_number || "" })}
    >
      <div className="space-y-5">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <p className={labelClass}>{t("inventory.transfers.columns.source")}</p>
            <p className="text-[13px] font-semibold text-surface-800 dark:text-surface-100">
              {transfer.source_warehouse_name || "-"}
            </p>
          </div>
          <div>
            <p className={labelClass}>{t("inventory.transfers.columns.destination")}</p>
            <p className="text-[13px] font-semibold text-surface-800 dark:text-surface-100">
              {transfer.destination_warehouse_name || "-"}
            </p>
          </div>
          <div>
            <p className={labelClass}>{t("inventory.transfers.columns.status")}</p>
            <Badge variant={statusBadge(transfer.status)}>
              {t(`inventory.transfers.statuses.${transfer.status}`)}
            </Badge>
          </div>
        </div>

        {transfer.notes && (
          <div>
            <p className={labelClass}>{t("inventory.transfers.form.notes")}</p>
            <p className="text-[13px] text-surface-600 dark:text-surface-300">{transfer.notes}</p>
          </div>
        )}

        <div>
          <p className={`${labelClass}`}>{t("inventory.transfers.details.items")}</p>
          <div className="rounded-xl border border-surface-200/80 dark:border-surface-700/60 overflow-hidden">
            <table className="w-full text-sm" role="table">
              <thead>
                <tr className="border-b border-surface-100 bg-surface-50/60 dark:border-surface-700/60 dark:bg-surface-700/30">
                  <th className="px-4 py-2.5 text-start text-[11px] font-semibold text-surface-500 uppercase tracking-wider">
                    {t("inventory.transfers.details.product")}
                  </th>
                  <th className="px-4 py-2.5 text-end text-[11px] font-semibold text-surface-500 uppercase tracking-wider">
                    {t("inventory.transfers.details.quantity")}
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-100 dark:divide-surface-700/60">
                {(transfer.items || []).map((item) => (
                  <tr key={item.id || item.product_id}>
                    <td className="px-4 py-2.5 text-[13px] text-surface-700 dark:text-surface-200">
                      {item.product_name || item.product_id}
                    </td>
                    <td className="px-4 py-2.5 text-end numeric-value text-[13px] font-semibold text-surface-700 dark:text-surface-200">
                      {item.quantity}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="flex justify-end pt-2">
          <button type="button" onClick={onClose} className={secondaryButtonClass}>
            {t("common.actions.close")}
          </button>
        </div>
      </div>
    </Modal>
  );
}

function CreateTransferModal({ isOpen, onClose }) {
  const { t } = useTranslation();
  const queryClient = useQueryClient();

  const { data: warehouses = [] } = useQuery({
    queryKey: ["warehouses"],
    queryFn: async () => (await warehouseService.getAll()).data.data,
    enabled: isOpen,
  });

  const { data: products = [] } = useQuery({
    queryKey: ["products"],
    queryFn: async () => (await productService.getAll()).data.data,
    enabled: isOpen,
  });

  const [sourceId, setSourceId] = useState("");
  const [destinationId, setDestinationId] = useState("");
  const [notes, setNotes] = useState("");
  const [items, setItems] = useState([{ product_id: "", quantity: "" }]);
  const [errors, setErrors] = useState({});

  const mutation = useMutation({
    mutationFn: (data) => transferService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transfers"] });
      queryClient.invalidateQueries({ queryKey: ["inventory"] });
      toast.success(t("inventory.transfers.toast.created"));
      handleClose();
    },
    onError: (err) =>
      toast.error(err.response?.data?.message || t("inventory.transfers.toast.createFailed")),
  });

  const handleClose = () => {
    setSourceId("");
    setDestinationId("");
    setNotes("");
    setItems([{ product_id: "", quantity: "" }]);
    setErrors({});
    onClose();
  };

  const updateItem = (index, field, value) => {
    setItems((prev) =>
      prev.map((item, i) => (i === index ? { ...item, [field]: value } : item))
    );
  };

  const addItemRow = () => setItems((prev) => [...prev, { product_id: "", quantity: "" }]);

  const removeItemRow = (index) =>
    setItems((prev) => prev.filter((_, i) => i !== index));

  const handleSubmit = (event) => {
    event.preventDefault();
    const nextErrors = {};
    if (!sourceId) nextErrors.sourceId = t("inventory.transfers.validation.sourceRequired");
    if (!destinationId) nextErrors.destinationId = t("inventory.transfers.validation.destinationRequired");
    if (sourceId && destinationId && sourceId === destinationId)
      nextErrors.destinationId = t("inventory.transfers.validation.sameWarehouse");
    if (items.length === 0) nextErrors.items = t("inventory.transfers.validation.itemsRequired");

    const cleanItems = [];
    items.forEach((item, index) => {
      const qty = Number(item.quantity);
      if (!item.product_id) {
        nextErrors[`product_${index}`] = t("inventory.transfers.validation.productRequired");
      }
      if (!Number.isFinite(qty) || qty <= 0 || !Number.isInteger(qty)) {
        nextErrors[`quantity_${index}`] = t("inventory.transfers.validation.quantityInvalid");
      }
      if (item.product_id && Number.isFinite(qty) && qty > 0) {
        cleanItems.push({ product_id: Number(item.product_id), quantity: qty });
      }
    });

    if (Object.keys(nextErrors).length > 0) {
      setErrors(nextErrors);
      return;
    }

    setErrors({});
    mutation.mutate({
      source_warehouse_id: Number(sourceId),
      destination_warehouse_id: Number(destinationId),
      items: cleanItems,
      notes: notes.trim() || null,
    });
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={handleClose}
      maxWidth="max-w-2xl"
      title={t("inventory.transfers.form.createTitle")}
    >
      <form onSubmit={handleSubmit} className="space-y-5">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className={labelClass}>{t("inventory.transfers.form.source")}</label>
            <select
              value={sourceId}
              onChange={(e) => setSourceId(e.target.value)}
              className={selectClass}
              aria-label={t("inventory.transfers.form.source")}
            >
              <option value="">{t("inventory.transfers.form.chooseWarehouse")}</option>
              {warehouses.map((w) => (
                <option key={w.id} value={w.id}>
                  {w.name}
                </option>
              ))}
            </select>
            {errors.sourceId && (
              <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.sourceId}</p>
            )}
          </div>
          <div>
            <label className={labelClass}>{t("inventory.transfers.form.destination")}</label>
            <select
              value={destinationId}
              onChange={(e) => setDestinationId(e.target.value)}
              className={selectClass}
              aria-label={t("inventory.transfers.form.destination")}
            >
              <option value="">{t("inventory.transfers.form.chooseWarehouse")}</option>
              {warehouses
                .filter((w) => String(w.id) !== String(sourceId))
                .map((w) => (
                  <option key={w.id} value={w.id}>
                    {w.name}
                  </option>
                ))}
            </select>
            {errors.destinationId && (
              <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.destinationId}</p>
            )}
          </div>
        </div>

        <div>
          <div className="flex items-center justify-between mb-2">
            <label className={`${labelClass} mb-0`}>{t("inventory.transfers.details.items")}</label>
            <button type="button" onClick={addItemRow} className={ghostButtonClass}>
              <Plus className="w-3.5 h-3.5" />
              {t("inventory.transfers.form.addItem")}
            </button>
          </div>
          <div className="space-y-3">
            {items.map((item, index) => (
              <div key={index} className="flex gap-3 items-start">
                <div className="flex-1">
                  <select
                    value={item.product_id}
                    onChange={(e) => updateItem(index, "product_id", e.target.value)}
                    className={selectClass}
                    aria-label={t("inventory.transfers.details.product")}
                  >
                    <option value="">{t("inventory.transfers.form.chooseProduct")}</option>
                    {products.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name}
                      </option>
                    ))}
                  </select>
                  {errors[`product_${index}`] && (
                    <p className="text-[11px] text-red-500 mt-1 font-medium">
                      {errors[`product_${index}`]}
                    </p>
                  )}
                </div>
                <div className="w-28">
                  <input
                    type="number"
                    min="1"
                    step="1"
                    placeholder={t("inventory.transfers.form.quantityPlaceholder")}
                    value={item.quantity}
                    onChange={(e) => updateItem(index, "quantity", e.target.value)}
                    className={inputClass}
                    aria-label={t("inventory.transfers.details.quantity")}
                  />
                  {errors[`quantity_${index}`] && (
                    <p className="text-[11px] text-red-500 mt-1 font-medium">
                      {errors[`quantity_${index}`]}
                    </p>
                  )}
                </div>
                <button
                  type="button"
                  onClick={() => removeItemRow(index)}
                  disabled={items.length === 1}
                  className="p-2 text-surface-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-500/10 rounded-xl transition-all duration-150 disabled:opacity-30 disabled:pointer-events-none"
                  title={t("inventory.transfers.form.removeItem")}
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>

        <div>
          <label className={labelClass}>{t("inventory.transfers.form.notes")}</label>
          <textarea
            rows={2}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className={`${inputClass} resize-none`}
          />
        </div>

        <div className="flex justify-end gap-3 pt-5 border-t border-surface-100 dark:border-surface-700/60">
          <button type="button" onClick={handleClose} className={secondaryButtonClass}>
            {t("common.actions.cancel")}
          </button>
          <button type="submit" disabled={mutation.isPending} className={primaryButtonClass}>
            {mutation.isPending
              ? t("common.actions.saving")
              : t("inventory.transfers.form.submitCreate")}
          </button>
        </div>
      </form>
    </Modal>
  );
}

