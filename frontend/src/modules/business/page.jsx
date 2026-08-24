import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";
import {
  Contact2,
  Layers,
  Handshake,
  UserCheck,
  ArrowRight,
} from "lucide-react";
import { businessDevelopmentService } from "./api";
import { dealService } from "../deals/api";
import { PageHeader } from "../../shared/components/PageHeader";
import { StatCard } from "../../shared/components/StatCard";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
import { Badge, statusBadge } from "../../shared/components/Badge";
import { cardClass } from "../../shared/components/styles";
import { formatCurrency } from "../../utils/formatCurrency";
import { getCurrentLocale } from "../../shared/utils/format";

export default function BusinessDashboardPage() {
  const { t, i18n } = useTranslation();
  const locale = getCurrentLocale(i18n.language);

  const statsQuery = useQuery({
    queryKey: ["business-development-statistics"],
    queryFn: async () => {
      const res = await businessDevelopmentService.getStatistics();
      return res.data.data;
    },
  });

  const dealsStatsQuery = useQuery({
    queryKey: ["deals-statistics"],
    queryFn: async () => {
      const res = await dealService.getStatistics();
      return res.data.data;
    },
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

  const kpis = [
    {
      label: t("business.dashboard.kpi.clients"),
      value: s.total_clients ?? 0,
      subtitle: t("business.dashboard.kpi.activeClients", {
        count: s.active_clients ?? 0,
      }),
      icon: Contact2,
      color: "blue",
      to: "/clients",
    },
    {
      label: t("business.dashboard.kpi.services"),
      value: s.total_services ?? 0,
      icon: Layers,
      color: "purple",
      to: "/business/services",
    },
    {
      label: t("business.dashboard.kpi.deals"),
      value: d.total_deals ?? 0,
      subtitle: t("business.dashboard.kpi.monthlyRevenue"),
      icon: Handshake,
      color: "green",
      to: "/deals",
    },
    {
      label: t("business.dashboard.kpi.clientServices"),
      value: s.total_client_services ?? 0,
      subtitle: t("business.dashboard.kpi.activeClientServices", {
        count: s.active_client_services ?? 0,
      }),
      icon: UserCheck,
      color: "orange",
      to: "/client-services",
    },
  ];

  return (
    <div>
      <PageHeader
        title={t("business.dashboard.title")}
        description={t("business.dashboard.description")}
        actions={
          <Link to="/business/reports" className="text-[13px] font-semibold text-primary-600 hover:text-primary-700 dark:text-primary-400 inline-flex items-center gap-1.5">
            {t("business.dashboard.viewReports")} <ArrowRight className="w-4 h-4 rtl:-scale-x-100" />
          </Link>
        }
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
        {kpis.map((kpi) => (
          <Link key={kpi.label} to={kpi.to}>
            <StatCard label={kpi.label} value={kpi.value} icon={kpi.icon} color={kpi.color} />
          </Link>
        ))}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        <div className={`${cardClass} p-5 xl:col-span-2`}>
          <h2 className="text-[14px] font-bold text-surface-900 dark:text-surface-100 mb-4">
            {t("business.dashboard.recentDeals")}
          </h2>
          {(d.recent_deals || []).length === 0 ? (
            <EmptyState compact title={t("business.dashboard.noDeals")} />
          ) : (
            <ul className="divide-y divide-surface-100 dark:divide-surface-700/60">
              {(d.recent_deals || []).map((deal) => (
                <li key={deal.id} className="flex items-center justify-between gap-3 py-3">
                  <div className="min-w-0">
                    <p className="text-[13px] font-semibold text-surface-800 dark:text-surface-100 truncate">
                      {deal.deal_number}
                      {deal.client_name ? ` — ${deal.client_name}` : ""}
                    </p>
                    <p className="text-[12px] text-surface-400 truncate">
                      {deal.service_name || "-"}
                    </p>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <span className="numeric-value text-[13px] font-bold text-surface-800 dark:text-surface-100">
                      {formatCurrency(deal.final_amount)}
                    </span>
                    <Badge variant={statusBadge(deal.deal_status)}>
                      {t(`business.dealStatus.${deal.deal_status}`)}
                    </Badge>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className={`${cardClass} p-5`}>
          <h2 className="text-[14px] font-bold text-surface-900 dark:text-surface-100 mb-4">
            {t("business.dashboard.bestServices")}
          </h2>
          {(d.best_services || []).length === 0 ? (
            <EmptyState compact title={t("business.dashboard.noBestServices")} />
          ) : (
            <ul className="divide-y divide-surface-100 dark:divide-surface-700/60">
              {(d.best_services || []).map((service, index) => (
                <li key={service.service_id ?? index} className="flex items-center justify-between gap-3 py-3">
                  <span className="text-[13px] font-medium text-surface-700 dark:text-surface-200 truncate">
                    {service.service_name || service.name || "-"}
                  </span>
                  <span className="numeric-value text-[13px] font-bold text-emerald-600 dark:text-emerald-400 shrink-0">
                    {formatCurrency(service.total_revenue)}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className={`${cardClass} p-5`}>
          <h2 className="text-[14px] font-bold text-surface-900 dark:text-surface-100 mb-4">
            {t("business.dashboard.revenue")}
          </h2>
          <div className="space-y-4">
            <div>
              <p className="text-[12px] font-semibold text-surface-400 uppercase tracking-wide">
                {t("business.dashboard.totalRevenue")}
              </p>
              <p className="numeric-value text-2xl font-bold text-primary-600 dark:text-primary-400 mt-1">
                {formatCurrency(d.total_revenue)}
              </p>
            </div>
            <div>
              <p className="text-[12px] font-semibold text-surface-400 uppercase tracking-wide">
                {t("business.dashboard.monthlyRevenue")}
              </p>
              <p className="numeric-value text-xl font-bold text-surface-800 dark:text-surface-100 mt-1">
                {formatCurrency(d.monthly_revenue)}
              </p>
            </div>
          </div>
        </div>

        <div className={`${cardClass} p-5`}>
          <h2 className="text-[14px] font-bold text-surface-900 dark:text-surface-100 mb-4">
            {t("business.dashboard.recentClientServices")}
          </h2>
          {(s.recent_client_services || []).length === 0 ? (
            <EmptyState compact title={t("business.dashboard.noClientServices")} />
          ) : (
            <ul className="divide-y divide-surface-100 dark:divide-surface-700/60">
              {(s.recent_client_services || []).slice(0, 5).map((cs) => (
                <li key={cs.id} className="py-3">
                  <div className="flex items-center justify-between gap-2">
                    <p className="text-[13px] font-semibold text-surface-800 dark:text-surface-100 truncate">
                      {cs.company_name || "-"}
                    </p>
                    <Badge variant={statusBadge(cs.status)}>
                      {t(`business.assignmentStatus.${cs.status}`)}
                    </Badge>
                  </div>
                  <p className="text-[12px] text-surface-400 truncate mt-0.5">
                    {cs.service_name || "-"}
                    {cs.end_date
                      ? ` · ${new Date(cs.end_date).toLocaleDateString(locale)}`
                      : ""}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className={`${cardClass} p-5`}>
          <h2 className="text-[14px] font-bold text-surface-900 dark:text-surface-100 mb-4">
            {t("business.dashboard.paymentBreakdown")}
          </h2>
          {Object.keys(d.payment_status_breakdown || {}).length === 0 ? (
            <EmptyState compact title={t("common.noDataAvailable")} />
          ) : (
            <ul className="space-y-3">
              {Object.entries(d.payment_status_breakdown || {}).map(([status, info]) => (
                <li key={status} className="flex items-center justify-between gap-2">
                  <Badge variant={statusBadge(status)}>
                    {t(`business.paymentStatus.${status}`)}
                  </Badge>
                  <span className="numeric-value text-[13px] font-bold text-surface-800 dark:text-surface-100">
                    {info?.count ?? 0}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
