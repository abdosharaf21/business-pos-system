import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { posService } from "./api";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { Printer, ArrowLeft, Plus } from "lucide-react";

export default function InvoicePage() {
  const { saleId } = useParams();
  const navigate = useNavigate();

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
      <div className="min-h-screen flex items-center justify-center bg-surface-50">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error || !invoice) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-surface-50">
        <div className="text-center max-w-sm">
          <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-red-50 flex items-center justify-center">
            <Printer className="w-7 h-7 text-red-400" />
          </div>
          <h1 className="text-lg font-bold text-surface-800 mb-2">Invoice Not Found</h1>
          <p className="text-sm text-surface-500 mb-6">
            The sale you are looking for does not exist or has been removed.
          </p>
          <button
            onClick={handleBack}
            className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-primary-600 text-white text-sm font-semibold hover:bg-primary-700 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to POS
          </button>
        </div>
      </div>
    );
  }

  const formattedDate = invoice.created_at
    ? new Date(invoice.created_at).toLocaleDateString("en-US", {
        year: "numeric",
        month: "long",
        day: "numeric",
      })
    : "—";

  const formattedTime = invoice.created_at
    ? new Date(invoice.created_at).toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
      })
    : "—";

  const paymentLabel = {
    cash: "Cash",
    card: "Card",
    transfer: "Transfer",
    mixed: "Mixed",
  }[invoice.payment_method] || invoice.payment_method;

  return (
    <div className="min-h-screen bg-surface-50">
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

      <div className="no-print bg-white border-b border-surface-200 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={handleBack}
            className="p-2 rounded-xl text-surface-500 hover:bg-surface-100 transition-colors"
            title="Back to POS"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h1 className="text-base font-bold text-surface-800">Invoice</h1>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handlePrint}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-primary-600 text-white text-sm font-semibold hover:bg-primary-700 transition-colors"
          >
            <Printer className="w-4 h-4" />
            Print
          </button>
          <button
            onClick={handleNewSale}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl border-2 border-surface-200 text-sm font-semibold text-surface-600 hover:bg-surface-50 transition-colors"
          >
            <Plus className="w-4 h-4" />
            New Sale
          </button>
        </div>
      </div>

      <div id="invoice-content" className="max-w-[210mm] mx-auto py-8 px-6">
        <div className="bg-white rounded-2xl border border-surface-200 p-8 shadow-sm">
          <div className="text-center mb-8">
            <h2 className="text-xl font-bold text-surface-900">POS System</h2>
            <p className="text-sm text-surface-500 mt-0.5">123 Business Avenue, Suite 100</p>
            <p className="text-sm text-surface-500">+1 (555) 123-4567</p>
          </div>

          <hr className="border-surface-200 mb-6" />

          <div className="flex items-start justify-between mb-6">
            <div className="space-y-1">
              <p className="text-[11px] font-semibold text-surface-400 uppercase tracking-wider">Invoice</p>
              <p className="text-base font-bold text-surface-900">{invoice.invoice_number}</p>
            </div>
            <div className="text-right space-y-1">
              <p className="text-sm text-surface-700">{formattedDate}</p>
              <p className="text-sm text-surface-500">{formattedTime}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6 mb-6">
            <div>
              <p className="text-[11px] font-semibold text-surface-400 uppercase tracking-wider mb-1">Cashier</p>
              <p className="text-sm font-medium text-surface-800">{invoice.cashier_name || "—"}</p>
            </div>
            <div>
              <p className="text-[11px] font-semibold text-surface-400 uppercase tracking-wider mb-1">Customer</p>
              <p className="text-sm font-medium text-surface-800">
                {invoice.customer_name || <span className="text-surface-400">Walk-in Customer</span>}
              </p>
              {invoice.customer_phone && (
                <p className="text-[13px] text-surface-500">{invoice.customer_phone}</p>
              )}
            </div>
          </div>

          <table className="w-full mb-6">
            <thead>
              <tr className="border-b-2 border-surface-200">
                <th className="text-left pb-3 text-[11px] font-semibold text-surface-400 uppercase tracking-wider">
                  Product
                </th>
                <th className="text-center pb-3 text-[11px] font-semibold text-surface-400 uppercase tracking-wider">
                  Qty
                </th>
                <th className="text-right pb-3 text-[11px] font-semibold text-surface-400 uppercase tracking-wider">
                  Unit Price
                </th>
                <th className="text-right pb-3 text-[11px] font-semibold text-surface-400 uppercase tracking-wider">
                  Total
                </th>
              </tr>
            </thead>
            <tbody>
              {invoice.items.map((item) => (
                <tr key={item.id} className="border-b border-surface-100">
                  <td className="py-3 text-sm font-medium text-surface-800">
                    {item.product_name}
                  </td>
                  <td className="py-3 text-sm text-surface-600 text-center">
                    {item.quantity}
                  </td>
                  <td className="py-3 text-sm text-surface-600 text-right tabular-nums">
                    ${Number(item.unit_price).toFixed(2)}
                  </td>
                  <td className="py-3 text-sm font-semibold text-surface-800 text-right tabular-nums">
                    ${Number(item.subtotal).toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="flex justify-end mb-6">
            <div className="w-64 space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-surface-500">Subtotal</span>
                <span className="font-medium text-surface-800 tabular-nums">
                  ${Number(invoice.subtotal).toFixed(2)}
                </span>
              </div>
              {Number(invoice.discount) > 0 && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-surface-500">Discount</span>
                  <span className="font-medium text-red-600 tabular-nums">
                    -${Number(invoice.discount).toFixed(2)}
                  </span>
                </div>
              )}
              <hr className="border-surface-200" />
              <div className="flex items-center justify-between">
                <span className="text-sm font-bold text-surface-800">Grand Total</span>
                <span className="text-lg font-bold text-primary-600 tabular-nums">
                  ${Number(invoice.grand_total).toFixed(2)}
                </span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="text-surface-500">Payment</span>
                <span className="font-medium text-surface-700">{paymentLabel}</span>
              </div>
            </div>
          </div>

          <hr className="border-surface-200 mb-6" />

          <div className="text-center">
            <p className="text-sm text-surface-500 font-medium">
              Thank you for your purchase!
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
