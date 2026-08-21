import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer,
} from "recharts";
import {
  DollarSign,
  ShoppingCart,
  ArrowUpDown,
  Package,
  AlertTriangle,
  Clock,
  ReceiptText,
  TrendingUp,
  ClipboardList,
  BarChart3,
  History,
  Bell,
  Zap,
  RefreshCw,
  ChevronRight,
  Inbox,
  CheckCircle2,
  Users,
  ArrowRight,
} from "lucide-react";
import { dashboardService } from "./api";
import { reportService } from "../reports/api";
import { purchaseService } from "../purchases/api";
import { auditService } from "../inventory_audits/api";
import { notificationService } from "../notifications/api";
import { getQuickActions } from "../../shared/layouts/navigationConfig";
import { useAuth } from "../../shared/context/AuthContext";
import { PageHeader } from "../../shared/components/PageHeader";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
import { formatCurrency } from "../../utils/formatCurrency";

const KPI_COLORS = {
  blue: {
    icon: "bg-primary-50 text-primary-600 ring-primary-100",
    value: "text-primary-600",
  },
  green: {
    icon: "bg-emerald-50 text-emerald-600 ring-emerald-100",
    value: "text-emerald-600",
  },
  purple: {
    icon: "bg-violet-50 text-violet-600 ring-violet-100",
    value: "text-violet-600",
  },
  orange: {
    icon: "bg-amber-50 text-amber-600 ring-amber-100",
    value: "text-amber-600",
  },
  red: {
    icon: "bg-red-50 text-red-600 ring-red-100",
    value: "text-red-600",
  },
};

const PANEL_ICON = {
  blue: "bg-primary-50 text-primary-600 ring-primary-100",
  green: "bg-emerald-50 text-emerald-600 ring-emerald-100",
  purple: "bg-violet-50 text-violet-600 ring-violet-100",
  orange: "bg-amber-50 text-amber-600 ring-amber-100",
  red: "bg-red-50 text-red-600 ring-red-100",
};

const AXIS_TICK = { fontSize: 11, fill: "var(--color-surface-400)" };
const AXIS_LINE = { stroke: "var(--color-surface-200)" };
const GRID_LINE = "var(--color-surface-200)";
const TOOLTIP_STYLE = {
  borderRadius: 12,
  border: "1px solid var(--color-surface-200)",
  boxShadow: "0 10px 15px -3px rgb(0 0 0 / 0.1)",
  fontSize: 13,
  backgroundColor: "var(--color-surface-0)",
  color: "var(--color-surface-800)",
};

