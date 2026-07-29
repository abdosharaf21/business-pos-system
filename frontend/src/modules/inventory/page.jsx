import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { inventoryService } from "./api";
import { useAuth } from "../../shared/context/AuthContext";
import { PageHeader } from "../../shared/components/PageHeader";
import { DataTable } from "../../shared/components/DataTable";
import { Modal } from "../../shared/components/Modal";
import { ConfirmDialog } from "../../shared/components/ConfirmDialog";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
import { Badge, statusBadge } from "../../shared/components/Badge";
import { StatCard } from "../../shared/components/StatCard";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Package, Search, PackagePlus, AlertTriangle, History, PackageOpen, ArrowUpDown } from "lucide-react";
import toast from "react-hot-toast";

const adjustSchema = z.object({
  type: z.string().min(1, "Type is required"),
  quantity: z.coerce.number().int("Must be a whole number").refine((n) => n !== 0, "Quantity cannot be zero"),
});

const INPUT_CLASS = "w-full px-3.5 py-2.5 border border-surface-200 bg-surface-50 rounded-xl text-sm text-surface-800 placeholder:text-surface-300 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150";
const LABEL_CLASS = "block text-[13px] font-semibold text-surface-700 mb-1.5";
const SELECT_CLASS = INPUT_CLASS;

const TYPE_LABELS = {
  purchase: "Purchase",
  sale: "Sale",
  adjustment: "Adjustment",
  return: "Return",
};

const TYPE_COLORS = {
  purchase: "success",
  sale: "danger",
  adjustment: "warning",
  return: "info",
};

