import { formatCurrency } from "../../utils/formatCurrency";
import { useState, useEffect, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import i18n from "../../i18n";
import { productService } from "./api";
import { useAuth } from "../../shared/context/AuthContext";
import { categoryService } from "../categories/api";
import { buildCategoryTree, flattenCategoryTree } from "../categories/tree";
import { PageHeader } from "../../shared/components/PageHeader";
import { DataTable } from "../../shared/components/DataTable";
import { Modal } from "../../shared/components/Modal";
import { ConfirmDialog } from "../../shared/components/ConfirmDialog";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
import { Badge } from "../../shared/components/Badge";
import { inputClass, selectClass, labelClass, searchInputClass, primaryButtonClass, secondaryButtonClass, iconButtonClass, dangerIconButtonClass } from "../../shared/components/styles";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Plus, Pencil, Trash2, Search, Package } from "lucide-react";
import toast from "react-hot-toast";
import { getCurrentLocale } from "../../shared/utils/format";

const productSchema = z.object({
  name: z.string().min(1, () => i18n.t("products.validation.nameRequired")),
  sku: z.string().optional(),
  barcode: z.string().min(1, () => i18n.t("products.validation.barcodeRequired")),
  category_id: z.string().min(1, () => i18n.t("products.validation.categoryRequired")),
  description: z.string().optional(),
  purchase_price: z.string().min(1, () => i18n.t("products.validation.required")).refine((v) => !isNaN(Number(v)) && Number(v) >= 0, () => i18n.t("products.validation.mustBePositive")),
  selling_price: z.string().min(1, () => i18n.t("products.validation.required")).refine((v) => !isNaN(Number(v)) && Number(v) >= 0, () => i18n.t("products.validation.mustBePositive")),
  quantity: z.string().min(1, () => i18n.t("products.validation.required")).refine((v) => !isNaN(Number(v)) && Number(v) >= 0 && Number.isInteger(Number(v)), () => i18n.t("products.validation.mustBePositive")),
  minimum_stock: z.string().min(1, () => i18n.t("products.validation.required")).refine((v) => !isNaN(Number(v)) && Number(v) >= 0 && Number.isInteger(Number(v)), () => i18n.t("products.validation.mustBePositive")),
  status: z.string().optional(),
}).refine((data) => {
  if (data.selling_price && data.purchase_price) {
    return Number(data.selling_price) >= Number(data.purchase_price);
  }
  return true;
}, { message: () => i18n.t("products.validation.priceNotLower"), path: ["selling_price"] });

const INPUT_CLASS = inputClass;
const LABEL_CLASS = labelClass;
const SELECT_CLASS = selectClass;

