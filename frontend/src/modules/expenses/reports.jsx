import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { useState } from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import { PieChart } from "lucide-react";
import { expenseService } from "./api";
import { PageHeader } from "../../shared/components/PageHeader";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { DataTable } from "../../shared/components/DataTable";
import { EmptyState } from "../../shared/components/EmptyState";
import { cardClass, ghostButtonClass } from "../../shared/components/styles";
import {
  AXIS_TICK,
  AXIS_LINE,
  GRID_LINE,
  TOOLTIP_STYLE,
} from "../../shared/utils/chartTheme";

const TABS = ["byCategory", "byPayment"];

export default function ExpenseReportsPage() {
  const { t } = useTranslation();
  const [tab, setTab] = useState("byCategory");

  const byCategoryQuery = useQuery({
    queryKey: ["expenses-report-category"],
    queryFn: async () => (await expenseService.getByCategory()).data.data,
  });

  const byPaymentQuery = useQuery({
    queryKey: ["expenses-report-payment"],
    queryFn: async () => (await expenseService.getByPayment()).data.data,
  });

  if (byCategoryQuery.isLoading || byPaymentQuery.isLoading) return <LoadingSpinner />;

  for (const q of [byCategoryQuery, byPaymentQuery]) {
    if (q.error)
      return (
        <ErrorDisplay
          message={q.error.response?.data?.message || q.error.message}
          onRetry={q.refetch}
        />
      );
  }

  const categoryData = byCategoryQuery.data?.data || [];
  const paymentData = byPaymentQuery.data?.data || [];

  const chartColors = ["#ef4444", "#f97316", "#eab308", "#10b981", "#3b82f6", "#8b5cf6", "#ec4899"];

  const buildColumns = (nameLabel) => [
    {
      key: "name",
      label: nameLabel,
      render: (val) => (
        <span className="text-[13px] font-semibold text-surface-800 dark:text-surface-100">{val}</span>
      ),
    },
    {
      key: "count",
      label: t("expenses.reports.columns.expenses"),
      render: (val) => (
        <span className="numeric-value text-[13px] text-surface-600 dark:text-surface-300">{val}</span>
      ),
    },
    {
      key: "total",
      label: t("expenses.reports.columns.total"),
      render: (val) => (
        <span className="numeric-value text-[13px] font-bold text-red-600 dark:text-red-400">
          {Number(val || 0).toFixed(2)}
        </span>
      ),
    },
    {
      key: "share",
      label: t("expenses.reports.columns.share"),
      render: (_, row) => {
        const total =
          tab === "byCategory"
            ? byCategoryQuery.data?.total_expenses
            : byPaymentQuery.data?.total_expenses;
        const pct = total > 0 ? ((row.total / total) * 100).toFixed(1) : "0.0";
        return (
          <span className="numeric-value text-[13px] font-semibold text-surface-700 dark:text-surface-200">
            {pct}%
          </span>
        );
      },
    },
  ];

  const activeRows =
    tab === "byCategory"
      ? categoryData.map((r) => ({ ...r, name: r.category }))
      : paymentData.map((r) => ({ ...r, name: r.payment_method }));

  const tabLabels = {
    byCategory: t("expenses.reports.tabs.byCategory"),
    byPayment: t("expenses.reports.tabs.byPayment"),
  };

  return (
    <div>
      <PageHeader
        title={t("expenses.reports.title")}
        description={t("expenses.reports.description")}
      />

      <div className="flex items-center gap-2 mb-6">
        {TABS.map((key) => (
          <button
            key={key}
            type="button"
            onClick={() => setTab(key)}
            className={`${ghostButtonClass} ${
              tab === key
                ? "!bg-primary-50 !text-primary-700 dark:!bg-primary-500/10 dark:!text-primary-400"
                : ""
            }`}
          >
            {tabLabels[key]}
          </button>
        ))}
      </div>

      {activeRows.length === 0 ? (
        <EmptyState icon={PieChart} compact title={t("common.noDataAvailable")} />
      ) : (
        <>
          <div className={`${cardClass} p-5 mb-6`}>
            <h2 className="text-[14px] font-bold text-surface-900 dark:text-surface-100 mb-4">
              {tabLabels[tab]}
            </h2>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={activeRows}>
                <CartesianGrid strokeDasharray="3 3" stroke={GRID_LINE} vertical={false} />
                <XAxis
                  dataKey="name"
                  tick={AXIS_TICK}
                  tickLine={false}
                  axisLine={AXIS_LINE}
                  interval={0}
                  angle={-20}
                  dy={10}
                  height={50}
                />
                <YAxis tick={AXIS_TICK} tickLine={false} axisLine={AXIS_LINE} width={52} />
                <Tooltip contentStyle={TOOLTIP_STYLE} cursor={{ fill: "rgba(239,68,68,0.06)" }} />
                <Bar dataKey="total" radius={[8, 8, 0, 0]} maxBarSize={48}>
                  {activeRows.map((_, i) => (
                    <rect key={`cell-${i}`} fill={chartColors[i % chartColors.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className={`${cardClass} p-5`}>
            <DataTable columns={buildColumns(tabLabels[tab])} data={activeRows} />
          </div>
        </>
      )}
    </div>
  );
}

