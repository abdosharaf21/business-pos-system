import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  UserCheck,
  CalendarCheck,
  Wallet,
  HandCoins,
  RefreshCw,
  ChevronRight,
  Inbox,
  HardHat,
  BadgeDollarSign,
  UsersRound,
} from "lucide-react";
import { workerManagementService } from "./api";
import { PageHeader } from "../../shared/components/PageHeader";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { StatCard } from "../../shared/components/StatCard";
import { Badge, statusBadge } from "../../shared/components/Badge";
import { useAuth } from "../../shared/context/AuthContext";

const NAV_ITEMS = [
  { to: "/worker-management/workers", key: "workers", icon: UserCheck, color: "blue" },
  { to: "/worker-management/attendance", key: "attendance", icon: CalendarCheck, color: "green" },
  { to: "/worker-management/salaries", key: "salaries", icon: Wallet, color: "orange" },
  { to: "/worker-management/advances", key: "advances", icon: HandCoins, color: "purple" },
  { to: "/worker-management/reports", key: "reports", icon: BadgeDollarSign, color: "red" },
];

function StatusBreakdown({ icon: Icon, title, items }) {
  const total = items.reduce((sum, item) => sum + item.value, 0) || 1;

  return (
    <section className="bg-white dark:bg-surface-800/60 rounded-2xl border border-surface-200/80 dark:border-surface-700/60 p-5 shadow-card">
      <div className="flex items-center gap-3 mb-5">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center ring-1 ring-surface-200/60 bg-surface-50 text-surface-500">
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

export default function WorkerManagementPage() {
  const { t, i18n } = useTranslation();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const canManage = ["admin", "manager"].includes(user?.role);
  const locale = i18n.language === "ar" ? "ar-EG" : "en-US";

  const { data: stats, isLoading, error, refetch } = useQuery({
    queryKey: ["worker-management", "statistics"],
    queryFn: async () => {
      const res = await workerManagementService.getStatistics();
      return res.data.data;
    },
  });

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: ["worker-management"] });
  };

  const formatCurrency = (value) =>
    new Intl.NumberFormat(locale, { maximumFractionDigits: 2 }).format(value || 0);

  const formatDate = (value) => {
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

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay message={error.response?.data?.message || error.message} onRetry={refetch} />;

  const attendanceBreakdown = [
    { label: t("workerManagement.statuses.present"), value: stats.attendance_by_status?.present || 0 },
    { label: t("workerManagement.statuses.absent"), value: stats.attendance_by_status?.absent || 0 },
    { label: t("workerManagement.statuses.late"), value: stats.attendance_by_status?.late || 0 },
    { label: t("workerManagement.statuses.half_day"), value: stats.attendance_by_status?.half_day || 0 },
    { label: t("workerManagement.statuses.leave"), value: stats.attendance_by_status?.leave || 0 },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title={t("workerManagement.title")}
        description={t("workerManagement.subtitle")}
        actions={
          <button
            onClick={handleRefresh}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-white dark:bg-surface-800/60 border border-surface-200/80 dark:border-surface-700/60 text-[13px] font-semibold text-surface-600 dark:text-surface-300 hover:text-primary-600 hover:border-primary-300 shadow-card transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            {t("workerManagement.refresh")}
          </button>
        }
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard icon={UsersRound} color="blue" label={t("workerManagement.kpis.totalWorkers")} value={stats.total_workers} />
        <StatCard icon={UserCheck} color="green" label={t("workerManagement.kpis.activeWorkers")} value={stats.active_workers} />
        <StatCard icon={CalendarCheck} color="orange" label={t("workerManagement.kpis.todayAttendance")} value={stats.today_attendance} />
        <StatCard icon={HandCoins} color="purple" label={t("workerManagement.kpis.outstandingAdvances")} value={formatCurrency(stats.outstanding_advances)} />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        <div className="sm:col-span-2 lg:col-span-1">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-1 gap-5">
            <section className="bg-white dark:bg-surface-800/60 rounded-2xl border border-surface-200/80 dark:border-surface-700/60 p-5 shadow-card">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center ring-1 ring-surface-200/60 bg-surface-50 text-surface-500">
                  <BadgeDollarSign className="w-5 h-5" strokeWidth={1.8} />
                </div>
                <h2 className="text-[14px] font-bold text-surface-900 dark:text-surface-100">{t("workerManagement.payroll.title")}</h2>
              </div>
              <div className="flex items-end justify-between">
                <div>
                  <p className="text-[11px] font-semibold text-surface-400 dark:text-surface-500 uppercase tracking-wide">{t("workerManagement.payroll.pending")}</p>
                  <p className="text-2xl font-extrabold text-surface-900 dark:text-surface-100 tabular-nums">{stats.pending_salary_count || 0}</p>
                </div>
                <div className="text-end">
                  <p className="text-[11px] font-semibold text-surface-400 dark:text-surface-500 uppercase tracking-wide">{t("workerManagement.payroll.total")}</p>
                  <p className="text-[15px] font-bold text-surface-900 dark:text-surface-100 tabular-nums">{formatCurrency(stats.pending_salary_total)}</p>
                </div>
              </div>
            </section>
            <section className="bg-white dark:bg-surface-800/60 rounded-2xl border border-surface-200/80 dark:border-surface-700/60 p-5 shadow-card">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center ring-1 ring-surface-200/60 bg-surface-50 text-surface-500">
                  <Wallet className="w-5 h-5" strokeWidth={1.8} />
                </div>
                <h2 className="text-[14px] font-bold text-surface-900 dark:text-surface-100">{t("workerManagement.workforce.title")}</h2>
              </div>
              <div className="flex items-end justify-between">
                <div>
                  <p className="text-[11px] font-semibold text-surface-400 dark:text-surface-500 uppercase tracking-wide">{t("workerManagement.workforce.total")}</p>
                  <p className="text-2xl font-extrabold text-surface-900 dark:text-surface-100 tabular-nums">{stats.total_workers || 0}</p>
                </div>
                <div className="text-end">
                  <p className="text-[11px] font-semibold text-surface-400 dark:text-surface-500 uppercase tracking-wide">{t("workerManagement.workforce.paidSalaries")}</p>
                  <p className="text-[15px] font-bold text-surface-900 dark:text-surface-100 tabular-nums">{stats.total_salaries_paid || 0}</p>
                </div>
              </div>
            </section>
          </div>
        </div>
        <StatusBreakdown
          icon={CalendarCheck}
          title={t("workerManagement.breakdown.attendance")}
          items={attendanceBreakdown}
        />
        <section className="bg-white dark:bg-surface-800/60 rounded-2xl border border-surface-200/80 dark:border-surface-700/60 p-5 shadow-card">
          <div className="flex items-center gap-3 mb-5">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center ring-1 ring-surface-200/60 bg-surface-50 text-surface-500">
              <HardHat className="w-5 h-5" strokeWidth={1.8} />
            </div>
            <h2 className="text-[14px] font-bold text-surface-900 dark:text-surface-100">{t("workerManagement.quickAccess.title")}</h2>
          </div>
          <ul className="space-y-1.5">
            {NAV_ITEMS.map(({ to, key, icon: Icon }) => (
              <li key={key}>
                <Link to={to} className="flex items-center gap-3 px-3 py-2.5 rounded-xl hover:bg-surface-50 dark:hover:bg-surface-700/40 group transition-colors">
                  <div className="w-9 h-9 rounded-xl bg-surface-100 dark:bg-surface-700/50 text-surface-500 dark:text-surface-300 flex items-center justify-center ring-1 ring-surface-200/60 dark:ring-surface-600/50 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                    <Icon className="w-4.5 h-4.5 w-5 h-5" strokeWidth={1.8} />
                  </div>
                  <span className="flex-1 text-[13px] font-semibold text-surface-700 dark:text-surface-200 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
                    {t(`nav.${key}`)}
                  </span>
                  <ChevronRight className="w-4 h-4 text-surface-300 dark:text-surface-600 rtl:rotate-180" />
                </Link>
              </li>
            ))}
          </ul>
        </section>
      </div>

      <section className="bg-white dark:bg-surface-800/60 rounded-2xl border border-surface-200/80 dark:border-surface-700/60 p-5 shadow-card">
        <div className="flex items-start justify-between gap-3 mb-5">
          <div className="flex items-center gap-3 min-w-0">
            <div className="shrink-0 w-10 h-10 rounded-xl bg-primary-50 text-primary-600 ring-primary-100 dark:bg-primary-500/10 dark:text-primary-400 dark:ring-primary-500/20 flex items-center justify-center ring-1">
              <UsersRound className="w-5 h-5" strokeWidth={1.8} />
            </div>
            <h2 className="text-[14px] font-bold text-surface-900 dark:text-surface-100 leading-tight">{t("workerManagement.recent.workers")}</h2>
          </div>
          <Link to="/worker-management/workers" className="inline-flex items-center gap-1 text-[12px] font-semibold text-primary-600 hover:text-primary-700">
            {t("workerManagement.viewAll")}
            <ChevronRight className="w-3.5 h-3.5 rtl:rotate-180" />
          </Link>
        </div>
        {!stats.recent_workers?.length ? (
          <div className="flex flex-col items-center justify-center py-10 text-center px-4">
            <div className="w-12 h-12 bg-surface-100 dark:bg-surface-700/50 rounded-xl flex items-center justify-center mb-3 ring-1 ring-surface-200/60">
              <Inbox className="w-6 h-6 text-surface-400" strokeWidth={1.5} />
            </div>
            <p className="text-[13px] font-semibold text-surface-600 dark:text-surface-300">{t("workerManagement.recent.noWorkers")}</p>
            {canManage && (
              <Link to="/worker-management/workers" className="mt-3 text-[13px] font-semibold text-primary-600 hover:text-primary-700">
                {t("workerManagement.addFirstWorker")}
              </Link>
            )}
          </div>
        ) : (
          <ul className="divide-y divide-surface-100 dark:divide-surface-700/60">
            {stats.recent_workers.map((worker) => (
              <li key={worker.id}>
                <Link to="/worker-management/workers" className="flex items-center gap-3 py-3 group">
                  <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-[11px] font-bold text-white shrink-0">
                    {worker.full_name?.charAt(0)?.toUpperCase() || "?"}
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-[13px] font-semibold text-surface-800 dark:text-surface-200 truncate group-hover:text-primary-600">
                      {worker.full_name}
                    </p>
                    <p className="text-[11px] text-surface-400 truncate">
                      {[worker.job_title, worker.department].filter(Boolean).join(" · ") || formatDate(worker.created_at)}
                    </p>
                  </div>
                  <Badge variant={statusBadge(worker.status)}>{t(`workerManagement.statuses.${worker.status}`)}</Badge>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
