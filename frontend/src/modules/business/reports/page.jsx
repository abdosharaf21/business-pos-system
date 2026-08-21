import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import {
  Users,
  Briefcase,
  ClipboardList,
  TrendingUp,
  Handshake,
  DollarSign,
} from "lucide-react";
import { bdDashboardService } from "../dashboard/api";
import { dealService } from "../../deals/api";
import { PageHeader } from "../../../shared/components/PageHeader";
import { StatCard } from "../../../shared/components/StatCard";
import { Badge, statusBadge } from "../../../shared/components/Badge";
import { LoadingSpinner } from "../../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../../shared/components/ErrorDisplay";
import { EmptyState } from "../../../shared/components/EmptyState";
import { cardClass } from "../../../shared/components/styles";

function formatCurrency(amount) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "EGP" }).format(amount || 0);
}

const BD_STATUS_VARIANTS = {
  lead: "info",
  prospect: "warning",
  customer: "success",
  active: "success",
  inactive: "default",
  pending: "warning",
  in_progress: "info",
  completed: "success",
  cancelled: "danger",
  draft: "default",
  confirmed: "info",
  delivered: "success",
  refunded: "danger",
  partial: "warning",
  paid: "success",
};

function StatusBadge({ status }) {
  const variant = BD_STATUS_VARIANTS[status] || statusBadge(status);
  return <Badge variant={variant}>{status}</Badge>;
}

