import { formatCurrency } from "../../utils/formatCurrency";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell,
} from "recharts";
import { reportService } from "./api";
import { PageHeader } from "../../shared/components/PageHeader";
import { StatCard } from "../../shared/components/StatCard";
import { DataTable } from "../../shared/components/DataTable";
import { Badge, statusBadge } from "../../shared/components/Badge";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { cardClass, filterBarClass } from "../../shared/components/styles";
import { getCurrentLocale } from "../../shared/utils/format";
import {
  AXIS_TICK,
  AXIS_LINE,
  GRID_LINE,
  TOOLTIP_STYLE,
} from "../../shared/utils/chartTheme";
import {
  DollarSign, ShoppingCart, Package, AlertTriangle,
  TrendingUp, TrendingDown, Clock, Users, BarChart3,
  Filter, Warehouse, Store, ArrowLeftRight, Wallet, ReceiptText,
  ClipboardList, ClipboardCheck, ArrowUpRight, ArrowDownRight,
  CheckCircle2, XCircle,
} from "lucide-react";

const EXPENSE_COLORS = [
  "#6366f1", "#f59e0b", "#ef4444", "#10b981", "#8b5cf6",
  "#ec4899", "#0ea5e9", "#f97316", "#14b8a6", "#84cc16",
  "#64748b",
];


function DateFilter({ period, onPeriodChange, startDate, endDate, onStartDateChange, onEndDateChange }) {
  const { t } = useTranslation();
  const PERIODS = [
    { key: "last_7_days", label: t("reports.filters.last7Days") },
    { key: "last_30_days", label: t("reports.filters.last30Days") },
    { key: "custom", label: t("reports.filters.custom") },
  ];
  return (
    <div className={filterBarClass + " mb-6 flex flex-wrap items-center gap-3"}>
      <Filter className="w-5 h-5 text-surface-400 dark:text-surface-500 shrink-0" />
      {PERIODS.map((p) => (
        <button
          key={p.key}
          onClick={() => onPeriodChange(p.key)}
          className={`px-4 py-2 rounded-xl text-[13px] font-medium transition-all duration-150 ${
            period === p.key
              ? "bg-primary-50 dark:bg-primary-500/10 text-primary-700 dark:text-primary-400 ring-1 ring-primary-200 dark:ring-primary-500/30"
              : "bg-surface-50 dark:bg-surface-700/40 text-surface-500 dark:text-surface-400 hover:bg-surface-100 dark:hover:bg-surface-700/60 hover:text-surface-700 dark:hover:text-surface-200"
          }`}
        >
          {p.label}
        </button>
      ))}
      {period === "custom" && (
        <div className="flex items-center gap-2 ms-2">
          <input
            type="date"
            value={startDate}
            onChange={(e) => onStartDateChange(e.target.value)}
            className="px-3 py-2 rounded-xl border border-surface-200 dark:border-surface-700/60 text-[13px] text-surface-700 dark:text-surface-200 bg-surface-50 dark:bg-surface-700/40 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
          />
          <span className="text-surface-400 dark:text-surface-500 text-[13px]">{t("reports.filters.to")}</span>
          <input
            type="date"
            value={endDate}
            onChange={(e) => onEndDateChange(e.target.value)}
            className="px-3 py-2 rounded-xl border border-surface-200 dark:border-surface-700/60 text-[13px] text-surface-700 dark:text-surface-200 bg-surface-50 dark:bg-surface-700/40 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
          />
        </div>
      )}
    </div>
  );
}

function SectionHeader({ icon: Icon, title }) {
  return (
    <div className="flex items-center gap-2 mb-5">
      <div className="w-8 h-8 rounded-lg bg-primary-50 dark:bg-primary-500/10 flex items-center justify-center ring-1 ring-primary-100 dark:ring-primary-500/20">
        <Icon className="w-4 h-4 text-primary-600 dark:text-primary-400" />
      </div>
      <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-100">{title}</h2>
    </div>
  );
}

