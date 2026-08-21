import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { dealService } from "./api";
import { clientService } from "../clients/api";
import { serviceService } from "../services/api";
import { useAuth } from "../../shared/context/AuthContext";
import { PageHeader } from "../../shared/components/PageHeader";
import { DataTable } from "../../shared/components/DataTable";
import { Badge } from "../../shared/components/Badge";
import { Modal } from "../../shared/components/Modal";
import { ConfirmDialog } from "../../shared/components/ConfirmDialog";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Plus, Pencil, Trash2, Search, Handshake, DollarSign, Clock, CheckCircle2 } from "lucide-react";
import toast from "react-hot-toast";

const dealSchema = z.object({
  client_id: z.coerce.number().min(1, "Client is required"),
  service_id: z.coerce.number().min(1, "Service is required"),
  package_name: z.string().optional().nullable(),
  sale_date: z.string().min(1, "Sale date is required"),
  price: z.coerce.number().min(0, "Price must be positive"),
  discount: z.coerce.number().min(0, "Discount must be positive"),
  tax: z.coerce.number().min(0, "Tax must be positive"),
  payment_status: z.enum(["pending", "partial", "paid", "refunded"]),
  deal_status: z.enum(["draft", "confirmed", "delivered", "cancelled"]),
  notes: z.string().optional().nullable(),
});

const PAYMENT_STATUSES = ["pending", "partial", "paid", "refunded"];
const DEAL_STATUSES = ["draft", "confirmed", "delivered", "cancelled"];

const PAYMENT_BADGE = {
  pending: "warning",
  partial: "info",
  paid: "success",
  refunded: "danger",
};

const DEAL_BADGE = {
  draft: "default",
  confirmed: "info",
  delivered: "success",
  cancelled: "danger",
};

const INPUT_CLASS = "w-full px-3.5 py-2.5 border border-surface-200 bg-surface-50 rounded-xl text-sm text-surface-800 placeholder:text-surface-300 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150";
const LABEL_CLASS = "block text-[13px] font-semibold text-surface-700 mb-1.5";
const SELECT_CLASS = INPUT_CLASS;

function formatCurrency(amount) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "EGP" }).format(amount || 0);
}

