import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { productService } from "./api";
import { useAuth } from "../../shared/context/AuthContext";
import { categoryService } from "../categories/api";
import { PageHeader } from "../../shared/components/PageHeader";
import { DataTable } from "../../shared/components/DataTable";
import { Modal } from "../../shared/components/Modal";
import { ConfirmDialog } from "../../shared/components/ConfirmDialog";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Plus, Pencil, Trash2, Search, Package, X } from "lucide-react";
import toast from "react-hot-toast";

const productSchema = z.object({
  name: z.string().min(1, "Name is required"),
  sku: z.string().optional(),
  barcode: z.string().min(1, "Barcode is required"),
  category_id: z.string().min(1, "Category is required"),
  description: z.string().optional(),
  purchase_price: z.string().min(1, "Required").refine((v) => !isNaN(Number(v)) && Number(v) >= 0, "Must be >= 0"),
  selling_price: z.string().min(1, "Required").refine((v) => !isNaN(Number(v)) && Number(v) >= 0, "Must be >= 0"),
  quantity: z.string().min(1, "Required").refine((v) => !isNaN(Number(v)) && Number(v) >= 0 && Number.isInteger(Number(v)), "Must be >= 0"),
  minimum_stock: z.string().min(1, "Required").refine((v) => !isNaN(Number(v)) && Number(v) >= 0 && Number.isInteger(Number(v)), "Must be >= 0"),
  status: z.string().optional(),
}).refine((data) => {
  if (data.selling_price && data.purchase_price) {
    return Number(data.selling_price) >= Number(data.purchase_price);
  }
  return true;
}, { message: "Selling price should not be lower than purchase price", path: ["selling_price"] });

const INPUT_CLASS = "w-full px-3.5 py-2.5 border border-surface-200 bg-surface-50 rounded-xl text-sm text-surface-800 placeholder:text-surface-300 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150";
const LABEL_CLASS = "block text-[13px] font-semibold text-surface-700 mb-1.5";
const SELECT_CLASS = "w-full px-3.5 py-2.5 border border-surface-200 bg-surface-50 rounded-xl text-sm text-surface-800 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150 appearance-none cursor-pointer";

