import { getCurrencySymbol } from "../shared/services/storeSettings";

export function formatCurrency(value) {
  const num = Number(value) || 0;
  const symbol = getCurrencySymbol();
  return `${num.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ${symbol}`;
}
