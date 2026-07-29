import { formatCurrency } from "../../utils/formatCurrency";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer,
} from "recharts";
import { reportService } from "./api";
import { PageHeader } from "../../shared/components/PageHeader";
import { StatCard } from "../../shared/components/StatCard";
import { DataTable } from "../../shared/components/DataTable";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import {
  DollarSign, ShoppingCart, Package, AlertTriangle,
  TrendingUp, TrendingDown, Clock, Users, BarChart3,
  Filter,
} from "lucide-react";

function DateFilter({ period, onPeriodChange, startDate, endDate, onStartDateChange, onEndDateChange }) {
  const { t } = useTranslation();
  const PERIODS = [
    { key: "last_7_days", label: t("reports.filters.last7Days") },
    { key: "last_30_days", label: t("reports.filters.last30Days") },
    { key: "custom", label: t("reports.filters.custom") },
  ];
  return (
    <div className="flex flex-wrap items-center gap-3 mb-6 p-4 bg-white rounded-2xl border border-surface-200/80 shadow-card">
      <Filter className="w-5 h-5 text-surface-400 shrink-0" />
      {PERIODS.map((p) => (
        <button
          key={p.key}
          onClick={() => onPeriodChange(p.key)}
          className={`px-4 py-2 rounded-xl text-[13px] font-medium transition-all duration-150 ${
            period === p.key
              ? "bg-primary-50 text-primary-700 ring-1 ring-primary-200"
              : "bg-surface-50 text-surface-500 hover:bg-surface-100 hover:text-surface-700"
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
            className="px-3 py-2 rounded-xl border border-surface-200 text-[13px] text-surface-700 bg-surface-50 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
          />
          <span className="text-surface-400 text-[13px]">{t("reports.filters.to")}</span>
          <input
            type="date"
            value={endDate}
            onChange={(e) => onEndDateChange(e.target.value)}
            className="px-3 py-2 rounded-xl border border-surface-200 text-[13px] text-surface-700 bg-surface-50 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
          />
        </div>
      )}
    </div>
  );
}

function SectionHeader({ icon: Icon, title }) {
  return (
    <div className="flex items-center gap-2 mb-5">
      <div className="w-8 h-8 rounded-lg bg-primary-50 flex items-center justify-center ring-1 ring-primary-100">
        <Icon className="w-4 h-4 text-primary-600" />
      </div>
      <h2 className="text-lg font-semibold text-surface-900">{title}</h2>
    </div>
  );
}

function SalesTrendChart({ data }) {
  const { t, i18n } = useTranslation();
  const locale = i18n.language === "ar" ? "ar-EG" : "en-US";

  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-2xl border border-surface-200/80 p-12 text-center shadow-card">
        <BarChart3 className="w-12 h-12 text-surface-300 mx-auto mb-3" />
        <p className="text-surface-400 text-sm font-medium">{t("reports.charts.noSalesData")}</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl border border-surface-200/80 p-6 shadow-card">
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 11, fill: "#94a3b8" }}
            tickLine={false}
            axisLine={{ stroke: "#e2e8f0" }}
            tickFormatter={(val) => {
              const d = new Date(val + "T00:00:00");
              return d.toLocaleDateString(locale, { month: "short", day: "numeric" });
            }}
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
  const locale = i18n.language === "ar" ? "ar-EG" : "en-US";
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

  const profitParams = period === "last_7_days" || period === "custom"
    ? { period: "custom", start_date: startDate, end_date: endDate }
    : { period };

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
            <TrendingUp className="w-5 h-5 text-primary-600" />
            <h2 className="text-lg font-semibold text-surface-900">{t("reports.topSelling.title")}</h2>
          </div>
          <DataTable
            columns={[
              { key: "name", label: t("reports.topSelling.product") },
              { key: "total_quantity", label: t("reports.topSelling.qtySold") },
              { key: "total_revenue", label: t("reports.topSelling.revenue"), render: (val) => formatCurrency(val) },
            ]}
            data={top_selling_products}
            emptyMessage={t("reports.topSelling.empty")}
          />
        </div>
        <div>
          <div className="flex items-center gap-2 mb-4">
            <Clock className="w-5 h-5 text-primary-600" />
            <h2 className="text-lg font-semibold text-surface-900">{t("reports.recentSales.title")}</h2>
          </div>
          <DataTable
            columns={[
              { key: "invoice_number", label: t("reports.recentSales.invoice") },
              { key: "total_amount", label: t("reports.recentSales.amount"), render: (val) => formatCurrency(val) },
              { key: "created_at", label: t("reports.recentSales.date"), render: (val) => val ? new Date(val).toLocaleDateString(locale, { year: "numeric", month: "short", day: "numeric" }) : "-" },
            ]}
            data={recent_sales}
            emptyMessage={t("reports.recentSales.empty")}
          />
        </div>
      </div>

      {/* Phase 2 - Sales Analytics */}
      <div className="mb-8 pt-8 border-t border-surface-200">
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
          <div className="bg-white rounded-2xl border border-surface-200/80 p-16 shadow-card">
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
            <p className="text-[13px] font-semibold text-surface-500 mb-3">{t("reports.productPerformanceSub.topPerforming")}</p>
            {productLoading ? (
              <LoadingSpinner />
            ) : productError ? (
              <ErrorDisplay message={productError.response?.data?.message || productError.message} />
            ) : (
              <DataTable
                columns={[
                  { key: "name", label: t("reports.productPerformanceSub.product") },
                  { key: "quantity_sold", label: t("reports.productPerformanceSub.qtySold") },
                  { key: "revenue", label: t("reports.productPerformanceSub.revenue"), render: (val) => formatCurrency(val) },
                ]}
                data={productData?.top_products}
                emptyMessage={t("reports.productPerformanceSub.topEmpty")}
              />
            )}
          </div>
          <div>
            <p className="text-[13px] font-semibold text-surface-500 mb-3">{t("reports.productPerformanceSub.slowMoving")}</p>
            {productLoading ? (
              <LoadingSpinner />
            ) : productError ? (
              <ErrorDisplay message={productError.response?.data?.message || productError.message} />
            ) : (
              <DataTable
                columns={[
                  { key: "name", label: t("reports.productPerformanceSub.product") },
                  { key: "quantity_sold", label: t("reports.productPerformanceSub.qtySold") },
                  { key: "revenue", label: t("reports.productPerformanceSub.revenue"), render: (val) => formatCurrency(val) },
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
              { key: "total_purchases", label: t("reports.supplierPerformanceSub.totalSpent"), render: (val) => formatCurrency(val) },
              { key: "purchase_count", label: t("reports.supplierPerformanceSub.orders") },
            ]}
            data={supplierData?.suppliers}
            emptyMessage={t("reports.supplierPerformanceSub.empty")}
          />
        )}
      </div>
    </div>
  );
}
