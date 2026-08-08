import { formatCurrency } from "../../utils/formatCurrency";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { posService } from "./api";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { useStoreSettings } from "../store-settings/hooks";
import { Printer, ArrowLeft, Plus } from "lucide-react";

export default function InvoicePage() {
  const { saleId } = useParams();
  const navigate = useNavigate();
  const { t, i18n } = useTranslation();
  const isRtl = i18n.language === "ar";
  const { data: storeSettings } = useStoreSettings();

  const { data: invoice, isLoading, error } = useQuery({
    queryKey: ["pos-invoice", saleId],
    queryFn: async () => {
      const res = await posService.getInvoice(saleId);
      return res.data.data;
    },
    retry: false,
  });

  const handlePrint = () => {
    window.print();
  };

  const handleNewSale = () => {
    navigate("/pos", { replace: true });
  };

  const handleBack = () => {
    navigate("/pos");
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-surface-50 dark:bg-surface-900">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error || !invoice) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-surface-50 dark:bg-surface-900">
        <div className="text-center max-w-sm">
          <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-red-50 dark:bg-red-500/10 flex items-center justify-center">
            <Printer className="w-7 h-7 text-red-400" />
          </div>
          <h1 className="text-lg font-bold text-surface-800 dark:text-surface-100 mb-2">{t("pos.invoice.notFound")}</h1>
          <p className="text-sm text-surface-500 dark:text-surface-400 mb-6">
            {t("pos.invoice.notFoundDesc")}
          </p>
          <button
            onClick={handleBack}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-primary-600 text-white text-sm font-semibold hover:bg-primary-700 transition-colors"
          >
            <ArrowLeft className={`w-4 h-4 ${isRtl ? "rotate-180" : ""}`} />
            {t("pos.invoice.backToPos")}
          </button>
        </div>
      </div>
    );
  }

  const locale = i18n.language === "ar" ? "ar-EG" : "en-US";

  const formattedDate = invoice.created_at
    ? new Date(invoice.created_at).toLocaleDateString(locale, {
        year: "numeric",
        month: "long",
        day: "numeric",
      })
    : "—";

  const formattedTime = invoice.created_at
    ? new Date(invoice.created_at).toLocaleTimeString(locale, {
        hour: "2-digit",
        minute: "2-digit",
      })
    : "—";

  const paymentLabel = {
    cash: t("pos.cash"),
    card: t("pos.card"),
    transfer: t("pos.transfer"),
    mixed: t("pos.mixed"),
    vodafone_cash: t("pos.vodafoneCash"),
  }[invoice.payment_method] || invoice.payment_method;

  return (
    <div className="min-h-screen bg-surface-50 dark:bg-surface-900">
      <style>{`
        @media print {
          body * {
            visibility: hidden;
          }
          #invoice-content, #invoice-content * {
            visibility: visible;
          }
          #invoice-content {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
          }
          .no-print {
            display: none !important;
          }
        }
      `}</style>

      <div className="no-print bg-white dark:bg-surface-800 border-b border-surface-200 dark:border-surface-700/60 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={handleBack}
            className="p-2 rounded-xl text-surface-500 dark:text-surface-400 hover:bg-surface-100 dark:hover:bg-surface-700/60 transition-colors"
            title={t("pos.invoice.backToPosTitle")}
          >
            <ArrowLeft className={`w-5 h-5 ${isRtl ? "rotate-180" : ""}`} />
          </button>
          <h1 className="text-base font-bold text-surface-800 dark:text-surface-100">{t("pos.invoice.title")}</h1>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handlePrint}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-primary-600 text-white text-sm font-semibold hover:bg-primary-700 transition-colors"
          >
            <Printer className="w-4 h-4" />
            {t("pos.invoice.print")}
          </button>
          <button
            onClick={handleNewSale}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl border-2 border-surface-200 dark:border-surface-700/60 text-sm font-semibold text-surface-600 dark:text-surface-300 hover:bg-surface-50 dark:hover:bg-surface-700/40 transition-colors"
          >
            <Plus className="w-4 h-4" />
            {t("pos.invoice.newSale")}
          </button>
        </div>
      </div>

      <div id="invoice-content" className="max-w-[210mm] mx-auto py-8 px-6">
        <div className="bg-white dark:bg-surface-800 rounded-2xl border border-surface-200 dark:border-surface-700/60 p-8 shadow-sm">
          <div className="text-center mb-8">
            {storeSettings?.logo_path && (
              <img
                src={`${window.location.origin}/api/store-settings/logo?v=${encodeURIComponent(storeSettings.logo_path)}`}
                alt={storeSettings?.store_name || t("pos.invoice.posSystem")}
                className="w-16 h-16 object-contain mx-auto mb-3"
              />
            )}
            <h2 className="text-xl font-bold text-surface-900 dark:text-surface-100">
              {storeSettings?.store_name || t("pos.invoice.posSystem")}
            </h2>
            {storeSettings?.phone && (
              <p className="text-sm text-surface-500 dark:text-surface-400" dir="ltr">{storeSettings.phone}</p>
            )}
            {storeSettings?.address && (
              <p className="text-sm text-surface-500 dark:text-surface-400 mt-0.5">{storeSettings.address}</p>
            )}
            {storeSettings?.email && (
              <p className="text-sm text-surface-500 dark:text-surface-400" dir="ltr">{storeSettings.email}</p>
            )}
            {storeSettings?.tax_number && (
              <p className="text-sm text-surface-500 dark:text-surface-400">
                {t("pos.invoice.taxNumber")}: {storeSettings.tax_number}
              </p>
            )}
          </div>

          <hr className="border-surface-200 dark:border-surface-700/60 mb-6" />

          <div className="flex items-start justify-between mb-6">
            <div className="space-y-1">
              <p className="text-[11px] font-semibold text-surface-400 dark:text-surface-500 uppercase tracking-wider">{t("pos.invoice.invoiceLabel")}</p>
              <p className="text-base font-bold text-surface-900 dark:text-surface-100">{invoice.invoice_number}</p>
            </div>
            <div className="text-right space-y-1">
              <p className="text-sm text-surface-700 dark:text-surface-200">{formattedDate}</p>
              <p className="text-sm text-surface-500 dark:text-surface-400">{formattedTime}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6 mb-6">
            <div>
              <p className="text-[11px] font-semibold text-surface-400 dark:text-surface-500 uppercase tracking-wider mb-1">{t("pos.invoice.cashier")}</p>
              <p className="text-sm font-medium text-surface-800 dark:text-surface-100">{invoice.cashier_name || "—"}</p>
            </div>
            <div>
              <p className="text-[11px] font-semibold text-surface-400 dark:text-surface-500 uppercase tracking-wider mb-1">{t("pos.invoice.customer")}</p>
              <p className="text-sm font-medium text-surface-800 dark:text-surface-100">
                {invoice.customer_name || <span className="text-surface-400 dark:text-surface-500">{t("pos.invoice.walkInCustomer")}</span>}
              </p>
              {invoice.customer_phone && (
                <p className="text-[13px] text-surface-500 dark:text-surface-400">{invoice.customer_phone}</p>
              )}
            </div>
          </div>

          <table className="w-full mb-6">
            <thead>
              <tr className="border-b-2 border-surface-200 dark:border-surface-700/60">
                <th className="text-start pb-3 text-[11px] font-semibold text-surface-400 dark:text-surface-500 uppercase tracking-wider">
                  {t("pos.invoice.product")}
                </th>
                <th className="text-center pb-3 text-[11px] font-semibold text-surface-400 dark:text-surface-500 uppercase tracking-wider">
                  {t("pos.invoice.qty")}
                </th>
                <th className="text-right pb-3 text-[11px] font-semibold text-surface-400 dark:text-surface-500 uppercase tracking-wider">
                  {t("pos.invoice.unitPrice")}
                </th>
                <th className="text-right pb-3 text-[11px] font-semibold text-surface-400 dark:text-surface-500 uppercase tracking-wider">
                  {t("pos.invoice.total")}
                </th>
              </tr>
            </thead>
            <tbody>
              {invoice.items.map((item) => (
                <tr key={item.id} className="border-b border-surface-100 dark:border-surface-700/60">
                  <td className="py-3 text-sm font-medium text-surface-800 dark:text-surface-100">
                    {item.product_name}
                  </td>
                  <td className="py-3 text-sm text-surface-600 dark:text-surface-300 text-center">
                    {item.quantity}
                  </td>
                  <td className="py-3 text-sm text-surface-600 dark:text-surface-300 text-right tabular-nums">
                    {formatCurrency(item.unit_price)}
                  </td>
                  <td className="py-3 text-sm font-semibold text-surface-800 dark:text-surface-100 text-right tabular-nums">
                    {formatCurrency(item.subtotal)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="flex justify-end mb-6">
            <div className="w-64 space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-surface-500 dark:text-surface-400">{t("pos.invoice.invoiceSubtotal")}</span>
                <span className="font-medium text-surface-800 dark:text-surface-100 tabular-nums">
                  {formatCurrency(invoice.subtotal)}
                </span>
              </div>
              {Number(invoice.discount) > 0 && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-surface-500 dark:text-surface-400">{t("pos.invoice.invoiceDiscount")}</span>
                  <span className="font-medium text-red-600 dark:text-red-400 tabular-nums">
                    {formatCurrency(-invoice.discount)}
                  </span>
                </div>
              )}
              <hr className="border-surface-200 dark:border-surface-700/60" />
              <div className="flex items-center justify-between">
                <span className="text-sm font-bold text-surface-800 dark:text-surface-100">{t("pos.invoice.invoiceGrandTotal")}</span>
                <span className="text-lg font-bold text-primary-600 dark:text-primary-400 tabular-nums">
                  {formatCurrency(invoice.grand_total)}
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-surface-500 dark:text-surface-400">{t("pos.invoice.payment")}</span>
                <span className="font-medium text-surface-700 dark:text-surface-200">{paymentLabel}</span>
              </div>
            </div>
          </div>

          <hr className="border-surface-200 dark:border-surface-700/60 mb-6" />

          <div className="text-center">
            <p className="text-sm text-surface-500 dark:text-surface-400 font-medium">
              {t("pos.invoice.thankYou")}
            </p>
            {storeSettings?.receipt_footer && (
              <p className="text-[13px] text-surface-500 dark:text-surface-400 mt-1.5">{storeSettings.receipt_footer}</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
