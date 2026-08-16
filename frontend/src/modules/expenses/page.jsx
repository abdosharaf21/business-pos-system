import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import toast from "react-hot-toast";
import {
  PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import { expenseService, PAYMENT_METHODS } from "./api";
import { useAuth } from "../../shared/context/AuthContext";
import { PageHeader } from "../../shared/components/PageHeader";
import { Pagination } from "../../shared/components/Pagination";
import { StatCard } from "../../shared/components/StatCard";
import { Modal } from "../../shared/components/Modal";
import { ConfirmDialog } from "../../shared/components/ConfirmDialog";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
import {
  inputClass, selectClass, labelClass, searchInputClass, filterBarClass, cardClass,
  cardClassOverflowHidden, primaryButtonClass, secondaryButtonClass, ghostButtonClass, iconButtonClass,
  dangerIconButtonClass, tableHeadClass, tableBodyClass, tableRowClass,
} from "../../shared/components/styles";
import { formatCurrency } from "../../utils/formatCurrency";
import {
  Plus, Pencil, Trash2, Eye, Search, Wallet, ReceiptText,
  CalendarDays, TrendingUp, Award, ArrowUp, ArrowUpDown, ArrowDown,
  Filter, X,
} from "lucide-react";

const INPUT_CLASS = inputClass;
const LABEL_CLASS = labelClass;
const SELECT_CLASS = selectClass;

const CATEGORY_COLORS = {
  Rent: "#6366f1",
  Salaries: "#10b981",
  Electricity: "#f59e0b",
  Water: "#0ea5e9",
  Internet: "#8b5cf6",
  Transportation: "#f97316",
  Maintenance: "#14b8a6",
  Taxes: "#ef4444",
  Purchases: "#a855f7",
  Marketing: "#ec4899",
  Other: "#64748b",
};

const SORT_COLUMNS = [
  { key: "expense_date", labelKey: "expenses.columns.date" },
  { key: "amount", labelKey: "expenses.columns.amount" },
  { key: "title", labelKey: "expenses.columns.title" },
  { key: "category", labelKey: "expenses.columns.category" },
];

function CategoryBadge({ category }) {
  const { t } = useTranslation();
  return (
    <span
      className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold"
      style={{
        backgroundColor: `${CATEGORY_COLORS[category] || "#64748b"}1A`,
        color: CATEGORY_COLORS[category] || "#64748b",
      }}
    >
      {t(`expenses.categories.${category}`)}
    </span>
  );
}

export default function ExpensesPage() {
  const { t, i18n } = useTranslation();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const canManage = ["admin", "manager"].includes(user?.role);
  const locale = i18n.language === "ar" ? "ar-EG" : "en-US";

  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [paymentMethod, setPaymentMethod] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [sort, setSort] = useState("expense_date");
  const [order, setOrder] = useState("desc");
  const [page, setPage] = useState(1);
  const perPage = 10;

  const [chartYear, setChartYear] = useState(new Date().getFullYear());
  const [chartMonth, setChartMonth] = useState(new Date().getMonth() + 1);

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [details, setDetails] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const { data: summary, isLoading: summaryLoading, error: summaryError, refetch: refetchSummary } = useQuery({
    queryKey: ["expenses-summary"],
    queryFn: async () => {
      const res = await expenseService.getSummary();
      return res.data.data;
    },
  });

  const { data: categories = [] } = useQuery({
    queryKey: ["expense-categories"],
    queryFn: async () => {
      const res = await expenseService.getCategories();
      return res.data.data;
    },
  });

  const { data: listData, isLoading, error, refetch } = useQuery({
    queryKey: ["expenses", search, category, paymentMethod, startDate, endDate, sort, order, page],
    queryFn: async () => {
      const res = await expenseService.getAll({
        search: search || undefined,
        category_id: category || undefined,
        payment_method: paymentMethod || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        sort,
        order,
        page,
        per_page: perPage,
      });
      return res.data.data;
    },
    keepPreviousData: true,
  });

  const { data: categoryData, isLoading: categoryLoading, error: categoryError } = useQuery({
    queryKey: ["expenses-category-chart", chartYear],
    queryFn: async () => {
      const startDate = `${chartYear}-01-01`;
      const endDate = `${chartYear}-12-31`;
      const res = await expenseService.getByCategory({ start_date: startDate, end_date: endDate });
      return res.data.data.data;
    },
    enabled: canManage,
  });

  const { data: monthlyData, isLoading: monthlyLoading, error: monthlyError } = useQuery({
    queryKey: ["expenses-monthly-chart", chartYear, chartMonth],
    queryFn: async () => {
      const res = await expenseService.getMonthly({ year: chartYear, month: chartMonth });
      return res.data.data.data;
    },
    keepPreviousData: true,
    enabled: canManage,
  });

  const { data: yearlyData, isLoading: yearlyLoading, error: yearlyError } = useQuery({
    queryKey: ["expenses-yearly-chart", chartYear],
    queryFn: async () => {
      const res = await expenseService.getYearly({ year: chartYear });
      return res.data.data.data;
    },
    keepPreviousData: true,
    enabled: canManage,
  });

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["expenses"] });
    queryClient.invalidateQueries({ queryKey: ["expenses-summary"] });
    queryClient.invalidateQueries({ queryKey: ["expenses-category-chart"] });
    queryClient.invalidateQueries({ queryKey: ["expenses-monthly-chart"] });
    queryClient.invalidateQueries({ queryKey: ["expenses-yearly-chart"] });
    queryClient.invalidateQueries({ queryKey: ["dashboard"] });
  };

  const createMutation = useMutation({
    mutationFn: (data) => expenseService.create(data),
    onSuccess: () => { invalidate(); toast.success(t("expenses.toast.created")); setModalOpen(false); },
    onError: (err) => toast.error(err.response?.data?.message || t("expenses.toast.createFailed")),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => expenseService.update(id, data),
    onSuccess: () => { invalidate(); toast.success(t("expenses.toast.updated")); setModalOpen(false); setEditing(null); },
    onError: (err) => toast.error(err.response?.data?.message || t("expenses.toast.updateFailed")),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => expenseService.delete(id),
    onSuccess: () => { invalidate(); toast.success(t("expenses.toast.deleted")); setDeleteTarget(null); },
    onError: (err) => toast.error(err.response?.data?.message || t("expenses.toast.deleteFailed")),
  });

  const clearFilters = () => {
    setSearch("");
    setCategory("");
    setPaymentMethod("");
    setStartDate("");
    setEndDate("");
    setPage(1);
  };

  const toggleSort = (key) => {
    if (sort === key) {
      setOrder((prev) => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSort(key);
      setOrder("asc");
    }
    setPage(1);
  };

  const handlePeriodFilterChange = (field, value) => {
    if (field === "start") setStartDate(value);
    if (field === "end") setEndDate(value);
    setPage(1);
  };

  const hasFilters = search || category || paymentMethod || startDate || endDate;

  const items = listData?.items || [];
  const total = listData?.total || 0;
  const pages = listData?.pages || 0;

  if (summaryLoading || isLoading) return <LoadingSpinner />;
  if (summaryError) return <ErrorDisplay message={summaryError.response?.data?.message || summaryError.message} onRetry={refetchSummary} />;
  if (error) return <ErrorDisplay message={error.response?.data?.message || error.message} onRetry={refetch} />;

  return (
    <div>
      <PageHeader
        title={t("expenses.title")}
        description={t("expenses.subtitle")}
        actions={
          canManage && (
            <button onClick={() => { setEditing(null); setModalOpen(true); }} className={primaryButtonClass}>
              <Plus className="w-4 h-4" />
              {t("expenses.newExpense")}
            </button>
          )
        }
      />

      {/* Summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 mb-8">
        <StatCard label={t("expenses.totalExpenses")} value={formatCurrency(summary.total_expenses)} icon={ReceiptText} color="blue" />
        <StatCard label={t("expenses.today")} value={formatCurrency(summary.today_total)} icon={CalendarDays} color="orange" />
        <StatCard label={t("expenses.thisMonth")} value={formatCurrency(summary.this_month_total)} icon={TrendingUp} color="green" />
        <StatCard label={t("expenses.thisYear")} value={formatCurrency(summary.this_year_total)} icon={Wallet} color="purple" />
        <StatCard label={t("expenses.avgMonth")} value={formatCurrency(summary.avg_monthly_total)} icon={ArrowUpDown} color="green" />
        <StatCard
          label={t("expenses.highestCategory")}
          value={summary.highest_category ? t(`expenses.categories.${summary.highest_category}`) : "—"}
          icon={Award}
          color="orange"
        />
      </div>

      {/* Filters */}
      <div className={filterBarClass + " mb-6"}>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-3 items-end">
          <div className="lg:col-span-2 relative">
            <Search className="w-4 h-4 absolute start-3.5 top-1/2 -translate-y-1/2 text-surface-400 dark:text-surface-500 pointer-events-none" />
            <input type="text" placeholder={t("expenses.searchPlaceholder")} value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} className={searchInputClass} aria-label={t("expenses.searchPlaceholder")} />
          </div>
          <div>
            <select value={category} onChange={(e) => { setCategory(e.target.value); setPage(1); }} className={SELECT_CLASS}>
              <option value="">{t("expenses.allCategories")}</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>{t(`expenses.categories.${c.name}`)}</option>
              ))}
            </select>
          </div>
          <div>
            <select value={paymentMethod} onChange={(e) => { setPaymentMethod(e.target.value); setPage(1); }} className={SELECT_CLASS}>
              <option value="">{t("expenses.allMethods")}</option>
              {PAYMENT_METHODS.map((m) => (
                <option key={m} value={m}>{t(`expenses.paymentMethods.${m}`)}</option>
              ))}
            </select>
          </div>
          <div>
            <input type="date" value={startDate} onChange={(e) => handlePeriodFilterChange("start", e.target.value)} className={INPUT_CLASS} aria-label={t("expenses.fromDate")} />
          </div>
          <div>
            <input type="date" value={endDate} onChange={(e) => handlePeriodFilterChange("end", e.target.value)} className={INPUT_CLASS} aria-label={t("expenses.toDate")} />
          </div>
        </div>
        <div className="flex items-center justify-between mt-3 pt-3 border-t border-surface-100 dark:border-surface-700/60">
          <div className="flex items-center gap-2 text-[12px] text-surface-400 dark:text-surface-500">
            <Filter className="w-4 h-4" />
            <span>{t("expenses.showing", { count: items.length, total })}</span>
          </div>
          <div className="flex items-center gap-2">
            {hasFilters && (
              <button onClick={clearFilters} className={ghostButtonClass}>
                <X className="w-3.5 h-3.5" />
                {t("expenses.clear")}
              </button>
            )}
            <select value={sort} onChange={(e) => { setSort(e.target.value); setPage(1); }} className="px-3 py-1.5 rounded-lg border border-surface-200 dark:border-surface-700/60 text-[12px] text-surface-700 dark:text-surface-200 bg-surface-50 dark:bg-surface-700/40 focus:outline-none focus:ring-2 focus:ring-primary-500/20" aria-label={t("expenses.sortBy")}>
              {SORT_COLUMNS.map((col) => (
                <option key={col.key} value={col.key}>{t(col.labelKey)}</option>
              ))}
            </select>
            <button onClick={() => { setOrder((prev) => (prev === "asc" ? "desc" : "asc")); setPage(1); }} className="px-3 py-1.5 rounded-lg border border-surface-200 dark:border-surface-700/60 text-[12px] font-semibold text-surface-600 dark:text-surface-300 bg-surface-50 dark:bg-surface-700/40 hover:bg-surface-100 dark:hover:bg-surface-700 transition-colors" title={order === "asc" ? t("expenses.sortAsc") : t("expenses.sortDesc")}>
              {order === "asc" ? <ArrowUp className="w-4 h-4" /> : <ArrowDown className="w-4 h-4" />}
            </button>
          </div>
        </div>
      </div>

      {/* Table */}
      {items.length === 0 ? (
        <EmptyState
          icon={ReceiptText}
          title={t("expenses.noExpenses")}
          description={t("expenses.noExpensesHint")}
          action={canManage && (
            <button onClick={() => { setEditing(null); setModalOpen(true); }} className={primaryButtonClass}>
              {t("expenses.newExpense")}
            </button>
          )}
        />
      ) : (
        <div className={cardClassOverflowHidden}>
          <div className="overflow-x-auto">
            <table className="w-full text-sm" role="table">
              <thead>
                <tr className={tableHeadClass}>
                  {[
                    { key: "title", labelKey: "expenses.columns.title" },
                    { key: "category", labelKey: "expenses.columns.category" },
                    { key: "amount", labelKey: "expenses.columns.amount" },
                    { key: "payment_method", labelKey: "expenses.columns.paymentMethod" },
                    { key: "expense_date", labelKey: "expenses.columns.date" },
                    { key: "created_by_name", labelKey: "expenses.columns.createdBy" },
                  ].map((col) => (
                    <th key={col.key} className="px-5 py-3.5 text-start text-[11px] font-semibold text-surface-500 dark:text-surface-400 uppercase tracking-wider">
                      <button
                        onClick={() => toggleSort(col.key)}
                        className="inline-flex items-center gap-1 uppercase tracking-wider hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
                        disabled={!canManage}
                      >
                        {t(col.labelKey)}
                        {sort === col.key && (order === "asc" ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />)}
                      </button>
                    </th>
                  ))}
                  <th className="px-5 py-3.5 text-end text-[11px] font-semibold text-surface-500 dark:text-surface-400 uppercase tracking-wider">{t("expenses.columns.actions")}</th>
                </tr>
              </thead>
              <tbody className={tableBodyClass}>
                {items.map((exp) => (
                  <tr key={exp.id} className={tableRowClass}>
                    <td className="px-5 py-3.5">
                      <button onClick={() => setDetails(exp)} className="text-[13px] font-semibold text-surface-800 dark:text-surface-100 hover:text-primary-600 dark:hover:text-primary-400 text-start transition-colors">
                        {exp.title}
                      </button>
                    </td>
                    <td className="px-5 py-3.5 whitespace-nowrap">
                      <CategoryBadge category={exp.category_name} />
                    </td>
                    <td className="px-5 py-3.5 whitespace-nowrap font-bold text-surface-800 dark:text-surface-100 tabular-nums">{formatCurrency(exp.amount)}</td>
                    <td className="px-5 py-3.5 whitespace-nowrap text-[13px] text-surface-600 dark:text-surface-300">{t(`expenses.paymentMethods.${exp.payment_method}`)}</td>
                    <td className="px-5 py-3.5 whitespace-nowrap text-[13px] text-surface-600 dark:text-surface-300">
                      {new Date(exp.expense_date).toLocaleDateString(locale, { year: "numeric", month: "short", day: "numeric" })}
                    </td>
                    <td className="px-5 py-3.5 whitespace-nowrap text-[13px] text-surface-500 dark:text-surface-400">{exp.created_by_name || "—"}</td>
                    <td className="px-5 py-3.5 whitespace-nowrap text-end">
                      <div className="inline-flex items-center gap-1">
                        <button onClick={() => setDetails(exp)} className={iconButtonClass} title={t("expenses.details.title")}>
                          <Eye className="w-4 h-4" />
                        </button>
                        {canManage && (
                          <>
                            <button onClick={() => { setEditing(exp); setModalOpen(true); }} className={iconButtonClass} title={t("expenses.form.titleEdit")}>
                              <Pencil className="w-4 h-4" />
                            </button>
                            <button onClick={() => setDeleteTarget(exp)} className={dangerIconButtonClass} title={t("expenses.confirmDelete.title")}>
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {pages > 1 && (
            <Pagination
              page={page}
              pages={pages}
              onPageChange={setPage}
              pageText={t("expenses.pageOf", { page, pages })}
              prevText={t("expenses.previous")}
              nextText={t("expenses.next")}
            />
          )}
        </div>
      )}

      {/* Charts */}
      {canManage && (
        <div className="mt-8 pt-8 border-t border-surface-200 dark:border-surface-700/60">
          <div className="flex items-center gap-2 mb-5">
            <div className="w-8 h-8 rounded-lg bg-primary-50 dark:bg-primary-500/10 flex items-center justify-center ring-1 ring-primary-100 dark:ring-primary-500/20">
              <TrendingUp className="w-4 h-4 text-primary-600" />
            </div>
            <h2 className="text-lg font-semibold text-surface-900 dark:text-surface-100">{t("expenses.charts.title")}</h2>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <div className={cardClass + " p-6"}>
              <h3 className="text-[15px] font-semibold text-surface-900 dark:text-surface-100 mb-4">{t("expenses.charts.byCategory")}</h3>
              {categoryLoading ? (
                <LoadingSpinner />
              ) : categoryError ? (
                <ErrorDisplay message={categoryError.response?.data?.message || categoryError.message} />
              ) : !categoryData || categoryData.length === 0 ? (
                <p className="text-center text-surface-400 dark:text-surface-500 py-12 text-[13px]">{t("expenses.charts.noData")}</p>
              ) : (
                <ResponsiveContainer width="100%" height={280}>
                  <PieChart>
                    <Pie data={categoryData} dataKey="total" nameKey="category" cx="50%" cy="50%" outerRadius={90} label={(entry) => t(`expenses.categories.${entry.category}`)} labelLine={false}>
                      {categoryData.map((entry) => (
                        <Cell key={entry.category} fill={CATEGORY_COLORS[entry.category] || "#64748b"} />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(value) => formatCurrency(value)}
                      contentStyle={{ borderRadius: "12px", border: "1px solid var(--color-surface-200)", boxShadow: "0 10px 15px -3px rgb(0 0 0 / 0.1)", fontSize: "13px", background: "var(--color-surface-50)", color: "var(--color-surface-800)" }}
                    />
                    <Legend formatter={(value) => t(`expenses.categories.${value}`)} />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>

            <div className={cardClass + " p-6"}>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-[15px] font-semibold text-surface-900 dark:text-surface-100">{t("expenses.charts.monthlyTrend")}</h3>
                <div className="flex items-center gap-2">
                  <select value={chartMonth} onChange={(e) => setChartMonth(Number(e.target.value))} className="px-3 py-1.5 rounded-lg border border-surface-200 dark:border-surface-700/60 text-[12px] text-surface-700 dark:text-surface-200 bg-surface-50 dark:bg-surface-700/40 focus:outline-none focus:ring-2 focus:ring-primary-500/20">
                    {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
                      <option key={m} value={m}>{m}</option>
                    ))}
                  </select>
                  <select value={chartYear} onChange={(e) => setChartYear(Number(e.target.value))} className="px-3 py-1.5 rounded-lg border border-surface-200 dark:border-surface-700/60 text-[12px] text-surface-700 dark:text-surface-200 bg-surface-50 dark:bg-surface-700/40 focus:outline-none focus:ring-2 focus:ring-primary-500/20">
                    {[new Date().getFullYear(), new Date().getFullYear() - 1].map((y) => (
                      <option key={y} value={y}>{y}</option>
                    ))}
                  </select>
                </div>
              </div>
              {monthlyLoading ? (
                <LoadingSpinner />
              ) : monthlyError ? (
                <ErrorDisplay message={monthlyError.response?.data?.message || monthlyError.message} />
              ) : !monthlyData || monthlyData.length === 0 ? (
                <p className="text-center text-surface-400 dark:text-surface-500 py-12 text-[13px]">{t("expenses.charts.noData")}</p>
              ) : (
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={monthlyData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-surface-200)" />
                    <XAxis dataKey="day" tick={{ fontSize: 11, fill: "var(--color-surface-400)" }} tickLine={false} axisLine={{ stroke: "var(--color-surface-200)" }} />
                    <YAxis tick={{ fontSize: 11, fill: "var(--color-surface-400)" }} tickLine={false} axisLine={{ stroke: "var(--color-surface-200)" }} />
                    <Tooltip
                      formatter={(value) => formatCurrency(value)}
                      contentStyle={{ borderRadius: "12px", border: "1px solid var(--color-surface-200)", boxShadow: "0 10px 15px -3px rgb(0 0 0 / 0.1)", fontSize: "13px", background: "var(--color-surface-50)", color: "var(--color-surface-800)" }}
                    />
                    <Bar dataKey="total" fill="#6366f1" radius={[4, 4, 0, 0]} maxBarSize={28} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>

          <div className={"mt-5 " + cardClass + " p-6"}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-[15px] font-semibold text-surface-900 dark:text-surface-100">{t("expenses.charts.yearlyTrend")}</h3>
              <select value={chartYear} onChange={(e) => setChartYear(Number(e.target.value))} className="px-3 py-1.5 rounded-lg border border-surface-200 dark:border-surface-700/60 text-[12px] text-surface-700 dark:text-surface-200 bg-surface-50 dark:bg-surface-700/40 focus:outline-none focus:ring-2 focus:ring-primary-500/20">
                {[new Date().getFullYear(), new Date().getFullYear() - 1].map((y) => (
                  <option key={y} value={y}>{y}</option>
                ))}
              </select>
            </div>
            {yearlyLoading ? (
              <LoadingSpinner />
            ) : yearlyError ? (
              <ErrorDisplay message={yearlyError.response?.data?.message || yearlyError.message} />
            ) : !yearlyData || yearlyData.length === 0 ? (
              <p className="text-center text-surface-400 dark:text-surface-500 py-12 text-[13px]">{t("expenses.charts.noData")}</p>
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={yearlyData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--color-surface-200)" />
                  <XAxis dataKey="month" tick={{ fontSize: 11, fill: "var(--color-surface-400)" }} tickLine={false} axisLine={{ stroke: "var(--color-surface-200)" }} />
                  <YAxis tick={{ fontSize: 11, fill: "var(--color-surface-400)" }} tickLine={false} axisLine={{ stroke: "var(--color-surface-200)" }} />
                  <Tooltip
                    formatter={(value) => formatCurrency(value)}
                    contentStyle={{ borderRadius: "12px", border: "1px solid var(--color-surface-200)", boxShadow: "0 10px 15px -3px rgb(0 0 0 / 0.1)", fontSize: "13px", background: "var(--color-surface-50)", color: "var(--color-surface-800)" }}
                  />
                  <Bar dataKey="total" fill="#10b981" radius={[4, 4, 0, 0]} maxBarSize={36} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      )}

      <ExpenseModal
        isOpen={modalOpen}
        onClose={() => { setModalOpen(false); setEditing(null); }}
        editing={editing}
        categories={categories}
        onSubmit={(data) => editing ? updateMutation.mutate({ id: editing.id, data }) : createMutation.mutate(data)}
        loading={createMutation.isPending || updateMutation.isPending}
      />

      <ExpenseDetailsModal expense={details} onClose={() => setDetails(null)} />

      <ConfirmDialog
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => deleteMutation.mutate(deleteTarget.id)}
        title={t("expenses.confirmDelete.title")}
        message={t("expenses.confirmDelete.message", { name: deleteTarget?.title })}
        loading={deleteMutation.isPending}
      />
    </div>
  );
}

function ExpenseModal({ isOpen, onClose, editing, onSubmit, loading, categories = [] }) {
  const { t } = useTranslation();

  const expenseSchema = useMemo(() => z.object({
    title: z.string().min(1, t("expenses.validation.titleRequired")),
    category_id: z.string().min(1, t("expenses.validation.categoryRequired")),
    amount: z.coerce.number().positive(t("expenses.validation.amountPositive")).refine((v) => v > 0, t("expenses.validation.amountPositive")),
    payment_method: z.string().optional(),
    expense_date: z.string().min(1, t("expenses.validation.dateRequired")),
    notes: z.string().optional(),
  }), [t]);

  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: zodResolver(expenseSchema),
    values: editing
      ? {
          title: editing.title,
          category_id: editing.category_id?.toString() || "",
          amount: editing.amount,
          payment_method: editing.payment_method,
          expense_date: editing.expense_date,
          notes: editing.notes || "",
        }
      : {
          title: "",
          category_id: categories[0]?.id?.toString() || "",
          payment_method: "Cash",
          expense_date: new Date().toISOString().slice(0, 10),
          notes: "",
        },
  });

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={editing ? t("expenses.form.titleEdit") : t("expenses.form.title")}>
      <form onSubmit={handleSubmit((data) => { onSubmit(data); reset(); })} className="space-y-5">
        <div>
          <label className={LABEL_CLASS}>{t("expenses.form.titleLabel")}</label>
          <input {...register("title")} placeholder={t("expenses.form.titlePlaceholder")} className={INPUT_CLASS} />
          {errors.title && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.title.message}</p>}
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>{t("expenses.form.categoryLabel")}</label>
            <select {...register("category_id")} className={SELECT_CLASS}>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>{t(`expenses.categories.${c.name}`)}</option>
              ))}
            </select>
            {errors.category_id && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.category_id.message}</p>}
          </div>
          <div>
            <label className={LABEL_CLASS}>{t("expenses.form.paymentMethodLabel")}</label>
            <select {...register("payment_method")} className={SELECT_CLASS}>
              {PAYMENT_METHODS.map((m) => (
                <option key={m} value={m}>{t(`expenses.paymentMethods.${m}`)}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>{t("expenses.form.amountLabel")}</label>
            <input type="number" step="0.01" min="0" {...register("amount")} placeholder={t("expenses.form.amountPlaceholder")} className={`${INPUT_CLASS} numeric-grow min-w-14`} />
            {errors.amount && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.amount.message}</p>}
          </div>
          <div>
            <label className={LABEL_CLASS}>{t("expenses.form.dateLabel")}</label>
            <input type="date" {...register("expense_date")} className={INPUT_CLASS} />
            {errors.expense_date && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.expense_date.message}</p>}
          </div>
        </div>
        <div>
          <label className={LABEL_CLASS}>{t("expenses.form.notesLabel")}</label>
          <textarea {...register("notes")} rows={3} placeholder={t("expenses.form.notesPlaceholder")} className={`${INPUT_CLASS} resize-none`} />
        </div>
        <div className="flex justify-end gap-3 pt-5 border-t border-surface-100 dark:border-surface-700/60">
          <button type="button" onClick={onClose} className={secondaryButtonClass}>{t("expenses.form.cancel")}</button>
          <button type="submit" disabled={loading} className={primaryButtonClass}>{loading ? t("expenses.form.saving") : t("expenses.form.save")}</button>
        </div>
      </form>
    </Modal>
  );
}

function ExpenseDetailsModal({ expense, onClose }) {
  const { t, i18n } = useTranslation();
  const locale = i18n.language === "ar" ? "ar-EG" : "en-US";

  if (!expense) return null;

  const rows = [
    { label: t("expenses.columns.category"), value: t(`expenses.categories.${expense.category_name}`) },
    { label: t("expenses.columns.amount"), value: formatCurrency(expense.amount), tabular: true },
    { label: t("expenses.columns.paymentMethod"), value: t(`expenses.paymentMethods.${expense.payment_method}`) },
    { label: t("expenses.columns.date"), value: new Date(expense.expense_date).toLocaleDateString(locale, { year: "numeric", month: "long", day: "numeric" }) },
    { label: t("expenses.columns.createdBy"), value: expense.created_by_name || "—" },
    { label: t("expenses.columns.createdAt"), value: new Date(expense.created_at).toLocaleString(locale) },
  ];

  return (
    <Modal isOpen={!!expense} onClose={onClose} title={t("expenses.details.title")}>
      <div className="space-y-4">
        <div className="bg-surface-50 dark:bg-surface-700/40 rounded-xl p-4">
          <p className="text-[11px] font-semibold text-surface-400 dark:text-surface-500 uppercase tracking-wide mb-1">{t("expenses.columns.title")}</p>
          <p className="text-[15px] font-bold text-surface-900 dark:text-surface-100">{expense.title}</p>
          {expense.notes && (
            <p className="text-[13px] text-surface-600 dark:text-surface-300 mt-3 leading-relaxed">{expense.notes}</p>
          )}
        </div>
        <div className="divide-y divide-surface-100 dark:divide-surface-700/60">
          {rows.map((row) => (
            <div key={row.label} className="flex items-center justify-between gap-3 py-2.5">
              <span className="text-[13px] text-surface-500 dark:text-surface-400">{row.label}</span>
              <span className={`text-[13px] font-semibold text-surface-800 dark:text-surface-100 text-end min-w-0 ${row.tabular ? "tabular-nums whitespace-nowrap" : ""}`}>{row.value}</span>
            </div>
          ))}
        </div>
        <div className="flex justify-end pt-4 border-t border-surface-100 dark:border-surface-700/60">
          <button onClick={onClose} className={secondaryButtonClass}>{t("expenses.details.close")}</button>
        </div>
      </div>
    </Modal>
  );
}
