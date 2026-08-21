import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import {
  Users,
  Briefcase,
  UserCheck,
  ClipboardList,
  Wrench,
  Plus,
  ArrowRight,
  Zap,
  Handshake,
  DollarSign,
} from "lucide-react";
import { bdDashboardService } from "./api";
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

function QuickAction({ label, icon: Icon, to, variant = "default" }) {
  const navigate = useNavigate();
  const styles = {
    default:
      "bg-surface-50 dark:bg-surface-700/40 text-surface-600 dark:text-surface-200 hover:bg-primary-50 dark:hover:bg-primary-500/10 hover:text-primary-700 dark:hover:text-primary-300",
    primary:
      "bg-primary-50 dark:bg-primary-500/10 text-primary-700 dark:text-primary-300 hover:bg-primary-100 dark:hover:bg-primary-500/20",
  };

  return (
    <button
      onClick={() => navigate(to)}
      className={`inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-[13px] font-semibold ring-1 ring-transparent hover:ring-primary-200 transition-all duration-150 ${styles[variant]}`}
    >
      <Icon className="w-4 h-4" strokeWidth={1.9} />
      {label}
    </button>
  );
}

export default function BusinessDashboardPage() {
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

  const quickActions = [
    { id: "deals", label: t("nav.deals", "Deals"), icon: Handshake, to: "/business/deals" },
    { id: "services", label: t("nav.services", "Services"), icon: Wrench, to: "/business/services" },
    { id: "clients", label: t("nav.clients", "Clients"), icon: Users, to: "/business/clients" },
    { id: "new-deal", label: t("quickActions.newDeal", "New Deal"), icon: Plus, to: "/business/deals", variant: "primary" },
    { id: "reports", label: t("nav.reports", "Reports"), icon: Briefcase, to: "/business/reports" },
  ];

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay message={error.response?.data?.message || error.message} onRetry={refetch} />;

  const totalClients = stats?.total_clients || 0;
  const activeClients = stats?.active_clients || 0;
  const totalServices = stats?.total_services || 0;
  const totalClientServices = stats?.total_client_services || 0;
  const activeClientServices = stats?.active_client_services || 0;

  const totalDeals = dealStats?.total_deals || 0;
  const totalRevenue = dealStats?.total_revenue || 0;
  const monthlyRevenue = dealStats?.monthly_revenue || 0;
  const recentDeals = dealStats?.recent_deals || [];
  const bestServices = dealStats?.best_services || [];

  const recentClients = stats?.recent_clients || [];
  const recentClientServices = stats?.recent_client_services || [];

  const hasData = totalClients > 0 || totalClientServices > 0 || totalDeals > 0;

  return (
    <div className="space-y-6">
      <PageHeader
        title={t("bdDashboard.title", "Business Development")}
        description={t("bdDashboard.description", "Overview of your business development activities")}
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

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          label={t("bdDashboard.activeClients", "Active Clients")}
          value={activeClients}
          icon={UserCheck}
          color="green"
        />
        <StatCard
          label={t("bdDashboard.totalServices", "Total Services")}
          value={totalServices}
          icon={Briefcase}
          color="purple"
        />
        <StatCard
          label={t("bdDashboard.totalClientServices", "Total Assignments")}
          value={totalClientServices}
          icon={ClipboardList}
          color="orange"
        />
        <StatCard
          label={t("bdDashboard.activeClientServices", "Active Assignments")}
          value={activeClientServices}
          icon={ClipboardList}
          color="blue"
        />
      </div>

      {/* Quick Access */}
      <div className={`${cardClass} p-4`}>
        <div className="flex flex-wrap items-center gap-2.5">
          <span className="inline-flex items-center gap-2 pe-2 text-[12px] font-semibold text-surface-400 dark:text-surface-400 uppercase tracking-wide">
            <Zap className="w-4 h-4" />
            {t("bdDashboard.quickAccess", "Quick Access")}
          </span>
          <span className="hidden sm:block w-px h-6 bg-surface-200/80 dark:bg-surface-700/60" />
          {quickActions.map((action) => (
            <QuickAction
              key={action.id}
              label={action.label}
              icon={action.icon}
              to={action.to}
              variant={action.variant}
            />
          ))}
        </div>
      </div>

      {!hasData ? (
        <EmptyState
          icon={Briefcase}
          title={t("bdDashboard.emptyTitle", "No Business Development Data")}
          description={t("bdDashboard.emptyDescription", "Start adding clients, services, and assignments to see your business development dashboard.")}
        />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {/* Recent Deals */}
          {recentDeals.length > 0 && (
            <div className={`${cardClass} p-5`}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-[14px] font-bold text-surface-900 dark:text-surface-100">
                  {t("bdDashboard.recentDeals", "Recent Deals")}
                </h3>
                <button
                  onClick={() => navigate("/business/deals")}
                  className="inline-flex items-center gap-1 text-[12px] font-semibold text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
                >
                  {t("dashboard.activity.viewAll", "View all")}
                  <ArrowRight className="w-3.5 h-3.5 rtl:rotate-180" />
                </button>
              </div>
              <div className="space-y-2.5">
                {recentDeals.map((deal) => (
                  <div
                    key={deal.id}
                    className="flex items-center justify-between p-3 rounded-xl bg-surface-50/50 dark:bg-surface-700/20 ring-1 ring-surface-100 dark:ring-surface-700/50"
                  >
                    <div className="min-w-0">
                      <p className="text-[13px] font-semibold text-surface-800 dark:text-surface-200 truncate">
                        {deal.deal_number}
                      </p>
                      <p className="text-[11px] text-surface-400 dark:text-surface-500 truncate">
                        {deal.company_name} — {deal.service_name}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-[13px] font-semibold text-surface-800 dark:text-surface-200">
                        {formatCurrency(deal.final_amount)}
                      </span>
                      <StatusBadge status={deal.deal_status} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Best Services by Revenue */}
          {bestServices.length > 0 && (
            <div className={`${cardClass} p-5`}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-[14px] font-bold text-surface-900 dark:text-surface-100">
                  {t("bdDashboard.bestServices", "Best Selling Services")}
                </h3>
              </div>
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

          {/* Recent Clients */}
          <div className={`${cardClass} p-5`}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-[14px] font-bold text-surface-900 dark:text-surface-100">
                {t("bdDashboard.recentClients", "Recent Clients")}
              </h3>
              {recentClients.length > 0 && (
                <button
                  onClick={() => navigate("/business/clients")}
                  className="inline-flex items-center gap-1 text-[12px] font-semibold text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
                >
                  {t("dashboard.activity.viewAll", "View all")}
                  <ArrowRight className="w-3.5 h-3.5 rtl:rotate-180" />
                </button>
              )}
            </div>
            {recentClients.length === 0 ? (
              <p className="text-[13px] text-surface-400 dark:text-surface-500">
                {t("bdDashboard.noRecentClients", "No recent clients")}
              </p>
            ) : (
              <div className="space-y-2.5">
                {recentClients.map((client) => (
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

          {/* Recent Client Services */}
          <div className={`${cardClass} p-5`}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-[14px] font-bold text-surface-900 dark:text-surface-100">
                {t("bdDashboard.recentClientServices", "Recent Assignments")}
              </h3>
              {recentClientServices.length > 0 && (
                <button
                  onClick={() => navigate("/business/client-services")}
                  className="inline-flex items-center gap-1 text-[12px] font-semibold text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
                >
                  {t("dashboard.activity.viewAll", "View all")}
                  <ArrowRight className="w-3.5 h-3.5 rtl:rotate-180" />
                </button>
              )}
            </div>
            {recentClientServices.length === 0 ? (
              <p className="text-[13px] text-surface-400 dark:text-surface-500">
                {t("bdDashboard.noRecentClientServices", "No recent assignments")}
              </p>
            ) : (
              <div className="space-y-2.5">
                {recentClientServices.map((cs) => (
                  <div
                    key={cs.id}
                    className="flex items-center justify-between p-3 rounded-xl bg-surface-50/50 dark:bg-surface-700/20 ring-1 ring-surface-100 dark:ring-surface-700/50"
                  >
                    <div className="min-w-0">
                      <p className="text-[13px] font-semibold text-surface-800 dark:text-surface-200 truncate">
                        {cs.company_name}
                      </p>
                      <p className="text-[11px] text-surface-400 dark:text-surface-500 truncate">
                        {cs.service_name}
                      </p>
                    </div>
                    <StatusBadge status={cs.status} />
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
