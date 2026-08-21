import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import {
  CreditCard,
  Package,
  Wallet,
  Users,
  ChevronRight,
  ExternalLink,
} from "lucide-react";
import { PageHeader } from "../../shared/components/PageHeader";
import { Badge } from "../../shared/components/Badge";
import { cardClass } from "../../shared/components/styles";

const APP_LIST = [
  {
    id: "pos",
    nameKey: "bdDashboard.services.pos.name",
    nameFallback: "POS System",
    descriptionKey: "bdDashboard.services.pos.description",
    descriptionFallback: "Core point-of-sale system for daily sales operations",
    icon: CreditCard,
    color: "blue",
    status: "active",
    route: "/dashboard",
    features: [
      { nameKey: "bdDashboard.services.pos.features.sales", nameFallback: "Sales" },
      { nameKey: "bdDashboard.services.pos.features.products", nameFallback: "Products" },
      { nameKey: "bdDashboard.services.pos.features.basicInventory", nameFallback: "Basic Inventory" },
      { nameKey: "bdDashboard.services.pos.features.purchases", nameFallback: "Purchases" },
      { nameKey: "bdDashboard.services.pos.features.basicReports", nameFallback: "Basic Reports" },
    ],
  },
  {
    id: "inventory",
    nameKey: "bdDashboard.services.inventory.name",
    nameFallback: "Advanced Inventory",
    descriptionKey: "bdDashboard.services.inventory.description",
    descriptionFallback: "Advanced inventory management with warehouses, audits, and reorder",
    icon: Package,
    color: "green",
    status: "active",
    route: "/inventory",
    features: [
      { nameKey: "bdDashboard.services.inventory.features.warehouses", nameFallback: "Warehouses" },
      { nameKey: "bdDashboard.services.inventory.features.transfers", nameFallback: "Transfers" },
      { nameKey: "bdDashboard.services.inventory.features.audits", nameFallback: "Audits" },
      { nameKey: "bdDashboard.services.inventory.features.reorder", nameFallback: "Reorder" },
      { nameKey: "bdDashboard.services.inventory.features.expiration", nameFallback: "Expiration" },
      { nameKey: "bdDashboard.services.inventory.features.advancedReports", nameFallback: "Advanced Reports" },
    ],
  },
  {
    id: "expenses",
    nameKey: "bdDashboard.services.expenses.name",
    nameFallback: "Expenses",
    descriptionKey: "bdDashboard.services.expenses.description",
    descriptionFallback: "Expense tracking and reporting",
    icon: Wallet,
    color: "orange",
    status: "active",
    route: "/expenses",
    features: [
      { nameKey: "bdDashboard.services.expenses.features.expenses", nameFallback: "Expenses" },
      { nameKey: "bdDashboard.services.expenses.features.categories", nameFallback: "Categories" },
      { nameKey: "bdDashboard.services.expenses.features.reports", nameFallback: "Reports" },
    ],
  },
  {
    id: "worker-management",
    nameKey: "bdDashboard.services.workerManagement.name",
    nameFallback: "Worker Management",
    descriptionKey: "bdDashboard.services.workerManagement.description",
    descriptionFallback: "Employee and workforce management — separate standalone application",
    icon: Users,
    color: "default",
    status: "external",
    route: null,
    features: [],
  },
];

