import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import { Receipt, CalendarDays, CalendarRange, TrendingUp } from "lucide-react";
import { expenseService } from "./api";
import { PageHeader } from "../../shared/components/PageHeader";
import { StatCard } from "../../shared/components/StatCard";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
import { DataTable } from "../../shared/components/DataTable";
import { cardClass } from "../../shared/components/styles";
import {
  AXIS_TICK,
  AXIS_LINE,
  GRID_LINE,
  TOOLTIP_STYLE,
} from "../../shared/utils/chartTheme";

export default function ExpensesDashboardPage() {
  const { t } = useTranslation();

  const summaryQuery = useQuery({
    queryKey: ["expenses-summary"],
    queryFn: async () => (await expenseService.getSummary()).data.data,
  });

  const yearlyQuery = useQuery({
    queryKey: ["expenses-yearly"],
    queryFn: async () => (await expenseService.getYearly()).data.data,
  });

  const byCategoryQuery = useQuery({
    queryKey: ["expenses-by-category"],
    queryFn: async () => (await expenseService.getByCategory()).data.data,
  });

  if (summaryQuery.isLoading || yearlyQuery.isLoading || byCategoryQuery.isLoading)
    return <LoadingSpinner />;

  for (const q of [summaryQuery, yearlyQuery, byCategoryQuery]) {
    if (q.error)
      return (
        <ErrorDisplay
          message={q.error.response?.data?.message || q.error.message}
          onRetry={q.refetch}
        />
      );
  }

  const s = summaryQuery.data || {};
  const yearData = (yearlyQuery.data?.data || []).map((row) => ({
    month: t(`common.months.${row.month}`),
    total: Number(row.total || 0),
  }));
  const categoryData = byCategoryQuery.data?.data || [];

  const categoryColumns = [
    {
      key: "category",
      label: t("expenses.dashboard.categoryColumns.category"),
      render: (val) => (
        <span className="text-[13px] font-semibold text-surface-800 dark:text-surface-100">{val}</span>
      ),
    },
    {
      key: "count",
      label: t("expenses.dashboard.categoryColumns.expenses"),
      render: (val) => (
        <span className="numeric-value text-[13px] text-surface-600 dark:text-surface-300">{val}</span>
      ),
    },
    {
      key: "total",
      label: t("expenses.dashboard.categoryColumns.total"),
      render: (val) => (
        <span className="numeric-value text-[13px] font-bold text-red-600 dark:text-red-400">
          {Number(val || 0).toFixed(2)}
        </span>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title={t("expenses.dashboard.title")}
        description={t("expenses.dashboard.description")}
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
        <StatCard
          label={t("expenses.dashboard.kpi.today")}
          value={(s.today_total ?? 0).toFixed(2)}
          icon={CalendarDays}
          color="blue"
        />
        <StatCard
          label={t("expenses.dashboard.kpi.thisMonth")}
          value={(s.this_month_total ?? 0).toFixed(2)}
          icon={CalendarRange}
          color="purple"
        />
        <StatCard
          label={t("expenses.dashboard.kpi.thisYear")}
          value={(s.this_year_total ?? 0).toFixed(2)}
          icon={Receipt}
          color="red"
        />
        <StatCard
          label={t("expenses.dashboard.kpi.avgMonthly")}
          value={(s.avg_monthly_total ?? 0).toFixed(2)}
          icon={TrendingUp}
          color="orange"
        />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 mb-6">
        <div className={`${cardClass} p-5`}>
          <h2 className="text-[14px] font-bold text-surface-900 dark:text-surface-100 mb-4">
            {t("expenses.dashboard.charts.yearly", { year: yearlyQuery.data?.year })}
          </h2>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={yearData}>
              <CartesianGrid strokeDasharray="3 3" stroke={GRID_LINE} vertical={false} />
              <XAxis dataKey="month" tick={AXIS_TICK} tickLine={false} axisLine={AXIS_LINE} />
              <YAxis tick={AXIS_TICK} tickLine={false} axisLine={AXIS_LINE} width={52} />
              <Tooltip contentStyle={TOOLTIP_STYLE} cursor={{ fill: "rgba(239,68,68,0.06)" }} />
              <Bar dataKey="total" fill="#ef4444" radius={[8, 8, 0, 0]} maxBarSize={36} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className={`${cardClass} p-5 flex flex-col`}>
          <h2 className="text-[14px] font-bold text-surface-900 dark:text-surface-100 mb-4">
            {t("expenses.dashboard.highestCategory.title")}
          </h2>
          {s.highest_category ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center py-8">
              <div className="w-16 h-16 bg-red-50 dark:bg-red-500/10 rounded-2xl flex items-center justify-center ring-1 ring-red-100 dark:ring-red-500/20 mb-5">
                <Receipt className="w-7 h-7 text-red-500" strokeWidth={1.5} />
              </div>
              <p className="text-lg font-bold text-surface-900 dark:text-surface-100">
                {s.highest_category}
              </p>
              <p className="numeric-value text-2xl font-extrabold text-red-600 dark:text-red-400 mt-1">
                {(s.highest_category_total ?? 0).toFixed(2)}
              </p>
            </div>
          ) : (
            <EmptyState compact title={t("common.noDataAvailable")} />
          )}
        </div>
      </div>

      <div className={`${cardClass} p-5`}>
        <h2 className="text-[14px] font-bold text-surface-900 dark:text-surface-100 mb-4">
          {t("expenses.dashboard.byCategory")}
        </h2>
        {categoryData.length === 0 ? (
          <EmptyState compact title={t("common.noDataAvailable")} />
        ) : (
          <DataTable columns={categoryColumns} data={categoryData} />
        )}
      </div>
    </div>
  );
}
