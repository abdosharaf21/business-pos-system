export function DataTable({ columns, data, emptyMessage = "No data available" }) {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-2xl border border-surface-200/80 p-16 text-center shadow-card">
        <p className="text-surface-400 text-sm font-medium">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl border border-surface-200/80 overflow-hidden shadow-card">
      <div className="overflow-x-auto">
        <table className="w-full text-sm" role="table">
          <thead>
            <tr className="border-b border-surface-100 bg-surface-50/60">
              {columns.map((col) => (
                <th
                  key={col.key}
                  className="px-5 py-3.5 text-left text-[11px] font-semibold text-surface-500 uppercase tracking-wider"
                >
                  {col.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-100">
            {data.map((row, i) => (
              <tr
                key={row.id || i}
                className="hover:bg-surface-50/50 transition-colors duration-100 group"
              >
                {columns.map((col) => (
                  <td key={col.key} className="px-5 py-3.5 whitespace-nowrap text-surface-700">
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