function KpiCard({ icon: Icon, label, value, color }) {
  return (
    <div className="bg-white rounded-2xl border border-surface-100 p-5 shadow-card">
      <div className="flex items-center gap-3 mb-3">
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${color}`}>
          <Icon className="w-5 h-5 text-white" />
        </div>
        <span className="text-[13px] font-medium text-surface-500">{label}</span>
      </div>
      <p className="text-2xl font-bold text-surface-800">{value}</p>
    </div>
  );
}

export default function DealsPage() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const canManage = ["admin", "manager"].includes(user?.role);
  const [search, setSearch] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const { data: deals = [], isLoading, error, refetch } = useQuery({
    queryKey: ["deals"],
    queryFn: async () => {
      const res = await dealService.getAll();
      return res.data.data;
    },
  });

  const { data: clients = [] } = useQuery({
    queryKey: ["clients"],
    queryFn: async () => {
      const res = await clientService.getAll();
      return res.data.data;
    },
  });

  const { data: services = [] } = useQuery({
    queryKey: ["services"],
    queryFn: async () => {
      const res = await serviceService.getAll();
      return res.data.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: (data) => dealService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["deals"] });
      toast.success("Deal created");
      setModalOpen(false);
    },
    onError: (err) => toast.error(err.response?.data?.message || "Failed to create"),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => dealService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["deals"] });
      toast.success("Deal updated");
      setModalOpen(false);
      setEditing(null);
    },
    onError: (err) => toast.error(err.response?.data?.message || "Failed to update"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => dealService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["deals"] });
      toast.success("Deal deleted");
      setDeleteTarget(null);
    },
    onError: (err) => toast.error(err.response?.data?.message || "Failed to delete"),
  });

  const filtered = deals.filter(
    (d) =>
      d.deal_number?.toLowerCase().includes(search.toLowerCase()) ||
      d.package_name?.toLowerCase().includes(search.toLowerCase()) ||
      String(d.final_amount).includes(search)
  );

  const totalRevenue = deals
    .filter((d) => d.deal_status !== "cancelled")
    .reduce((sum, d) => sum + (d.final_amount || 0), 0);
  const pendingDeals = deals.filter((d) => d.payment_status === "pending").length;
  const confirmedDeals = deals.filter((d) => d.deal_status === "confirmed").length;

  const columns = [
    {
      key: "deal_number",
      label: "Deal #",
      render: (val, row) => (
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-primary-50 flex items-center justify-center text-[11px] font-bold text-primary-600 shrink-0">
            {val?.slice(-2) || "?"}
          </div>
          <div className="min-w-0">
            <p className="text-[13px] font-semibold text-surface-800 truncate">{val}</p>
            <p className="text-[11px] text-surface-400 truncate">{row.package_name || "N/A"}</p>
          </div>
        </div>
      ),
    },
    {
      key: "sale_date",
      label: "Date",
      render: (val) => <span className="text-surface-600">{val || "-"}</span>,
    },
    {
      key: "final_amount",
      label: "Total",
      render: (val) => <span className="text-[13px] font-semibold text-surface-800">{formatCurrency(val)}</span>,
    },
    {
      key: "deal_status",
      label: "Deal Status",
      render: (val) => <Badge variant={DEAL_BADGE[val] || "default"}>{val}</Badge>,
    },
    {
      key: "payment_status",
      label: "Payment",
      render: (val) => <Badge variant={PAYMENT_BADGE[val] || "default"}>{val}</Badge>,
    },
    ...(canManage
      ? [
          {
            key: "id",
            label: "Actions",
            render: (_, row) => (
              <div className="flex items-center gap-1">
                <button onClick={() => openEdit(row)} className="p-2 text-surface-400 hover:text-primary-600 hover:bg-primary-50 rounded-xl transition-all duration-150" title="Edit">
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

  const openCreate = () => {
    setEditing(null);
    setModalOpen(true);
  };

  const openEdit = (deal) => {
    setEditing(deal);
    setModalOpen(true);
  };

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay message={error.response?.data?.message || error.message} onRetry={refetch} />;

  return (
    <div>
      <PageHeader
        title="Deals"
        description="Manage your sales and deals"
        actions={
          canManage && (
            <button
              onClick={openCreate}
              className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white text-[13px] font-semibold rounded-xl hover:from-primary-700 hover:to-primary-800 transition-all duration-150 shadow-sm shadow-primary-600/20"
            >
              <Plus className="w-4 h-4" />
              New Deal
            </button>
          )
        }
      />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <KpiCard icon={Handshake} label="Total Deals" value={deals.length} color="bg-primary-600" />
        <KpiCard icon={DollarSign} label="Total Revenue" value={formatCurrency(totalRevenue)} color="bg-emerald-600" />
        <KpiCard icon={Clock} label="Pending Payment" value={pendingDeals} color="bg-amber-500" />
        <KpiCard icon={CheckCircle2} label="Confirmed Deals" value={confirmedDeals} color="bg-blue-600" />
      </div>

      <div className="mb-6 relative">
        <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-surface-400 pointer-events-none" />
        <input
          type="text"
          placeholder="Search deals..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2.5 border border-surface-200 bg-white rounded-xl text-sm text-surface-800 placeholder:text-surface-300 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150 shadow-card"
          aria-label="Search deals"
        />
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          icon={Handshake}
          title="No deals found"
          description={search ? "Try a different search term" : "Get started by creating your first deal"}
          action={
            !search && canManage && (
              <button onClick={openCreate} className="px-4 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white text-[13px] font-semibold rounded-xl hover:from-primary-700 hover:to-primary-800 shadow-sm shadow-primary-600/20">
                New Deal
              </button>
            )
          }
        />
      ) : (
        <DataTable columns={columns} data={filtered} />
      )}

      <DealModal
        isOpen={modalOpen}
        onClose={() => { setModalOpen(false); setEditing(null); }}
        editing={editing}
        clients={clients}
        services={services}
        onSubmit={(data) => {
          if (editing) {
            updateMutation.mutate({ id: editing.id, data });
          } else {
            createMutation.mutate(data);
          }
        }}
        loading={createMutation.isPending || updateMutation.isPending}
      />

      <ConfirmDialog
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => deleteMutation.mutate(deleteTarget.id)}
        title="Delete Deal"
        message={`Are you sure you want to delete deal "${deleteTarget?.deal_number}"? This action cannot be undone.`}
        loading={deleteMutation.isPending}
      />
    </div>
  );
}

function DealModal({ isOpen, onClose, editing, clients, services, onSubmit, loading }) {
  const {
    register,
    handleSubmit,
    reset,
    watch,
    setValue,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(dealSchema),
    values: editing
      ? {
          client_id: editing.client_id,
          service_id: editing.service_id,
          package_name: editing.package_name || "",
          sale_date: editing.sale_date,
          price: editing.price,
          discount: editing.discount,
          tax: editing.tax,
          payment_status: editing.payment_status,
          deal_status: editing.deal_status,
          notes: editing.notes || "",
        }
      : {
          client_id: "",
          service_id: "",
          package_name: "",
          sale_date: new Date().toISOString().split("T")[0],
          price: 0,
          discount: 0,
          tax: 0,
          payment_status: "pending",
          deal_status: "draft",
          notes: "",
        },
  });

  const watchedServiceId = watch("service_id");
  const price = watch("price") || 0;
  const discount = watch("discount") || 0;
  const tax = watch("tax") || 0;
  const finalAmount = Math.max(0, price - discount + tax);

  useEffect(() => {
    if (editing || !watchedServiceId) return;
    const selected = services.find((s) => s.id === Number(watchedServiceId));
    if (selected && selected.price != null) {
      setValue("price", selected.price, { shouldValidate: true });
    }
  }, [watchedServiceId, services, editing, setValue]);

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={editing ? "Edit Deal" : "New Deal"} size="lg">
      <form
        onSubmit={handleSubmit((data) => {
          onSubmit(data);
          reset();
        })}
        className="space-y-5"
      >
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>Client *</label>
            <select {...register("client_id")} className={SELECT_CLASS}>
              <option value="">Select client</option>
              {clients.map((c) => (
                <option key={c.id} value={c.id}>{c.company_name}</option>
              ))}
            </select>
            {errors.client_id && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.client_id.message}</p>}
          </div>
          <div>
            <label className={LABEL_CLASS}>Service *</label>
            <select {...register("service_id")} className={SELECT_CLASS}>
              <option value="">Select service</option>
              {services.map((s) => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
            {errors.service_id && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.service_id.message}</p>}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>Package Name</label>
            <input type="text" {...register("package_name")} placeholder="Basic Package" className={INPUT_CLASS} />
          </div>
          <div>
            <label className={LABEL_CLASS}>Sale Date *</label>
            <input type="date" {...register("sale_date")} className={INPUT_CLASS} />
            {errors.sale_date && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.sale_date.message}</p>}
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className={LABEL_CLASS}>Price *</label>
            <input type="number" step="0.01" {...register("price")} className={INPUT_CLASS} />
            {errors.price && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.price.message}</p>}
          </div>
          <div>
            <label className={LABEL_CLASS}>Discount</label>
            <input type="number" step="0.01" {...register("discount")} className={INPUT_CLASS} />
          </div>
          <div>
            <label className={LABEL_CLASS}>Tax</label>
            <input type="number" step="0.01" {...register("tax")} className={INPUT_CLASS} />
          </div>
        </div>

        <div className="bg-surface-50 rounded-xl p-4 border border-surface-100">
          <p className="text-[13px] text-surface-500">Final Amount</p>
          <p className="text-xl font-bold text-surface-800">{formatCurrency(finalAmount)}</p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>Payment Status</label>
            <select {...register("payment_status")} className={SELECT_CLASS}>
              {PAYMENT_STATUSES.map((s) => (
                <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
              ))}
            </select>
          </div>
          <div>
            <label className={LABEL_CLASS}>Deal Status</label>
            <select {...register("deal_status")} className={SELECT_CLASS}>
              {DEAL_STATUSES.map((s) => (
                <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className={LABEL_CLASS}>Notes</label>
          <textarea {...register("notes")} rows={3} placeholder="Additional notes..." className={INPUT_CLASS + " resize-none"} />
        </div>

        <div className="flex justify-end gap-3 pt-5 border-t border-surface-100">
          <button type="button" onClick={onClose} className="px-4 py-2.5 text-[13px] font-semibold text-surface-600 bg-white border border-surface-200 rounded-xl hover:bg-surface-50 transition-all duration-150">
            Cancel
          </button>
          <button type="submit" disabled={loading} className="px-4 py-2.5 text-[13px] font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl hover:from-primary-700 hover:to-primary-800 disabled:opacity-50 transition-all duration-150 shadow-sm shadow-primary-600/20">
            {loading ? "Saving..." : editing ? "Update" : "Create"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
