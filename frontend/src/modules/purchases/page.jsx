import { formatCurrency } from "../../utils/formatCurrency";
import { useState, useRef, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { purchaseService } from "./api";
import { supplierService } from "../suppliers/api";
import { useAuth } from "../../shared/context/AuthContext";
import { PageHeader } from "../../shared/components/PageHeader";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
import {
  inputClass, selectClass, labelClass, searchInputClass, filterBarClass, cardClass,
  cardClassOverflowHidden, primaryButtonClass, secondaryButtonClass, ghostButtonClass,
  iconButtonClass, paginationButtonClass, tableHeadClass, tableBodyClass, tableRowClass,
} from "../../shared/components/styles";
import { Plus, Search, ShoppingCart, Trash2, Eye, X, Minus, Plus as PlusIcon, Filter, ChevronLeft, ChevronRight, ReceiptText } from "lucide-react";
import toast from "react-hot-toast";

const INPUT_CLASS = inputClass;
const LABEL_CLASS = labelClass;
const SELECT_CLASS = selectClass;

const PAYMENT_METHODS = ["cash", "card", "transfer", "mixed", "vodafone_cash"];

export default function PurchasesPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const { t, i18n } = useTranslation();
  const canManage = ["admin", "manager"].includes(user?.role);
  const locale = i18n.language === "ar" ? "ar-EG" : "en-US";

  const [search, setSearch] = useState("");
  const [date, setDate] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [page, setPage] = useState(1);
  const perPage = 10;
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [searchParams, setSearchParams] = useSearchParams();
  const newParam = searchParams.get("new") === "1";

  useEffect(() => {
    if (newParam && canManage && !showCreateForm) {
      setShowCreateForm(true);
      const next = new URLSearchParams(searchParams);
      next.delete("new");
      setSearchParams(next, { replace: true });
    }
  }, [newParam, canManage, showCreateForm, searchParams, setSearchParams]);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["purchases", search, date, dateFrom, dateTo, page],
    queryFn: async () => {
      const res = await purchaseService.getAll({
        search: search || undefined,
        date: date || undefined,
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
        page,
        per_page: perPage,
      });
      return res.data.data;
    },
    keepPreviousData: true,
  });

  const items = data?.items ?? [];
  const total = data?.total ?? 0;
  const pages = data?.pages ?? 0;
  const hasFilters = Boolean(search || date || dateFrom || dateTo);

  const clearFilters = () => {
    setSearch("");
    setDate("");
    setDateFrom("");
    setDateTo("");
    setPage(1);
  };

  const paymentLabel = (method) => t(`purchases.paymentMethods.${method}`) || method;

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay message={error.response?.data?.message || error.message} onRetry={refetch} />;

  return (
    <div>
      <PageHeader
        title={t("purchases.title")}
        description={t("purchases.subtitle")}
        actions={
          canManage && !showCreateForm && (
            <button onClick={() => setShowCreateForm(true)} className={primaryButtonClass}>
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
            setPage(1);
            queryClient.invalidateQueries({ queryKey: ["purchases"] });
          }}
          onCancel={() => setShowCreateForm(false)}
        />
      )}

      {!showCreateForm && (
        <>
          {/* Filters */}
          <div className={filterBarClass + " mb-6"}>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 items-end">
              <div className="relative">
                <Search className="w-4 h-4 absolute start-3.5 top-1/2 -translate-y-1/2 text-surface-400 dark:text-surface-500 pointer-events-none" />
                <input type="text" placeholder={t("purchases.searchPlaceholder")} value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} className={searchInputClass} aria-label={t("purchases.searchAriaLabel")} />
              </div>
              <div>
                <label className="block text-[12px] font-semibold text-surface-600 dark:text-surface-400 mb-1">{t("purchases.filters.date")}</label>
                <input type="date" value={date} onChange={(e) => { setDate(e.target.value); setPage(1); }} className={INPUT_CLASS} />
              </div>
              <div>
                <label className="block text-[12px] font-semibold text-surface-600 dark:text-surface-400 mb-1">{t("purchases.filters.from")}</label>
                <input type="date" value={dateFrom} onChange={(e) => { setDateFrom(e.target.value); setPage(1); }} className={INPUT_CLASS} />
              </div>
              <div>
                <label className="block text-[12px] font-semibold text-surface-600 dark:text-surface-400 mb-1">{t("purchases.filters.to")}</label>
                <input type="date" value={dateTo} onChange={(e) => { setDateTo(e.target.value); setPage(1); }} className={INPUT_CLASS} />
              </div>
            </div>
            <div className="flex items-center justify-between mt-3 pt-3 border-t border-surface-100 dark:border-surface-700/60">
              <div className="flex items-center gap-2 text-[12px] text-surface-400 dark:text-surface-500">
                <Filter className="w-4 h-4" />
                <span>{t("purchases.showing", { count: items.length, total })}</span>
              </div>
              {hasFilters && (
                <button onClick={clearFilters} className={ghostButtonClass}>
                  <X className="w-3.5 h-3.5" />
                  {t("purchases.clear")}
                </button>
              )}
            </div>
          </div>

          {/* Table */}
          {items.length === 0 ? (
            <EmptyState
              icon={ShoppingCart}
              title={t("purchases.noPurchasesFound")}
              description={hasFilters ? t("purchases.tryDifferentSearch") : t("purchases.createYourFirst")}
              action={!hasFilters && canManage && <button onClick={() => setShowCreateForm(true)} className={primaryButtonClass}>{t("purchases.newPurchase")}</button>}
            />
          ) : (
            <div className={cardClassOverflowHidden}>
              <div className="overflow-x-auto">
                <table className="w-full text-sm" role="table">
                  <thead>
                    <tr className={tableHeadClass}>
                      <th className="px-5 py-3.5 text-start text-[11px] font-semibold text-surface-500 dark:text-surface-400 uppercase tracking-wider">{t("purchases.columns.invoice")}</th>
                      <th className="px-5 py-3.5 text-start text-[11px] font-semibold text-surface-500 dark:text-surface-400 uppercase tracking-wider">{t("purchases.columns.supplier")}</th>
                      <th className="px-5 py-3.5 text-start text-[11px] font-semibold text-surface-500 dark:text-surface-400 uppercase tracking-wider">{t("purchases.columns.date")}</th>
                      <th className="px-5 py-3.5 text-end text-[11px] font-semibold text-surface-500 dark:text-surface-400 uppercase tracking-wider">{t("purchases.columns.total")}</th>
                      <th className="px-5 py-3.5 text-start text-[11px] font-semibold text-surface-500 dark:text-surface-400 uppercase tracking-wider">{t("purchases.columns.paymentMethod")}</th>
                      <th className="px-5 py-3.5 text-start text-[11px] font-semibold text-surface-500 dark:text-surface-400 uppercase tracking-wider">{t("purchases.columns.createdBy")}</th>
                      <th className="px-5 py-3.5 text-end text-[11px] font-semibold text-surface-500 dark:text-surface-400 uppercase tracking-wider">{t("purchases.columns.actions")}</th>
                    </tr>
                  </thead>
                  <tbody className={tableBodyClass}>
                    {items.map((purchase) => (
                      <tr key={purchase.id} onClick={() => navigate(`/purchases/${purchase.id}`)} className={tableRowClass + " cursor-pointer"}>
                        <td className="px-5 py-3.5 whitespace-nowrap text-[13px] font-mono font-semibold text-surface-800 dark:text-surface-100">{purchase.invoice_number}</td>
                        <td className="px-5 py-3.5 text-[13px] text-surface-600 dark:text-surface-300">{purchase.supplier_name || "—"}</td>
                        <td className="px-5 py-3.5 whitespace-nowrap text-[13px] text-surface-500 dark:text-surface-400">
                          {purchase.created_at ? new Date(purchase.created_at).toLocaleDateString(locale, { year: "numeric", month: "short", day: "numeric" }) : "—"}
                        </td>
                        <td className="px-5 py-3.5 whitespace-nowrap text-end text-[13px] font-semibold text-surface-800 dark:text-surface-100 tabular-nums">{formatCurrency(purchase.total_amount)}</td>
                        <td className="px-5 py-3.5 whitespace-nowrap">
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-primary-50 text-primary-700 dark:bg-primary-500/10 dark:text-primary-400 capitalize">
                            {paymentLabel(purchase.payment_method)}
                          </span>
                        </td>
                        <td className="px-5 py-3.5 whitespace-nowrap text-[13px] text-surface-500 dark:text-surface-400">{purchase.user_name || "—"}</td>
                        <td className="px-5 py-3.5 whitespace-nowrap text-end">
                          <div className="inline-flex items-center gap-1">
                            <button onClick={(e) => { e.stopPropagation(); navigate(`/purchases/${purchase.id}`); }} className={iconButtonClass} title={t("purchases.viewDetails")}>
                              <Eye className="w-4 h-4" />
                            </button>
                            <button onClick={(e) => { e.stopPropagation(); navigate(`/purchases/${purchase.id}`); }} className={iconButtonClass} title={t("purchases.invoice")}>
                              <ReceiptText className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {pages > 1 && (
                <div className="flex items-center justify-between px-5 py-3.5 border-t border-surface-100 dark:border-surface-700/60">
                  <p className="text-[12px] text-surface-400 dark:text-surface-500">{t("purchases.pageOf", { page, pages })}</p>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setPage((p) => Math.max(1, p - 1))}
                      disabled={page <= 1}
                      className={paginationButtonClass}
                    >
                      <ChevronLeft className="w-4 h-4" />
                      {t("purchases.previous")}
                    </button>
                    <button
                      onClick={() => setPage((p) => Math.min(pages, p + 1))}
                      disabled={page >= pages}
                      className={paginationButtonClass}
                    >
                      {t("purchases.next")}
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </>
      )}
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
  const [paymentMethod, setPaymentMethod] = useState("cash");
  const [notes, setNotes] = useState("");
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
      expiration_date: "",
    }]);
    setProductSearch("");
    setSearchResults([]);
    setShowResults(false);
  };

  const updateItem = (index, field, value) => {
    const updated = [...items];
    if (field === "quantity") {
      updated[index][field] = Math.max(1, parseInt(value) || 1);
    } else if (field === "expiration_date") {
      updated[index][field] = value;
    } else {
      updated[index][field] = parseFloat(value) || 0;
    }
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
        payment_method: paymentMethod,
        notes: notes.trim() || null,
        items: items.map((i) => ({
          product_id: i.product_id,
          quantity: i.quantity,
          cost_price: i.cost_price,
          expiration_date: i.expiration_date || null,
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
    <div className={cardClass + " p-6 mb-6"}>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-[15px] font-bold text-surface-900 dark:text-surface-100">{t("purchases.form.title")}</h2>
        <button onClick={onCancel} className="p-2 text-surface-400 hover:text-surface-600 dark:hover:text-surface-200 rounded-xl hover:bg-surface-100 dark:hover:bg-surface-700/50 transition-all">
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
            className="px-3.5 py-2.5 text-[13px] font-semibold text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-500/10 border border-primary-200 dark:border-primary-500/30 rounded-xl hover:bg-primary-100 dark:hover:bg-primary-500/20 transition-all duration-150 whitespace-nowrap"
          >
            {t("purchases.form.addSupplier")}
          </button>
        </div>
      </div>

      {showAddSupplier && (
        <div className="mb-5 p-4 border border-primary-200 dark:border-primary-500/30 bg-primary-50/40 dark:bg-primary-500/5 rounded-xl">
          <h3 className="text-[14px] font-bold text-surface-900 dark:text-surface-100 mb-4">{t("purchases.supplierForm.title")}</h3>
          <div className="grid grid-cols-2 gap-3 mb-3">
            <div>
              <label className="block text-[12px] font-semibold text-surface-600 dark:text-surface-400 mb-1">{t("purchases.supplierForm.name")}</label>
              <input
                type="text"
                value={supplierForm.name}
                onChange={(e) => setSupplierForm({ ...supplierForm, name: e.target.value })}
                placeholder={t("purchases.supplierForm.namePlaceholder")}
                className={`${INPUT_CLASS} ${supplierErrors.name ? "border-red-300 dark:border-red-500/60" : ""}`}
              />
              {supplierErrors.name && <p className="text-[11px] text-red-500 mt-0.5">{supplierErrors.name}</p>}
            </div>
            <div>
              <label className="block text-[12px] font-semibold text-surface-600 dark:text-surface-400 mb-1">{t("purchases.supplierForm.phone")}</label>
              <input
                type="text"
                value={supplierForm.phone}
                onChange={(e) => setSupplierForm({ ...supplierForm, phone: e.target.value })}
                placeholder={t("purchases.supplierForm.phonePlaceholder")}
                className={`${INPUT_CLASS} ${supplierErrors.phone ? "border-red-300 dark:border-red-500/60" : ""}`}
              />
              {supplierErrors.phone && <p className="text-[11px] text-red-500 mt-0.5">{supplierErrors.phone}</p>}
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3 mb-3">
            <div>
              <label className="block text-[12px] font-semibold text-surface-600 dark:text-surface-400 mb-1">{t("purchases.supplierForm.email")}</label>
              <input
                type="email"
                value={supplierForm.email}
                onChange={(e) => setSupplierForm({ ...supplierForm, email: e.target.value })}
                placeholder={t("purchases.supplierForm.emailPlaceholder")}
                className={`${INPUT_CLASS} ${supplierErrors.email ? "border-red-300 dark:border-red-500/60" : ""}`}
              />
              {supplierErrors.email && <p className="text-[11px] text-red-500 mt-0.5">{supplierErrors.email}</p>}
            </div>
            <div>
              <label className="block text-[12px] font-semibold text-surface-600 dark:text-surface-400 mb-1">{t("purchases.supplierForm.address")}</label>
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
              className={secondaryButtonClass}
            >
              {t("purchases.supplierForm.cancel")}
            </button>
            <button
              type="button"
              onClick={handleAddSupplier}
              disabled={supplierSaving}
              className={primaryButtonClass}
            >
              {supplierSaving ? t("purchases.supplierForm.saving") : t("purchases.supplierForm.save")}
            </button>
          </div>
        </div>
      )}

      <div className="mb-5" ref={searchRef}>
        <label className={LABEL_CLASS}>{t("purchases.form.addProducts")}</label>
        <div className="relative">
          <Search className="w-4 h-4 absolute start-3.5 top-1/2 -translate-y-1/2 text-surface-400 dark:text-surface-500 pointer-events-none" />
          <input
            type="text"
            placeholder={t("purchases.form.searchPlaceholder")}
            value={productSearch}
            onChange={(e) => handleProductSearch(e.target.value)}
            onFocus={() => { if (searchResults.length > 0 || searching) setShowResults(true); }}
            className={searchInputClass}
          />
        </div>
        {showResults && (
          <div className="mt-2 border border-surface-200 dark:border-surface-700/60 rounded-xl overflow-hidden bg-white dark:bg-surface-700/40 shadow-card max-h-64 overflow-y-auto">
            {searching ? (
              <div className="px-4 py-3 text-[13px] text-surface-400 dark:text-surface-500 text-center">{t("purchases.form.searching")}</div>
            ) : searchResults.length === 0 ? (
              <div className="px-4 py-3 text-[13px] text-surface-400 dark:text-surface-500 text-center">{t("purchases.form.noProductsFound")}</div>
            ) : (
              searchResults.map((p) => (
                <button key={p.id} onClick={() => addItem(p)} className="flex items-center justify-between w-full px-4 py-2.5 hover:bg-surface-50 dark:hover:bg-surface-700/40 text-start transition-colors border-b border-surface-100 dark:border-surface-700/60 last:border-b-0">
                  <div className="min-w-0 flex-1">
                    <span className="text-[13px] font-semibold text-surface-800 dark:text-surface-100">{p.name}</span>
                    <div className="flex gap-2 mt-0.5">
                      {p.sku && <span className="text-[11px] font-mono text-surface-400 dark:text-surface-500">{t("purchases.form.skuPrefix", { code: p.sku })}</span>}
                      {p.barcode && <span className="text-[11px] font-mono text-surface-400 dark:text-surface-500">{t("purchases.form.barcodeFormat", { code: p.barcode })}</span>}
                    </div>
                  </div>
                  <span className="text-[12px] text-surface-500 dark:text-surface-400 ms-3 whitespace-nowrap">{formatCurrency(p.purchase_price)}</span>
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
                <tr className="border-b border-surface-200 dark:border-surface-700/60">
                  <th className="text-start py-2.5 px-3 text-[12px] font-semibold text-surface-500 dark:text-surface-400 uppercase tracking-wider">{t("purchases.items.product")}</th>
                  <th className="text-center py-2.5 px-3 text-[12px] font-semibold text-surface-500 dark:text-surface-400 uppercase tracking-wider w-[130px]">{t("purchases.items.qty")}</th>
                  <th className="text-center py-2.5 px-3 text-[12px] font-semibold text-surface-500 dark:text-surface-400 uppercase tracking-wider w-[140px]">{t("purchases.items.costPrice")}</th>
                  <th className="text-center py-2.5 px-3 text-[12px] font-semibold text-surface-500 dark:text-surface-400 uppercase tracking-wider w-[150px]">{t("purchases.items.expiration")}</th>
                  <th className="text-end py-2.5 px-3 text-[12px] font-semibold text-surface-500 dark:text-surface-400 uppercase tracking-wider w-[140px]">{t("purchases.items.subtotal")}</th>
                  <th className="py-2.5 px-3 w-[40px]"></th>
                </tr>
              </thead>
              <tbody>
                {items.map((item, i) => (
                  <tr key={i} className="border-b border-surface-100 dark:border-surface-700/60">
                    <td className="py-2.5 px-3 text-[13px] font-medium text-surface-800 dark:text-surface-100">{item.product_name}</td>
                    <td className="py-2.5 px-3">
                      <div className="flex items-center justify-center gap-1">
                        <button onClick={() => updateItem(i, "quantity", item.quantity - 1)} className="p-1 text-surface-400 hover:text-primary-600 dark:hover:text-primary-400 rounded-lg hover:bg-primary-50 dark:hover:bg-primary-500/10 transition-all"><Minus className="w-3.5 h-3.5" /></button>
                        <input type="number" min="1" value={item.quantity} onChange={(e) => updateItem(i, "quantity", e.target.value)} className="numeric-grow min-w-16 text-center px-2 py-1 border border-surface-200 dark:border-surface-700/60 bg-surface-50 dark:bg-surface-700/40 rounded-lg text-[13px] text-surface-800 dark:text-surface-200 focus:outline-none focus:ring-2 focus:ring-primary-500/20" />
                        <button onClick={() => updateItem(i, "quantity", item.quantity + 1)} className="p-1 text-surface-400 hover:text-primary-600 dark:hover:text-primary-400 rounded-lg hover:bg-primary-50 dark:hover:bg-primary-500/10 transition-all"><PlusIcon className="w-3.5 h-3.5" /></button>
                      </div>
                    </td>
                    <td className="py-2.5 px-3">
                      <input type="number" step="0.01" min="0" value={item.cost_price} onChange={(e) => updateItem(i, "cost_price", e.target.value)} className="w-full px-2 py-1 border border-surface-200 dark:border-surface-700/60 bg-surface-50 dark:bg-surface-700/40 rounded-lg text-[13px] text-surface-800 dark:text-surface-200 text-center focus:outline-none focus:ring-2 focus:ring-primary-500/20" />
                    </td>
                    <td className="py-2.5 px-3">
                      <input
                        type="date"
                        value={item.expiration_date}
                        onChange={(e) => updateItem(i, "expiration_date", e.target.value)}
                        aria-label={t("purchases.items.expirationAria")}
                        className="w-full px-2 py-1 border border-surface-200 dark:border-surface-700/60 bg-surface-50 dark:bg-surface-700/40 rounded-lg text-[13px] text-surface-800 dark:text-surface-200 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                      />
                    </td>
                    <td className="py-2.5 px-3 text-end text-[13px] font-semibold text-surface-800 dark:text-surface-100 tabular-nums whitespace-nowrap">{formatCurrency(item.quantity * item.cost_price)}</td>
                    <td className="py-2.5 px-3">
                      <button onClick={() => removeItem(i)} className="p-1.5 text-surface-400 hover:text-red-600 rounded-lg hover:bg-red-50 dark:hover:bg-red-500/10 transition-all"><Trash2 className="w-3.5 h-3.5" /></button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="flex justify-end mt-4 pt-4 border-t border-surface-200 dark:border-surface-700/60">
            <div className="text-end min-w-0">
              <span className="text-[12px] text-surface-500 dark:text-surface-400 font-medium">{t("purchases.form.total")}</span>
              <p className="numeric-value text-xl font-bold text-surface-900 dark:text-surface-100">{formatCurrency(subtotal)}</p>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-5">
        <div>
          <label className={LABEL_CLASS}>{t("purchases.form.paymentMethod")}</label>
          <select value={paymentMethod} onChange={(e) => setPaymentMethod(e.target.value)} className={SELECT_CLASS}>
            {PAYMENT_METHODS.map((m) => (
              <option key={m} value={m}>{t(`purchases.paymentMethods.${m}`)}</option>
            ))}
          </select>
        </div>
        <div>
          <label className={LABEL_CLASS}>{t("purchases.form.notes")}</label>
          <input
            type="text"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder={t("purchases.form.notesPlaceholder")}
            maxLength={1000}
            className={INPUT_CLASS}
          />
        </div>
      </div>

      <div className="flex justify-end gap-3 pt-5 border-t border-surface-100 dark:border-surface-700/60">
        <button onClick={onCancel} className={secondaryButtonClass}>{t("purchases.form.cancel")}</button>
        <button onClick={handleSubmit} disabled={submitting || items.length === 0} className={primaryButtonClass}>
          {submitting ? t("purchases.form.creating") : t("purchases.form.complete")}
        </button>
      </div>
    </div>
  );
}