export default function InventoryPage() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const canManage = ["admin", "manager"].includes(user?.role);
  const [search, setSearch] = useState("");
  const [adjustTarget, setAdjustTarget] = useState(null);
  const [viewHistory, setViewHistory] = useState(null);
  const [tab, setTab] = useState("all");

  const { data: inventory = [], isLoading, error, refetch } = useQuery({
    queryKey: ["inventory", search],
    queryFn: async () => {
      const res = await inventoryService.getAll();
      return res.data.data;
    },
  });

  const { data: summary } = useQuery({
    queryKey: ["inventory-summary"],
    queryFn: async () => {
      const res = await inventoryService.getSummary();
      return res.data.data;
    },
  });

  const { data: transactions = [] } = useQuery({
    queryKey: ["inventory-transactions", viewHistory],
    queryFn: async () => {
      const res = await inventoryService.getTransactions(viewHistory);
      return res.data.data;
    },
    enabled: !!viewHistory,
  });

  const adjustMutation = useMutation({
    mutationFn: (data) => inventoryService.adjustStock(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["inventory"] });
      queryClient.invalidateQueries({ queryKey: ["inventory-summary"] });
      queryClient.invalidateQueries({ queryKey: ["dashboard"] });
      toast.success("Stock adjusted");
      setAdjustTarget(null);
    },
    onError: (err) => toast.error(err.response?.data?.message || "Failed to adjust stock"),
  });

  const lowStock = inventory.filter((p) => p.quantity <= p.minimum_stock);
  const displayData = tab === "low" ? lowStock : inventory;

  const filtered = displayData.filter(
    (p) =>
      p.name?.toLowerCase().includes(search.toLowerCase()) ||
      (p.barcode || "").toLowerCase().includes(search.toLowerCase())
  );

  const columns = [
    {
      key: "name",
      label: "Product",
      render: (val, row) => (
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-[11px] font-bold text-white shrink-0">
            {val?.charAt(0)?.toUpperCase() || "?"}
          </div>
          <div className="min-w-0">
            <p className="text-[13px] font-semibold text-surface-800 truncate">{val}</p>
            <p className="text-[11px] text-surface-400 truncate">{row.barcode || "No barcode"}</p>
          </div>
        </div>
      ),
    },
    {
      key: "category_name",
      label: "Category",
      render: (val) => (
        <span className="text-[12px] text-surface-500">{val || "-"}</span>
      ),
    },
    {
      key: "quantity",
      label: "Stock",
      render: (val, row) => {
        const isLow = val <= row.minimum_stock;
        return (
          <div className="flex items-center gap-2">
            <span className={`text-[13px] font-bold ${isLow ? "text-red-600" : "text-surface-800"}`}>
              {val}
            </span>
            {isLow && (
              <Badge variant="danger">Low</Badge>
            )}
          </div>
        );
      },
    },
    {
      key: "minimum_stock",
      label: "Min Stock",
      render: (val) => <span className="text-[13px] text-surface-500">{val}</span>,
    },
    {
      key: "selling_price",
      label: "Price",
      render: (val) => (
        <span className="text-[13px] font-semibold text-surface-800">
          ${parseFloat(val || 0).toFixed(2)}
        </span>
      ),
    },
    {
      key: "status",
      label: "Status",
      render: (val) => <Badge variant={statusBadge(val)}>{val}</Badge>,
    },
    ...(canManage
      ? [
          {
            key: "id",
            label: "Actions",
            render: (_, row) => (
              <div className="flex items-center gap-1">
                <button
                  onClick={() => setAdjustTarget(row)}
                  className="p-2 text-surface-400 hover:text-primary-600 hover:bg-primary-50 rounded-xl transition-all duration-150"
                  title="Adjust Stock"
                >
                  <PackagePlus className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewHistory(row.id)}
                  className="p-2 text-surface-400 hover:text-amber-600 hover:bg-amber-50 rounded-xl transition-all duration-150"
                  title="Transaction History"
                >
                  <History className="w-4 h-4" />
                </button>
              </div>
            ),
          },
        ]
      : [
          {
            key: "id",
            label: "History",
            render: (_, row) => (
              <button
                onClick={() => setViewHistory(row.id)}
                className="p-2 text-surface-400 hover:text-amber-600 hover:bg-amber-50 rounded-xl transition-all duration-150"
                title="Transaction History"
              >
                <History className="w-4 h-4" />
              </button>
            ),
          },
        ]),
  ];

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay message={error.response?.data?.message || error.message} onRetry={refetch} />;

  return (
    <div>
      <PageHeader
        title="Inventory"
        description="Manage product stock levels"
      />

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
        <StatCard label="Total Products" value={summary?.total_products ?? 0} icon={Package} color="blue" />
        <StatCard label="Total Stock" value={summary?.total_quantity ?? 0} icon={PackageOpen} color="green" />
        <StatCard
          label="Inventory Value"
          value={`$${(summary?.total_value ?? 0).toLocaleString()}`}
          icon={ArrowUpDown}
          color="purple"
        />
        <StatCard label="Low Stock Items" value={summary?.low_stock_count ?? 0} icon={AlertTriangle} color="orange" />
      </div>

      {/* Tabs */}
      <div className="flex gap-1 mb-6 p-1 bg-surface-100 rounded-xl w-fit">
        <button
          onClick={() => { setTab("all"); setSearch(""); }}
          className={`px-4 py-2 text-[13px] font-semibold rounded-xl transition-all duration-150 ${
            tab === "all" ? "bg-white text-surface-800 shadow-sm" : "text-surface-500 hover:text-surface-700"
          }`}
        >
          All Products
        </button>
        <button
          onClick={() => { setTab("low"); setSearch(""); }}
          className={`px-4 py-2 text-[13px] font-semibold rounded-xl transition-all duration-150 flex items-center gap-2 ${
            tab === "low" ? "bg-white text-surface-800 shadow-sm" : "text-surface-500 hover:text-surface-700"
          }`}
        >
          <AlertTriangle className="w-3.5 h-3.5" />
          Low Stock
          {summary?.low_stock_count > 0 && (
            <span className="inline-flex items-center justify-center w-5 h-5 text-[10px] font-bold text-white bg-red-500 rounded-full">
              {summary.low_stock_count}
            </span>
          )}
        </button>
      </div>

      {/* Search */}
      <div className="mb-6 relative">
        <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-surface-400 pointer-events-none" />
        <input
          type="text"
          placeholder="Search products..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2.5 border border-surface-200 bg-white rounded-xl text-sm text-surface-800 placeholder:text-surface-300 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150 shadow-card"
          aria-label="Search inventory"
        />
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          icon={Package}
          title="No products found"
          description={search ? "Try a different search" : "No products in inventory"}
        />
      ) : (
        <DataTable columns={columns} data={filtered} />
      )}

      {/* Adjust Stock Modal */}
      <AdjustStockModal
        isOpen={!!adjustTarget}
        onClose={() => setAdjustTarget(null)}
        product={adjustTarget}
        onSubmit={(data) =>
          adjustMutation.mutate({
            product_id: adjustTarget.id,
            ...data,
          })
        }
        loading={adjustMutation.isPending}
      />

      {/* Transaction History Modal */}
      <TransactionHistoryModal
        isOpen={!!viewHistory}
        onClose={() => setViewHistory(null)}
        transactions={transactions}
        product={inventory.find((p) => p.id === viewHistory)}
      />
    </div>
  );
}