function toLocalIso(date) {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function lastNDays(n) {
  const out = [];
  const today = new Date();
  for (let i = n - 1; i >= 0; i--) {
    const d = new Date(today);
    d.setDate(today.getDate() - i);
    out.push(toLocalIso(d));
  }
  return out;
}

function fillDailySeries(rows, days, valueKey) {
  const byDate = new Map(
    (rows || []).map((row) => [String(row.date || "").slice(0, 10), row])
  );
  return lastNDays(days).map((date) => {
    const row = byDate.get(date);
    return {
      date,
      [valueKey]: row ? Number(row[valueKey]) : 0,
      count: row ? Number(row.count || 0) : 0,
    };
  });
}

function fillMonths(rows) {
  const byMonth = new Map(
    (rows || []).map((row) => [Number(row.month), row])
  );
  return Array.from({ length: 12 }, (_, i) => {
    const month = i + 1;
    const row = byMonth.get(month);
    return {
      month,
      quantity: row ? Number(row.quantity) : 0,
      count: row ? Number(row.count) : 0,
    };
  });
}

function aggregateByDate(items, days) {
  const totals = {};
  (items || []).forEach((item) => {
    const date = item.created_at ? item.created_at.slice(0, 10) : null;
    if (!date) return;
    totals[date] = (totals[date] || 0) + Number(item.total_amount || 0);
  });
  return lastNDays(days).map((date) => ({
    date,
    total_amount: totals[date] || 0,
  }));
}

function compactNumber(value) {
  const num = Number(value) || 0;
  if (Math.abs(num) >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (Math.abs(num) >= 1000) return `${(num / 1000).toFixed(1)}k`;
  return String(Math.round(num));
}

function KpiCard({ icon: Icon, color = "blue", label, value, subtitle }) {
  const s = KPI_COLORS[color] || KPI_COLORS.blue;
  return (
    <div className="relative overflow-hidden bg-white dark:bg-surface-800 rounded-xl border border-surface-200/80 dark:border-surface-700/60 p-5 shadow-card hover:shadow-card-hover transition-shadow duration-200">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-[12px] font-semibold text-surface-400 dark:text-surface-400 uppercase tracking-wide">{label}</p>
          <p className={`numeric-value mt-1.5 text-[24px] font-bold tracking-tight leading-snug ${s.value}`}>{value}</p>
          {subtitle && (
            <p className="mt-1 text-[12px] text-surface-400 dark:text-surface-400 truncate">{subtitle}</p>
          )}
        </div>
        <div className={`shrink-0 w-10 h-10 rounded-lg flex items-center justify-center ring-1 ${s.icon}`}>
          <Icon className="w-5 h-5" strokeWidth={1.8} />
        </div>
      </div>
    </div>
  );
}

function Panel({ icon: Icon, iconColor = "blue", title, subtitle, action, className, children }) {
  const iconClass = PANEL_ICON[iconColor] || PANEL_ICON.blue;
  return (
    <section className={`bg-white dark:bg-surface-800 rounded-xl border border-surface-200/80 dark:border-surface-700/60 p-5 shadow-card ${className || ""}`}>
      <div className="flex items-start justify-between gap-3 mb-5">
        <div className="flex items-start gap-3 min-w-0">
          <div className={`shrink-0 w-9 h-9 rounded-lg flex items-center justify-center ring-1 ${iconClass}`}>
            <Icon className="w-[18px] h-[18px]" strokeWidth={1.8} />
          </div>
          <div className="min-w-0">
            <h2 className="text-[14px] font-bold text-surface-900 dark:text-surface-100 leading-tight">{title}</h2>
            {subtitle && (
              <p className="text-[12px] text-surface-400 dark:text-surface-400 mt-0.5">{subtitle}</p>
            )}
          </div>
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}

function PanelEmpty({ icon: Icon = Inbox, title, description }) {
  return (
    <div className="flex flex-col items-center justify-center py-10 text-center px-4">
      <div className="w-12 h-12 bg-surface-100 dark:bg-surface-700/50 rounded-lg flex items-center justify-center mb-3 ring-1 ring-surface-200/60">
        <Icon className="w-6 h-6 text-surface-400 dark:text-surface-300" strokeWidth={1.5} />
      </div>
      <p className="text-[13px] font-semibold text-surface-600 dark:text-surface-300">{title}</p>
      {description && (
        <p className="text-[12px] text-surface-400 dark:text-surface-400 mt-1 max-w-xs leading-relaxed">{description}</p>
      )}
    </div>
  );
}

function PanelSkeleton() {
  return (
    <div className="animate-pulse space-y-4 p-2">
      <div className="h-4 w-1/3 bg-surface-200/70 dark:bg-surface-700/50 rounded" />
      <div className="h-32 bg-surface-100/80 dark:bg-surface-700/30 rounded-xl" />
    </div>
  );
}

function PanelError({ message, onRetry }) {
  const { t } = useTranslation();
  return (
    <div className="py-8 text-center">
      <p className="text-[13px] text-red-500 font-medium mb-3">{message || t("common.somethingWentWrong")}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="text-[12px] font-semibold text-primary-600 hover:text-primary-700 inline-flex items-center gap-1.5"
        >
          <RefreshCw className="w-3.5 h-3.5" /> {t("common.tryAgain")}
        </button>
      )}
    </div>
  );
}

function ChartBar({ data, dataKey, color, label, height = 280 }) {
  const { i18n } = useTranslation();
  const locale = i18n.language === "ar" ? "ar-EG" : "en-US";

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 5, right: 8, left: 8, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={GRID_LINE} vertical={false} />
        <XAxis
          dataKey="date"
          tick={AXIS_TICK}
          tickLine={false}
          axisLine={AXIS_LINE}
          tickFormatter={(val) => {
            const d = new Date(`${val}T00:00:00`);
            return d.toLocaleDateString(locale, { month: "short", day: "numeric" });
          }}
          interval="preserveStartEnd"
          minTickGap={24}
        />
        <YAxis
          tick={AXIS_TICK}
          tickLine={false}
          axisLine={AXIS_LINE}
          width={52}
          tickFormatter={compactNumber}
        />
        <Tooltip
          contentStyle={TOOLTIP_STYLE}
          labelFormatter={(val) => {
            const d = new Date(`${val}T00:00:00`);
            return d.toLocaleDateString(locale, {
              weekday: "short", month: "short", day: "numeric", year: "numeric",
            });
          }}
          formatter={(value) => [formatCurrency(Number(value)), label]}
        />
        <Bar dataKey={dataKey} fill={color} radius={[4, 4, 0, 0]} maxBarSize={22} />
      </BarChart>
    </ResponsiveContainer>
  );
}

