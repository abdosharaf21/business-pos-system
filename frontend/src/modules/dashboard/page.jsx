import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Users,
  Briefcase,
  Link2,
  DollarSign,
  RefreshCw,
  ChevronRight,
  Inbox,
  Zap,
  TrendingUp,
  Wallet,
  ArrowRight,
  HardHat,
  ReceiptText,
} from "lucide-react";
import { dashboardService } from "./api";
import { PageHeader } from "../../shared/components/PageHeader";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
import { StatCard } from "../../shared/components/StatCard";
import { Badge, statusBadge } from "../../shared/components/Badge";
import { getQuickActions } from "../../shared/layouts/navigationConfig";
import { useAuth } from "../../shared/context/AuthContext";
import { formatCurrency } from "../../utils/formatCurrency";

function BreakdownPanel({ icon: Icon, title, items }) {
  const total = items.reduce((sum, item) => sum + item.value, 0) || 1;

  return (
    <section className="bg-white dark:bg-surface-800/60 rounded-2xl border border-surface-200/80 dark:border-surface-700/60 p-5 shadow-card">
      <div className="flex items-center gap-3 mb-5">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center ring-1 ring-surface-200/60 bg-surface-50 text-surface-500 dark:bg-surface-700/50 dark:text-surface-300">
          <Icon className="w-5 h-5" strokeWidth={1.8} />
        </div>
        <h2 className="text-[14px] font-bold text-surface-900 dark:text-surface-100">{title}</h2>
      </div>
      <div className="space-y-4">
        {items.map((item) => (
          <div key={item.label}>
            <div className="flex items-center justify-between gap-3 mb-1.5">
              <span className="text-[13px] font-medium text-surface-700 dark:text-surface-200">{item.label}</span>
              <span className="numeric-value text-[13px] font-bold text-surface-900 dark:text-surface-100">{item.value}</span>
            </div>
            <div className="h-1.5 rounded-full bg-surface-100 dark:bg-surface-700/60 overflow-hidden">
              <div
                className="h-full rounded-full bg-gradient-to-r from-primary-500 to-primary-400"
                style={{ width: `${(item.value / total) * 100}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function RecentList({ icon: Icon, iconColor = "blue", title, items, emptyTitle, to, renderItem }) {
  const { t } = useTranslation();
  const iconClass = {
    blue: "bg-primary-50 text-primary-600 ring-primary-100 dark:bg-primary-500/10 dark:text-primary-400 dark:ring-primary-500/20",
    green: "bg-emerald-50 text-emerald-600 ring-emerald-100 dark:bg-emerald-500/10 dark:text-emerald-400 dark:ring-emerald-500/20",
    purple: "bg-violet-50 text-violet-600 ring-violet-100 dark:bg-violet-500/10 dark:text-violet-400 dark:ring-violet-500/20",
  }[iconColor];

  return (
    <section className="bg-white dark:bg-surface-800/60 rounded-2xl border border-surface-200/80 dark:border-surface-700/60 p-5 shadow-card">
      <div className="flex items-start justify-between gap-3 mb-5">
        <div className="flex items-center gap-3 min-w-0">
          <div className={`shrink-0 w-10 h-10 rounded-xl flex items-center justify-center ring-1 ${iconClass}`}>
            <Icon className="w-5 h-5" strokeWidth={1.8} />
          </div>
          <h2 className="text-[14px] font-bold text-surface-900 dark:text-surface-100 leading-tight">{title}</h2>
        </div>
        <Link to={to} className="inline-flex items-center gap-1 text-[12px] font-semibold text-primary-600 hover:text-primary-700 shrink-0">
          {t("dashboard.activity.viewAll")}
          <ChevronRight className="w-3.5 h-3.5 rtl:rotate-180" />
        </Link>
      </div>
      {!items || !items.length ? (
        <div className="flex flex-col items-center justify-center py-10 text-center px-4">
          <div className="w-12 h-12 bg-surface-100 dark:bg-surface-700/50 rounded-xl flex items-center justify-center mb-3 ring-1 ring-surface-200/60">
            <Inbox className="w-6 h-6 text-surface-400" strokeWidth={1.5} />
          </div>
          <p className="text-[13px] font-semibold text-surface-600 dark:text-surface-300">{emptyTitle}</p>
        </div>
      ) : (
        <ul className="divide-y divide-surface-100 dark:divide-surface-700/60">{items.map(renderItem)}</ul>
      )}
    </section>
  );
}

export default function DashboardPage() {
  const { t, i18n } = useTranslation();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const locale = i18n.language === "ar" ? "ar-EG" : "en-US";

  const statsQuery = useQuery({
    queryKey: ["dashboard", "stats"],
    queryFn: async () => {
      const res = await dashboardService.getStats();
      return res.data.data;
    },
  });

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ["dashboard"] });
  };

  const formatTime = (value) => {
    if (!value) return "";
    try {
      return new Date(value).toLocaleDateString(locale, {
        month: "short",
        day: "numeric",
        year: "numeric",
      });
    } catch {
      return "";
    }
  };

  if (statsQuery.isLoading) return <LoadingSpinner />;
  if (statsQuery.error) {
    return (
      <ErrorDisplay
        message={statsQuery.error.response?.data?.message || statsQuery.error.message}
        onRetry={handleRefresh}
      />
    );
  }

  const stats = statsQuery.data;

  const hasData = stats.total_workers > 0 || stats.total_expenses > 0;

  const quickActions = getQuickActions("dashboard", user?.role);

  const workerStatuses = [
    { label: t("workerManagement.statuses.active"), value: stats.workers_by_status?.active || 0 },
    { label: t("workerManagement.statuses.inactive"), value: stats.workers_by_status?.inactive || 0 },
  ];

  const expenseStatuses = [
    { label: t("expenses.statuses.pending"), value: stats.expenses_by_status?.pending || 0 },
    { label: t("expenses.statuses.completed"), value: stats.expenses_by_status?.completed || 0 },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title={t("dashboard.title")}
        description={t("dashboard.subtitle")}
        actions={
          <button
            onClick={handleRefresh}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white dark:bg-surface-800/60 border border-surface-200/80 dark:border-surface-700/60 text-[13px] font-semibold text-surface-600 dark:text-surface-300 hover:text-primary-600 hover:border-primary-300 shadow-card transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            {t("dashboard.refresh")}
          </button>
        }
      />

      {!hasData && (
        <div className="bg-white dark:bg-surface-800/60 rounded-2xl border border-surface-200/80 dark:border-surface-700/60 shadow-card">
          <EmptyState
            icon={TrendingUp}
            title={t("dashboard.emptyTitle")}
            description={t("dashboard.emptyDescription")}
            action={
              <Link
                to="/worker-management/workers"
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-primary-600 text-white text-[13px] font-semibold hover:bg-primary-700 transition-colors shadow-sm"
              >
                {t("dashboard.emptyAction")}
                <ArrowRight className="w-4 h-4 rtl:rotate-180" />
              </Link>
            }
          />
        </div>
      )}

      <div className="bg-white dark:bg-surface-800/60 rounded-2xl border border-surface-200/80 dark:border-surface-700/60 p-4 shadow-card">
        <div className="flex flex-wrap items-center gap-2.5">
          <span className="inline-flex items-center gap-2 pe-2 text-[12px] font-semibold text-surface-400 uppercase tracking-wide">
            <Zap className="w-4 h-4" />
            {t("dashboard.quickActions")}
          </span>
          <span className="hidden sm:block w-px h-6 bg-surface-200/80 dark:bg-surface-700/60" />
          {quickActions.map((action) => {
            const Icon = action.icon;
            return (
              <Link
                key={action.id}
                to={action.to}
                className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-surface-50 dark:bg-surface-700/40 text-[13px] font-semibold text-surface-600 dark:text-surface-200 hover:bg-primary-50 dark:hover:bg-primary-500/10 hover:text-primary-700 dark:hover:text-primary-300 ring-1 ring-transparent hover:ring-primary-200 transition-all duration-150"
              >
                <Icon className="w-4 h-4" strokeWidth={1.9} />
                {t(action.labelKey)}
              </Link>
            );
          })}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5">
        <StatCard icon={Users} color="blue" label={t("dashboard.kpis.totalWorkers")} value={stats.total_workers} />
        <StatCard icon={Briefcase} color="green" label={t("dashboard.kpis.activeWorkers")} value={stats.workers_by_status?.active || 0} />
        <StatCard icon={Link2} color="purple" label={t("dashboard.kpis.totalExpenses")} value={stats.total_expenses} />
        <StatCard
          icon={DollarSign}
          color="orange"
          label={t("dashboard.kpis.monthlyExpenses")}
          value={formatCurrency(stats.monthly_expenses ?? 0)}
        />
      </div>

      <div className="grid grid-cols-2 xl:grid-cols-4 gap-5">
        <StatCard
          icon={DollarSign}
          color="green"
          label={t("dashboard.kpis.todayExpenses")}
          value={formatCurrency(stats.today_expenses ?? 0)}
        />
        <StatCard
          icon={Wallet}
          color="red"
          label={t("dashboard.kpis.monthExpenses")}
          value={formatCurrency(stats.month_expenses ?? 0)}
        />
        <StatCard
          icon={Briefcase}
          color="blue"
          label={t("dashboard.kpis.totalAdvances")}
          value={stats.total_advances}
        />
        <StatCard
          icon={Wallet}
          color="purple"
          label={t("dashboard.kpis.outstandingAdvances")}
          value={formatCurrency(stats.outstanding_advances ?? 0)}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
        <BreakdownPanel icon={Users} title={t("dashboard.breakdowns.workers")} items={workerStatuses} />
        <BreakdownPanel icon={Briefcase} title={t("dashboard.breakdowns.expenses")} items={expenseStatuses} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 2xl:grid-cols-4 gap-5">
        <RecentList
          icon={Users}
          iconColor="blue"
          title={t("dashboard.activity.recentWorkers")}
          to="/worker-management/workers"
          emptyTitle={t("dashboard.activity.noWorkers")}
          items={stats.recent_workers || []}
          renderItem={(worker) => (
            <li key={worker.id}>
              <Link to="/worker-management/workers" className="flex items-center gap-3 py-3 group">
                <div className="min-w-0 flex-1">
                  <p className="text-[13px] font-semibold text-surface-800 dark:text-surface-200 truncate group-hover:text-primary-600">
                    {worker.full_name}
                  </p>
                  <p className="text-[11px] text-surface-400 truncate">{worker.job_title} · {formatTime(worker.created_at)}</p>
                </div>
                <Badge variant={statusBadge(worker.status)}>{t(`workerManagement.statuses.${worker.status}`)}</Badge>
              </Link>
            </li>
          )}
        />

        <RecentList
          icon={ReceiptText}
          iconColor="green"
          title={t("dashboard.activity.recentExpenses")}
          to="/expenses"
          emptyTitle={t("dashboard.activity.noExpenses")}
          items={stats.recent_expenses || []}
          renderItem={(expense) => (
            <li key={expense.id}>
              <Link to="/expenses" className="flex items-center gap-3 py-3 group">
                <div className="min-w-0 flex-1">
                  <p className="text-[13px] font-semibold text-surface-800 dark:text-surface-200 truncate group-hover:text-primary-600">
                    {expense.title}
                  </p>
                  <p className="text-[11px] text-surface-400 truncate">{expense.category_name} · {formatTime(expense.created_at)}</p>
                </div>
                <span className="numeric-value text-[13px] font-bold text-emerald-600 shrink-0">
                  {formatCurrency(expense.amount)}
                </span>
              </Link>
            </li>
          )}
        />

        <section className="bg-white dark:bg-surface-800/60 rounded-2xl border border-surface-200/80 dark:border-surface-700/60 p-5 shadow-card">
          <div className="flex items-start justify-between gap-3 mb-5">
            <div className="flex items-center gap-3 min-w-0">
              <div className="shrink-0 w-10 h-10 rounded-xl flex items-center justify-center ring-1 bg-primary-50 text-primary-600 ring-primary-100 dark:bg-primary-500/10 dark:text-primary-400">
                <Link2 className="w-5 h-5" strokeWidth={1.8} />
              </div>
              <div className="min-w-0">
                <h2 className="text-[14px] font-bold text-surface-900 dark:text-surface-100 leading-tight">
                  {t("dashboard.services.overview")}
                </h2>
                <p className="text-[12px] text-surface-400 mt-0.5">{t("dashboard.services.overviewSubtitle")}</p>
              </div>
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <Link
              to="/worker-management"
              className="group flex items-center gap-3 rounded-xl border border-surface-200/80 dark:border-surface-700/60 bg-surface-50/60 dark:bg-surface-700/30 p-4 hover:border-primary-300 dark:hover:border-primary-500/40 hover:bg-primary-50/60 dark:hover:bg-primary-500/10 transition-all duration-150"
            >
              <div className="shrink-0 w-10 h-10 rounded-xl bg-white dark:bg-surface-800/60 text-primary-600 dark:text-primary-400 flex items-center justify-center ring-1 ring-surface-200/60 shadow-sm">
                <HardHat className="w-5 h-5" strokeWidth={1.8} />
              </div>
              <div className="min-w-0">
                <p className="text-[13px] font-bold text-surface-800 dark:text-surface-200 truncate group-hover:text-primary-700 dark:group-hover:text-primary-300 transition-colors">
                  {t("services.workerManagement")}
                </p>
                <p className="text-[11px] text-surface-400 truncate">{t("dashboard.services.open")}</p>
              </div>
            </Link>
            <Link
              to="/expenses"
              className="group flex items-center gap-3 rounded-xl border border-surface-200/80 dark:border-surface-700/60 bg-surface-50/60 dark:bg-surface-700/30 p-4 hover:border-primary-300 dark:hover:border-primary-500/40 hover:bg-primary-50/60 dark:hover:bg-primary-500/10 transition-all duration-150"
            >
              <div className="shrink-0 w-10 h-10 rounded-xl bg-white dark:bg-surface-800/60 text-primary-600 dark:text-primary-400 flex items-center justify-center ring-1 ring-surface-200/60 shadow-sm">
                <Wallet className="w-5 h-5" strokeWidth={1.8} />
              </div>
              <div className="min-w-0">
                <p className="text-[13px] font-bold text-surface-800 dark:text-surface-200 truncate group-hover:text-primary-700 dark:group-hover:text-primary-300 transition-colors">
                  {t("services.expenses")}
                </p>
                <p className="text-[11px] text-surface-400 truncate">{t("dashboard.services.open")}</p>
              </div>
            </Link>
          </div>
        </section>
      </div>

      <section className="bg-white dark:bg-surface-800/60 rounded-2xl border border-surface-200/80 dark:border-surface-700/60 p-5 shadow-card">
        <div className="flex items-start justify-between gap-3 mb-5">
          <div className="flex items-center gap-3 min-w-0">
            <div className="shrink-0 w-10 h-10 rounded-xl flex items-center justify-center ring-1 ring-primary-100 bg-primary-50 text-primary-600 dark:bg-primary-500/10 dark:text-primary-400 dark:ring-primary-500/20">
              <Briefcase className="w-5 h-5" strokeWidth={1.8} />
            </div>
            <div className="min-w-0">
              <h2 className="text-[14px] font-bold text-surface-900 dark:text-surface-100 leading-tight">
                {t("dashboard.services.overview")}
              </h2>
              <p className="text-[12px] text-surface-400 mt-0.5">{t("dashboard.services.overviewSubtitle")}</p>
            </div>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-4">
          <Link
            to="/worker-management"
            className="group flex items-center gap-3 rounded-xl border border-surface-200/80 dark:border-surface-700/60 bg-surface-50/60 dark:bg-surface-700/30 p-4 hover:border-primary-300 dark:hover:border-primary-500/40 hover:bg-primary-50/60 dark:hover:bg-primary-500/10 transition-all duration-150"
          >
            <div className="shrink-0 w-10 h-10 rounded-xl bg-white dark:bg-surface-800/60 text-primary-600 dark:text-primary-400 flex items-center justify-center ring-1 ring-surface-200/60 shadow-sm">
              <HardHat className="w-5 h-5" strokeWidth={1.8} />
            </div>
            <div className="min-w-0">
              <p className="text-[13px] font-bold text-surface-800 dark:text-surface-200 truncate group-hover:text-primary-700 dark:group-hover:text-primary-300 transition-colors">
                {t("services.workerManagement")}
              </p>
              <p className="text-[11px] text-surface-400 truncate">{t("dashboard.services.open")}</p>
            </div>
          </Link>
          <Link
            to="/expenses"
            className="group flex items-center gap-3 rounded-xl border border-surface-200/80 dark:border-surface-700/60 bg-surface-50/60 dark:bg-surface-700/30 p-4 hover:border-primary-300 dark:hover:border-primary-500/40 hover:bg-primary-50/60 dark:hover:bg-primary-500/10 transition-all duration-150"
          >
            <div className="shrink-0 w-10 h-10 rounded-xl bg-white dark:bg-surface-800/60 text-primary-600 dark:text-primary-400 flex items-center justify-center ring-1 ring-surface-200/60 shadow-sm">
              <Wallet className="w-5 h-5" strokeWidth={1.8} />
            </div>
            <div className="min-w-0">
              <p className="text-[13px] font-bold text-surface-800 dark:text-surface-200 truncate group-hover:text-primary-700 dark:group-hover:text-primary-300 transition-colors">
                {t("services.expenses")}
              </p>
              <p className="text-[11px] text-surface-400 truncate">{t("dashboard.services.open")}</p>
            </div>
          </Link>
        </div>
      </section>
    </div>
  );
}