import { formatCurrency } from "../../utils/formatCurrency";
import { useState, useRef, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { purchaseService, supplierService } from "./api";
import { useAuth } from "../../shared/context/AuthContext";
import { PageHeader } from "../../shared/components/PageHeader";
import { DataTable } from "../../shared/components/DataTable";
import { Modal } from "../../shared/components/Modal";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
import { Plus, Search, ShoppingCart, Trash2, Eye, X, Minus, Plus as PlusIcon } from "lucide-react";
import toast from "react-hot-toast";

const INPUT_CLASS = "w-full px-3.5 py-2.5 border border-surface-200 bg-surface-50 rounded-xl text-sm text-surface-800 placeholder:text-surface-300 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150";
const LABEL_CLASS = "block text-[13px] font-semibold text-surface-700 mb-1.5";
const SELECT_CLASS = "w-full px-3.5 py-2.5 border border-surface-200 bg-surface-50 rounded-xl text-sm text-surface-800 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150 appearance-none cursor-pointer";

export default function PurchasesPage() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const { t } = useTranslation();
  const canManage = ["admin", "manager"].includes(user?.role);
  const [search, setSearch] = useState("");
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [viewPurchase, setViewPurchase] = useState(null);
  const [viewInvoice, setViewInvoice] = useState(null);

  const { data: purchases = [], isLoading, error, refetch } = useQuery({
    queryKey: ["purchases"],
    queryFn: async () => {
      const res = await purchaseService.getAll();
      return res.data.data;
    },
  });

  const filtered = purchases.filter((p) => {
    const term = search.toLowerCase();
    return !search ||
      p.invoice_number?.toLowerCase().includes(term) ||
      p.supplier_name?.toLowerCase().includes(term);
  });

  const columns = [
    {
      key: "invoice_number",
      label: t("purchases.columns.invoice"),
      render: (val) => <span className="text-[13px] font-mono font-semibold text-surface-800">{val}</span>,
    },
    {
      key: "supplier_name",
      label: t("purchases.columns.supplier"),
      render: (val) => <span className="text-[13px] text-surface-600">{val || "-"}</span>,
    },
    {
      key: "total_amount",
      label: t("purchases.columns.total"),
      render: (val) => <span className="text-[13px] font-semibold text-surface-800">{formatCurrency(val)}</span>,
    },
    {
      key: "status",
      label: t("purchases.columns.status"),
      render: (val) => {
        const labels = {
          completed: t("purchases.statusCompleted"),
          pending: t("purchases.statusPending"),
          cancelled: t("purchases.statusCancelled"),
        };
        return (
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold ${
            val === "completed" ? "bg-emerald-50 text-emerald-700" :
            val === "pending" ? "bg-amber-50 text-amber-700" :
            "bg-surface-100 text-surface-400"
          }`}>{labels[val] || val}</span>
        );
      },
    },
    {
      key: "created_at",
      label: t("purchases.columns.date"),
      render: (val) => <span className="text-[13px] text-surface-500">{val ? new Date(val).toLocaleDateString() : "-"}</span>,
    },
    {
      key: "id",
      label: t("purchases.columns.actions"),
      render: (_, row) => (
        <div className="flex items-center gap-1">
          <button onClick={() => setViewPurchase(row)} className="p-2 text-surface-400 hover:text-primary-600 hover:bg-primary-50 rounded-xl transition-all duration-150" title={t("purchases.viewDetails")}>
            <Eye className="w-4 h-4" />
          </button>
          <button onClick={() => handleViewInvoice(row)} className="p-2 text-surface-400 hover:text-primary-600 hover:bg-primary-50 rounded-xl transition-all duration-150" title={t("purchases.invoice")}>
            <ShoppingCart className="w-4 h-4" />
          </button>
        </div>
      ),
    },
  ];

  const handleViewInvoice = async (purchase) => {
    try {
      const res = await purchaseService.getInvoice(purchase.id);
      setViewInvoice(res.data.data);
    } catch {
      toast.error(t("purchases.failedToLoadInvoice"));
    }
  };

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay message={error.response?.data?.message || error.message} onRetry={refetch} />;

  return (
    <div>
      <PageHeader
        title={t("purchases.title")}
        description={t("purchases.subtitle")}
        actions={
          canManage && !showCreateForm && (
            <button onClick={() => setShowCreateForm(true)} className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white text-[13px] font-semibold rounded-xl hover:from-primary-700 hover:to-primary-800 transition-all duration-150 shadow-sm shadow-primary-600/20">
              <Plus className="w-4 h-4" />
              {t("purchases.newPurchase")}
            </button>
          )
        }
      />

      {showCreateForm && (
        <CreatePurchaseForm
          onDone={() => {
            setShowCreateForm(false);
            queryClient.invalidateQueries({ queryKey: ["purchases"] });
          }}
          onCancel={() => setShowCreateForm(false)}
        />
      )}

      {!showCreateForm && (
        <>
          <div className="mb-6 relative">
            <Search className="w-4 h-4 absolute start-3.5 top-1/2 -translate-y-1/2 text-surface-400 pointer-events-none" />
            <input type="text" placeholder={t("purchases.searchPlaceholder")} value={search} onChange={(e) => setSearch(e.target.value)} className="w-full ps-10 pe-4 py-2.5 border border-surface-200 bg-white rounded-xl text-sm text-surface-800 placeholder:text-surface-300 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150 shadow-card" aria-label={t("purchases.searchAriaLabel")} />
          </div>

          {filtered.length === 0 ? (
            <EmptyState icon={ShoppingCart} title={t("purchases.noPurchasesFound")} description={search ? t("purchases.tryDifferentSearch") : t("purchases.createYourFirst")} action={!search && canManage && <button onClick={() => setShowCreateForm(true)} className="px-4 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white text-[13px] font-semibold rounded-xl hover:from-primary-700 hover:to-primary-800 shadow-sm shadow-primary-600/20">{t("purchases.newPurchase")}</button>} />
          ) : (
            <DataTable columns={columns} data={filtered} />
          )}
        </>
      )}

      <PurchaseDetailModal purchase={viewPurchase} onClose={() => setViewPurchase(null)} />

      <InvoiceModal invoice={viewInvoice} onClose={() => setViewInvoice(null)} />
    </div>
  );
}

function CreatePurchaseForm({ onDone, onCancel }) {
  const { t } = useTranslation();
  const [supplierId, setSupplierId] = useState("");
  const [productSearch, setProductSearch] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [showResults, setShowResults] = useState(false);
  const [searching, setSearching] = useState(false);
  const [items, setItems] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [showAddSupplier, setShowAddSupplier] = useState(false);
  const [supplierForm, setSupplierForm] = useState({ name: "", phone: "", email: "", address: "" });
  const [supplierSaving, setSupplierSaving] = useState(false);
  const [supplierErrors, setSupplierErrors] = useState({});
  const queryClient = useQueryClient();
  const searchRef = useRef(null);
  const debounceRef = useRef(null);

  const { data: suppliers = [] } = useQuery({
    queryKey: ["suppliers"],
    queryFn: async () => {
      const res = await supplierService.getAll();
      return res.data.data;
    },
  });

  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, []);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (searchRef.current && !searchRef.current.contains(e.target)) {
        setShowResults(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleProductSearch = (term) => {
    setProductSearch(term);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (!term.trim()) {
      setSearchResults([]);
      setShowResults(false);
      setSearching(false);
      return;
    }
    setSearching(true);
    setShowResults(true);
    debounceRef.current = setTimeout(async () => {
      try {
        const res = await purchaseService.searchProducts(term);
        setSearchResults(res.data.data);
      } catch { setSearchResults([]); }
      setSearching(false);
    }, 300);
  };

  const addItem = (product) => {
    if (items.find((i) => i.product_id === product.id)) {
      toast.error(t("purchases.validation.productAlreadyAdded"));
      return;
    }
    setItems([...items, {
      product_id: product.id,
      product_name: product.name,
      quantity: 1,
      cost_price: parseFloat(product.purchase_price) || 0,
    }]);
    setProductSearch("");
    setSearchResults([]);
    setShowResults(false);
  };

  const updateItem = (index, field, value) => {
    const updated = [...items];
    updated[index][field] = field === "quantity" ? Math.max(1, parseInt(value) || 1) : parseFloat(value) || 0;
    setItems(updated);
  };

  const removeItem = (index) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const subtotal = items.reduce((sum, item) => sum + item.quantity * item.cost_price, 0);

  const handleAddSupplier = async () => {
    setSupplierErrors({});
    const errors = {};
    if (!supplierForm.name.trim()) errors.name = t("purchases.validation.supplierRequired");
    if (!supplierForm.phone.trim()) errors.phone = t("purchases.validation.phoneRequired");
    if (supplierForm.email.trim() && (!supplierForm.email.includes("@") || !supplierForm.email.split("@")[1].includes("."))) {
      errors.email = t("purchases.validation.invalidEmail");
    }
    if (Object.keys(errors).length > 0) { setSupplierErrors(errors); return; }
    setSupplierSaving(true);
    try {
      const res = await supplierService.create({
        name: supplierForm.name.trim(),
        phone: supplierForm.phone.trim(),
        email: supplierForm.email.trim() || null,
        address: supplierForm.address.trim() || null,
      });
      queryClient.invalidateQueries({ queryKey: ["suppliers"] });
      setSupplierId(res.data.data.id);
      setShowAddSupplier(false);
      setSupplierForm({ name: "", phone: "", email: "", address: "" });
      toast.success(t("purchases.toast.supplierCreated"));
    } catch (err) {
      toast.error(err.response?.data?.message || t("purchases.toast.supplierFailed"));
    } finally {
      setSupplierSaving(false);
    }
  };

  const handleSubmit = async () => {
    if (!supplierId) { toast.error(t("purchases.validation.selectSupplier")); return; }
    if (items.length === 0) { toast.error(t("purchases.validation.addProduct")); return; }
    for (const item of items) {
      if (item.quantity <= 0) { toast.error(t("purchases.validation.quantityPositive")); return; }
      if (item.cost_price < 0) { toast.error(t("purchases.validation.costNotNegative")); return; }
    }
    setSubmitting(true);
    try {
      await purchaseService.create({
        supplier_id: parseInt(supplierId),
        items: items.map((i) => ({
          product_id: i.product_id,
          quantity: i.quantity,
          cost_price: i.cost_price,
        })),
      });
      toast.success(t("purchases.toast.purchaseCreated"));
      onDone();
    } catch (err) {
      toast.error(err.response?.data?.message || t("purchases.toast.purchaseFailed"));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-white border border-surface-200 rounded-2xl p-6 mb-6 shadow-card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-[15px] font-bold text-surface-900">{t("purchases.form.title")}</h2>
        <button onClick={onCancel} className="p-2 text-surface-400 hover:text-surface-600 rounded-xl hover:bg-surface-100 transition-all">
          <X className="w-5 h-5" />
        </button>
      </div>

      <div className="mb-5">
        <label className={LABEL_CLASS}>{t("purchases.form.supplier")}</label>
        <div className="flex gap-2">
          <select value={supplierId} onChange={(e) => setSupplierId(e.target.value)} className={SELECT_CLASS + " flex-1"}>
            <option value="">{t("purchases.form.supplierPlaceholder")}</option>
            {suppliers.map((s) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
          <button
            type="button"
            onClick={() => setShowAddSupplier(true)}
            className="px-3.5 py-2.5 text-[13px] font-semibold text-primary-600 bg-primary-50 border border-primary-200 rounded-xl hover:bg-primary-100 transition-all duration-150 whitespace-nowrap"
          >
            {t("purchases.form.addSupplier")}
          </button>
        </div>
      </div>

      {showAddSupplier && (
        <div className="mb-5 p-4 border border-primary-200 bg-primary-50/40 rounded-xl">
          <h3 className="text-[14px] font-bold text-surface-900 mb-4">{t("purchases.supplierForm.title")}</h3>
          <div className="grid grid-cols-2 gap-3 mb-3">
            <div>
              <label className="block text-[12px] font-semibold text-surface-600 mb-1">{t("purchases.supplierForm.name")}</label>
              <input
                type="text"
                value={supplierForm.name}
                onChange={(e) => setSupplierForm({ ...supplierForm, name: e.target.value })}
                placeholder={t("purchases.supplierForm.namePlaceholder")}
                className={`${INPUT_CLASS} ${supplierErrors.name ? "border-red-300" : ""}`}
              />
              {supplierErrors.name && <p className="text-[11px] text-red-500 mt-0.5">{supplierErrors.name}</p>}
            </div>
            <div>
              <label className="block text-[12px] font-semibold text-surface-600 mb-1">{t("purchases.supplierForm.phone")}</label>
              <input
                type="text"
                value={supplierForm.phone}
                onChange={(e) => setSupplierForm({ ...supplierForm, phone: e.target.value })}
                placeholder={t("purchases.supplierForm.phonePlaceholder")}
                className={`${INPUT_CLASS} ${supplierErrors.phone ? "border-red-300" : ""}`}
              />
              {supplierErrors.phone && <p className="text-[11px] text-red-500 mt-0.5">{supplierErrors.phone}</p>}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3 mb-3">
            <div>
              <label className="block text-[12px] font-semibold text-surface-600 mb-1">{t("purchases.supplierForm.email")}</label>
              <input
                type="email"
                value={supplierForm.email}
                onChange={(e) => setSupplierForm({ ...supplierForm, email: e.target.value })}
                placeholder={t("purchases.supplierForm.emailPlaceholder")}
                className={`${INPUT_CLASS} ${supplierErrors.email ? "border-red-300" : ""}`}
              />
              {supplierErrors.email && <p className="text-[11px] text-red-500 mt-0.5">{supplierErrors.email}</p>}
            </div>
            <div>
              <label className="block text-[12px] font-semibold text-surface-600 mb-1">{t("purchases.supplierForm.address")}</label>
              <input
                type="text"
                value={supplierForm.address}
                onChange={(e) => setSupplierForm({ ...supplierForm, address: e.target.value })}
                placeholder={t("purchases.supplierForm.addressPlaceholder")}
                className={INPUT_CLASS}
              />
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => { setShowAddSupplier(false); setSupplierErrors({}); setSupplierForm({ name: "", phone: "", email: "", address: "" }); }}
              className="px-3.5 py-2 text-[12px] font-semibold text-surface-600 bg-white border border-surface-200 rounded-xl hover:bg-surface-50 transition-all"
            >
              {t("purchases.supplierForm.cancel")}
            </button>
            <button
              type="button"
              onClick={handleAddSupplier}
              disabled={supplierSaving}
              className="px-3.5 py-2 text-[12px] font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl hover:from-primary-700 hover:to-primary-800 disabled:opacity-50 transition-all shadow-sm shadow-primary-600/20"
            >
              {supplierSaving ? t("purchases.supplierForm.saving") : t("purchases.supplierForm.save")}
            </button>
          </div>
        </div>
      )}

      <div className="mb-5" ref={searchRef}>
        <label className={LABEL_CLASS}>{t("purchases.form.addProducts")}</label>
        <div className="relative">
          <Search className="w-4 h-4 absolute start-3.5 top-1/2 -translate-y-1/2 text-surface-400 pointer-events-none" />
          <input
            type="text"
            placeholder={t("purchases.form.searchPlaceholder")}
            value={productSearch}
            onChange={(e) => handleProductSearch(e.target.value)}
            onFocus={() => { if (searchResults.length > 0 || searching) setShowResults(true); }}
            className="w-full ps-10 pe-4 py-2.5 border border-surface-200 bg-white rounded-xl text-sm text-surface-800 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150"
          />
        </div>
        {showResults && (
          <div className="mt-2 border border-surface-200 rounded-xl overflow-hidden bg-white shadow-card max-h-64 overflow-y-auto">
            {searching ? (
              <div className="px-4 py-3 text-[13px] text-surface-400 text-center">{t("purchases.form.searching")}</div>
            ) : searchResults.length === 0 ? (
              <div className="px-4 py-3 text-[13px] text-surface-400 text-center">{t("purchases.form.noProductsFound")}</div>
            ) : (
              searchResults.map((p) => (
                <button key={p.id} onClick={() => addItem(p)} className="flex items-center justify-between w-full px-4 py-2.5 hover:bg-surface-50 text-start transition-colors border-b border-surface-100 last:border-b-0">
                  <div className="min-w-0 flex-1">
                    <span className="text-[13px] font-semibold text-surface-800">{p.name}</span>
                    <div className="flex gap-2 mt-0.5">
                      {p.sku && <span className="text-[11px] font-mono text-surface-400">{t("purchases.form.skuPrefix", { code: p.sku })}</span>}
                      {p.barcode && <span className="text-[11px] font-mono text-surface-400">{t("purchases.form.barcodeFormat", { code: p.barcode })}</span>}
                    </div>
                  </div>
                  <span className="text-[12px] text-surface-500 ms-3 whitespace-nowrap">{formatCurrency(p.purchase_price)}</span>
                </button>
              ))
            )}
          </div>
        )}
      </div>

      {items.length > 0 && (
        <div className="mb-5">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-surface-200">
                  <th className="text-start py-2.5 px-3 text-[12px] font-semibold text-surface-500 uppercase tracking-wider">{t("purchases.items.product")}</th>
                  <th className="text-center py-2.5 px-3 text-[12px] font-semibold text-surface-500 uppercase tracking-wider w-[100px]">{t("purchases.items.qty")}</th>
                  <th className="text-center py-2.5 px-3 text-[12px] font-semibold text-surface-500 uppercase tracking-wider w-[120px]">{t("purchases.items.costPrice")}</th>
                  <th className="text-right py-2.5 px-3 text-[12px] font-semibold text-surface-500 uppercase tracking-wider w-[100px]">{t("purchases.items.subtotal")}</th>
                  <th className="py-2.5 px-3 w-[40px]"></th>
                </tr>
              </thead>
              <tbody>
                {items.map((item, i) => (
                  <tr key={i} className="border-b border-surface-100">
                    <td className="py-2.5 px-3 text-[13px] font-medium text-surface-800">{item.product_name}</td>
                    <td className="py-2.5 px-3">
                      <div className="flex items-center justify-center gap-1">
                        <button onClick={() => updateItem(i, "quantity", item.quantity - 1)} className="p-1 text-surface-400 hover:text-primary-600 rounded-lg hover:bg-primary-50 transition-all"><Minus className="w-3.5 h-3.5" /></button>
                        <input type="number" min="1" value={item.quantity} onChange={(e) => updateItem(i, "quantity", e.target.value)} className="w-14 text-center px-2 py-1 border border-surface-200 bg-surface-50 rounded-lg text-[13px] text-surface-800 focus:outline-none focus:ring-2 focus:ring-primary-500/20" />
                        <button onClick={() => updateItem(i, "quantity", item.quantity + 1)} className="p-1 text-surface-400 hover:text-primary-600 rounded-lg hover:bg-primary-50 transition-all"><PlusIcon className="w-3.5 h-3.5" /></button>
                      </div>
                    </td>
                    <td className="py-2.5 px-3">
                      <input type="number" step="0.01" min="0" value={item.cost_price} onChange={(e) => updateItem(i, "cost_price", e.target.value)} className="w-full px-2 py-1 border border-surface-200 bg-surface-50 rounded-lg text-[13px] text-surface-800 text-center focus:outline-none focus:ring-2 focus:ring-primary-500/20" />
                    </td>
                    <td className="py-2.5 px-3 text-right text-[13px] font-semibold text-surface-800">{formatCurrency(item.quantity * item.cost_price)}</td>
                    <td className="py-2.5 px-3">
                      <button onClick={() => removeItem(i)} className="p-1.5 text-surface-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition-all"><Trash2 className="w-3.5 h-3.5" /></button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="flex justify-end mt-4 pt-4 border-t border-surface-200">
            <div className="text-right">
              <span className="text-[12px] text-surface-500 font-medium">{t("purchases.form.total")}</span>
              <p className="text-xl font-bold text-surface-900">{formatCurrency(subtotal)}</p>
            </div>
          </div>
        </div>
      )}

      <div className="flex justify-end gap-3 pt-5 border-t border-surface-100">
        <button onClick={onCancel} className="px-4 py-2.5 text-[13px] font-semibold text-surface-600 bg-white border border-surface-200 rounded-xl hover:bg-surface-50 transition-all duration-150">{t("purchases.form.cancel")}</button>
        <button onClick={handleSubmit} disabled={submitting || items.length === 0} className="px-6 py-2.5 text-[13px] font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl hover:from-primary-700 hover:to-primary-800 disabled:opacity-50 transition-all duration-150 shadow-sm shadow-primary-600/20">
          {submitting ? t("purchases.form.creating") : t("purchases.form.complete")}
        </button>
      </div>
    </div>
  );
}

function PurchaseDetailModal({ purchase, onClose }) {
  const { t } = useTranslation();
  const { data: details, isLoading } = useQuery({
    queryKey: ["purchase", purchase?.id],
    queryFn: async () => {
      if (!purchase?.id) return null;
      const res = await purchaseService.getById(purchase.id);
      return res.data.data;
    },
    enabled: !!purchase?.id,
  });

  return (
    <Modal isOpen={!!purchase} onClose={onClose} title={t("purchases.detail.title", { number: details?.invoice_number || "" })} size="lg">
      {isLoading ? <LoadingSpinner /> : details ? (
        <div className="space-y-5">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-[12px] font-semibold text-surface-400 uppercase tracking-wider">{t("purchases.detail.supplier")}</span>
              <p className="text-[14px] font-semibold text-surface-800 mt-0.5">{details.supplier_name || "-"}</p>
            </div>
            <div className="text-right">
              <span className="text-[12px] font-semibold text-surface-400 uppercase tracking-wider">{t("purchases.detail.date")}</span>
              <p className="text-[14px] text-surface-800 mt-0.5">{details.created_at ? new Date(details.created_at).toLocaleDateString() : "-"}</p>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-surface-200">
                  <th className="text-start py-2.5 text-[12px] font-semibold text-surface-500 uppercase tracking-wider">{t("purchases.detail.items.product")}</th>
                  <th className="text-center py-2.5 text-[12px] font-semibold text-surface-500 uppercase tracking-wider">{t("purchases.detail.items.qty")}</th>
                  <th className="text-right py-2.5 text-[12px] font-semibold text-surface-500 uppercase tracking-wider">{t("purchases.detail.items.cost")}</th>
                  <th className="text-right py-2.5 text-[12px] font-semibold text-surface-500 uppercase tracking-wider">{t("purchases.detail.items.subtotal")}</th>
                </tr>
              </thead>
              <tbody>
                {details.items?.map((item, i) => (
                  <tr key={i} className="border-b border-surface-100">
                    <td className="py-2.5 text-[13px] text-surface-800">{item.product_name}</td>
                    <td className="py-2.5 text-center text-[13px] text-surface-600">{item.quantity}</td>
                    <td className="py-2.5 text-right text-[13px] text-surface-600">{formatCurrency(item.cost_price)}</td>
                    <td className="py-2.5 text-right text-[13px] font-semibold text-surface-800">{formatCurrency(item.subtotal)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex justify-end pt-3 border-t border-surface-200">
            <div className="text-right">
              <span className="text-[12px] text-surface-500 font-medium">{t("purchases.detail.totalAmount")}</span>
              <p className="text-xl font-bold text-surface-900">{formatCurrency(details.total_amount)}</p>
            </div>
          </div>
        </div>
      ) : null}
    </Modal>
  );
}

function InvoiceModal({ invoice, onClose }) {
  const { t } = useTranslation();
  if (!invoice) return null;
  return (
    <Modal isOpen={!!invoice} onClose={onClose} title={t("purchases.invoiceModal.title", { number: invoice.invoice_number })} size="lg">
      <div className="space-y-5">
        <div className="text-center pb-4 border-b border-surface-200">
          <h2 className="text-lg font-bold text-surface-900">{t("purchases.invoiceModal.header")}</h2>
          <p className="text-[13px] text-surface-500">#{invoice.invoice_number}</p>
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-[12px] font-semibold text-surface-400 uppercase tracking-wider">{t("purchases.invoiceModal.supplier")}</span>
            <p className="text-[14px] font-semibold text-surface-800 mt-0.5">{invoice.supplier_name || "-"}</p>
            {invoice.supplier_phone && <p className="text-[12px] text-surface-500">{invoice.supplier_phone}</p>}
            {invoice.supplier_email && <p className="text-[12px] text-surface-500">{invoice.supplier_email}</p>}
            {invoice.supplier_address && <p className="text-[12px] text-surface-500">{invoice.supplier_address}</p>}
          </div>
          <div className="text-right">
            <span className="text-[12px] font-semibold text-surface-400 uppercase tracking-wider">{t("purchases.invoiceModal.date")}</span>
            <p className="text-[14px] text-surface-800 mt-0.5">{invoice.created_at ? new Date(invoice.created_at).toLocaleDateString() : "-"}</p>
            <span className="text-[12px] font-semibold text-surface-400 uppercase tracking-wider block mt-3">{t("purchases.invoiceModal.processedBy")}</span>
            <p className="text-[14px] text-surface-800 mt-0.5">{invoice.user_name || "-"}</p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-surface-200">
                <th className="text-start py-2.5 text-[12px] font-semibold text-surface-500 uppercase tracking-wider">{t("purchases.invoiceModal.columns.num")}</th>
                <th className="text-start py-2.5 text-[12px] font-semibold text-surface-500 uppercase tracking-wider">{t("purchases.invoiceModal.columns.product")}</th>
                <th className="text-center py-2.5 text-[12px] font-semibold text-surface-500 uppercase tracking-wider">{t("purchases.invoiceModal.columns.barcode")}</th>
                <th className="text-center py-2.5 text-[12px] font-semibold text-surface-500 uppercase tracking-wider">{t("purchases.invoiceModal.columns.qty")}</th>
                <th className="text-right py-2.5 text-[12px] font-semibold text-surface-500 uppercase tracking-wider">{t("purchases.invoiceModal.columns.price")}</th>
                <th className="text-right py-2.5 text-[12px] font-semibold text-surface-500 uppercase tracking-wider">{t("purchases.invoiceModal.columns.total")}</th>
              </tr>
            </thead>
            <tbody>
              {invoice.items?.map((item, i) => (
                <tr key={i} className="border-b border-surface-100">
                  <td className="py-2.5 text-[13px] text-surface-500">{i + 1}</td>
                  <td className="py-2.5 text-[13px] font-medium text-surface-800">{item.product_name}</td>
                  <td className="py-2.5 text-center text-[13px] font-mono text-surface-500">{item.barcode || "-"}</td>
                  <td className="py-2.5 text-center text-[13px] text-surface-600">{item.quantity}</td>
                  <td className="py-2.5 text-right text-[13px] text-surface-600">{formatCurrency(item.cost_price)}</td>
                  <td className="py-2.5 text-right text-[13px] font-semibold text-surface-800">{formatCurrency(item.subtotal)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="flex justify-end pt-3 border-t border-surface-200">
          <div className="text-right">
            <span className="text-[12px] text-surface-500 font-medium">{t("purchases.invoiceModal.totalAmount")}</span>
            <p className="text-2xl font-bold text-surface-900">{formatCurrency(invoice.total_amount)}</p>
          </div>
        </div>

        <div className="text-center pt-4 border-t border-surface-200">
          <p className="text-[11px] text-surface-400">{t("purchases.invoiceModal.footer")}</p>
        </div>
      </div>
    </Modal>
  );
}
