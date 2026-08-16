import { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { workerManagementService } from "./api";
import { useAuth } from "../../shared/context/AuthContext";
import { PageHeader } from "../../shared/components/PageHeader";
import { DataTable } from "../../shared/components/DataTable";
import { StatCard } from "../../shared/components/StatCard";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
import { Badge } from "../../shared/components/Badge";
import { inputClass, secondaryButtonClass } from "../../shared/components/styles";
import {
  ClipboardList, Wallet, CalendarRange, TrendingUp, UserCheck,
} from "lucide-react";

const INPUT_CLASS = inputClass;

export default function ReportsPage() {
  const { t, i18n } = useTranslation();
  const { user } = useAuth();
  const canManage = ["admin", "manager"].includes(user?.role);
  const locale = i18n.language === "ar" ? "ar-EG" : "en-US";
  const [attFrom, setAttFrom] = useState("");
  const [attTo, setAttTo] = useState("");
  const [salFrom, setSalFrom] = useState("");
  const [salTo, setSalTo] = useState("");
  const [tab, setTab] = useState("attendance");

  const attendanceQuery = useQuery({
    queryKey: ["worker-management", "reports", "attendance", attFrom, attTo],
    queryFn: async () => {
      const res = await workerManagementService.getAttendanceReport({
        from: attFrom || undefined,
        to: attTo || undefined,
      });
      return res.data.data;
    },
  });

  const salaryQuery = useQuery({
    queryKey: ["worker-management", "reports", "salaries", salFrom, salTo],
    queryFn: async () => {
      const res = await workerManagementService.getSalaryReport({
        from: salFrom || undefined,
        to: salTo || undefined,
      });
      return res.data.data;
    },
  });

  const attendanceRows = attendanceQuery.data || [];
  const salaryRows = salaryQuery.data || [];

  const totals = useMemo(() => attendanceRows.reduce(
    (acc, r) => ({
      total_days: acc.total_days + (Number(r.total_days) || 0),
      present_days: acc.present_days + (Number(r.present_days) || 0),
      late_days: acc.late_days + (Number(r.late_days) || 0),
      absent_days: acc.absent_days + (Number(r.absent_days) || 0),
    }),
    { total_days: 0, present_days: 0, late_days: 0, absent_days: 0 },
  // eslint-disable-next-line react-hooks/exhaustive-deps
  ), [attendanceRows]);

  const payroll = useMemo(() => salaryRows.reduce(
    (acc, r) => ({
      gross: acc.gross + (Number(r.base_salary) || 0) + (Number(r.bonuses) || 0),
      advances: acc.advances + (Number(r.advances_deduction) || 0),
      net: acc.net + (Number(r.net_amount) || 0),
    }),
    { gross: 0, advances: 0, net: 0 },
  // eslint-disable-next-line react-hooks/exhaustive-deps
  ), [salaryRows]);

  const formatMoney = (value) => (Number(value) || 0).toLocaleString(locale, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const formatDate = (value) => {
    if (!value) return "—";
    try {
      return new Date(value).toLocaleDateString(locale, { year: "numeric", month: "short", day: "numeric" });
    } catch {
      return "—";
    }
  };

  const attendanceColumns = [
    { key: "worker_name", label: t("workerManagement.reports.attendance.columns.worker"), render: (val) => <span className="text-[13px] font-semibold text-surface-800 dark:text-surface-100">{val}</span> },
    { key: "total_days", label: t("workerManagement.reports.attendance.columns.total") },
    { key: "present_days", label: t("workerManagement.reports.attendance.columns.present"), render: (val) => <Badge variant="success">{val}</Badge> },
    { key: "late_days", label: t("workerManagement.reports.attendance.columns.late"), render: (val) => <Badge variant="warning">{val}</Badge> },
    { key: "half_days", label: t("workerManagement.reports.attendance.columns.half") },
    { key: "absent_days", label: t("workerManagement.reports.attendance.columns.absent"), render: (val) => <Badge variant="danger">{val}</Badge> },
    { key: "leave_days", label: t("workerManagement.reports.attendance.columns.leave"), render: (val) => <Badge variant="info">{val}</Badge> },
  ];

  const salaryColumns = [
    { key: "worker_name", label: t("workerManagement.reports.salaries.columns.worker"), render: (val) => <span className="text-[13px] font-semibold text-surface-800 dark:text-surface-100">{val}</span> },
    { key: "salary_period", label: t("workerManagement.reports.salaries.columns.period") },
    { key: "base_salary", label: t("workerManagement.reports.salaries.columns.base"), render: (val) => <span className="tabular-nums">{formatMoney(val)}</span> },
    { key: "bonuses", label: t("workerManagement.reports.salaries.columns.bonuses"), render: (val) => <span className="tabular-nums">{formatMoney(val)}</span> },
    { key: "deductions", label: t("workerManagement.reports.salaries.columns.deductions"), render: (val) => <span className="tabular-nums">{formatMoney(val)}</span> },
    { key: "advances_deduction", label: t("workerManagement.reports.salaries.columns.advances"), render: (val) => <span className="tabular-nums text-rose-600 dark:text-rose-400">-{formatMoney(val)}</span> },
    { key: "net_amount", label: t("workerManagement.reports.salaries.columns.net"), render: (val) => <span className="font-bold tabular-nums">{formatMoney(val)}</span> },
    { key: "payment_status", label: t("workerManagement.reports.salaries.columns.status"), render: (val) => <Badge variant={val === "paid" ? "success" : val === "partial" ? "warning" : "info"}>{t(`workerManagement.statuses.${val}`)}</Badge> },
    { key: "payment_date", label: t("workerManagement.reports.salaries.columns.paidAt"), render: formatDate },
  ];

  if (attendanceQuery.isLoading || salaryQuery.isLoading) return <LoadingSpinner />;

  return (
    <div>
      <PageHeader
        title={t("workerManagement.reports.title")}
        description={t("workerManagement.reports.subtitle")}
      />

      <div className="flex items-center gap-2 mb-6 border-b border-surface-100 dark:border-surface-700/60">
        <button
          onClick={() => setTab("attendance")}
          className={`px-4 py-2.5 text-[13px] font-semibold rounded-t-lg border-b-2 transition-colors ${tab === "attendance" ? "border-primary-500 text-primary-600 dark:text-primary-400" : "border-transparent text-surface-500 dark:text-surface-400 hover:text-surface-700 dark:hover:text-surface-200"}`}
        >
          {t("workerManagement.reports.attendance.tab")}
        </button>
        <button
          onClick={() => setTab("salaries")}
          className={`px-4 py-2.5 text-[13px] font-semibold rounded-t-lg border-b-2 transition-colors ${tab === "salaries" ? "border-primary-500 text-primary-600 dark:text-primary-400" : "border-transparent text-surface-500 dark:text-surface-400 hover:text-surface-700 dark:hover:text-surface-200"}`}
        >
          {t("workerManagement.reports.salaries.tab")}
        </button>
      </div>

      {tab === "attendance" ? (
        <div className="space-y-6">
          {attendanceRows.length > 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard icon={UserCheck} color="green" label={t("workerManagement.reports.attendance.summary.present")} value={totals.present_days} />
              <StatCard icon={CalendarRange} color="orange" label={t("workerManagement.reports.attendance.summary.late")} value={totals.late_days} />
              <StatCard icon={ClipboardList} color="red" label={t("workerManagement.reports.attendance.summary.absent")} value={totals.absent_days} />
              <StatCard icon={TrendingUp} color="blue" label={t("workerManagement.reports.attendance.summary.total")} value={totals.total_days} />
            </div>
          )}

          <div className="flex flex-wrap items-end gap-3 mb-4">
            <div>
              <label className="block text-[11px] font-semibold uppercase tracking-wide text-surface-500 dark:text-surface-400 mb-1.5">{t("workerManagement.reports.attendance.from")}</label>
              <input type="date" value={attFrom} onChange={(e) => setAttFrom(e.target.value)} className={INPUT_CLASS} />
            </div>
            <div>
              <label className="block text-[11px] font-semibold uppercase tracking-wide text-surface-500 dark:text-surface-400 mb-1.5">{t("workerManagement.reports.attendance.to")}</label>
              <input type="date" value={attTo} onChange={(e) => setAttTo(e.target.value)} className={INPUT_CLASS} />
            </div>
            {(attFrom || attTo) && (
              <button onClick={() => { setAttFrom(""); setAttTo(""); }} className={secondaryButtonClass}>
                {t("workerManagement.reports.clear")}
              </button>
            )}
          </div>

          {attendanceQuery.isError ? (
            <ErrorDisplay message={attendanceQuery.error.response?.data?.message || attendanceQuery.error.message} onRetry={() => attendanceQuery.refetch()} />
          ) : attendanceRows.length === 0 ? (
            <EmptyState icon={ClipboardList} title={t("workerManagement.reports.attendance.empty.title")} description={t("workerManagement.reports.attendance.empty.description")} />
          ) : (
            <DataTable columns={attendanceColumns} data={attendanceRows} />
          )}
        </div>
      ) : (
        <div className="space-y-6">
          {salaryRows.length > 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <StatCard icon={Wallet} color="blue" label={t("workerManagement.reports.salaries.summary.gross")} value={formatMoney(payroll.gross)} />
              <StatCard icon={TrendingUp} color="red" label={t("workerManagement.reports.salaries.summary.advances")} value={formatMoney(payroll.advances)} />
              <StatCard icon={Wallet} color="green" label={t("workerManagement.reports.salaries.summary.net")} value={formatMoney(payroll.net)} />
            </div>
          )}

          <div className="flex flex-wrap items-end gap-3 mb-4">
            <div>
              <label className="block text-[11px] font-semibold uppercase tracking-wide text-surface-500 dark:text-surface-400 mb-1.5">{t("workerManagement.reports.salaries.from")}</label>
              <input type="month" value={salFrom} onChange={(e) => setSalFrom(e.target.value)} className={INPUT_CLASS} />
            </div>
            <div>
              <label className="block text-[11px] font-semibold uppercase tracking-wide text-surface-500 dark:text-surface-400 mb-1.5">{t("workerManagement.reports.salaries.to")}</label>
              <input type="month" value={salTo} onChange={(e) => setSalTo(e.target.value)} className={INPUT_CLASS} />
            </div>
            {(salFrom || salTo) && (
              <button onClick={() => { setSalFrom(""); setSalTo(""); }} className={secondaryButtonClass}>
                {t("workerManagement.reports.clear")}
              </button>
            )}
          </div>

          {salaryQuery.isError ? (
            <ErrorDisplay message={salaryQuery.error.response?.data?.message || salaryQuery.error.message} onRetry={() => salaryQuery.refetch()} />
          ) : salaryRows.length === 0 ? (
            <EmptyState icon={Wallet} title={t("workerManagement.reports.salaries.empty.title")} description={t("workerManagement.reports.salaries.empty.description")} />
          ) : (
            <DataTable columns={salaryColumns} data={salaryRows} />
          )}
        </div>
      )}

      {!canManage && (
        <p className="mt-6 text-[12px] text-surface-400 dark:text-surface-500">
          {t("workerManagement.reports.readOnlyHint")}
        </p>
      )}
    </div>
  );
}