function MonthChart({ data, color, height = 280 }) {
  const { t, i18n } = useTranslation();
  const locale = i18n.language === "ar" ? "ar-EG" : "en-US";

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} margin={{ top: 5, right: 8, left: 8, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke={GRID_LINE} vertical={false} />
        <XAxis
          dataKey="month"
          tick={AXIS_TICK}
          tickLine={false}
          axisLine={AXIS_LINE}
          tickFormatter={(val) =>
            new Date(2000, Number(val) - 1, 1).toLocaleDateString(locale, { month: "short" })
          }
        />
        <YAxis tick={AXIS_TICK} tickLine={false} axisLine={AXIS_LINE} width={52} tickFormatter={compactNumber} />
        <Tooltip
          contentStyle={TOOLTIP_STYLE}
          labelFormatter={(val) =>
            new Date(2000, Number(val) - 1, 1).toLocaleDateString(locale, { month: "long", year: "numeric" })
          }
          formatter={(value) => [compactNumber(Number(value)), t("dashboard.charts.units")]}
        />
        <Bar dataKey="quantity" fill={color} radius={[4, 4, 0, 0]} maxBarSize={22} />
      </BarChart>
    </ResponsiveContainer>
  );
}

function TopProducts({ products }) {
  const { t } = useTranslation();
  const max = products.length ? Math.max(...products.map((p) => Number(p.revenue) || 0)) : 0;

  if (!products.length) {
    return <PanelEmpty title={t("dashboard.charts.noData")} />;
  }

  return (
    <ul className="space-y-4">
      {products.slice(0, 6).map((product, index) => (
        <li key={product.id}>
          <div className="flex items-center justify-between gap-3 mb-1.5">
            <span className="text-[13px] font-medium text-surface-700 dark:text-surface-200 truncate">
              <span className="text-surface-300 me-1.5 font-semibold">{index + 1}</span>
              {product.name}
            </span>
            <span className="numeric-value text-[13px] font-bold text-surface-900 dark:text-surface-100 shrink-0">
              {formatCurrency(product.revenue)}
            </span>
          </div>
          <div className="h-1.5 rounded-full bg-surface-100 dark:bg-surface-700/60 overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-primary-500 to-primary-400"
              style={{ width: `${max ? (Number(product.revenue) / max) * 100 : 0}%` }}
            />
          </div>
          <p className="mt-1 text-[11px] text-surface-400 dark:text-surface-400">
            {t("dashboard.charts.quantity")}: {Number(product.quantity_sold).toLocaleString()}
          </p>
        </li>
      ))}
    </ul>
  );
}

function LowestStock({ products }) {
  const { t } = useTranslation();
  const show = (products || []).slice(0, 6);

  if (!show.length) {
    return <PanelEmpty title={t("dashboard.charts.noData")} />;
  }

  return (
    <ul className="divide-y divide-surface-100 dark:divide-surface-700/60">
      {show.map((product) => (
        <li key={product.id}>
          <Link
            to="/products"
            className="flex items-center gap-3 py-3 group"
          >
            <div className="w-8 h-8 rounded-lg bg-red-50 dark:bg-red-500/10 text-red-500 flex items-center justify-center ring-1 ring-red-100 shrink-0">
              <Package className="w-4 h-4" strokeWidth={1.8} />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-[13px] font-semibold text-surface-800 dark:text-surface-200 truncate group-hover:text-primary-600">
                {product.name}
              </p>
              <p className="text-[11px] text-surface-400 dark:text-surface-400 truncate">
                {product.category_name || "—"}
              </p>
            </div>
            <div className="text-end shrink-0">
              <p className="numeric-value text-[13px] font-bold text-red-500">{product.total}</p>
              <p className="text-[10px] text-surface-400 dark:text-surface-400">min {product.minimum_stock}</p>
            </div>
          </Link>
        </li>
      ))}
    </ul>
  );
}

