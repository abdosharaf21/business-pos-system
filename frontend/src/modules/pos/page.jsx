import { useState, useMemo, useCallback, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { posService } from "./api";
import { useBarcodeScanner } from "../../shared/hooks/useBarcodeScanner";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { Badge } from "../../shared/components/Badge";
import { Modal } from "../../shared/components/Modal";
import { inputClass, selectClass, labelClass, primaryButtonClass, secondaryButtonClass } from "../../shared/components/styles";
import toast from "react-hot-toast";
import { formatCurrency } from "../../utils/formatCurrency";
import {
  Search,
  Barcode,
  ShoppingCart,
  Trash2,
  Minus,
  Plus,
  Calculator,
  Package,
  CreditCard,
  User,
  Check,
  Loader2,
} from "lucide-react";

const INPUT_CLASS = inputClass;
const SELECT_CLASS = selectClass;

export default function PosPage() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [cart, setCart] = useState([]);
  const [checkoutOpen, setCheckoutOpen] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState("cash");
  const [customerSearch, setCustomerSearch] = useState("");
  const [customerResults, setCustomerResults] = useState([]);
  const [selectedCustomer, setSelectedCustomer] = useState(null);
  const customerTimeout = useRef(null);

  const {
    data: products = [],
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["pos-products"],
    queryFn: async () => {
      const res = await posService.getProducts();
      return res.data.data;
    },
  });

  const { data: categories = [] } = useQuery({
    queryKey: ["pos-categories"],
    queryFn: async () => {
      const res = await posService.getCategories();
      return res.data.data;
    },
  });

  const checkoutMutation = useMutation({
    mutationFn: (data) => posService.checkout(data),
    onSuccess: (res) => {
      const saleId = res.data.data.id;
      setCart([]);
      setCheckoutOpen(false);
      setSelectedCustomer(null);
      setCustomerSearch("");
      setCustomerResults([]);
      setPaymentMethod("cash");
      navigate(`/pos/invoice/${saleId}`);
    },
    onError: (err) => {
      const msg =
        err.response?.data?.message || t("pos.checkoutFailed");
      toast.error(msg);
    },
  });

  const handleCustomerSearch = useCallback((value) => {
    setCustomerSearch(value);
    setSelectedCustomer(null);
    if (customerTimeout.current) clearTimeout(customerTimeout.current);
    if (!value.trim()) {
      setCustomerResults([]);
      return;
    }
    customerTimeout.current = setTimeout(async () => {
      try {
        const res = await posService.searchCustomers(value);
        setCustomerResults(res.data.data);
      } catch {
        setCustomerResults([]);
      }
    }, 300);
  }, []);

  const handleCheckout = useCallback(() => {
    checkoutMutation.mutate({
      items: cart.map((item) => ({
        product_id: item.id,
        quantity: item.quantity,
        unit_price: item.selling_price,
      })),
      customer_id: selectedCustomer?.id || null,
      payment_method: paymentMethod,
    });
  }, [cart, selectedCustomer, paymentMethod, checkoutMutation]);

  const filtered = useMemo(() => {
    let result = products;
    if (search) {
      const term = search.toLowerCase();
      result = result.filter(
        (p) =>
          p.name?.toLowerCase().includes(term) ||
          (p.barcode && p.barcode.toLowerCase().includes(term))
      );
    }
    if (categoryFilter) {
      result = result.filter((p) => {
        const cat = categories.find((c) => String(c.id) === categoryFilter);
        return p.category === cat?.name;
      });
    }
    return result;
  }, [products, search, categoryFilter, categories]);

  const addToCart = useCallback(
    (product) => {
      setCart((prev) => {
        const existing = prev.find((item) => item.id === product.id);
        if (existing) {
          if (existing.quantity >= product.quantity) {
            return prev;
          }
          return prev.map((item) =>
            item.id === product.id
              ? { ...item, quantity: item.quantity + 1 }
              : item
          );
        }
        return [...prev, { ...product, quantity: 1 }];
      });
    },
    []
  );

  const handleScan = useCallback(
    (barcode) => {
      const term = barcode.trim();
      if (!term) return;
      const product =
        products.find(
          (p) => p.barcode && p.barcode.toLowerCase() === term.toLowerCase()
        ) ||
        products.find(
          (p) => p.sku && p.sku.toLowerCase() === term.toLowerCase()
        );
      if (!product) {
        toast.error(t("pos.productNotFound"));
        return;
      }
      if (product.quantity <= 0) {
        toast.error(t("pos.outOfStock"));
        return;
      }
      addToCart(product);
    },
    [products, addToCart, t]
  );

  const barcodeInputRef = useBarcodeScanner({
    onScan: handleScan,
    enabled: !checkoutOpen,
  });

  useEffect(() => {
    barcodeInputRef.current?.focus();
  }, [barcodeInputRef]);

  const updateQuantity = useCallback((productId, delta) => {
    setCart((prev) => {
      const updated = prev
        .map((item) => {
          if (item.id !== productId) return item;
          const newQty = item.quantity + delta;
          if (newQty < 1) return null;
          return { ...item, quantity: newQty };
        })
        .filter(Boolean);

      const cartItem = updated.find((i) => i.id === productId);
      if (cartItem) {
        const product = products.find((p) => p.id === productId);
        if (product && cartItem.quantity > product.quantity) {
          return prev;
        }
      }
      return updated;
    });
  }, [products]);

  const removeItem = useCallback((productId) => {
    setCart((prev) => prev.filter((item) => item.id !== productId));
  }, []);

  const clearCart = useCallback(() => {
    setCart([]);
  }, []);

  const subtotal = useMemo(
    () => cart.reduce((sum, item) => sum + item.quantity * item.selling_price, 0),
    [cart]
  );

  if (isLoading) return <LoadingSpinner size="lg" />;
  if (error) return <ErrorDisplay message={t("pos.failedToLoadProducts")} onRetry={refetch} />;

  return (
    <div className="h-[calc(100vh-2rem)] flex gap-4 p-4">
      <div className="w-1/2 flex flex-col gap-4 min-w-0">
        <div className="flex gap-3">
          <div className="relative flex-1">
            <Search className="absolute start-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400 dark:text-surface-500" />
            <input
              type="text"
              placeholder={t("pos.searchPlaceholder")}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className={`${INPUT_CLASS} ps-10`}
            />
          </div>
          <div className="relative w-48">
            <Barcode className="absolute start-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400 dark:text-surface-500" />
            <input
              ref={barcodeInputRef}
              type="text"
              data-testid="barcode-input"
              placeholder={t("pos.barcodePlaceholder")}
              defaultValue=""
              autoComplete="off"
              className={`${INPUT_CLASS} ps-10`}
            />
          </div>
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className={`${SELECT_CLASS} w-48`}
          >
            <option value="">{t("pos.allCategories")}</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>
                {cat.name}
              </option>
            ))}
          </select>
        </div>

        <div className="flex-1 overflow-y-auto">
          <div className="grid grid-cols-2 gap-3">
            {filtered.map((product) => (
              <button
                key={product.id}
                onClick={() => addToCart(product)}
                disabled={product.quantity <= 0}
                className={`text-start p-4 rounded-2xl border transition-all duration-150 ${
                  product.quantity <= 0
                    ? "border-surface-200 dark:border-surface-700/60 bg-surface-50 dark:bg-surface-700/30 opacity-50 cursor-not-allowed"
                    : "border-surface-200 dark:border-surface-700/60 bg-white dark:bg-surface-800/60 hover:border-primary-300 dark:hover:border-primary-500/40 hover:shadow-md hover:-translate-y-0.5 cursor-pointer active:scale-[0.98]"
                }`}
              >
                <div className="flex items-start justify-between gap-2 mb-2">
                  <span className="text-sm font-semibold text-surface-800 dark:text-surface-100 leading-tight line-clamp-2">
                    {product.name}
                  </span>
                  {product.quantity <= 0 && (
                    <Badge variant="danger">{t("pos.outOfStock")}</Badge>
                  )}
                  {product.quantity > 0 && product.quantity <= product.minimum_stock && (
                    <Badge variant="warning">{t("pos.lowStock")}</Badge>
                  )}
                </div>
                {product.barcode && (
                  <p className="text-[11px] font-mono text-surface-400 dark:text-surface-500 mb-2">
                    {product.barcode}
                  </p>
                )}
                <div className="flex items-center justify-between gap-2 min-w-0">
                  <span className="numeric-value text-lg font-bold text-primary-600 dark:text-primary-400 leading-snug">
                    {formatCurrency(product.selling_price)}
                  </span>
                  <span className="text-xs text-surface-500 dark:text-surface-400 tabular-nums whitespace-nowrap">
                    <Package className="inline w-3 h-3 me-1" />
                    {product.quantity}
                  </span>
                </div>
              </button>
            ))}
            {filtered.length === 0 && (
              <div className="col-span-2 flex flex-col items-center justify-center py-16 text-surface-400 dark:text-surface-500">
                <Package className="w-12 h-12 mb-3" />
                <p className="text-sm font-medium">{t("pos.noProductsFound")}</p>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="w-1/3 flex flex-col gap-4 min-w-0">
        <div className="bg-white dark:bg-surface-800/60 rounded-2xl border border-surface-200 dark:border-surface-700/60 flex-1 flex flex-col">
          <div className="flex items-center justify-between px-5 py-4 border-b border-surface-100 dark:border-surface-700/60">
            <div className="flex items-center gap-2">
              <ShoppingCart className="w-5 h-5 text-surface-600 dark:text-surface-400" />
              <h2 className="text-sm font-semibold text-surface-800 dark:text-surface-100">
                {t("pos.cartTitle")}
              </h2>
            </div>
            {cart.length > 0 && (
              <span
                data-testid="cart-count"
                className="text-[11px] font-semibold bg-primary-50 dark:bg-primary-500/10 text-primary-600 dark:text-primary-400 px-2.5 py-1 rounded-full"
              >
                {cart.reduce((s, i) => s + i.quantity, 0)}
              </span>
            )}
          </div>

          <div className="flex-1 overflow-y-auto">
            {cart.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-surface-400 dark:text-surface-500 px-4">
                <ShoppingCart className="w-10 h-10 mb-2" />
                <p className="text-sm font-medium">{t("pos.cartEmpty")}</p>
                <p className="text-[11px] mt-1">{t("pos.cartEmptyHint")}</p>
              </div>
            ) : (
              <div className="divide-y divide-surface-100 dark:divide-surface-700/60">
                {cart.map((item) => {
                  const product = products.find((p) => p.id === item.id);
                  const maxQty = product ? product.quantity : Infinity;
                  const canIncrease = item.quantity < maxQty;
                  return (
                    <div
                      key={item.id}
                      className="px-5 py-3 flex items-center gap-3"
                    >
                      <div className="flex-1 min-w-0">
                        <p className="text-[13px] font-semibold text-surface-800 dark:text-surface-100 truncate">
                          {item.name}
                        </p>
                        <p className="text-[11px] text-surface-400 dark:text-surface-500">
                          {t("pos.perUnit", { price: formatCurrency(item.selling_price) })}
                        </p>
                      </div>
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => updateQuantity(item.id, -1)}
                          disabled={item.quantity <= 1}
                          className="w-7 h-7 flex items-center justify-center rounded-lg border border-surface-200 dark:border-surface-700/60 text-surface-500 dark:text-surface-400 hover:bg-surface-50 dark:hover:bg-surface-700/40 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                        >
                          <Minus className="w-3.5 h-3.5" />
                        </button>
                        <span className="min-w-8 px-1 text-center text-sm font-semibold text-surface-800 dark:text-surface-100 tabular-nums">
                          {item.quantity}
                        </span>
                        <button
                          onClick={() => updateQuantity(item.id, 1)}
                          disabled={!canIncrease}
                          className="w-7 h-7 flex items-center justify-center rounded-lg border border-surface-200 dark:border-surface-700/60 text-surface-500 dark:text-surface-400 hover:bg-surface-50 dark:hover:bg-surface-700/40 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
                        >
                          <Plus className="w-3.5 h-3.5" />
                        </button>
                      </div>
                      <div className="min-w-20 text-end">
                        <p className="text-sm font-bold text-surface-800 dark:text-surface-100 tabular-nums whitespace-nowrap">
                          {formatCurrency(item.quantity * item.selling_price)}
                        </p>
                      </div>
                      <button
                        onClick={() => removeItem(item.id)}
                        className="p-1.5 rounded-lg text-surface-300 dark:text-surface-500 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="w-[200px] flex flex-col gap-4 min-w-0">
        <div className="bg-white dark:bg-surface-800/60 rounded-2xl border border-surface-200 dark:border-surface-700/60 p-5">
          <div className="flex items-center gap-2 mb-4">
            <Calculator className="w-4 h-4 text-surface-500 dark:text-surface-400" />
            <h2 className="text-sm font-semibold text-surface-800 dark:text-surface-100">{t("pos.summary")}</h2>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm">
              <span className="text-surface-500 dark:text-surface-400">{t("pos.subtotal")}</span>
              <span className="font-semibold text-surface-800 dark:text-surface-100 tabular-nums">
                {formatCurrency(subtotal)}
              </span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-surface-500 dark:text-surface-400">{t("pos.discount")}</span>
              <span className="text-surface-300 dark:text-surface-500">{formatCurrency(0)}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-surface-500 dark:text-surface-400">{t("pos.tax")}</span>
              <span className="text-surface-300 dark:text-surface-500">—</span>
            </div>
            <hr className="border-surface-100 dark:border-surface-700/60" />
            <div className="flex items-center justify-between">
              <span className="text-sm font-bold text-surface-800 dark:text-surface-100">
                {t("pos.grandTotal")}
              </span>
              <span className="numeric-value text-lg font-bold text-primary-600 dark:text-primary-400 text-end min-w-0">
                {formatCurrency(subtotal)}
              </span>
            </div>
          </div>
        </div>

        <div className="space-y-2">
          <button
            onClick={clearCart}
            disabled={cart.length === 0}
            className={secondaryButtonClass + " w-full py-3"}
          >
            {t("pos.clearCart")}
          </button>
          <button
            onClick={() => setCheckoutOpen(true)}
            disabled={cart.length === 0 || checkoutMutation.isPending}
            className={primaryButtonClass + " w-full py-3.5"}
          >
            {checkoutMutation.isPending ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <CreditCard className="w-4 h-4" />
            )}
            {checkoutMutation.isPending ? null : t("pos.checkout")}
          </button>
        </div>
      </div>

      <Modal
        isOpen={checkoutOpen}
        onClose={() => { if (!checkoutMutation.isPending) { setCheckoutOpen(false); setSelectedCustomer(null); setCustomerSearch(""); setCustomerResults([]); } }}
        title={t("pos.checkoutTitle")}
        maxWidth="max-w-md"
      >
        <div className="space-y-4">
          <div>
            <label className={labelClass}>
              {t("pos.customerLabel")} <span className="text-surface-400 dark:text-surface-500 font-normal">{t("pos.customerOptional")}</span>
            </label>
            <input
              type="text"
              placeholder={t("pos.customerSearchPlaceholder")}
              value={customerSearch}
              onChange={(e) => handleCustomerSearch(e.target.value)}
              className={INPUT_CLASS}
            />
            {customerResults.length > 0 && !selectedCustomer && (
              <div className="mt-1 border border-surface-200 dark:border-surface-700/60 rounded-xl overflow-hidden bg-white dark:bg-surface-700/40">
                {customerResults.map((c) => (
                  <button
                    key={c.id}
                    type="button"
                    onClick={() => {
                      setSelectedCustomer(c);
                      setCustomerSearch(`${c.name} — ${c.phone || ""}`);
                      setCustomerResults([]);
                    }}
                    className="w-full text-start px-3.5 py-2.5 text-sm text-surface-700 dark:text-surface-200 hover:bg-surface-50 dark:hover:bg-surface-700/40 border-b border-surface-100 dark:border-surface-700/60 last:border-0"
                  >
                    <span className="font-medium">{c.name}</span>
                    {c.phone && <span className="text-surface-400 ms-2">{c.phone}</span>}
                  </button>
                ))}
              </div>
            )}
            {selectedCustomer && (
              <div className="mt-1.5 flex items-center gap-2 text-[13px] text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-500/10 px-3 py-2 rounded-xl">
                <User className="w-3.5 h-3.5" />
                <span>{selectedCustomer.name}</span>
              </div>
            )}
          </div>

          <div>
            <label className={labelClass}>
              {t("pos.paymentMethod")}
            </label>
            <select
              value={paymentMethod}
              onChange={(e) => setPaymentMethod(e.target.value)}
              className={SELECT_CLASS}
            >
              <option value="cash">{t("pos.cash")}</option>
              <option value="card">{t("pos.card")}</option>
              <option value="transfer">{t("pos.transfer")}</option>
              <option value="mixed">{t("pos.mixed")}</option>
              <option value="vodafone_cash">{t("pos.vodafoneCash")}</option>
            </select>
          </div>

          <hr className="border-surface-100 dark:border-surface-700/60" />

          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-surface-500 dark:text-surface-400">{t("pos.items")}</span>
              <span className="font-medium text-surface-700 dark:text-surface-200">
                {cart.reduce((s, i) => s + i.quantity, 0)}
              </span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-surface-500 dark:text-surface-400">{t("pos.subtotal")}</span>
              <span className="font-semibold text-surface-800 dark:text-surface-100 tabular-nums">
                {formatCurrency(subtotal)}
              </span>
            </div>
            <hr className="border-surface-100 dark:border-surface-700/60" />
            <div className="flex items-center justify-between">
              <span className="text-sm font-bold text-surface-800 dark:text-surface-100">{t("pos.grandTotal")}</span>
              <span className="numeric-value text-lg font-bold text-primary-600 dark:text-primary-400 text-end min-w-0">
                {formatCurrency(subtotal)}
              </span>
            </div>
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={() => { setCheckoutOpen(false); setSelectedCustomer(null); setCustomerSearch(""); setCustomerResults([]); }}
              disabled={checkoutMutation.isPending}
              className={secondaryButtonClass + " flex-1"}
            >
              {t("pos.cancel")}
            </button>
            <button
              type="button"
              onClick={handleCheckout}
              disabled={checkoutMutation.isPending}
              className={primaryButtonClass + " flex-1"}
            >
              {checkoutMutation.isPending ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Check className="w-4 h-4" />
              )}
              {checkoutMutation.isPending ? t("pos.processing") : t("pos.confirmSale")}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