export default function BusinessReportsPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const {
    data: stats,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["bd-statistics"],
    queryFn: async () => {
      const res = await bdDashboardService.getStatistics();
      return res.data.data;
    },
  });

  const { data: dealStats } = useQuery({
    queryKey: ["deal-statistics"],
    queryFn: async () => {
      const res = await dealService.getStatistics();
      return res.data.data;
    },
  });

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay message={error.response?.data?.message || error.message} onRetry={refetch} />;

  const clientsByStatus = stats?.clients_by_status || {};
  const servicesByStatus = stats?.services_by_status || {};
  const clientServicesByStatus = stats?.client_services_by_status || {};
  const recentClients = stats?.recent_clients || [];
  const recentClientServices = stats?.recent_client_services || [];

  const totalClients = stats?.total_clients || 0;
  const activeClients = stats?.active_clients || 0;
  const totalServices = stats?.total_services || 0;
  const activeServices = stats?.active_services || 0;
  const totalClientServices = stats?.total_client_services || 0;

  const totalDeals = dealStats?.total_deals || 0;
  const totalRevenue = dealStats?.total_revenue || 0;
  const monthlyRevenue = dealStats?.monthly_revenue || 0;
  const paymentBreakdown = dealStats?.payment_status_breakdown || {};
  const dealStatusBreakdown = dealStats?.deal_status_breakdown || {};
  const bestServices = dealStats?.best_services || [];

  const clientActivationRate = totalClients > 0 ? Math.round((activeClients / totalClients) * 100) : 0;
  const serviceUtilizationRate = totalServices > 0 ? Math.round((activeServices / totalServices) * 100) : 0;
  const assignmentRate = totalClients > 0 ? Math.round((totalClientServices / totalClients) * 100) : 0;

  const hasData = totalClients > 0 || totalServices > 0 || totalClientServices > 0 || totalDeals > 0;

  if (!hasData) {
    return (
      <div className="space-y-6">
        <PageHeader
          title={t("nav.reports")}
          description={t("bdDashboard.title")}
        />
        <EmptyState
          icon={Briefcase}
          title={t("bdDashboard.emptyTitle", "No Business Development Data")}
          description={t("bdDashboard.emptyDescription", "Start adding clients, services, and assignments to see your reports.")}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={t("nav.reports")}
        description={t("bdDashboard.title")}
      />

      {/* KPI Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          label={t("bdDashboard.totalDeals", "Total Deals")}
          value={totalDeals}
          icon={Handshake}
          color="blue"
        />
        <StatCard
          label={t("bdDashboard.totalRevenue", "Total Revenue")}
          value={formatCurrency(totalRevenue)}
          icon={DollarSign}
          color="green"
        />
        <StatCard
          label={t("bdDashboard.monthlyRevenue", "This Month")}
          value={formatCurrency(monthlyRevenue)}
          icon={DollarSign}
          color="purple"
        />
        <StatCard
          label={t("bdDashboard.totalClients", "Total Clients")}
          value={totalClients}
          icon={Users}
          color="blue"
        />
      </div>

      {/* Rate Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className={`${cardClass} p-5`}>
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-emerald-50 dark:bg-emerald-500/10 ring-1 ring-emerald-100 dark:ring-emerald-500/20">
              <TrendingUp className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
            </div>
            <div>
              <p className="text-[13px] font-semibold text-surface-500 dark:text-surface-400">
                {t("bdReports.clientActivationRate", "Client Activation")}
              </p>
              <p className="text-[22px] font-bold text-surface-900 dark:text-surface-100">
                {clientActivationRate}%
              </p>
            </div>
          </div>
          <div className="w-full h-2 rounded-full bg-surface-100 dark:bg-surface-700/50">
            <div
              className="h-2 rounded-full bg-emerald-500 transition-all"
              style={{ width: `${clientActivationRate}%` }}
            />
          </div>
          <p className="text-[11px] text-surface-400 dark:text-surface-500 mt-2">
            {activeClients} / {totalClients} {t("bdReports.clientsActive", "clients active")}
          </p>
        </div>

        <div className={`${cardClass} p-5`}>
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-primary-50 dark:bg-primary-500/10 ring-1 ring-primary-100 dark:ring-primary-500/20">
              <Briefcase className="w-5 h-5 text-primary-600 dark:text-primary-400" />
            </div>
            <div>
              <p className="text-[13px] font-semibold text-surface-500 dark:text-surface-400">
                {t("bdReports.serviceUtilization", "Service Utilization")}
              </p>
              <p className="text-[22px] font-bold text-surface-900 dark:text-surface-100">
                {serviceUtilizationRate}%
              </p>
            </div>
          </div>
          <div className="w-full h-2 rounded-full bg-surface-100 dark:bg-surface-700/50">
            <div
              className="h-2 rounded-full bg-primary-500 transition-all"
              style={{ width: `${serviceUtilizationRate}%` }}
            />
          </div>
          <p className="text-[11px] text-surface-400 dark:text-surface-500 mt-2">
            {activeServices} / {totalServices} {t("bdReports.servicesActive", "services active")}
          </p>
        </div>

        <div className={`${cardClass} p-5`}>
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-amber-50 dark:bg-amber-500/10 ring-1 ring-amber-100 dark:ring-amber-500/20">
              <ClipboardList className="w-5 h-5 text-amber-600 dark:text-amber-400" />
            </div>
            <div>
              <p className="text-[13px] font-semibold text-surface-500 dark:text-surface-400">
                {t("bdReports.assignmentRate", "Assignment Rate")}
              </p>
              <p className="text-[22px] font-bold text-surface-900 dark:text-surface-100">
                {assignmentRate}%
              </p>
            </div>
          </div>
          <div className="w-full h-2 rounded-full bg-surface-100 dark:bg-surface-700/50">
            <div
              className="h-2 rounded-full bg-amber-500 transition-all"
              style={{ width: `${Math.min(assignmentRate, 100)}%` }}
            />
          </div>
          <p className="text-[11px] text-surface-400 dark:text-surface-500 mt-2">
            {totalClientServices} / {totalClients} {t("bdReports.assignmentsTotal", "total assignments")}
          </p>
        </div>
      </div>

      {/* Breakdown by Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatusBreakdown
          title={t("bdDashboard.clientsByStatus", "Clients by Status")}
          data={clientsByStatus}
          total={totalClients}
          emptyMessage={t("bdDashboard.noClients", "No clients yet")}
          t={t}
        />
        <StatusBreakdown
          title={t("bdDashboard.servicesByStatus", "Services by Status")}
          data={servicesByStatus}
          total={totalServices}
          emptyMessage={t("bdDashboard.noServices", "No services yet")}
          t={t}
        />
        <StatusBreakdown
          title={t("bdDashboard.clientServicesByStatus", "Assignments by Status")}
          data={clientServicesByStatus}
          total={totalClientServices}
          emptyMessage={t("bdDashboard.noClientServices", "No assignments yet")}
          t={t}
        />
        <StatusBreakdown
          title={t("bdDashboard.dealStatusBreakdown", "Deals by Status")}
          data={dealStatusBreakdown}
          total={totalDeals}
          emptyMessage={t("bdDashboard.noDeals", "No deals yet")}
          t={t}
        />
      </div>

      {/* Payment Breakdown */}
      {Object.keys(paymentBreakdown).length > 0 && (
        <div className={`${cardClass} p-5`}>
          <h3 className="text-[14px] font-bold text-surface-900 dark:text-surface-100 mb-4">
            {t("bdDashboard.paymentBreakdown", "Payment Status Breakdown")}
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(paymentBreakdown).map(([status, data]) => (
              <div key={status} className="p-3 rounded-xl bg-surface-50/50 dark:bg-surface-700/20 ring-1 ring-surface-100 dark:ring-surface-700/50">
                <StatusBadge status={status} />
                <p className="text-[12px] text-surface-500 dark:text-surface-400 mt-1">{data.count} {t("bdDashboard.deals", "deals")}</p>
                <p className="text-[14px] font-bold text-surface-800 dark:text-surface-200">{formatCurrency(data.total)}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Best Services */}
      {bestServices.length > 0 && (
        <div className={`${cardClass} p-5`}>
          <h3 className="text-[14px] font-bold text-surface-900 dark:text-surface-100 mb-4">
            {t("bdDashboard.bestServices", "Best Selling Services")}
          </h3>
          <div className="space-y-2.5">
            {bestServices.map((service) => (
              <div
                key={service.id}
                className="flex items-center justify-between p-3 rounded-xl bg-surface-50/50 dark:bg-surface-700/20 ring-1 ring-surface-100 dark:ring-surface-700/50"
              >
                <div className="min-w-0">
                  <p className="text-[13px] font-semibold text-surface-800 dark:text-surface-200 truncate">
                    {service.name}
                  </p>
                  <p className="text-[11px] text-surface-400 dark:text-surface-500 truncate">
                    {service.deal_count} {t("bdDashboard.deals", "deals")}
                  </p>
                </div>
                <span className="text-[13px] font-semibold text-emerald-600 dark:text-emerald-400">
                  {formatCurrency(service.total_revenue)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Activity Tables */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <RecentClientsTable
          clients={recentClients}
          onNavigate={() => navigate("/business/clients")}
          t={t}
        />
        <RecentAssignmentsTable
          assignments={recentClientServices}
          onNavigate={() => navigate("/business/client-services")}
          t={t}
        />
      </div>
    </div>
  );
}

function StatusBreakdown({ title, data, total, emptyMessage }) {
  const entries = Object.entries(data);

  if (entries.length === 0) {
    return (
      <div className={`${cardClass} p-5`}>
        <h3 className="text-[14px] font-bold text-surface-900 dark:text-surface-100 mb-4">{title}</h3>
        <p className="text-[13px] text-surface-400 dark:text-surface-500">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className={`${cardClass} p-5`}>
      <h3 className="text-[14px] font-bold text-surface-900 dark:text-surface-100 mb-4">{title}</h3>
      <div className="space-y-3">
        {entries.map(([status, count]) => {
          const pct = total > 0 ? Math.round((count / total) * 100) : 0;
          return (
            <div key={status}>
              <div className="flex items-center justify-between mb-1">
                <StatusBadge status={status} />
                <span className="text-[12px] font-semibold text-surface-600 dark:text-surface-300">
                  {count} <span className="text-surface-400 dark:text-surface-500">({pct}%)</span>
                </span>
              </div>
              <div className="w-full h-1.5 rounded-full bg-surface-100 dark:bg-surface-700/50">
                <div
                  className="h-1.5 rounded-full bg-primary-400 dark:bg-primary-500 transition-all"
                  style={{ width: `${pct}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function RecentClientsTable({ clients, onNavigate, t }) {
  return (
    <div className={`${cardClass} p-5`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-[14px] font-bold text-surface-900 dark:text-surface-100">
          {t("bdDashboard.recentClients", "Recent Clients")}
        </h3>
        {clients.length > 0 && (
          <button
            onClick={onNavigate}
            className="text-[12px] font-semibold text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
          >
            {t("dashboard.activity.viewAll", "View all")}
          </button>
        )}
      </div>
      {clients.length === 0 ? (
        <p className="text-[13px] text-surface-400 dark:text-surface-500">
          {t("bdDashboard.noRecentClients", "No recent clients")}
        </p>
      ) : (
        <div className="space-y-2.5">
          {clients.map((client) => (
            <div
              key={client.id}
              className="flex items-center justify-between p-3 rounded-xl bg-surface-50/50 dark:bg-surface-700/20 ring-1 ring-surface-100 dark:ring-surface-700/50"
            >
              <div className="min-w-0">
                <p className="text-[13px] font-semibold text-surface-800 dark:text-surface-200 truncate">
                  {client.company_name}
                </p>
                {client.contact_person && (
                  <p className="text-[11px] text-surface-400 dark:text-surface-500 truncate">
                    {client.contact_person}
                  </p>
                )}
              </div>
              <StatusBadge status={client.status} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function RecentAssignmentsTable({ assignments, onNavigate, t }) {
  return (
    <div className={`${cardClass} p-5`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-[14px] font-bold text-surface-900 dark:text-surface-100">
          {t("bdDashboard.recentClientServices", "Recent Assignments")}
        </h3>
        {assignments.length > 0 && (
          <button
            onClick={onNavigate}
            className="text-[12px] font-semibold text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
          >
            {t("dashboard.activity.viewAll", "View all")}
          </button>
        )}
      </div>
      {assignments.length === 0 ? (
        <p className="text-[13px] text-surface-400 dark:text-surface-500">
          {t("bdDashboard.noRecentClientServices", "No recent assignments")}
        </p>
      ) : (
        <div className="space-y-2.5">
          {assignments.map((a) => (
            <div
              key={a.id}
              className="flex items-center justify-between p-3 rounded-xl bg-surface-50/50 dark:bg-surface-700/20 ring-1 ring-surface-100 dark:ring-surface-700/50"
            >
              <div className="min-w-0">
                <p className="text-[13px] font-semibold text-surface-800 dark:text-surface-200 truncate">
                  {a.company_name}
                </p>
                <p className="text-[11px] text-surface-400 dark:text-surface-500 truncate">
                  {a.service_name}
                </p>
              </div>
              <StatusBadge status={a.status} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