function ActivityList({ items, renderItem, emptyTitle }) {
  const { t } = useTranslation();
  if (!items || !items.length) {
    return <PanelEmpty title={emptyTitle || t("common.noDataAvailable")} />;
  }
  return <ul className="divide-y divide-surface-100 dark:divide-surface-700/60">{items.map(renderItem)}</ul>;
}

export default function DashboardPage() {
  const { t, i18n } = useTranslation();
  const locale = i18n.language === "ar" ? "ar-EG" : "en-US";
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const [movementYear, setMovementYear] = useState(new Date().getFullYear());

  const statsQuery = useQuery({
    queryKey: ["dashboard", "stats"],
    queryFn: async () => {
      const res = await dashboardService.getStats();
      return res.data.data;
    },
  });

  const reportsQuery = useQuery({
    queryKey: ["dashboard", "reports"],
    queryFn: async () => {
      const res = await reportService.getDashboard();
      return res.data.data;
    },
  });

  const salesTrendQuery = useQuery({
    queryKey: ["dashboard", "sales-trend"],
    queryFn: async () => {
      const res = await reportService.getSalesTrend({ period: "last_30_days" });
      return res.data.data.data;
    },
  });

  const purchasesQuery = useQuery({
    queryKey: ["dashboard", "purchases"],
    queryFn: async () => {
      const res = await purchaseService.getAll({ page: 1, per_page: 100 });
      return res.data.data;
    },
  });

  const movementQuery = useQuery({
    queryKey: ["dashboard", "movement", movementYear],
    queryFn: async () => {
      const res = await reportService.getMovementReport({ period: "yearly", year: movementYear });
      return res.data.data;
    },
    keepPreviousData: true,
  });

  const topProductsQuery = useQuery({
    queryKey: ["dashboard", "top-products"],
    queryFn: async () => {
      const res = await reportService.getProductsPerformance();
      return res.data.data;
    },
  });

  const expensesQuery = useQuery({
    queryKey: ["dashboard", "expenses-daily"],
    queryFn: async () => {
      const res = await reportService.getExpensesDaily();
      return res.data.data;
    },
  });

  const lowestStockQuery = useQuery({
    queryKey: ["dashboard", "lowest-stock"],
    queryFn: async () => {
      const res = await reportService.getLowestStock();
      return res.data.data;
    },
  });

  const recentAuditsQuery = useQuery({
    queryKey: ["dashboard", "recent-audits"],
    queryFn: async () => {
      const res = await auditService.getAll({ page: 1, per_page: 5, sort: "created_at", order: "desc" });
      return res.data.data;
    },
  });

  const notificationsQuery = useQuery({
    queryKey: ["dashboard", "notifications"],
    queryFn: async () => {
      const res = await notificationService.getAll({ limit: 6 });
      return res.data.data;
    },
  });

  const stats = statsQuery.data;
  const reports = reportsQuery.data;
  const sales = reports?.sales;
  const purchaseSummary = reports?.purchases;

  const purchasesTrend = useMemo(
    () => aggregateByDate(purchasesQuery.data?.items, 30),
    [purchasesQuery.data]
  );

  const salesTrendData = useMemo(
    () => fillDailySeries(salesTrendQuery.data, 30, "total_sales"),
    [salesTrendQuery.data]
  );

  const expensesTrendData = useMemo(
    () => fillDailySeries(expensesQuery.data?.data, 30, "total"),
    [expensesQuery.data]
  );

  const movementData = useMemo(
    () => fillMonths(movementQuery.data?.data),
    [movementQuery.data]
  );

  const pendingPurchases = useMemo(
    () => (purchasesQuery.data?.items || []).filter((p) => p.status === "pending").length,
    [purchasesQuery.data]
  );

  const recentPurchases = purchasesQuery.data?.items?.slice(0, 5) || [];
  const recentSales = reports?.recent_sales || [];
  const recentAudits = recentAuditsQuery.data?.items?.slice(0, 5) || [];
  const notifications = notificationsQuery.data || [];
  const quickActions = getQuickActions("dashboard", user?.role);

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ["dashboard"] });
  };

  const formatTime = (value) => {
    if (!value) return "";
    try {
      return new Date(value).toLocaleString(locale, {
        month: "short",
        day: "numeric",
        hour: "numeric",
        minute: "2-digit",
      });
    } catch {
      return "";
    }
  };

  if (statsQuery.isLoading || reportsQuery.isLoading) return <LoadingSpinner />;
  if (statsQuery.error) {
    return (
      <ErrorDisplay
        message={statsQuery.error.response?.data?.message || statsQuery.error.message}
        onRetry={handleRefresh}
      />
    );
  }
  if (reportsQuery.error) {
    return (
      <ErrorDisplay
        message={reportsQuery.error.response?.data?.message || reportsQuery.error.message}
        onRetry={handleRefresh}
      />
    );
  }

  const hasData =
    stats.total_products > 0 || stats.total_customers > 0 || stats.total_sales > 0;

  return (
    <div className="space-y-6">
      <PageHeader
        title={t("dashboard.title")}
        description={t("dashboard.subtitle")}
        actions={
          <button
            onClick={handleRefresh}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-white dark:bg-surface-800 border border-surface-200/80 dark:border-surface-700/60 text-[13px] font-semibold text-surface-600 dark:text-surface-300 hover:text-primary-600 hover:border-primary-300 shadow-card transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            {t("dashboard.refresh")}
          </button>
        }
      />

      {!hasData && (
        <div className="bg-white dark:bg-surface-800 rounded-2xl border border-surface-200/80 dark:border-surface-700/60 shadow-card">
          <EmptyState
            icon={TrendingUp}
            title={t("dashboard.emptyTitle")}
            description={t("dashboard.emptyDescription")}
          />
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white dark:bg-surface-800 rounded-2xl border border-surface-200/80 dark:border-surface-700/60 p-4 shadow-card">
        <div className="flex flex-wrap items-center gap-2.5">
          <span className="inline-flex items-center gap-2 pe-2 text-[12px] font-semibold text-surface-400 dark:text-surface-400 uppercase tracking-wide">
            <Zap className="w-4 h-4" />
            {t("dashboard.activity.quickActions")}
          </span>
          <span className="hidden sm:block w-px h-6 bg-surface-200/80 dark:bg-surface-700/60" />
          {quickActions.map((action) => {
            const Icon = action.icon;
            return (
              <button
                key={action.id}
                onClick={() => navigate(action.to)}
                className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-surface-50 dark:bg-surface-700/40 text-[13px] font-semibold text-surface-600 dark:text-surface-200 hover:bg-primary-50 dark:hover:bg-primary-500/10 hover:text-primary-700 dark:hover:text-primary-300 ring-1 ring-transparent hover:ring-primary-200 transition-all duration-150"
              >
                <Icon className="w-4 h-4" strokeWidth={1.9} />
                {t(action.labelKey)}
              </button>
            );
          })}
        </div>
      </div>

      {/* KPI Row 1 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-5">
        <KpiCard
          icon={DollarSign}
          color="blue"
          label={t("dashboard.kpis.revenue")}
          value={formatCurrency(sales?.monthly_sales ?? 0)}
          subtitle={t("dashboard.kpis.monthlyRevenueSubtitle")}
        />
        <KpiCard
          icon={ShoppingCart}
          color="green"
          label={t("dashboard.kpis.todaySales")}
          value={stats.todays_sales}
          subtitle={t("dashboard.kpis.todaySalesSubtitle", { count: stats.todays_sales })}
        />
        <KpiCard
          icon={ArrowUpDown}
          color="purple"
          label={t("dashboard.kpis.monthlyPurchases")}
          value={formatCurrency(purchaseSummary?.monthly_purchases ?? 0)}
          subtitle={t("dashboard.kpis.monthlyPurchasesSubtitle")}
        />
        <KpiCard
          icon={Package}
          color="orange"
          label={t("dashboard.kpis.inventoryValue")}
          value={formatCurrency(stats.inventory_value)}
          subtitle={t("dashboard.kpis.inventoryValueSubtitle", { count: stats.total_products })}
        />
        <KpiCard
          icon={AlertTriangle}
          color="red"
          label={t("dashboard.kpis.lowStock")}
          value={stats.low_stock_products}
          subtitle={t("dashboard.kpis.lowStockSubtitle")}
        />
      </div>

      {/* KPI Row 2 */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-5">
        <KpiCard
          icon={Clock}
          color="orange"
          label={t("dashboard.kpis.pendingPurchases")}
          value={pendingPurchases}
          subtitle={t("dashboard.kpis.pendingPurchasesSubtitle")}
        />
        <KpiCard
          icon={ReceiptText}
          color="red"
          label={t("dashboard.kpis.todayExpenses")}
          value={formatCurrency(stats.today_expenses)}
        />
        <KpiCard
          icon={TrendingUp}
          color="blue"
          label={t("dashboard.kpis.avgInvoice")}
          value={formatCurrency(sales?.average_invoice_value ?? 0)}
        />
        <KpiCard
          icon={ClipboardList}
          color="purple"
          label={t("dashboard.kpis.openAudits")}
          value={stats.open_audits}
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <Panel
          icon={BarChart3}
          iconColor="blue"
          title={t("dashboard.charts.salesTrend")}
          subtitle={t("dashboard.charts.salesTrendSubtitle")}
          action={
            <Link to="/reports" className="inline-flex items-center gap-1 text-[12px] font-semibold text-primary-600 hover:text-primary-700">
              {t("dashboard.activity.viewAll")}
              <ChevronRight className="w-3.5 h-3.5 rtl:rotate-180" />
            </Link>
          }
          className="lg:col-span-2"
        >
          {salesTrendQuery.isLoading ? (
            <PanelSkeleton />
          ) : salesTrendQuery.error ? (
            <PanelError message={salesTrendQuery.error.response?.data?.message || salesTrendQuery.error.message} onRetry={handleRefresh} />
          ) : !salesTrendData.some((d) => d.total_sales > 0) ? (
            <PanelEmpty icon={BarChart3} title={t("dashboard.charts.noData")} />
          ) : (
            <ChartBar data={salesTrendData} dataKey="total_sales" color="var(--color-primary-500)" label={t("dashboard.charts.salesTrend")} />
          )}
        </Panel>

        <Panel
          icon={TrendingUp}
          iconColor="green"
          title={t("dashboard.charts.topProducts")}
          subtitle={t("dashboard.charts.topProductsSubtitle")}
        >
          {topProductsQuery.isLoading ? (
            <PanelSkeleton />
          ) : topProductsQuery.error ? (
            <PanelError message={topProductsQuery.error.response?.data?.message || topProductsQuery.error.message} onRetry={handleRefresh} />
          ) : (
            <TopProducts products={topProductsQuery.data?.top_products || []} />
          )}
        </Panel>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <Panel
          icon={ArrowUpDown}
          iconColor="purple"
          title={t("dashboard.charts.purchasesTrend")}
          subtitle={t("dashboard.charts.purchasesTrendSubtitle")}
        >
          {purchasesQuery.isLoading ? (
            <PanelSkeleton />
          ) : purchasesQuery.error ? (
            <PanelError message={purchasesQuery.error.response?.data?.message || purchasesQuery.error.message} onRetry={handleRefresh} />
          ) : !purchasesTrend.some((d) => d.total_amount > 0) ? (
            <PanelEmpty icon={ArrowUpDown} title={t("dashboard.charts.noData")} />
          ) : (
            <ChartBar data={purchasesTrend} dataKey="total_amount" color="var(--color-violet-500)" label={t("dashboard.charts.purchasesTrend")} />
          )}
        </Panel>

        <Panel
          icon={ReceiptText}
          iconColor="orange"
          title={t("dashboard.charts.expensesTrend")}
          subtitle={t("dashboard.charts.expensesTrendSubtitle")}
        >
          {expensesQuery.isLoading ? (
            <PanelSkeleton />
          ) : expensesQuery.error ? (
            <PanelError message={expensesQuery.error.response?.data?.message || expensesQuery.error.message} onRetry={handleRefresh} />
          ) : !expensesTrendData.some((d) => d.total > 0) ? (
            <PanelEmpty icon={ReceiptText} title={t("dashboard.charts.noData")} />
          ) : (
            <ChartBar data={expensesTrendData} dataKey="total" color="var(--color-amber-500)" label={t("dashboard.charts.expensesTrend")} />
          )}
        </Panel>

        <Panel
          icon={History}
          iconColor="orange"
          title={t("dashboard.charts.inventoryMovement")}
          subtitle={t("dashboard.charts.inventoryMovementSubtitle")}
          action={
            <select
              value={movementYear}
              onChange={(e) => setMovementYear(Number(e.target.value))}
              className="px-2.5 py-1.5 rounded-lg border border-surface-200 dark:border-surface-700/60 text-[12px] text-surface-700 dark:text-surface-200 bg-surface-50 dark:bg-surface-700/40 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
            >
              {[new Date().getFullYear(), new Date().getFullYear() - 1, new Date().getFullYear() - 2].map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
          }
        >
          {movementQuery.isLoading ? (
            <PanelSkeleton />
          ) : movementQuery.error ? (
            <PanelError message={movementQuery.error.response?.data?.message || movementQuery.error.message} onRetry={handleRefresh} />
          ) : !movementData.some((d) => d.quantity > 0) ? (
            <PanelEmpty icon={History} title={t("dashboard.charts.noData")} />
          ) : (
            <MonthChart data={movementData} color="var(--color-amber-500)" />
          )}
        </Panel>
      </div>

      {/* Charts Row 3 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <Panel
          icon={Users}
          iconColor="purple"
          title={t("dashboard.charts.topCustomers")}
          subtitle={t("dashboard.charts.topCustomersSubtitle")}
        >
          <PanelEmpty
            icon={Users}
            title={t("dashboard.charts.topCustomersEmptyTitle")}
            description={t("dashboard.charts.topCustomersEmptyDescription")}
          />
        </Panel>

        <Panel
          icon={AlertTriangle}
          iconColor="red"
          title={t("dashboard.kpis.lowStock")}
          subtitle={t("dashboard.kpis.lowStockSubtitle")}
          className="lg:col-span-2"
          action={
            <Link to="/inventory" className="inline-flex items-center gap-1 text-[12px] font-semibold text-primary-600 hover:text-primary-700">
              {t("dashboard.activity.viewAll")}
              <ChevronRight className="w-3.5 h-3.5 rtl:rotate-180" />
            </Link>
          }
        >
          {lowestStockQuery.isLoading ? (
            <PanelSkeleton />
          ) : lowestStockQuery.error ? (
            <PanelError message={lowestStockQuery.error.response?.data?.message || lowestStockQuery.error.message} onRetry={handleRefresh} />
          ) : (
            <LowestStock products={lowestStockQuery.data?.lowest_stock || []} />
          )}
        </Panel>
      </div>

      {/* Activity Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5">
        <Panel
          icon={ShoppingCart}
          iconColor="green"
          title={t("dashboard.activity.recentSales")}
          action={
            <Link to="/reports" className="inline-flex items-center gap-1 text-[12px] font-semibold text-primary-600 hover:text-primary-700">
              {t("dashboard.activity.viewAll")}
              <ChevronRight className="w-3.5 h-3.5 rtl:rotate-180" />
            </Link>
          }
        >
          <ActivityList
            emptyTitle={t("dashboard.activity.noSales")}
            items={recentSales}
            renderItem={(sale) => (
              <li key={sale.id}>
                <Link to={`/pos/invoice/${sale.id}`} className="flex items-center gap-3 py-3 group">
                  <div className="w-8 h-8 rounded-lg bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 ring-1 ring-emerald-100 flex items-center justify-center shrink-0">
                    <CheckCircle2 className="w-4 h-4" strokeWidth={1.8} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-[13px] font-semibold text-surface-800 dark:text-surface-200 truncate group-hover:text-primary-600">
                      {sale.invoice_number}
                    </p>
                    <p className="text-[11px] text-surface-400 dark:text-surface-400">{formatTime(sale.created_at)}</p>
                  </div>
                  <span className="numeric-value text-[13px] font-bold text-emerald-600 shrink-0">
                    {formatCurrency(sale.total_amount)}
                  </span>
                </Link>
              </li>
            )}
          />
        </Panel>

        <Panel
          icon={ArrowUpDown}
          iconColor="purple"
          title={t("dashboard.activity.recentPurchases")}
          action={
            <Link to="/purchases" className="inline-flex items-center gap-1 text-[12px] font-semibold text-primary-600 hover:text-primary-700">
              {t("dashboard.activity.viewAll")}
              <ChevronRight className="w-3.5 h-3.5 rtl:rotate-180" />
            </Link>
          }
        >
          {purchasesQuery.isLoading ? (
            <PanelSkeleton />
          ) : (
            <ActivityList
              emptyTitle={t("dashboard.activity.noPurchases")}
              items={recentPurchases}
              renderItem={(purchase) => (
                <li key={purchase.id}>
                  <Link to={`/purchases/${purchase.id}`} className="flex items-center gap-3 py-3 group">
                    <div className="w-8 h-8 rounded-lg bg-violet-50 dark:bg-violet-500/10 text-violet-600 ring-1 ring-violet-100 flex items-center justify-center shrink-0">
                      <ArrowRight className="w-4 h-4 rtl:rotate-180" strokeWidth={1.8} />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-[13px] font-semibold text-surface-800 dark:text-surface-200 truncate group-hover:text-primary-600">
                        {purchase.supplier_name || purchase.invoice_number}
                      </p>
                      <p className="text-[11px] text-surface-400 dark:text-surface-400 truncate">{purchase.invoice_number}</p>
                    </div>
                    <span className="numeric-value text-[13px] font-bold text-surface-900 dark:text-surface-100 shrink-0">
                      {formatCurrency(purchase.total_amount)}
                    </span>
                  </Link>
                </li>
              )}
            />
          )}
        </Panel>

        <Panel
          icon={ClipboardList}
          iconColor="orange"
          title={t("dashboard.activity.recentAudits")}
          action={
            <Link to="/inventory/audits" className="inline-flex items-center gap-1 text-[12px] font-semibold text-primary-600 hover:text-primary-700">
              {t("dashboard.activity.viewAll")}
              <ChevronRight className="w-3.5 h-3.5 rtl:rotate-180" />
            </Link>
          }
        >
          {recentAuditsQuery.isLoading ? (
            <PanelSkeleton />
          ) : (
            <ActivityList
              emptyTitle={t("dashboard.activity.noAudits")}
              items={recentAudits}
              renderItem={(audit) => (
                <li key={audit.id}>
                  <Link to="/inventory/audits" className="flex items-center gap-3 py-3 group">
                    <div className="w-8 h-8 rounded-lg bg-amber-50 dark:bg-amber-500/10 text-amber-600 ring-1 ring-amber-100 flex items-center justify-center shrink-0">
                      <ClipboardList className="w-4 h-4" strokeWidth={1.8} />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-[13px] font-semibold text-surface-800 dark:text-surface-200 truncate group-hover:text-primary-600">
                        {audit.name || t("dashboard.activity.recentAudits")}
                      </p>
                      <p className="text-[11px] text-surface-400 dark:text-surface-400">{formatTime(audit.created_at)}</p>
                    </div>
                    <span
                      className={`shrink-0 text-[10px] font-semibold uppercase tracking-wide px-2 py-0.5 rounded-full ${
                        audit.status === "completed"
                          ? "bg-emerald-50 text-emerald-700"
                          : audit.status === "cancelled"
                            ? "bg-red-50 text-red-600"
                            : "bg-amber-50 text-amber-700"
                      }`}
                    >
                      {audit.status}
                    </span>
                  </Link>
                </li>
              )}
            />
          )}
        </Panel>

        <Panel
          icon={Bell}
          iconColor="blue"
          title={t("dashboard.activity.notifications")}
          action={
            <Link to="/products" className="inline-flex items-center gap-1 text-[12px] font-semibold text-primary-600 hover:text-primary-700">
              {t("dashboard.activity.viewAll")}
              <ChevronRight className="w-3.5 h-3.5 rtl:rotate-180" />
            </Link>
          }
        >
          {notificationsQuery.isLoading ? (
            <PanelSkeleton />
          ) : (
            <ActivityList
              emptyTitle={t("dashboard.activity.noNotifications")}
              items={notifications}
              renderItem={(notification) => (
                <li key={notification.id}>
                  <Link
                    to={`/products?product=${notification.product_id}`}
                    className="flex items-center gap-3 py-3 group"
                  >
                    <div className="w-8 h-8 rounded-lg bg-primary-50 dark:bg-primary-500/10 text-primary-600 ring-1 ring-primary-100 flex items-center justify-center shrink-0">
                      <Bell className="w-4 h-4" strokeWidth={1.8} />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-[13px] font-semibold text-surface-800 dark:text-surface-200 truncate group-hover:text-primary-600">
                        {notification.product_name}
                      </p>
                      <span className="text-[10px] font-semibold uppercase tracking-wide text-surface-400 dark:text-surface-400">
                        {t(`notifications.types.${notification.notification_type}`)}
                      </span>
                    </div>
                    <span className="shrink-0 text-[10px] text-surface-400 dark:text-surface-400">
                      {formatTime(notification.created_at)}
                    </span>
                  </Link>
                </li>
              )}
            />
          )}
        </Panel>
      </div>
    </div>
  );
}