function AdjustStockModal({ isOpen, onClose, product, onSubmit, loading }) {
  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(adjustSchema),
    defaultValues: { type: "adjustment", quantity: 0 },
  });

  const quantity = watch("quantity", 0);
  const newStock = product ? Number(product.quantity) + Number(quantity) : 0;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Adjust Stock — ${product?.name || ""}`}>
      <form
        onSubmit={handleSubmit((data) => {
          onSubmit(data);
          reset();
        })}
        className="space-y-5"
      >
        <div className="bg-surface-50 rounded-xl p-4">
          <div className="flex justify-between text-[13px]">
            <span className="text-surface-500">Current Stock</span>
            <span className="font-bold text-surface-800">{product?.quantity ?? 0}</span>
          </div>
          <div className="flex justify-between text-[13px] mt-1">
            <span className="text-surface-500">After Adjustment</span>
            <span className={`font-bold ${newStock < 0 ? "text-red-600" : "text-surface-800"}`}>
              {newStock}
            </span>
          </div>
        </div>

        <div>
          <label className={LABEL_CLASS}>Type</label>
          <select {...register("type")} className={SELECT_CLASS}>
            <option value="adjustment">Adjustment</option>
            <option value="purchase">Purchase</option>
            <option value="return">Return</option>
            <option value="sale">Sale</option>
          </select>
          {errors.type && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.type.message}</p>}
        </div>

        <div>
          <label className={LABEL_CLASS}>Quantity</label>
          <input
            type="number"
            {...register("quantity")}
            className={INPUT_CLASS}
            placeholder="e.g. 10 (positive) or -5 (negative)"
          />
          <p className="text-[11px] text-surface-400 mt-1">
            Positive adds stock, negative removes stock
          </p>
          {errors.quantity && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.quantity.message}</p>}
        </div>

        <div className="flex justify-end gap-3 pt-5 border-t border-surface-100">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2.5 text-[13px] font-semibold text-surface-600 bg-white border border-surface-200 rounded-xl hover:bg-surface-50 transition-all duration-150"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading || newStock < 0}
            className="px-4 py-2.5 text-[13px] font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl hover:from-primary-700 hover:to-primary-800 disabled:opacity-50 transition-all duration-150 shadow-sm shadow-primary-600/20"
          >
            {loading ? "Adjusting..." : "Adjust Stock"}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function TransactionHistoryModal({ isOpen, onClose, transactions, product }) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Transaction History — ${product?.name || ""}`}>
      <div className="space-y-4">
        {transactions.length === 0 ? (
          <p className="text-center text-surface-400 py-8 text-[13px]">No transactions recorded</p>
        ) : (
          <div className="divide-y divide-surface-100 max-h-96 overflow-y-auto">
            {transactions.map((t) => (
              <div key={t.id} className="flex items-center justify-between py-3">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-surface-100 flex items-center justify-center text-[11px] font-bold text-surface-500 shrink-0">
                    <Package className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="text-[13px] font-semibold text-surface-800 capitalize">
                      {TYPE_LABELS[t.transaction_type] || t.transaction_type}
                    </p>
                    <p className="text-[11px] text-surface-400">
                      {new Date(t.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
                <span className={`text-[13px] font-bold ${t.quantity > 0 ? "text-emerald-600" : "text-red-600"}`}>
                  {t.quantity > 0 ? "+" : ""}{t.quantity}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </Modal>
  );
}
