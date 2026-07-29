import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
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

const PERIODS = [
  { key: "last_7_days", label: "Last 7 Days" },
  { key: "last_30_days", label: "Last 30 Days" },
  { key: "custom", label: "Custom" },
];

function DateFilter({ period, onPeriodChange, startDate, endDate, onStartDateChange, onEndDateChange }) {
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
        <div className="flex items-center gap-2 ml-2">
          <input
            type="date"
            value={startDate}
            onChange={(e) => onStartDateChange(e.target.value)}
            className="px-3 py-2 rounded-xl border border-surface-200 text-[13px] text-surface-700 bg-surface-50 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500"
          />
          <span className="text-surface-400 text-[13px]">to</span>
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
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-2xl border border-surface-200/80 p-12 text-center shadow-card">
        <BarChart3 className="w-12 h-12 text-surface-300 mx-auto mb-3" />
        <p className="text-surface-400 text-sm font-medium">No sales data in this period</p>
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
              return d.toLocaleDateString("en-US", { month: "short", day: "numeric" });
            }}
          />
          <YAxis
            tick={{ fontSize: 11, fill: "#94a3b8" }}
            tickLine={false}
            axisLine={{ stroke: "#e2e8f0" }}
            tickFormatter={(val) => `$${val}`}
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
              return d.toLocaleDateString("en-US", {
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
  if (!data) return null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
      <StatCard
        label="Revenue"
        value={`$${(data.total_revenue || 0).toLocaleString()}`}
        icon={TrendingUp}
        color="green"
      />
      <StatCard
        label="Purchase Cost"
        value={`$${(data.total_purchase_cost || 0).toLocaleString()}`}
        icon={TrendingDown}
        color="orange"
      />
      <StatCard
        label="Gross Profit"
        value={`$${(data.gross_profit || 0).toLocaleString()}`}
        icon={DollarSign}
        color="blue"
      />
      <StatCard
        label="Profit Margin"
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
        title="Reports & Analytics"
        description="Business performance overview and insights"
      />

      {/* Phase 1 - Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <StatCard label="Today Sales" value={`$${(sales.today_sales || 0).toLocaleString()}`} icon={DollarSign} color="blue" />
        <StatCard label="Monthly Sales" value={`$${(sales.monthly_sales || 0).toLocaleString()}`} icon={TrendingUp} color="green" />
        <StatCard label="Total Invoices" value={sales.total_invoices || 0} icon={ShoppingCart} color="purple" />
        <StatCard label="Avg Invoice Value" value={`$${(sales.average_invoice_value || 0).toLocaleString()}`} icon={DollarSign} color="orange" />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <StatCard label="Today Purchases" value={`$${(purchases.today_purchases || 0).toLocaleString()}`} icon={ShoppingCart} color="blue" />
        <StatCard label="Monthly Purchases" value={`$${(purchases.monthly_purchases || 0).toLocaleString()}`} icon={TrendingUp} color="green" />
        <StatCard label="Inventory Value" value={`$${(inventory.inventory_value || 0).toLocaleString()}`} icon={Package} color="purple" />
        <StatCard label="Low Stock Items" value={inventory.low_stock_count || 0} icon={AlertTriangle} color="orange" />
      </div>

      {/* Phase 1 - Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 mb-12">
        <div>
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="w-5 h-5 text-primary-600" />
            <h2 className="text-lg font-semibold text-surface-900">Top Selling Products</h2>
          </div>
          <DataTable
            columns={[
              { key: "name", label: "Product" },
              { key: "total_quantity", label: "Qty Sold" },
              { key: "total_revenue", label: "Revenue", render: (val) => `$${(val || 0).toLocaleString()}` },
            ]}
            data={top_selling_products}
            emptyMessage="No sales data available"
          />
        </div>
        <div>
          <div className="flex items-center gap-2 mb-4">
            <Clock className="w-5 h-5 text-primary-600" />
            <h2 className="text-lg font-semibold text-surface-900">Recent Sales</h2>
          </div>
          <DataTable
            columns={[
              { key: "invoice_number", label: "Invoice" },
              { key: "total_amount", label: "Amount", render: (val) => `$${(val || 0).toLocaleString()}` },
              { key: "created_at", label: "Date", render: (val) => val ? new Date(val).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" }) : "-" },
            ]}
            data={recent_sales}
            emptyMessage="No recent sales"
          />
        </div>
      </div>

      {/* Phase 2 - Sales Analytics */}
      <div className="mb-8 pt-8 border-t border-surface-200">
        <SectionHeader icon={BarChart3} title="Sales Analytics" />
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
        <SectionHeader icon={DollarSign} title="Profit Analytics" />
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
        <SectionHeader icon={Package} title="Product Performance" />
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          <div>
            <p className="text-[13px] font-semibold text-surface-500 mb-3">Top Performing</p>
            {productLoading ? (
              <LoadingSpinner />
            ) : productError ? (
              <ErrorDisplay message={productError.response?.data?.message || productError.message} />
            ) : (
              <DataTable
                columns={[
                  { key: "name", label: "Product" },
                  { key: "quantity_sold", label: "Qty Sold" },
                  { key: "revenue", label: "Revenue", render: (val) => `$${(val || 0).toLocaleString()}` },
                ]}
                data={productData?.top_products}
                emptyMessage="No product sales data"
              />
            )}
          </div>
          <div>
            <p className="text-[13px] font-semibold text-surface-500 mb-3">Slow Moving</p>
            {productLoading ? (
              <LoadingSpinner />
            ) : productError ? (
              <ErrorDisplay message={productError.response?.data?.message || productError.message} />
            ) : (
              <DataTable
                columns={[
                  { key: "name", label: "Product" },
                  { key: "quantity_sold", label: "Qty Sold" },
                  { key: "revenue", label: "Revenue", render: (val) => `$${(val || 0).toLocaleString()}` },
                ]}
                data={productData?.slow_products}
                emptyMessage="All products have sales"
              />
            )}
          </div>
        </div>
      </div>

      {/* Phase 2 - Supplier Performance */}
      <div className="mb-8 pt-4">
        <SectionHeader icon={Users} title="Supplier Performance" />
        {supplierLoading ? (
          <LoadingSpinner />
        ) : supplierError ? (
          <ErrorDisplay message={supplierError.response?.data?.message || supplierError.message} />
        ) : (
          <DataTable
            columns={[
              { key: "name", label: "Supplier" },
              { key: "total_purchases", label: "Total Spent", render: (val) => `$${(val || 0).toLocaleString()}` },
              { key: "purchase_count", label: "Orders" },
            ]}
            data={supplierData?.suppliers}
            emptyMessage="No supplier data available"
          />
        )}
      </div>
    </div>
  );
}
