import { useTranslation } from "react-i18next";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer,
} from "recharts";
import { dashboardService } from "./api";
import { expenseService } from "../expenses/api";
import { StatCard } from "../../shared/components/StatCard";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
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
  TrendingDown,
  DollarSign,
  ReceiptText,
  Wallet,
  ClipboardList,
  ClipboardCheck,
} from "lucide-react";

export default function DashboardPage() {
  const { t, i18n } = useTranslation();
  const locale = i18n.language === "ar" ? "ar-EG" : "en-US";
  const [expenseYear, setExpenseYear] = useState(new Date().getFullYear());
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["dashboard"],
    queryFn: async () => {
      const res = await dashboardService.getStats();
      return res.data.data;
    },
  });

  const { data: expenseYearData, isLoading: expenseChartLoading, error: expenseChartError } = useQuery({
    queryKey: ["dashboard-expenses-year", expenseYear],
    queryFn: async () => {
      const res = await expenseService.getYearly({ year: expenseYear });
      return res.data.data.data;
    },
    keepPreviousData: true,
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

      {/* Inventory Audits Overview */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <StatCard label={t("dashboard.audits.open")} value={data.open_audits} icon={ClipboardList} color="orange" />
        <StatCard label={t("dashboard.audits.completed")} value={data.completed_audits} icon={ClipboardCheck} color="green" />
      </div>

      {/* Expenses Overview */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <StatCard label={t("dashboard.expenses.today")} value={formatCurrency(data.today_expenses)} icon={ReceiptText} color="orange" />
        <StatCard label={t("dashboard.expenses.month")} value={formatCurrency(data.month_expenses)} icon={Wallet} color="red" />
        <StatCard label={t("dashboard.expenses.year")} value={formatCurrency(data.year_expenses)} icon={TrendingDown} color="blue" />
        <StatCard label={t("dashboard.expenses.avgMonth")} value={formatCurrency(data.avg_month_expenses)} icon={DollarSign} color="purple" />
      </div>

      <div className="bg-white rounded-2xl border border-surface-200/80 p-6 shadow-card mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-[15px] font-semibold text-surface-900">{t("dashboard.expenses.highestCategory")}</h2>
            <p className="text-[13px] text-surface-500 mt-0.5">
              {data.highest_expense_category ? t(`expenses.categories.${data.highest_expense_category}`) : t("dashboard.expenses.noExpenses")}
            </p>
          </div>
          <select
            value={expenseYear}
            onChange={(e) => setExpenseYear(Number(e.target.value))}
            className="px-3 py-1.5 rounded-lg border border-surface-200 text-[12px] text-surface-700 bg-surface-50 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
          >
            {[new Date().getFullYear(), new Date().getFullYear() - 1, new Date().getFullYear() - 2].map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </div>
        {expenseChartLoading ? (
          <LoadingSpinner />
        ) : expenseChartError ? (
          <ErrorDisplay message={expenseChartError.response?.data?.message || expenseChartError.message} />
        ) : !expenseYearData?.length ? (
          <div className="py-10 text-center">
            <ReceiptText className="w-10 h-10 text-surface-300 mx-auto mb-3" />
            <p className="text-surface-400 text-sm font-medium">{t("dashboard.expenses.noExpenses")}</p>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={expenseYearData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis
                dataKey="month"
                tick={{ fontSize: 11, fill: "#94a3b8" }}
                tickLine={false}
                axisLine={{ stroke: "#e2e8f0" }}
                tickFormatter={(val) => new Date(2000, val - 1, 1).toLocaleDateString(locale, { month: "short" })}
              />
              <YAxis
                tick={{ fontSize: 11, fill: "#94a3b8" }}
                tickLine={false}
                axisLine={{ stroke: "#e2e8f0" }}
                tickFormatter={(val) => formatCurrency(val)}
              />
              <Tooltip
                contentStyle={{
                  borderRadius: "12px",
                  border: "1px solid #e2e8f0",
                  boxShadow: "0 10px 15px -3px rgb(0 0 0 / 0.1)",
                  fontSize: "13px",
                }}
                formatter={(value) => formatCurrency(Number(value))}
              />
              <Bar dataKey="total" name={t("dashboard.expenses.month")} fill="var(--color-primary-500, #6366f1)" radius={[4, 4, 0, 0]} maxBarSize={30} />
            </BarChart>
          </ResponsiveContainer>
        )}
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