function SalesTrendChart({ data }) {
  const { t, i18n } = useTranslation();
  const locale = getCurrentLocale(i18n.language);

  if (!data || data.length === 0) {
    return (
      <div className={cardClass + " p-12 text-center"}>
        <BarChart3 className="w-12 h-12 text-surface-300 dark:text-surface-600 mx-auto mb-3" />
        <p className="text-surface-400 dark:text-surface-500 text-sm font-medium">{t("reports.charts.noSalesData")}</p>
      </div>
    );
  }

  return (
    <div className={cardClass + " p-6"}>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={GRID_LINE} />
          <XAxis
            dataKey="date"
            tick={AXIS_TICK}
            tickLine={false}
            axisLine={AXIS_LINE}
            tickFormatter={(val) => {
              const d = new Date(val + "T00:00:00");
              return d.toLocaleDateString(locale, { month: "short", day: "numeric" });
            }}
          />
          <YAxis
            tick={AXIS_TICK}
            tickLine={false}
            axisLine={AXIS_LINE}
            tickFormatter={(val) => formatCurrency(val)}
          />
          <Tooltip
            contentStyle={TOOLTIP_STYLE}
            labelFormatter={(val) => {
              const d = new Date(val + "T00:00:00");
              return d.toLocaleDateString(locale, {
                weekday: "short", month: "short", day: "numeric", year: "numeric",
              });
            }}
          />
          <Bar
            dataKey="total_sales"
            fill="var(--color-primary-500, #6366f1)"
            radius={[4, 4, 0, 0]}
            maxBarSize={40}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function ProfitCards({ data }) {
  const { t } = useTranslation();
  if (!data) return null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
      <StatCard
        label={t("reports.profitCards.revenue")}
        value={formatCurrency(data.total_revenue)}
        icon={TrendingUp}
        color="green"
      />
      <StatCard
        label={t("reports.profitCards.purchaseCost")}
        value={formatCurrency(data.total_purchase_cost)}
        icon={TrendingDown}
        color="orange"
      />
      <StatCard
        label={t("reports.profitCards.grossProfit")}
        value={formatCurrency(data.gross_profit)}
        icon={DollarSign}
        color="blue"
      />
      <StatCard
        label={t("reports.profitCards.profitMargin")}
        value={`${(data.profit_margin || 0).toFixed(1)}%`}
        icon={BarChart3}
        color="purple"
      />
    </div>
  );
}

function getDefaultDates(period) {
  const today = new Date();
  const toInput = (d) => d.toISOString().split("T")[0];
  if (period === "last_7_days") {
    const start = new Date(today);
    start.setDate(start.getDate() - 6);
    return { startDate: toInput(start), endDate: toInput(today) };
  }
  if (period === "last_30_days") {
    const start = new Date(today);
    start.setDate(start.getDate() - 29);
    return { startDate: toInput(start), endDate: toInput(today) };
  }
  return { startDate: toInput(today), endDate: toInput(today) };
}

export default function ReportsPage() {
  const { t, i18n } = useTranslation();
  const locale = getCurrentLocale(i18n.language);
  const [period, setPeriod] = useState("last_30_days");
  const defaults = getDefaultDates(period);
  const [startDate, setStartDate] = useState(defaults.startDate);
  const [endDate, setEndDate] = useState(defaults.endDate);

  const handlePeriodChange = (newPeriod) => {
    setPeriod(newPeriod);
    const d = getDefaultDates(newPeriod);
    setStartDate(d.startDate);
    setEndDate(d.endDate);
  };

  const trendParams = { period };
  if (period === "custom") {
    trendParams.start_date = startDate;
    trendParams.end_date = endDate;
  }

  const profitParams = { period: "custom", start_date: startDate, end_date: endDate };

  const { data: dashData, isLoading: dashLoading, error: dashError, refetch: refetchDash } = useQuery({
    queryKey: ["reports-dashboard"],
    queryFn: async () => {
      const res = await reportService.getDashboard();
      return res.data.data;
    },
  });

  const { data: trendData, isLoading: trendLoading, error: trendError } = useQuery({
    queryKey: ["reports-sales-trend", trendParams],
    queryFn: async () => {
      const res = await reportService.getSalesTrend(trendParams);
      return res.data.data;
    },
    keepPreviousData: true,
  });

  const { data: profitData, isLoading: profitLoading, error: profitError } = useQuery({
    queryKey: ["reports-profit", profitParams],
    queryFn: async () => {
      const res = await reportService.getProfit(profitParams);
      return res.data.data;
    },
    keepPreviousData: true,
  });

  const { data: productData, isLoading: productLoading, error: productError } = useQuery({
    queryKey: ["reports-products-performance"],
    queryFn: async () => {
      const res = await reportService.getProductsPerformance();
      return res.data.data;
    },
  });

  const { data: supplierData, isLoading: supplierLoading, error: supplierError } = useQuery({
    queryKey: ["reports-suppliers-performance"],
    queryFn: async () => {
      const res = await reportService.getSuppliersPerformance();
      return res.data.data;
    },
  });

  const [reportYear, setReportYear] = useState(new Date().getFullYear());
  const [reportMonth, setReportMonth] = useState(new Date().getMonth() + 1);

  const { data: inventoryReport, isLoading: inventoryReportLoading, error: inventoryReportError } = useQuery({
    queryKey: ["reports-inventory-report"],
    queryFn: async () => {
      const res = await reportService.getInventoryReport();
      return res.data.data.inventory;
    },
  });

  const { data: monthlyMovement, isLoading: monthlyLoading, error: monthlyError } = useQuery({
    queryKey: ["reports-movement-monthly", reportYear, reportMonth],
    queryFn: async () => {
      const res = await reportService.getMovementReport({
        period: "monthly",
        year: reportYear,
        month: reportMonth,
      });
      return res.data.data.data;
    },
    keepPreviousData: true,
  });

  const { data: yearlyMovement, isLoading: yearlyLoading, error: yearlyError } = useQuery({
    queryKey: ["reports-movement-yearly", reportYear],
    queryFn: async () => {
      const res = await reportService.getMovementReport({
        period: "yearly",
        year: reportYear,
      });
      return res.data.data.data;
    },
    keepPreviousData: true,
  });

  const { data: mostTransferred, isLoading: mostTransferredLoading, error: mostTransferredError } = useQuery({
    queryKey: ["reports-most-transferred"],
    queryFn: async () => {
      const res = await reportService.getMostTransferred();
      return res.data.data.most_transferred;
    },
  });

  const { data: lowestStock, isLoading: lowestStockLoading, error: lowestStockError } = useQuery({
    queryKey: ["reports-lowest-stock"],
    queryFn: async () => {
      const res = await reportService.getLowestStock();
      return res.data.data.lowest_stock;
    },
  });

  const [expensePeriod, setExpensePeriod] = useState("last_30_days");
  const expenseDefaults = getDefaultDates(expensePeriod);
  const [expenseStartDate, setExpenseStartDate] = useState(expenseDefaults.startDate);
  const [expenseEndDate, setExpenseEndDate] = useState(expenseDefaults.endDate);

  const handleExpensePeriodChange = (newPeriod) => {
    setExpensePeriod(newPeriod);
    const d = getDefaultDates(newPeriod);
    setExpenseStartDate(d.startDate);
    setExpenseEndDate(d.endDate);
  };

  const expenseParams = expensePeriod === "custom"
    ? { start_date: expenseStartDate, end_date: expenseEndDate }
    : { start_date: expenseStartDate, end_date: expenseEndDate };

  const { data: expensesDaily, isLoading: expensesDailyLoading, error: expensesDailyError } = useQuery({
    queryKey: ["reports-expenses-daily", expenseStartDate, expenseEndDate],
    queryFn: async () => {
      const res = await reportService.getExpensesDaily(expenseParams);
      return res.data.data;
    },
    keepPreviousData: true,
  });

  const { data: expensesCategory, isLoading: expensesCategoryLoading, error: expensesCategoryError } = useQuery({
    queryKey: ["reports-expenses-category", expenseStartDate, expenseEndDate],
    queryFn: async () => {
      const res = await reportService.getExpensesCategory(expenseParams);
      return res.data.data.data;
    },
    keepPreviousData: true,
  });

  const { data: expensesPayment, isLoading: expensesPaymentLoading, error: expensesPaymentError } = useQuery({
    queryKey: ["reports-expenses-payment", expenseStartDate, expenseEndDate],
    queryFn: async () => {
      const res = await reportService.getExpensesPaymentMethod(expenseParams);
      return res.data.data.data;
    },
    keepPreviousData: true,
  });

  const [expenseComparisonYear, setExpenseComparisonYear] = useState(new Date().getFullYear());

  const { data: expensesMonthlyComparison, isLoading: expensesMonthlyComparisonLoading, error: expensesMonthlyComparisonError } = useQuery({
    queryKey: ["reports-expenses-monthly-comparison", expenseComparisonYear],
    queryFn: async () => {
      const res = await reportService.getExpensesMonthlyComparison({ year: expenseComparisonYear });
      return res.data.data.data;
    },
    keepPreviousData: true,
  });

  const { data: expensesHighest, isLoading: expensesHighestLoading, error: expensesHighestError } = useQuery({
    queryKey: ["reports-expenses-highest"],
    queryFn: async () => {
      const res = await reportService.getExpensesHighestCategories();
      return res.data.data.highest_categories;
    },
  });

  const [auditComparisonYear, setAuditComparisonYear] = useState(new Date().getFullYear());

  const { data: auditReport, isLoading: auditReportLoading, error: auditReportError } = useQuery({
    queryKey: ["reports-inventory-audits"],
    queryFn: async () => {
      const res = await reportService.getInventoryAuditReport();
      return res.data.data;
    },
  });

  const { data: auditsMonthly, isLoading: auditsMonthlyLoading, error: auditsMonthlyError } = useQuery({
    queryKey: ["reports-inventory-audits-monthly", auditComparisonYear],
    queryFn: async () => {
      const res = await reportService.getInventoryAuditsMonthly({ year: auditComparisonYear });
      return res.data.data.data;
    },
    keepPreviousData: true,
  });

  const { data: auditsYearly, isLoading: auditsYearlyLoading, error: auditsYearlyError } = useQuery({
    queryKey: ["reports-inventory-audits-yearly", auditComparisonYear],
    queryFn: async () => {
      const res = await reportService.getInventoryAuditsYearly({ from_year: auditComparisonYear - 4, to_year: auditComparisonYear });
      return res.data.data.data;
    },
    keepPreviousData: true,
  });

  if (dashLoading) return <LoadingSpinner />;
  if (dashError) return <ErrorDisplay message={dashError.response?.data?.message || dashError.message} onRetry={refetchDash} />;

  const { sales, purchases, inventory, top_selling_products, recent_sales } = dashData;

  return (
    <div>
      <PageHeader
        title={t("reports.title")}
        description={t("reports.description")}
      />

      {/* Phase 1 - Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <StatCard label={t("reports.summary.todaySales")} value={formatCurrency(sales.today_sales)} icon={DollarSign} color="blue" />
        <StatCard label={t("reports.summary.monthlySales")} value={formatCurrency(sales.monthly_sales)} icon={TrendingUp} color="green" />
        <StatCard label={t("reports.summary.totalInvoices")} value={sales.total_invoices || 0} icon={ShoppingCart} color="purple" />
        <StatCard label={t("reports.summary.avgInvoiceValue")} value={formatCurrency(sales.average_invoice_value)} icon={DollarSign} color="orange" />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <StatCard label={t("reports.summary.todayPurchases")} value={formatCurrency(purchases.today_purchases)} icon={ShoppingCart} color="blue" />
        <StatCard label={t("reports.summary.monthlyPurchases")} value={formatCurrency(purchases.monthly_purchases)} icon={TrendingUp} color="green" />
        <StatCard label={t("reports.summary.inventoryValue")} value={formatCurrency(inventory.inventory_value)} icon={Package} color="purple" />
        <StatCard label={t("reports.summary.lowStockItems")} value={inventory.low_stock_count || 0} icon={AlertTriangle} color="orange" />
      </div>

      {/* Phase 1 - Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-12">
        <div>
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-primary-600 dark:text-primary-400" />
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-100">{t("reports.topSelling.title")}</h2>
          </div>
          <DataTable
            columns={[
              { key: "name", label: t("reports.topSelling.product") },
              { key: "total_quantity", label: t("reports.topSelling.qtySold") },
              { key: "total_revenue", label: t("reports.topSelling.revenue"), render: (val) => <span className="tabular-nums whitespace-nowrap">{formatCurrency(val)}</span> },
            ]}
            data={top_selling_products}
            emptyMessage={t("reports.topSelling.empty")}
          />
        </div>
        <div>
          <div className="flex items-center gap-2 mb-4">
            <Clock className="w-5 h-5 text-primary-600 dark:text-primary-400" />
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-100">{t("reports.recentSales.title")}</h2>
          </div>
          <DataTable
            columns={[
              { key: "invoice_number", label: t("reports.recentSales.invoice") },
              { key: "total_amount", label: t("reports.recentSales.amount"), render: (val) => <span className="tabular-nums whitespace-nowrap">{formatCurrency(val)}</span> },
              { key: "created_at", label: t("reports.recentSales.date"), render: (val) => val ? new Date(val).toLocaleDateString(locale, { year: "numeric", month: "short", day: "numeric" }) : "-" },
            ]}
            data={recent_sales}
            emptyMessage={t("reports.recentSales.empty")}
          />
        </div>
      </div>

      {/* Phase 2 - Sales Analytics */}
      <div className="mb-8 pt-8 border-t border-surface-200 dark:border-surface-700/60">
        <SectionHeader icon={BarChart3} title={t("reports.salesAnalytics")} />
        <DateFilter
          period={period}
          onPeriodChange={handlePeriodChange}
          startDate={startDate}
          endDate={endDate}
          onStartDateChange={setStartDate}
          onEndDateChange={setEndDate}
        />
        {trendLoading ? (
          <div className={cardClass + " p-16"}>
            <LoadingSpinner />
          </div>
        ) : trendError ? (
          <ErrorDisplay message={trendError.response?.data?.message || trendError.message} />
        ) : (
          <SalesTrendChart data={trendData?.data} />
        )}
      </div>

      {/* Phase 2 - Profit Analytics */}
      <div className="mb-8 pt-4">
        <SectionHeader icon={DollarSign} title={t("reports.profitAnalytics")} />
        {profitLoading ? (
          <LoadingSpinner />
        ) : profitError ? (
          <ErrorDisplay message={profitError.response?.data?.message || profitError.message} />
        ) : (
          <ProfitCards data={profitData} />
        )}
      </div>

      {/* Phase 2 - Product Performance */}
      <div className="mb-8 pt-4">
        <SectionHeader icon={Package} title={t("reports.productPerformance")} />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <div>
            <p className="text-[13px] font-semibold text-surface-500 dark:text-surface-400 mb-3">{t("reports.productPerformanceSub.topPerforming")}</p>
            {productLoading ? (
              <LoadingSpinner />
            ) : productError ? (
              <ErrorDisplay message={productError.response?.data?.message || productError.message} />
            ) : (
              <DataTable
                columns={[
                  { key: "name", label: t("reports.productPerformanceSub.product") },
                  { key: "quantity_sold", label: t("reports.productPerformanceSub.qtySold") },
                  { key: "revenue", label: t("reports.productPerformanceSub.revenue"), render: (val) => <span className="tabular-nums whitespace-nowrap">{formatCurrency(val)}</span> },
                ]}
                data={productData?.top_products}
                emptyMessage={t("reports.productPerformanceSub.topEmpty")}
              />
            )}
          </div>
          <div>
            <p className="text-[13px] font-semibold text-surface-500 dark:text-surface-400 mb-3">{t("reports.productPerformanceSub.slowMoving")}</p>
            {productLoading ? (
              <LoadingSpinner />
            ) : productError ? (
              <ErrorDisplay message={productError.response?.data?.message || productError.message} />
            ) : (
              <DataTable
                columns={[
                  { key: "name", label: t("reports.productPerformanceSub.product") },
                  { key: "quantity_sold", label: t("reports.productPerformanceSub.qtySold") },
                  { key: "revenue", label: t("reports.productPerformanceSub.revenue"), render: (val) => <span className="tabular-nums whitespace-nowrap">{formatCurrency(val)}</span> },
                ]}
                data={productData?.slow_products}
                emptyMessage={t("reports.productPerformanceSub.slowEmpty")}
              />
            )}
          </div>
        </div>
      </div>

      {/* Phase 2 - Supplier Performance */}
      <div className="mb-8 pt-4">
        <SectionHeader icon={Users} title={t("reports.supplierPerformance")} />
        {supplierLoading ? (
          <LoadingSpinner />
        ) : supplierError ? (
          <ErrorDisplay message={supplierError.response?.data?.message || supplierError.message} />
        ) : (
          <DataTable
            columns={[
              { key: "name", label: t("reports.supplierPerformanceSub.supplier") },
              { key: "total_purchases", label: t("reports.supplierPerformanceSub.totalSpent"), render: (val) => <span className="tabular-nums whitespace-nowrap">{formatCurrency(val)}</span> },
              { key: "purchase_count", label: t("reports.supplierPerformanceSub.orders") },
            ]}
            data={supplierData?.suppliers}
            emptyMessage={t("reports.supplierPerformanceSub.empty")}
          />
        )}
      </div>

      {/* Phase 3 - Inventory Reports */}
      <div className="mb-8 pt-8 border-t border-surface-200 dark:border-surface-700/60">
        <SectionHeader icon={Package} title={t("reports.inventoryReport.title")} />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-8">
          <div className={cardClass + " p-6"}>
            <div className="flex items-center gap-2 mb-4">
              <Warehouse className="w-5 h-5 text-primary-600 dark:text-primary-400" />
              <h3 className="text-[15px] font-semibold text-surface-900 dark:text-surface-100">{t("reports.inventoryReport.subtitle")}</h3>
            </div>
            {inventoryReportLoading ? (
              <LoadingSpinner />
            ) : inventoryReportError ? (
              <ErrorDisplay message={inventoryReportError.response?.data?.message || inventoryReportError.message} />
            ) : (
              <DataTable
                columns={[
                  { key: "name", label: t("reports.inventoryReport.product") },
                  { key: "warehouse_qty", label: t("reports.inventoryReport.warehouse") },
                  { key: "store_qty", label: t("reports.inventoryReport.store") },
                  { key: "total", label: t("reports.inventoryReport.total"), render: (val) => <span className="font-bold">{val}</span> },
                  {
                    key: "expiration_date",
                    label: t("reports.inventoryReport.expiration"),
                    render: (val, row) => (
                      <div className="flex items-center gap-2">
                        <span className="text-[12px] text-surface-600 dark:text-surface-300 whitespace-nowrap">
                          {val ? new Date(val + "T00:00:00").toLocaleDateString(locale, { year: "numeric", month: "short", day: "numeric" }) : "—"}
                        </span>
                        {row.expiration_status && (
                          <Badge variant={statusBadge(row.expiration_status)}>
                            {t(`reports.inventoryReport.statuses.${row.expiration_status}`)}
                          </Badge>
                        )}
                      </div>
                    ),
                  },
                ]}
                data={inventoryReport}
                emptyMessage={t("reports.inventoryReport.empty")}
              />
            )}
          </div>

          <div className={cardClass + " p-6"}>
            <div className="flex items-center gap-2 mb-4">
              <ArrowLeftRight className="w-5 h-5 text-primary-600 dark:text-primary-400" />
              <h3 className="text-[15px] font-semibold text-surface-900 dark:text-surface-100">{t("reports.inventoryReport.mostTransferred")}</h3>
            </div>
            {mostTransferredLoading ? (
              <LoadingSpinner />
            ) : mostTransferredError ? (
              <ErrorDisplay message={mostTransferredError.response?.data?.message || mostTransferredError.message} />
            ) : (
              <DataTable
                columns={[
                  { key: "name", label: t("reports.inventoryReport.product") },
                  { key: "total_quantity", label: t("reports.inventoryReport.qtyTransferred") },
                  { key: "transfer_count", label: t("reports.inventoryReport.transferCount") },
                ]}
                data={mostTransferred}
                emptyMessage={t("reports.inventoryReport.empty")}
              />
            )}
          </div>
        </div>

        {/* Movement charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <div className={cardClass + " p-6"}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-[15px] font-semibold text-surface-900 dark:text-surface-100">{t("reports.inventoryReport.monthlyMovement")}</h3>
              <div className="flex items-center gap-2">
                <select
                  value={reportMonth}
                  onChange={(e) => setReportMonth(Number(e.target.value))}
                  className="px-3 py-1.5 rounded-lg border border-surface-200 dark:border-surface-700/60 text-[12px] text-surface-700 dark:text-surface-200 bg-surface-50 dark:bg-surface-700/40 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                >
                  {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>
                <select
                  value={reportYear}
                  onChange={(e) => setReportYear(Number(e.target.value))}
                  className="px-3 py-1.5 rounded-lg border border-surface-200 dark:border-surface-700/60 text-[12px] text-surface-700 dark:text-surface-200 bg-surface-50 dark:bg-surface-700/40 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
                >
                  {[new Date().getFullYear(), new Date().getFullYear() - 1].map((y) => (
                    <option key={y} value={y}>{y}</option>
                  ))}
                </select>
              </div>
            </div>
            {monthlyLoading ? (
              <LoadingSpinner />
            ) : monthlyError ? (
              <ErrorDisplay message={monthlyError.response?.data?.message || monthlyError.message} />
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={monthlyMovement} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={GRID_LINE} />
                  <XAxis
                    dataKey="movement_type"
                    tick={AXIS_TICK}
                    tickLine={false}
                    axisLine={AXIS_LINE}
                    tickFormatter={(val) => t(`inventory.history.${val}`)}
                  />
                  <YAxis tick={AXIS_TICK} tickLine={false} axisLine={AXIS_LINE} />
                  <Tooltip
                    contentStyle={TOOLTIP_STYLE}
                  />
                  <Bar dataKey="quantity" fill="var(--color-primary-500, #6366f1)" radius={[4, 4, 0, 0]} maxBarSize={40} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className={cardClass + " p-6"}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-[15px] font-semibold text-surface-900 dark:text-surface-100">{t("reports.inventoryReport.yearlyMovement")}</h3>
              <select
                value={reportYear}
                onChange={(e) => setReportYear(Number(e.target.value))}
                className="px-3 py-1.5 rounded-lg border border-surface-200 dark:border-surface-700/60 text-[12px] text-surface-700 dark:text-surface-200 bg-surface-50 dark:bg-surface-700/40 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
              >
                {[new Date().getFullYear(), new Date().getFullYear() - 1].map((y) => (
                  <option key={y} value={y}>{y}</option>
                ))}
              </select>
            </div>
            {yearlyLoading ? (
              <LoadingSpinner />
            ) : yearlyError ? (
              <ErrorDisplay message={yearlyError.response?.data?.message || yearlyError.message} />
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={yearlyMovement} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={GRID_LINE} />
                  <XAxis
                    dataKey="month"
                    tick={AXIS_TICK}
                    tickLine={false}
                    axisLine={AXIS_LINE}
                    tickFormatter={(val) => `${val}`}
                  />
                  <YAxis tick={AXIS_TICK} tickLine={false} axisLine={AXIS_LINE} />
                  <Tooltip
                    contentStyle={TOOLTIP_STYLE}
                  />
                  <Bar dataKey="quantity" fill="var(--color-primary-500, #6366f1)" radius={[4, 4, 0, 0]} maxBarSize={30} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Lowest stock */}
        <div className={"mt-8 " + cardClass + " p-6"}>
          <div className="flex items-center gap-2 mb-4">
            <Store className="w-5 h-5 text-primary-600 dark:text-primary-400" />
            <h3 className="text-[15px] font-semibold text-surface-900 dark:text-surface-100">{t("reports.inventoryReport.lowestStock")}</h3>
          </div>
          {lowestStockLoading ? (
            <LoadingSpinner />
          ) : lowestStockError ? (
            <ErrorDisplay message={lowestStockError.response?.data?.message || lowestStockError.message} />
          ) : (
            <DataTable
              columns={[
                { key: "name", label: t("reports.inventoryReport.product") },
                { key: "warehouse_qty", label: t("reports.inventoryReport.warehouse") },
                { key: "store_qty", label: t("reports.inventoryReport.store") },
                { key: "total", label: t("reports.inventoryReport.total"), render: (val) => <span className="font-bold">{val}</span> },
                { key: "minimum_stock", label: t("reports.inventoryReport.minStock") },
              ]}
              data={lowestStock}
              emptyMessage={t("reports.inventoryReport.empty")}
            />
          )}
        </div>
      </div>

      {/* Phase 4 - Expenses Reports */}
      <div className="pt-8 border-t border-surface-200 dark:border-surface-700/60">
        <SectionHeader icon={Wallet} title={t("reports.expenses.title")} />
        <DateFilter
          period={expensePeriod}
          onPeriodChange={handleExpensePeriodChange}
          startDate={expenseStartDate}
          endDate={expenseEndDate}
          onStartDateChange={setExpenseStartDate}
          onEndDateChange={setExpenseEndDate}
        />

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
          <StatCard label={t("reports.expenses.totalExpenses")} value={formatCurrency(expensesDaily?.total_expenses)} icon={ReceiptText} color="orange" />
          <StatCard label={t("reports.expenses.highestCategory")} value={expensesHighest?.[0] ? t(`expenses.categories.${expensesHighest[0].category}`) : "—"} icon={TrendingUp} color="purple" />
          <StatCard label={t("reports.expenses.monthlyComparison")} value={formatCurrency(expensesMonthlyComparison?.reduce?.((sum, r) => sum + Number(r.total || 0), 0))} icon={BarChart3} color="blue" />
          <StatCard label={t("reports.expenses.periodExpenses")} value={expensesCategory ? `${expensesCategory.length}` : "—"} icon={Wallet} color="green" />
        </div>

        <div className="mb-8">
          <h3 className="text-[15px] font-semibold text-surface-900 dark:text-surface-100 mb-4">{t("reports.expenses.dailyTrend")}</h3>
          {expensesDailyLoading ? (
            <LoadingSpinner />
          ) : expensesDailyError ? (
            <ErrorDisplay message={expensesDailyError.response?.data?.message || expensesDailyError.message} />
          ) : !expensesDaily?.data?.length ? (
            <div className={cardClass + " p-12 text-center"}>
              <ReceiptText className="w-12 h-12 text-surface-300 dark:text-surface-600 mx-auto mb-3" />
              <p className="text-surface-400 dark:text-surface-500 text-sm font-medium">{t("reports.expenses.noData")}</p>
            </div>
          ) : (
            <div className={cardClass + " p-6"}>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={expensesDaily.data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={GRID_LINE} />
                  <XAxis
                    dataKey="date"
                    tick={AXIS_TICK}
                    tickLine={false}
                    axisLine={AXIS_LINE}
                    tickFormatter={(val) => {
                      const d = new Date(val + "T00:00:00");
                      return d.toLocaleDateString(locale, { month: "short", day: "numeric" });
                    }}
                  />
                  <YAxis
                    tick={AXIS_TICK}
                    tickLine={false}
                    axisLine={AXIS_LINE}
                    tickFormatter={(val) => formatCurrency(val)}
                  />
                  <Tooltip
                    contentStyle={TOOLTIP_STYLE}
                  />
                  <Bar dataKey="total" name={t("reports.expenses.totalExpenses")} fill="var(--color-primary-500, #6366f1)" radius={[4, 4, 0, 0]} maxBarSize={40} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-8">
          <div className={cardClass + " p-6"}>
            <h3 className="text-[15px] font-semibold text-surface-900 dark:text-surface-100 mb-4">{t("reports.expenses.categoryBreakdown")}</h3>
            {expensesCategoryLoading ? (
              <LoadingSpinner />
            ) : expensesCategoryError ? (
              <ErrorDisplay message={expensesCategoryError.response?.data?.message || expensesCategoryError.message} />
            ) : !expensesCategory?.length ? (
              <p className="text-surface-400 dark:text-surface-500 text-sm font-medium text-center py-8">{t("reports.expenses.noData")}</p>
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie
                    data={expensesCategory}
                    dataKey="total"
                    nameKey="category"
                    cx="50%"
                    cy="50%"
                    outerRadius={90}
                    label={(entry) => t(`expenses.categories.${entry.category}`)}
                    labelLine={false}
                  >
                    {expensesCategory.map((entry, i) => (
                      <Cell key={entry.category} fill={EXPENSE_COLORS[i % EXPENSE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={TOOLTIP_STYLE}
                    formatter={(value) => formatCurrency(Number(value))}
                  />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className={cardClass + " p-6"}>
            <h3 className="text-[15px] font-semibold text-surface-900 dark:text-surface-100 mb-4">{t("reports.expenses.paymentBreakdown")}</h3>
            {expensesPaymentLoading ? (
              <LoadingSpinner />
            ) : expensesPaymentError ? (
              <ErrorDisplay message={expensesPaymentError.response?.data?.message || expensesPaymentError.message} />
            ) : (
              <DataTable
                columns={[
                  { key: "payment_method", label: t("reports.expenses.paymentMethod"), render: (val) => t(`expenses.paymentMethods.${val}`) },
                  { key: "count", label: t("reports.expenses.count") },
                  { key: "total", label: t("reports.expenses.totalExpenses"), render: (val) => <span className="tabular-nums whitespace-nowrap">{formatCurrency(val)}</span> },
                ]}
                data={expensesPayment}
                emptyMessage={t("reports.expenses.noData")}
              />
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <div className={cardClass + " p-6"}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-[15px] font-semibold text-surface-900 dark:text-surface-100">{t("reports.expenses.monthlyComparison")}</h3>
              <select
                value={expenseComparisonYear}
                onChange={(e) => setExpenseComparisonYear(Number(e.target.value))}
                className="px-3 py-1.5 rounded-lg border border-surface-200 dark:border-surface-700/60 text-[12px] text-surface-700 dark:text-surface-200 bg-surface-50 dark:bg-surface-700/40 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
              >
                {[new Date().getFullYear(), new Date().getFullYear() - 1].map((y) => (
                  <option key={y} value={y}>{y}</option>
                ))}
              </select>
            </div>
            {expensesMonthlyComparisonLoading ? (
              <LoadingSpinner />
            ) : expensesMonthlyComparisonError ? (
              <ErrorDisplay message={expensesMonthlyComparisonError.response?.data?.message || expensesMonthlyComparisonError.message} />
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={expensesMonthlyComparison} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={GRID_LINE} />
                  <XAxis
                    dataKey="month"
                    tick={AXIS_TICK}
                    tickLine={false}
                    axisLine={AXIS_LINE}
                    tickFormatter={(val) => new Date(2000, val - 1, 1).toLocaleDateString(locale, { month: "short" })}
                  />
                  <YAxis
                    tick={AXIS_TICK}
                    tickLine={false}
                    axisLine={AXIS_LINE}
                    tickFormatter={(val) => formatCurrency(val)}
                  />
                  <Tooltip
                    contentStyle={TOOLTIP_STYLE}
                  />
                  <Bar dataKey="total" name={t("reports.expenses.totalExpenses")} fill="var(--color-primary-500, #6366f1)" radius={[4, 4, 0, 0]} maxBarSize={30} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className={cardClass + " p-6"}>
            <h3 className="text-[15px] font-semibold text-surface-900 dark:text-surface-100 mb-4">{t("reports.expenses.highestCategories")}</h3>
            {expensesHighestLoading ? (
              <LoadingSpinner />
            ) : expensesHighestError ? (
              <ErrorDisplay message={expensesHighestError.response?.data?.message || expensesHighestError.message} />
            ) : (
              <DataTable
                columns={[
                  { key: "category", label: t("reports.expenses.category"), render: (val) => t(`expenses.categories.${val}`) },
                  { key: "count", label: t("reports.expenses.count") },
                  { key: "total", label: t("reports.expenses.totalExpenses"), render: (val) => <span className="tabular-nums whitespace-nowrap">{formatCurrency(val)}</span> },
                ]}
                data={expensesHighest}
                emptyMessage={t("reports.expenses.noData")}
              />
            )}
          </div>
        </div>
      </div>

      {/* Phase 5 - Inventory Audit Reports */}
      <div className="pt-8 border-t border-surface-200 dark:border-surface-700/60">
        <SectionHeader icon={ClipboardCheck} title={t("reports.audits.title")} />

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
          <StatCard label={t("reports.audits.totalAudits")} value={auditReport?.metrics?.total_audits ?? 0} icon={ClipboardList} color="blue" />
          <StatCard label={t("reports.audits.openAudits")} value={auditReport?.metrics?.open_audits ?? 0} icon={ClipboardCheck} color="orange" />
          <StatCard label={t("reports.audits.completedAudits")} value={auditReport?.metrics?.completed_audits ?? 0} icon={CheckCircle2} color="green" />
          <StatCard label={t("reports.audits.unitsAdjusted")} value={`${(auditReport?.metrics?.units_added ?? 0) - (auditReport?.metrics?.units_removed ?? 0)}`} icon={ArrowLeftRight} color="purple" />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
          <StatCard label={t("reports.audits.unitsAdded")} value={auditReport?.metrics?.units_added ?? 0} icon={ArrowUpRight} color="green" />
          <StatCard label={t("reports.audits.unitsRemoved")} value={auditReport?.metrics?.units_removed ?? 0} icon={ArrowDownRight} color="red" />
          <StatCard label={t("reports.audits.adjustedItems")} value={auditReport?.metrics?.adjusted_items ?? 0} icon={AlertTriangle} color="orange" />
          <StatCard label={t("reports.audits.cancelledAudits")} value={auditReport?.metrics?.cancelled_audits ?? 0} icon={XCircle} color="blue" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-8">
          <div className={cardClass + " p-6"}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-[15px] font-semibold text-surface-900 dark:text-surface-100">{t("reports.audits.monthlyTrend")}</h3>
              <select
                value={auditComparisonYear}
                onChange={(e) => setAuditComparisonYear(Number(e.target.value))}
                className="px-3 py-1.5 rounded-lg border border-surface-200 dark:border-surface-700/60 text-[12px] text-surface-700 dark:text-surface-200 bg-surface-50 dark:bg-surface-700/40 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
              >
                {[new Date().getFullYear(), new Date().getFullYear() - 1].map((y) => (
                  <option key={y} value={y}>{y}</option>
                ))}
              </select>
            </div>
            {auditsMonthlyLoading ? (
              <LoadingSpinner />
            ) : auditsMonthlyError ? (
              <ErrorDisplay message={auditsMonthlyError.response?.data?.message || auditsMonthlyError.message} />
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={auditsMonthly} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={GRID_LINE} />
                  <XAxis
                    dataKey="month"
                    tick={AXIS_TICK}
                    tickLine={false}
                    axisLine={AXIS_LINE}
                    tickFormatter={(val) => new Date(2000, val - 1, 1).toLocaleDateString(locale, { month: "short" })}
                  />
                  <YAxis allowDecimals={false} tick={AXIS_TICK} tickLine={false} axisLine={AXIS_LINE} />
                  <Tooltip
                    contentStyle={TOOLTIP_STYLE}
                  />
                  <Bar dataKey="audits" name={t("reports.audits.completedAudits")} fill="var(--color-primary-500, #6366f1)" radius={[4, 4, 0, 0]} maxBarSize={30} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>

          <div className={cardClass + " p-6"}>
            <h3 className="text-[15px] font-semibold text-surface-900 dark:text-surface-100 mb-4">{t("reports.audits.yearlyTrend")}</h3>
            {auditsYearlyLoading ? (
              <LoadingSpinner />
            ) : auditsYearlyError ? (
              <ErrorDisplay message={auditsYearlyError.response?.data?.message || auditsYearlyError.message} />
            ) : (
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={auditsYearly} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={GRID_LINE} />
                  <XAxis
                    dataKey="year"
                    tick={AXIS_TICK}
                    tickLine={false}
                    axisLine={AXIS_LINE}
                  />
                  <YAxis allowDecimals={false} tick={AXIS_TICK} tickLine={false} axisLine={AXIS_LINE} />
                  <Tooltip
                    contentStyle={TOOLTIP_STYLE}
                  />
                  <Bar dataKey="audits" name={t("reports.audits.completedAudits")} fill="#10b981" radius={[4, 4, 0, 0]} maxBarSize={36} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <div>
            <h3 className="text-[15px] font-semibold text-surface-900 dark:text-surface-100 mb-4">{t("reports.audits.largestShortages")}</h3>
            {auditReportLoading ? (
              <LoadingSpinner />
            ) : auditReportError ? (
              <ErrorDisplay message={auditReportError.response?.data?.message || auditReportError.message} />
            ) : (
              <DataTable
                columns={[
                  { key: "product_name", label: t("reports.audits.product") },
                  { key: "audit_name", label: t("reports.audits.audit") },
                  { key: "difference", label: t("reports.audits.difference"), render: (val) => <span className="font-bold text-red-600 dark:text-red-400">{val}</span> },
                ]}
                data={auditReport?.largest_shortages}
                emptyMessage={t("reports.audits.noData")}
              />
            )}
          </div>

          <div>
            <h3 className="text-[15px] font-semibold text-surface-900 dark:text-surface-100 mb-4">{t("reports.audits.largestOverages")}</h3>
            {auditReportLoading ? (
              <LoadingSpinner />
            ) : auditReportError ? (
              <ErrorDisplay message={auditReportError.response?.data?.message || auditReportError.message} />
            ) : (
              <DataTable
                columns={[
                  { key: "product_name", label: t("reports.audits.product") },
                  { key: "audit_name", label: t("reports.audits.audit") },
                  { key: "difference", label: t("reports.audits.difference"), render: (val) => <span className="font-bold text-emerald-600 dark:text-emerald-400">+{val}</span> },
                ]}
                data={auditReport?.largest_overages}
                emptyMessage={t("reports.audits.noData")}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
