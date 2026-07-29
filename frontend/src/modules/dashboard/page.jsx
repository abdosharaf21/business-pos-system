import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import { dashboardService } from "./api";
import { StatCard } from "../../shared/components/StatCard";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
import { Badge, statusBadge } from "../../shared/components/Badge";
import { formatCurrency } from "../../utils/formatCurrency";
import {
  Package,
  FolderOpen,
  Users,
  Truck,
  ShoppingCart,
  ArrowUpDown,
  AlertTriangle,
  TrendingUp,
  DollarSign,
} from "lucide-react";

export default function DashboardPage() {
  const { t } = useTranslation();
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["dashboard"],
    queryFn: async () => {
      const res = await dashboardService.getStats();
      return res.data.data;
    },
  });

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay message={error.response?.data?.message || error.message} onRetry={refetch} />;

  const hasData = data.total_products > 0 || data.total_customers > 0 || data.total_sales > 0;

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-surface-900 tracking-tight">{t("dashboard.title")}</h1>
        <p className="text-sm text-surface-400 mt-1">{t("dashboard.subtitle")}</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <StatCard label={t("dashboard.totalProducts")} value={data.total_products} icon={Package} color="blue" />
        <StatCard label={t("dashboard.categories")} value={data.total_categories} icon={FolderOpen} color="purple" />
        <StatCard label={t("dashboard.customers")} value={data.total_customers} icon={Users} color="green" />
        <StatCard label={t("dashboard.suppliers")} value={data.total_suppliers} icon={Truck} color="orange" />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <StatCard label={t("dashboard.totalSales")} value={data.total_sales} icon={ShoppingCart} color="blue" />
        <StatCard label={t("dashboard.totalPurchases")} value={data.total_purchases} icon={ArrowUpDown} color="green" />
        <StatCard label={t("dashboard.inventoryValue")} value={formatCurrency(data.inventory_value)} icon={DollarSign} color="purple" />
        <StatCard label={t("dashboard.lowStockItems")} value={data.low_stock_products} icon={AlertTriangle} color="orange" />
      </div>

      {/* Today's Activity */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 mb-8">
        <div className="bg-white rounded-2xl border border-surface-200/80 p-6 shadow-card">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center ring-1 ring-primary-100">
              <TrendingUp className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <p className="text-[13px] font-semibold text-surface-800">{t("dashboard.todaysSales")}</p>
              <p className="text-[11px] text-surface-400">{t("dashboard.transactions", { count: data.todays_sales })}</p>
            </div>
          </div>
          <p className="text-3xl font-bold text-surface-900">{formatCurrency(data.todays_revenue)}</p>
        </div>
        <div className="bg-white rounded-2xl border border-surface-200/80 p-6 shadow-card">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center ring-1 ring-emerald-100">
              <Package className="w-5 h-5 text-emerald-600" />
            </div>
            <div>
              <p className="text-[13px] font-semibold text-surface-800">{t("dashboard.inventoryHealth")}</p>
              <p className="text-[11px] text-surface-400">{t("dashboard.productsTracked", { count: data.total_products })}</p>
            </div>
          </div>
          <p className="text-3xl font-bold text-surface-900">{data.total_products - data.low_stock_products}/{data.total_products}</p>
          <p className="text-[11px] text-surface-400 mt-1">{t("dashboard.adequatelyStocked")}</p>
        </div>
      </div>

      {!hasData && (
        <div className="bg-white rounded-2xl border border-surface-200/80 shadow-card">
          <EmptyState
            icon={TrendingUp}
            title={t("dashboard.emptyTitle")}
            description={t("dashboard.emptyDescription")}
          />
        </div>
      )}
    </div>
  );
}
