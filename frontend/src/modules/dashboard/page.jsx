import { useQuery } from "@tanstack/react-query";
import { dashboardService } from "./api";
import { StatCard } from "../../shared/components/StatCard";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
import { Badge, statusBadge } from "../../shared/components/Badge";
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
        <h1 className="text-2xl font-bold text-surface-900 tracking-tight">POS Dashboard</h1>
        <p className="text-sm text-surface-400 mt-1">Overview of your point of sale system</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <StatCard label="Total Products" value={data.total_products} icon={Package} color="blue" />
        <StatCard label="Categories" value={data.total_categories} icon={FolderOpen} color="purple" />
        <StatCard label="Customers" value={data.total_customers} icon={Users} color="green" />
        <StatCard label="Suppliers" value={data.total_suppliers} icon={Truck} color="orange" />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <StatCard label="Total Sales" value={data.total_sales} icon={ShoppingCart} color="blue" />
        <StatCard label="Total Purchases" value={data.total_purchases} icon={ArrowUpDown} color="green" />
        <StatCard label="Inventory Value" value={`$${(data.inventory_value || 0).toLocaleString()}`} icon={DollarSign} color="purple" />
        <StatCard label="Low Stock Items" value={data.low_stock_products} icon={AlertTriangle} color="orange" />
      </div>

      {/* Today's Activity */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 mb-8">
        <div className="bg-white rounded-2xl border border-surface-200/80 p-6 shadow-card">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center ring-1 ring-primary-100">
              <TrendingUp className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <p className="text-[13px] font-semibold text-surface-800">Today's Sales</p>
              <p className="text-[11px] text-surface-400">{data.todays_sales} transactions</p>
            </div>
          </div>
          <p className="text-3xl font-bold text-surface-900">${(data.todays_revenue || 0).toLocaleString()}</p>
        </div>
        <div className="bg-white rounded-2xl border border-surface-200/80 p-6 shadow-card">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center ring-1 ring-emerald-100">
              <Package className="w-5 h-5 text-emerald-600" />
            </div>
            <div>
              <p className="text-[13px] font-semibold text-surface-800">Inventory Health</p>
              <p className="text-[11px] text-surface-400">{data.total_products} products tracked</p>
            </div>
          </div>
          <p className="text-3xl font-bold text-surface-900">{data.total_products - data.low_stock_products}/{data.total_products}</p>
          <p className="text-[11px] text-surface-400 mt-1">Products adequately stocked</p>
        </div>
      </div>

      {!hasData && (
        <div className="bg-white rounded-2xl border border-surface-200/80 shadow-card">
          <EmptyState
            icon={TrendingUp}
            title="Welcome to POS"
            description="Your system is ready. Start by adding products, customers, and making sales to see your business data here."
          />
        </div>
      )}
    </div>
  );
}