const COLOR_MAP = {
  blue: {
    icon: "bg-primary-50 text-primary-600 ring-primary-100 dark:bg-primary-500/10 dark:text-primary-400 dark:ring-primary-500/20",
    border: "border-primary-200/60 dark:border-primary-500/20",
    bg: "bg-primary-50/50 dark:bg-primary-500/5",
  },
  green: {
    icon: "bg-emerald-50 text-emerald-600 ring-emerald-100 dark:bg-emerald-500/10 dark:text-emerald-400 dark:ring-emerald-500/20",
    border: "border-emerald-200/60 dark:border-emerald-500/20",
    bg: "bg-emerald-50/50 dark:bg-emerald-500/5",
  },
  orange: {
    icon: "bg-amber-50 text-amber-600 ring-amber-100 dark:bg-amber-500/10 dark:text-amber-400 dark:ring-amber-500/20",
    border: "border-amber-200/60 dark:border-amber-500/20",
    bg: "bg-amber-50/50 dark:bg-amber-500/5",
  },
  default: {
    icon: "bg-surface-100 text-surface-500 ring-surface-200 dark:bg-surface-700/50 dark:text-surface-400 dark:ring-surface-600/50",
    border: "border-surface-200/60 dark:border-surface-700/40",
    bg: "bg-surface-50/50 dark:bg-surface-700/20",
  },
};

const STATUS_CONFIG = {
  active: { variant: "success", labelKey: "bdDashboard.statuses.active" },
  external: { variant: "default", labelKey: "bdDashboard.statuses.external" },
};

function AppCard({ app, t, navigate }) {
  const AppIcon = app.icon;
  const colors = COLOR_MAP[app.color] || COLOR_MAP.default;
  const statusConf = STATUS_CONFIG[app.status] || STATUS_CONFIG.active;
  const isExternal = app.status === "external";

  return (
    <div
      className={`${cardClass} p-5 flex flex-col gap-4 transition-shadow duration-200 hover:shadow-card-hover ${
        isExternal ? "opacity-75" : ""
      }`}
    >
      <div className="flex items-start gap-4">
        <div
          className={`shrink-0 w-12 h-12 rounded-xl flex items-center justify-center ring-1 ${colors.icon}`}
        >
          <AppIcon className="w-6 h-6" strokeWidth={1.8} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="text-[15px] font-bold text-surface-900 dark:text-surface-100 leading-tight">
              {t(app.nameKey, app.nameFallback)}
            </h3>
            <Badge variant={statusConf.variant}>
              {t(statusConf.labelKey, statusConf.variant)}
            </Badge>
          </div>
          <p className="text-[13px] text-surface-500 dark:text-surface-400 mt-1 leading-relaxed">
            {t(app.descriptionKey, app.descriptionFallback)}
          </p>
        </div>
      </div>

      {app.features.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {app.features.map((feat, i) => (
            <span
              key={i}
              className={`inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-medium ring-1 ring-inset ${colors.bg} ${colors.border} text-surface-600 dark:text-surface-300`}
            >
              {t(feat.nameKey, feat.nameFallback)}
            </span>
          ))}
        </div>
      )}

      {isExternal && (
        <p className="text-[12px] text-surface-400 dark:text-surface-500 italic">
          {t("bdDashboard.externalNotice", "Separate standalone application — not part of MAIN codebase")}
        </p>
      )}

      <div className="mt-auto pt-2 border-t border-surface-100 dark:border-surface-700/50">
        {isExternal ? (
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 text-[12px] font-semibold text-surface-400 dark:text-surface-500 bg-surface-50 dark:bg-surface-700/30 rounded-lg border border-surface-200/80 dark:border-surface-700/40 cursor-not-allowed">
            <ExternalLink className="w-3.5 h-3.5" />
            {t("bdDashboard.external", "External")}
          </span>
        ) : (
          <button
            onClick={() => navigate(app.route)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-[12px] font-semibold text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 bg-primary-50 hover:bg-primary-100 dark:bg-primary-500/10 dark:hover:bg-primary-500/20 rounded-lg transition-colors"
          >
            {t("applications.open", "Open")}
            <ChevronRight className="w-3.5 h-3.5 rtl:rotate-180" />
          </button>
        )}
      </div>
    </div>
  );
}

export default function ApplicationsPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <PageHeader
        title={t("applications.title", "Applications")}
        description={t("applications.description", "Software applications and modules available in your suite")}
      />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {APP_LIST.map((app) => (
          <AppCard key={app.id} app={app} t={t} navigate={navigate} />
        ))}
      </div>
    </div>
  );
}