function Badge({ children, variant = "default" }) {
  const variants = {
    default: "bg-surface-100 text-surface-600",
    success: "bg-emerald-50 text-emerald-700",
    inactive: "bg-surface-100 text-surface-400",
    warning: "bg-amber-50 text-amber-700",
  };
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-[11px] font-semibold ${variants[variant]}`}>
      {children}
    </span>
  );
}

export default function ProductsPage() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const canManage = ["admin", "manager"].includes(user?.role);
  const [search, setSearch] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const { data: products = [], isLoading, error, refetch } = useQuery({
    queryKey: ["products"],
    queryFn: async () => {
      const res = await productService.getAll();
      return res.data.data;
    },
  });

  const { data: categories = [] } = useQuery({
    queryKey: ["categories"],
    queryFn: async () => {
      const res = await categoryService.getAll();
      return res.data.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: (data) => productService.create(data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["products"] }); toast.success("Product created"); setModalOpen(false); },
    onError: (err) => toast.error(err.response?.data?.message || "Failed to create product"),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => productService.update(id, data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["products"] }); toast.success("Product updated"); setModalOpen(false); setEditing(null); },
    onError: (err) => toast.error(err.response?.data?.message || "Failed to update product"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => productService.delete(id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["products"] }); toast.success("Product deleted"); setDeleteTarget(null); },
    onError: (err) => toast.error(err.response?.data?.message || "Failed to delete product"),
  });

  const filtered = products.filter((p) => {
    const term = search.toLowerCase();
    const matchesSearch = !search ||
      p.name?.toLowerCase().includes(term) ||
      p.barcode?.toLowerCase().includes(term) ||
      p.sku?.toLowerCase().includes(term);
    const matchesCategory = !categoryFilter || String(p.category_id) === categoryFilter;
    const matchesStatus = !statusFilter || p.status === statusFilter;
    return matchesSearch && matchesCategory && matchesStatus;
  });

  const columns = [
    {
      key: "sku",
      label: "SKU",
      render: (val) => <span className="text-[13px] font-mono text-surface-500">{val || "-"}</span>,
    },
    {
      key: "name",
      label: "Name",
      render: (val) => <span className="text-[13px] font-semibold text-surface-800">{val}</span>,
    },
    {
      key: "barcode",
      label: "Barcode",
      render: (val) => <span className="text-[13px] font-mono text-surface-600">{val}</span>,
    },
    {
      key: "category_name",
      label: "Category",
      render: (val) => <span className="text-[13px] text-surface-500">{val || "-"}</span>,
    },
    {
      key: "purchase_price",
      label: "Purchase Price",
      render: (val) => <span className="text-[13px] text-surface-600">${Number(val).toFixed(2)}</span>,
    },
    {
      key: "selling_price",
      label: "Selling Price",
      render: (val) => <span className="text-[13px] font-semibold text-surface-800">${Number(val).toFixed(2)}</span>,
    },
    {
      key: "quantity",
      label: "Qty",
      render: (val, row) => {
        const isLow = val <= row.minimum_stock;
        return (
          <span className={`text-[13px] font-semibold ${isLow ? "text-red-600" : "text-surface-800"}`}>
            {val}
          </span>
        );
      },
    },
    {
      key: "minimum_stock",
      label: "Min Stock",
      render: (val) => <span className="text-[13px] text-surface-500">{val}</span>,
    },
    {
      key: "status",
      label: "Status",
      render: (val) => (
        <Badge variant={val === "active" ? "success" : "inactive"}>
          {val}
        </Badge>
      ),
    },
    ...(canManage
      ? [
          {
            key: "id",
            label: "Actions",
            render: (_, row) => (
              <div className="flex items-center gap-1">
                <button onClick={() => { setEditing(row); setModalOpen(true); }} className="p-2 text-surface-400 hover:text-primary-600 hover:bg-primary-50 rounded-xl transition-all duration-150" title="Edit">
                  <Pencil className="w-4 h-4" />
                </button>
                <button onClick={() => setDeleteTarget(row)} className="p-2 text-surface-400 hover:text-red-600 hover:bg-red-50 rounded-xl transition-all duration-150" title="Delete">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ),
          },
        ]
      : []),
  ];

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay message={error.response?.data?.message || error.message} onRetry={refetch} />;

  return (
    <div>
      <PageHeader
        title="Products"
        description="Manage your product catalog"
        actions={
          canManage && (
            <button onClick={() => { setEditing(null); setModalOpen(true); }} className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white text-[13px] font-semibold rounded-xl hover:from-primary-700 hover:to-primary-800 transition-all duration-150 shadow-sm shadow-primary-600/20">
              <Plus className="w-4 h-4" />
              New Product
            </button>
          )
        }
      />

      <div className="mb-6 flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-surface-400 pointer-events-none" />
          <input type="text" placeholder="Search by name or barcode..." value={search} onChange={(e) => setSearch(e.target.value)} className="w-full pl-10 pr-4 py-2.5 border border-surface-200 bg-white rounded-xl text-sm text-surface-800 placeholder:text-surface-300 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150 shadow-card" aria-label="Search products" />
        </div>
        <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)} className={SELECT_CLASS + " min-w-[160px]"}>
          <option value="">All Categories</option>
          {categories.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className={SELECT_CLASS + " min-w-[130px]"}>
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>

      {filtered.length === 0 ? (
        <EmptyState icon={Package} title="No products found" description={search || categoryFilter || statusFilter ? "Try different filters" : "Add your first product"} action={!search && !categoryFilter && !statusFilter && canManage && <button onClick={() => { setEditing(null); setModalOpen(true); }} className="px-4 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white text-[13px] font-semibold rounded-xl hover:from-primary-700 hover:to-primary-800 shadow-sm shadow-primary-600/20">Add Product</button>} />
      ) : (
        <DataTable columns={columns} data={filtered} />
      )}

      <ProductModal isOpen={modalOpen} onClose={() => { setModalOpen(false); setEditing(null); }} editing={editing} categories={categories} onSubmit={(data) => editing ? updateMutation.mutate({ id: editing.id, data }) : createMutation.mutate(data)} loading={createMutation.isPending || updateMutation.isPending} />

      <ConfirmDialog isOpen={!!deleteTarget} onClose={() => setDeleteTarget(null)} onConfirm={() => deleteMutation.mutate(deleteTarget.id)} title="Delete Product" message={`Delete "${deleteTarget?.name}"? This action cannot be undone.`} loading={deleteMutation.isPending} />
    </div>
  );
}

function ProductModal({ isOpen, onClose, editing, categories, onSubmit, loading }) {
  const { register, handleSubmit, reset, watch, formState: { errors } } = useForm({
    resolver: zodResolver(productSchema),
    values: editing ? {
      name: editing.name || "",
      sku: editing.sku || "",
      barcode: editing.barcode || "",
      category_id: String(editing.category_id || ""),
      description: editing.description || "",
      purchase_price: String(editing.purchase_price ?? ""),
      selling_price: String(editing.selling_price ?? ""),
      quantity: String(editing.quantity ?? ""),
      minimum_stock: String(editing.minimum_stock ?? ""),
      status: editing.status || "active",
    } : {
      name: "",
      sku: "",
      barcode: "",
      category_id: "",
      description: "",
      purchase_price: "",
      selling_price: "",
      quantity: "0",
      minimum_stock: "0",
      status: "active",
    },
  });

  const formValues = watch();
  const purchasePrice = Number(formValues.purchase_price) || 0;
  const sellingPrice = Number(formValues.selling_price) || 0;
  const showPriceWarning = purchasePrice > 0 && sellingPrice > 0 && sellingPrice < purchasePrice;

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={editing ? "Edit Product" : "New Product"} size="lg">
      <form onSubmit={handleSubmit((data) => { onSubmit(data); reset(); })} className="space-y-5">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>Name</label>
            <input {...register("name")} placeholder="Product name" className={INPUT_CLASS} />
            {errors.name && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.name.message}</p>}
          </div>
          <div>
            <label className={LABEL_CLASS}>Barcode</label>
            <input {...register("barcode")} placeholder="Barcode" className={INPUT_CLASS} />
            {errors.barcode && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.barcode.message}</p>}
          </div>
        </div>
        <div>
          <label className={LABEL_CLASS}>SKU (Stock Keeping Unit)</label>
          <input {...register("sku")} placeholder="Optional SKU code" className={INPUT_CLASS} />
          {errors.sku && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.sku.message}</p>}
        </div>
        <div>
          <label className={LABEL_CLASS}>Category</label>
          <select {...register("category_id")} className={SELECT_CLASS}>
            <option value="">Select category</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
          {errors.category_id && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.category_id.message}</p>}
        </div>
        <div>
          <label className={LABEL_CLASS}>Description</label>
          <textarea {...register("description")} rows={2} placeholder="Brief description (optional)" className={`${INPUT_CLASS} resize-none`} />
          {errors.description && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.description.message}</p>}
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>Purchase Price</label>
            <input {...register("purchase_price")} type="number" step="0.01" min="0" placeholder="0.00" className={INPUT_CLASS} />
            {errors.purchase_price && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.purchase_price.message}</p>}
          </div>
          <div>
            <label className={LABEL_CLASS}>Selling Price</label>
            <input {...register("selling_price")} type="number" step="0.01" min="0" placeholder="0.00" className={`${INPUT_CLASS} ${showPriceWarning ? "border-amber-300" : ""}`} />
            {errors.selling_price && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.selling_price.message}</p>}
            {showPriceWarning && !errors.selling_price && (
              <p className="text-[11px] text-amber-600 mt-1 font-medium">Selling price should not be lower than purchase price</p>
            )}
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>Quantity</label>
            <input {...register("quantity")} type="number" min="0" step="1" placeholder="0" className={INPUT_CLASS} />
            {errors.quantity && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.quantity.message}</p>}
          </div>
          <div>
            <label className={LABEL_CLASS}>Minimum Stock</label>
            <input {...register("minimum_stock")} type="number" min="0" step="1" placeholder="0" className={INPUT_CLASS} />
            {errors.minimum_stock && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.minimum_stock.message}</p>}
          </div>
        </div>
        {editing && (
          <div>
            <label className={LABEL_CLASS}>Status</label>
            <select {...register("status")} className={SELECT_CLASS}>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
            {errors.status && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.status.message}</p>}
          </div>
        )}
        <div className="flex justify-end gap-3 pt-5 border-t border-surface-100">
          <button type="button" onClick={onClose} className="px-4 py-2.5 text-[13px] font-semibold text-surface-600 bg-white border border-surface-200 rounded-xl hover:bg-surface-50 transition-all duration-150">Cancel</button>
          <button type="submit" disabled={loading} className="px-4 py-2.5 text-[13px] font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl hover:from-primary-700 hover:to-primary-800 disabled:opacity-50 transition-all duration-150 shadow-sm shadow-primary-600/20">{loading ? "Saving..." : editing ? "Update" : "Create"}</button>
        </div>
      </form>
    </Modal>
  );
}
