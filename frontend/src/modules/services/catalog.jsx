import { useLocation, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { ArrowRight, BriefcaseBusiness } from "lucide-react";
import { PageHeader } from "../../shared/components/PageHeader";
import {
  APPLICATION_LAUNCH_ROUTES,
  MODULES,
  getActiveModule,
} from "../../shared/layouts/navigationConfig";

const CARD_CLASS =
  "group w-full text-start bg-white dark:bg-surface-900 rounded-2xl border border-surface-200/80 dark:border-surface-700 shadow-card p-5 flex flex-col gap-4 transition-all duration-150 hover:border-primary-300 dark:hover:border-primary-500/40 hover:shadow-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500";

const ICON_TILES = {
  business: "bg-primary-50 dark:bg-primary-500/10 text-primary-600 dark:text-primary-400 ring-primary-100 dark:ring-primary-500/20",
  pos: "bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 ring-emerald-100 dark:ring-emerald-500/20",
  inventory: "bg-amber-50 dark:bg-amber-500/10 text-amber-600 dark:text-amber-400 ring-amber-100 dark:ring-amber-500/20",
  expenses: "bg-violet-50 dark:bg-violet-500/10 text-violet-600 dark:text-violet-400 ring-violet-100 dark:ring-violet-500/20",
};

export default function ApplicationCatalogPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const activeModuleId = getActiveModule(pathname);

  return (
    <div>
      <PageHeader
        title={t("catalog.title")}
        description={t("catalog.description")}
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {MODULES.map((module) => {
          const Icon = module.icon;
          const isCurrent = module.id === activeModuleId;
          return (
            <button
              key={module.id}
              type="button"
              onClick={() => navigate(APPLICATION_LAUNCH_ROUTES[module.id])}
              className={CARD_CLASS}
              aria-label={t(module.labelKey)}
            >
              <div className="flex items-center justify-between">
                <span
                  className={`w-11 h-11 rounded-xl flex items-center justify-center ring-1 shrink-0 ${ICON_TILES[module.id]}`}
                >
                  <Icon className="w-5 h-5" strokeWidth={2} />
                </span>
                {isCurrent && (
                  <span className="inline-flex items-center px-2.5 py-1 rounded-full bg-primary-50 dark:bg-primary-500/10 text-primary-700 dark:text-primary-400 ring-1 ring-primary-200 dark:ring-primary-500/30 text-[10px] font-semibold uppercase tracking-wider">
                    {t("catalog.currentApp")}
                  </span>
                )}
              </div>
              <div className="flex-1">
                <h2 className="text-[15px] font-bold text-surface-900 dark:text-surface-100 tracking-tight">
                  {t(module.labelKey)}
                </h2>
                <p className="text-[12px] text-surface-400 mt-1 leading-relaxed line-clamp-2">
                  {t(`catalog.appDescriptions.${module.id}`)}
                </p>
              </div>
              <span className="inline-flex items-center gap-1.5 text-[13px] font-semibold text-primary-600 dark:text-primary-400">
                {t("catalog.open")}
                <ArrowRight className="w-4 h-4 rtl:-scale-x-100 transition-transform duration-150 group-hover:translate-x-0.5 rtl:group-hover:-translate-x-0.5" />
              </span>
            </button>
          );
        })}
      </div>

      <div className="mt-6 bg-white dark:bg-surface-900 rounded-2xl border border-surface-200/80 dark:border-surface-700 shadow-card p-5 flex flex-col sm:flex-row sm:items-center gap-4 justify-between">
        <div className="flex items-start gap-3 min-w-0">
          <span className="w-10 h-10 rounded-xl flex items-center justify-center ring-1 shrink-0 bg-surface-50 dark:bg-surface-800 text-surface-500 dark:text-surface-400 ring-surface-200 dark:ring-surface-700">
            <BriefcaseBusiness className="w-5 h-5" strokeWidth={1.8} />
          </span>
          <div className="min-w-0">
            <h2 className="text-[14px] font-bold text-surface-900 dark:text-surface-100 tracking-tight">
              {t("catalog.serviceRecords.title")}
            </h2>
            <p className="text-[12px] text-surface-400 mt-0.5 leading-relaxed">
              {t("catalog.serviceRecords.description")}
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={() => navigate("/business/services")}
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-[13px] font-semibold text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-500/10 ring-1 ring-primary-100 dark:ring-primary-500/20 hover:bg-primary-100 dark:hover:bg-primary-500/20 transition-colors shrink-0"
        >
          {t("catalog.serviceRecords.manage")}
        </button>
      </div>
    </div>
  );
}
