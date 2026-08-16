import { useTranslation } from "react-i18next";

export function DataTable({ columns, data, emptyMessage }) {
  const { t } = useTranslation();
  const msg = emptyMessage || t("common.noDataAvailable");

  if (!data || data.length === 0) {
    return (
      <div className="bg-white dark:bg-surface-800/60 rounded-2xl border border-surface-200/80 dark:border-surface-700/60 p-16 text-center shadow-card">
        <p className="text-surface-400 dark:text-surface-400 text-sm font-medium">{msg}</p>
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-surface-800/60 rounded-2xl border border-surface-200/80 dark:border-surface-700/60 overflow-hidden shadow-card">
      <div className="overflow-x-auto">
        <table className="w-full text-sm" role="table">
          <thead>
            <tr className="border-b border-surface-100 bg-surface-50/60 dark:border-surface-700/60 dark:bg-surface-700/30">
              {columns.map((col) => (
                <th
                  key={col.key}
                  className="px-5 py-3.5 text-start text-[12px] font-semibold text-surface-500 dark:text-surface-400 uppercase tracking-wider"
                >
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-100 dark:divide-surface-700/60">
            {data.map((row, i) => (
              <tr
                key={row.id || i}
                className="hover:bg-surface-50/50 dark:hover:bg-surface-700/30 transition-colors duration-100 group"
              >
                {columns.map((col) => (
                  <td key={col.key} className="px-5 py-3.5 whitespace-nowrap text-surface-700 dark:text-surface-200">
                    {col.render ? col.render(row[col.key], row) : row[col.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
