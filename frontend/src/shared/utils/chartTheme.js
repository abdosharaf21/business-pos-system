/**
 * Shared chart theme constants for recharts surfaces.
 *
 * Single source of truth used by dashboard and reports so axis, grid
 * and tooltip styling stays identical across every chart in the
 * application.
 */

export const AXIS_TICK = { fontSize: 11, fill: "var(--color-surface-400)" };
export const AXIS_LINE = { stroke: "var(--color-surface-200)" };
export const GRID_LINE = "var(--color-surface-200)";
export const TOOLTIP_STYLE = {
  borderRadius: 12,
  border: "1px solid var(--color-surface-200)",
  boxShadow: "0 10px 15px -3px rgb(0 0 0 / 0.1)",
  fontSize: 13,
  backgroundColor: "var(--color-surface-0)",
  color: "var(--color-surface-800)",
};