export default function ProductsPage() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const { t } = useTranslation();
  const canManage = ["admin", "manager"].includes(user?.role);
  const [searchParams, setSearchParams] = useSearchParams();
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const productParam = searchParams.get("product");

  const { data: products = [], isLoading, error, refetch } = useQuery({
    queryKey: ["products"],
    queryFn: async () => {
      const res = await productService.getAll();
      return res.data.data;
    },
  });

  const { data: categories = [] } = useQuery({
    queryKey: ["categories"],
    queryFn: async () => {
      const res = await categoryService.getAll();
      return res.data.data;
    },
  });

  useEffect(() => {
    if (!productParam || isLoading || products.length === 0) return;
    const target = products.find((p) => String(p.id) === productParam);
    if (!target) return;
    if (canManage) {
      setEditing(target);
      setModalOpen(true);
    }
    const next = new URLSearchParams(searchParams);
    next.delete("product");
    setSearchParams(next, { replace: true });
  }, [productParam, isLoading, products, searchParams, canManage, setSearchParams]);

  const categoryOptions = useMemo(() => flattenCategoryTree(buildCategoryTree(categories)), [categories]);

  const createMutation = useMutation({
    mutationFn: (data) => productService.create(data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["products"] }); toast.success(t("products.toast.created")); setModalOpen(false); },
    onError: (err) => toast.error(err.response?.data?.message || t("products.toast.createFailed")),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => productService.update(id, data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["products"] }); toast.success(t("products.toast.updated")); setModalOpen(false); setEditing(null); },
    onError: (err) => toast.error(err.response?.data?.message || t("products.toast.updateFailed")),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => productService.delete(id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["products"] }); toast.success(t("products.toast.deleted")); setDeleteTarget(null); },
    onError: (err) => toast.error(err.response?.data?.message || t("products.toast.deleteFailed")),
  });

  const filtered = products.filter((p) => {
    const term = search.toLowerCase();
    const matchesSearch = !search ||
      p.name?.toLowerCase().includes(term) ||
      p.barcode?.toLowerCase().includes(term) ||
      p.sku?.toLowerCase().includes(term);
    const matchesCategory = !categoryFilter || String(p.category_id) === categoryFilter;
    const matchesStatus = !statusFilter || p.status === statusFilter;
    return matchesSearch && matchesCategory && matchesStatus;
  });

  const columns = [
    {
      key: "sku",
      label: t("products.columns.sku"),
      render: (val) => <span className="text-[13px] font-mono text-surface-500 dark:text-surface-400">{val || "-"}</span>,
    },
    {
      key: "name",
      label: t("products.columns.name"),
      render: (val) => <span className="text-[13px] font-semibold text-surface-800 dark:text-surface-100">{val}</span>,
    },
    {
      key: "barcode",
      label: t("products.columns.barcode"),
      render: (val) => <span className="text-[13px] font-mono text-surface-600 dark:text-surface-300">{val}</span>,
    },
    {
      key: "category_name",
      label: t("products.columns.category"),
      render: (val) => <span className="text-[13px] text-surface-500 dark:text-surface-400">{val || "-"}</span>,
    },
    {
      key: "purchase_price",
      label: t("products.columns.purchasePrice"),
      render: (val) => <span className="text-[13px] text-surface-600 dark:text-surface-300 tabular-nums whitespace-nowrap">{formatCurrency(val)}</span>,
    },
    {
      key: "selling_price",
      label: t("products.columns.sellingPrice"),
      render: (val) => <span className="text-[13px] font-semibold text-surface-800 dark:text-surface-100 tabular-nums whitespace-nowrap">{formatCurrency(val)}</span>,
    },
    {
      key: "quantity",
      label: t("products.columns.qty"),
      render: (val, row) => {
        const isLow = val <= row.minimum_stock;
        return (
          <span className={`text-[13px] font-semibold tabular-nums whitespace-nowrap ${isLow ? "text-red-600 dark:text-red-400" : "text-surface-800 dark:text-surface-100"}`}>
            {val}
          </span>
        );
      },
    },
    {
      key: "minimum_stock",
      label: t("products.columns.minStock"),
      render: (val) => <span className="text-[13px] text-surface-500 dark:text-surface-400 tabular-nums whitespace-nowrap">{val}</span>,
    },
    {
      key: "expiration_date",
      label: t("products.columns.expiration"),
      render: (val, row) => {
        const locale = getCurrentLocale(i18n.language);
        const badgeVariant =
          row.expiration_status === "expired" ? "danger"
            : row.expiration_status === "expiring_soon" ? "warning"
              : row.expiration_status === "normal" ? "success" : "default";
        return (
          <div className="flex items-center gap-2">
            <span className="text-[13px] text-surface-600 dark:text-surface-300 whitespace-nowrap">
              {val ? new Date(val + "T00:00:00").toLocaleDateString(locale, { year: "numeric", month: "short", day: "numeric" }) : "—"}
            </span>
            {row.expiration_status && (
              <Badge variant={badgeVariant}>
                {t(`products.expiration.statuses.${row.expiration_status}`)}
              </Badge>
            )}
          </div>
        );
      },
    },
    {
      key: "status",
      label: t("products.columns.status"),
      render: (val) => (
        <Badge variant={val === "active" ? "success" : "default"}>
          {val === "active" ? t("products.active") : t("products.inactive")}
        </Badge>
      ),
    },
    ...(canManage
      ? [
          {
            key: "id",
            label: t("products.columns.actions"),
            render: (_, row) => (
              <div className="flex items-center gap-1">
                <button onClick={() => { setEditing(row); setModalOpen(true); }} className={iconButtonClass} title={t("products.edit")}>
                  <Pencil className="w-4 h-4" />
                </button>
                <button onClick={() => setDeleteTarget(row)} className={dangerIconButtonClass} title={t("products.delete")}>
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
        title={t("products.title")}
        description={t("products.subtitle")}
        actions={
          canManage && (
            <button onClick={() => { setEditing(null); setModalOpen(true); }} className={primaryButtonClass}>
              <Plus className="w-4 h-4" />
              {t("products.newProduct")}
            </button>
          )
        }
      />

      <div className="mb-6 flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="w-4 h-4 absolute start-3.5 top-1/2 -translate-y-1/2 text-surface-400 dark:text-surface-500 pointer-events-none" />
          <input type="text" placeholder={t("products.searchPlaceholder")} value={search} onChange={(e) => setSearch(e.target.value)} className={searchInputClass} aria-label={t("products.searchAriaLabel")} />
        </div>
        <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)} className={SELECT_CLASS + " min-w-[160px]"}>
          <option value="">{t("products.allCategories")}</option>
          {categoryOptions.map((c) => (
            <option key={c.id} value={c.id}>{"\u00A0\u00A0".repeat(c.depth)}{c.name}</option>
          ))}
        </select>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className={SELECT_CLASS + " min-w-[130px]"}>
          <option value="">{t("products.allStatus")}</option>
          <option value="active">{t("products.active")}</option>
          <option value="inactive">{t("products.inactive")}</option>
        </select>
      </div>

      {filtered.length === 0 ? (
        <EmptyState icon={Package} title={t("products.noProductsFound")} description={search || categoryFilter || statusFilter ? t("products.tryDifferentFilters") : t("products.addYourFirstProduct")} action={!search && !categoryFilter && !statusFilter && canManage && <button onClick={() => { setEditing(null); setModalOpen(true); }} className={primaryButtonClass}>{t("products.addProduct")}</button>} />
      ) : (
        <DataTable columns={columns} data={filtered} />
      )}

      <ProductModal isOpen={modalOpen} onClose={() => { setModalOpen(false); setEditing(null); }} editing={editing} categories={categoryOptions} onSubmit={(data) => editing ? updateMutation.mutate({ id: editing.id, data }) : createMutation.mutate(data)} loading={createMutation.isPending || updateMutation.isPending} />

      <ConfirmDialog isOpen={!!deleteTarget} onClose={() => setDeleteTarget(null)} onConfirm={() => deleteMutation.mutate(deleteTarget.id)} title={t("products.confirmDelete.title")} message={t("products.confirmDelete.message", { name: deleteTarget?.name })} confirmText={t("products.confirmDelete.confirm")} loadingText={t("products.confirmDelete.deleting")} loading={deleteMutation.isPending} />
    </div>
  );
}

function ProductModal({ isOpen, onClose, editing, categories, onSubmit, loading }) {
  const { t } = useTranslation();
  const { register, handleSubmit, reset, watch, formState: { errors } } = useForm({
    resolver: zodResolver(productSchema),
    values: editing ? {
      name: editing.name || "",
      sku: editing.sku || "",
      barcode: editing.barcode || "",
      category_id: String(editing.category_id || ""),
      description: editing.description || "",
      purchase_price: String(editing.purchase_price ?? ""),
      selling_price: String(editing.selling_price ?? ""),
      quantity: String(editing.quantity ?? ""),
      minimum_stock: String(editing.minimum_stock ?? ""),
      status: editing.status || "active",
    } : {
      name: "",
      sku: "",
      barcode: "",
      category_id: "",
      description: "",
      purchase_price: "",
      selling_price: "",
      quantity: "0",
      minimum_stock: "0",
      status: "active",
    },
  });

  const formValues = watch();
  const purchasePrice = Number(formValues.purchase_price) || 0;
  const sellingPrice = Number(formValues.selling_price) || 0;
  const showPriceWarning = purchasePrice > 0 && sellingPrice > 0 && sellingPrice < purchasePrice;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={editing ? t("products.form.titleEdit") : t("products.form.titleCreate")} maxWidth="max-w-2xl">
      <form onSubmit={handleSubmit((data) => { onSubmit(data); reset(); })} className="space-y-5">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>{t("products.form.name")}</label>
            <input {...register("name")} placeholder={t("products.form.namePlaceholder")} className={INPUT_CLASS} />
            {errors.name && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.name.message}</p>}
          </div>
          <div>
            <label className={LABEL_CLASS}>{t("products.form.barcode")}</label>
            <input {...register("barcode")} placeholder={t("products.form.barcodePlaceholder")} className={INPUT_CLASS} />
            {errors.barcode && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.barcode.message}</p>}
          </div>
        </div>
        <div>
          <label className={LABEL_CLASS}>{t("products.form.sku")}</label>
          <input {...register("sku")} placeholder={t("products.form.skuPlaceholder")} className={INPUT_CLASS} />
          {errors.sku && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.sku.message}</p>}
        </div>
        <div>
          <label className={LABEL_CLASS}>{t("products.form.category")}</label>
          <select {...register("category_id")} className={SELECT_CLASS}>
            <option value="">{t("products.form.categoryPlaceholder")}</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>{"\u00A0\u00A0".repeat(c.depth)}{c.name}</option>
            ))}
          </select>
          {errors.category_id && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.category_id.message}</p>}
        </div>
        <div>
          <label className={LABEL_CLASS}>{t("products.form.description")}</label>
          <textarea {...register("description")} rows={2} placeholder={t("products.form.descriptionPlaceholder")} className={`${INPUT_CLASS} resize-none`} />
          {errors.description && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.description.message}</p>}
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>{t("products.form.purchasePrice")}</label>
            <input {...register("purchase_price")} type="number" step="0.01" min="0" placeholder={t("products.form.placeholderDecimal")} className={`${INPUT_CLASS} numeric-grow min-w-14`} />
            {errors.purchase_price && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.purchase_price.message}</p>}
          </div>
          <div>
            <label className={LABEL_CLASS}>{t("products.form.sellingPrice")}</label>
            <input {...register("selling_price")} type="number" step="0.01" min="0" placeholder={t("products.form.placeholderDecimal")} className={`${INPUT_CLASS} numeric-grow min-w-14 ${showPriceWarning ? "border-amber-300 dark:border-amber-500/60" : ""}`} />
            {errors.selling_price && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.selling_price.message}</p>}
            {showPriceWarning && !errors.selling_price && (
              <p className="text-[11px] text-amber-600 dark:text-amber-400 mt-1 font-medium">{t("products.validation.priceNotLower")}</p>
            )}
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>{t("products.form.quantity")}</label>
            <input {...register("quantity")} type="number" min="0" step="1" placeholder={t("products.form.placeholderZero")} className={`${INPUT_CLASS} numeric-grow min-w-14`} />
            {errors.quantity && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.quantity.message}</p>}
          </div>
          <div>
            <label className={LABEL_CLASS}>{t("products.form.minStock")}</label>
            <input {...register("minimum_stock")} type="number" min="0" step="1" placeholder={t("products.form.placeholderZero")} className={`${INPUT_CLASS} numeric-grow min-w-14`} />
            {errors.minimum_stock && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.minimum_stock.message}</p>}
          </div>
        </div>
        {editing && (
          <div>
            <label className={LABEL_CLASS}>{t("products.form.status")}</label>
            <select {...register("status")} className={SELECT_CLASS}>
              <option value="active">{t("products.form.formActive")}</option>
              <option value="inactive">{t("products.form.formInactive")}</option>
            </select>
            {errors.status && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.status.message}</p>}
          </div>
        )}
        <div className="flex justify-end gap-3 pt-5 border-t border-surface-100 dark:border-surface-700/60">
          <button type="button" onClick={onClose} className={secondaryButtonClass}>{t("products.form.cancel")}</button>
          <button type="submit" disabled={loading} className={primaryButtonClass}>{loading ? t("products.form.saving") : editing ? t("products.form.update") : t("products.form.create")}</button>
        </div>
      </form>
    </Modal>
  );
}
