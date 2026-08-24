import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { BarChart3 } from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import { businessDevelopmentService } from "./api";
import { dealService, DEAL_STATUSES } from "../deals/api";
import { PageHeader } from "../../shared/components/PageHeader";
import { StatCard } from "../../shared/components/StatCard";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
import { DataTable } from "../../shared/components/DataTable";
import { cardClass } from "../../shared/components/styles";
import { formatCurrency } from "../../utils/formatCurrency";
import {
  AXIS_TICK,
  AXIS_LINE,
  GRID_LINE,
  TOOLTIP_STYLE,
} from "../../shared/utils/chartTheme";

export default function BusinessReportsPage() {
  const { t } = useTranslation();

  const statsQuery = useQuery({
    queryKey: ["business-development-statistics"],
    queryFn: async () => (await businessDevelopmentService.getStatistics()).data.data,
  });

  const dealsStatsQuery = useQuery({
    queryKey: ["deals-statistics"],
    queryFn: async () => (await dealService.getStatistics()).data.data,
  });

  if (statsQuery.isLoading || dealsStatsQuery.isLoading) return <LoadingSpinner />;
  if (statsQuery.error)
    return (
      <ErrorDisplay
        message={statsQuery.error.response?.data?.message || statsQuery.error.message}
        onRetry={statsQuery.refetch}
      />
    );
  if (dealsStatsQuery.error)
    return (
      <ErrorDisplay
        message={dealsStatsQuery.error.response?.data?.message || dealsStatsQuery.error.message}
        onRetry={dealsStatsQuery.refetch}
      />
    );

  const s = statsQuery.data || {};
  const d = dealsStatsQuery.data || {};

  const paymentData = Object.entries(d.payment_status_breakdown || {}).map(
    ([status, info]) => ({
      status: t(`business.paymentStatus.${status}`),
      revenue: Number(info?.total ?? 0),
      count: info?.count ?? 0,
    })
  );

  const dealStatusData = DEAL_STATUSES.map((status) => ({
    status: t(`business.dealStatus.${status}`),
    count: d.deal_status_breakdown?.[status] ?? 0,
  })).filter((row) => row.count > 0);

  const columns = [
    {
      key: "service_name",
      label: t("business.reports.columns.service"),
      render: (val) => (
        <span className="text-[13px] font-semibold text-surface-800 dark:text-surface-100">{val || "-"}</span>
      ),
    },
    {
      key: "deals_count",
      label: t("business.reports.columns.deals"),
      render: (val) => <span className="numeric-value text-[13px] text-surface-600 dark:text-surface-300">{val ?? 0}</span>,
    },
    {
      key: "total_revenue",
      label: t("business.reports.columns.revenue"),
      render: (val) => (
        <span className="numeric-value text-[13px] font-bold text-emerald-600 dark:text-emerald-400">
          {formatCurrency(val)}
        </span>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title={t("business.reports.title")}
        description={t("business.reports.description")}
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
        <StatCard label={t("business.reports.kpi.totalDeals")} value={d.total_deals ?? 0} icon={BarChart3} color="blue" />
        <StatCard
          label={t("business.reports.kpi.totalRevenue")}
          value={formatCurrency(d.total_revenue)}
          icon={BarChart3}
          color="green"
        />
        <StatCard
          label={t("business.reports.kpi.monthlyRevenue")}
          value={formatCurrency(d.monthly_revenue)}
          icon={BarChart3}
          color="purple"
        />
        <StatCard label={t("business.reports.kpi.clients")} value={s.total_clients ?? 0} icon={BarChart3} color="orange" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 mb-6">
        {paymentData.length > 0 && (
          <div className={`${cardClass} p-5`}>
            <h2 className="text-[14px] font-bold text-surface-900 dark:text-surface-100 mb-4">
              {t("business.reports.charts.paymentStatus")}
            </h2>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={paymentData}>
                <CartesianGrid strokeDasharray="3 3" stroke={GRID_LINE} vertical={false} />
                <XAxis dataKey="status" tick={AXIS_TICK} tickLine={false} axisLine={AXIS_LINE} />
                <YAxis tick={AXIS_TICK} tickLine={false} axisLine={AXIS_LINE} width={52} />
                <Tooltip contentStyle={TOOLTIP_STYLE} cursor={{ fill: "rgba(59,130,246,0.06)" }} />
                <Bar dataKey="revenue" fill="#3b82f6" radius={[8, 8, 0, 0]} maxBarSize={48} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
        {dealStatusData.length > 0 && (
          <div className={`${cardClass} p-5`}>
            <h2 className="text-[14px] font-bold text-surface-900 dark:text-surface-100 mb-4">
              {t("business.reports.charts.dealStatus")}
            </h2>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={dealStatusData}>
                <CartesianGrid strokeDasharray="3 3" stroke={GRID_LINE} vertical={false} />
                <XAxis dataKey="status" tick={AXIS_TICK} tickLine={false} axisLine={AXIS_LINE} />
                <YAxis tick={AXIS_TICK} tickLine={false} axisLine={AXIS_LINE} width={52} allowDecimals={false} />
                <Tooltip contentStyle={TOOLTIP_STYLE} cursor={{ fill: "rgba(16,185,129,0.06)" }} />
                <Bar dataKey="count" fill="#10b981" radius={[8, 8, 0, 0]} maxBarSize={48} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      <div className={`${cardClass} p-5`}>
        <h2 className="text-[14px] font-bold text-surface-900 dark:text-surface-100 mb-4">
          {t("business.reports.tables.serviceRevenue")}
        </h2>
        {(d.best_services || []).length === 0 ? (
          <EmptyState title={t("common.noDataAvailable")} />
        ) : (
          <DataTable columns={columns} data={d.best_services || []} />
        )}
      </div>
    </div>
  );
}
