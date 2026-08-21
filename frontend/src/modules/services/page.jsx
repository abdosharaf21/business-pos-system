import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { serviceService } from "./api";
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
import { Plus, Pencil, Trash2, Search, Wrench } from "lucide-react";
import toast from "react-hot-toast";

const serviceSchema = z.object({
  name: z.string().min(1, "Service name is required"),
  description: z.string().optional().nullable(),
  price: z.coerce.number().min(0, "Price must be positive").optional().nullable(),
  duration_days: z.coerce.number().min(1, "Duration must be at least 1 day").optional().nullable(),
  status: z.enum(["active", "inactive"]),
});

const STATUS_OPTIONS = ["active", "inactive"];

const INPUT_CLASS = "w-full px-3.5 py-2.5 border border-surface-200 bg-surface-50 rounded-xl text-sm text-surface-800 placeholder:text-surface-300 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150";
const LABEL_CLASS = "block text-[13px] font-semibold text-surface-700 mb-1.5";
const SELECT_CLASS = INPUT_CLASS;

function formatCurrency(amount) {
  return new Intl.NumberFormat("en-US", { style: "currency", currency: "EGP" }).format(amount || 0);
}

export default function ServicesPage() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const canManage = ["admin", "manager"].includes(user?.role);
  const [search, setSearch] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const { data: services = [], isLoading, error, refetch } = useQuery({
    queryKey: ["services"],
    queryFn: async () => {
      const res = await serviceService.getAll();
      return res.data.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: (data) => serviceService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["services"] });
      toast.success("Service created");
      setModalOpen(false);
    },
    onError: (err) => toast.error(err.response?.data?.message || "Failed to create"),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => serviceService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["services"] });
      toast.success("Service updated");
      setModalOpen(false);
      setEditing(null);
    },
    onError: (err) => toast.error(err.response?.data?.message || "Failed to update"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => serviceService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["services"] });
      toast.success("Service deleted");
      setDeleteTarget(null);
    },
    onError: (err) => toast.error(err.response?.data?.message || "Failed to delete"),
  });

  const filtered = services.filter(
    (s) =>
      s.name?.toLowerCase().includes(search.toLowerCase()) ||
      s.description?.toLowerCase().includes(search.toLowerCase())
  );

  const columns = [
    {
      key: "name",
      label: "Service",
      render: (val) => (
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-purple-50 flex items-center justify-center text-[11px] font-bold text-purple-600 shrink-0">
            {val?.charAt(0)?.toUpperCase() || "?"}
          </div>
          <div className="min-w-0">
            <p className="text-[13px] font-semibold text-surface-800 truncate">{val}</p>
          </div>
        </div>
      ),
    },
    {
      key: "price",
      label: "Price",
      render: (val) => <span className="text-[13px] font-semibold text-surface-800">{formatCurrency(val)}</span>,
    },
    {
      key: "duration_days",
      label: "Duration",
      render: (val) => <span className="text-surface-600">{val ? `${val} days` : "-"}</span>,
    },
    {
      key: "status",
      label: "Status",
      render: (val) => (
        <Badge variant={val === "active" ? "success" : "default"}>{val}</Badge>
      ),
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

  const openEdit = (service) => {
    setEditing(service);
    setModalOpen(true);
  };

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay message={error.response?.data?.message || error.message} onRetry={refetch} />;

  return (
    <div>
      <PageHeader
        title="Services"
        description="Manage your billable services and offerings"
        actions={
          canManage && (
            <button
              onClick={openCreate}
              className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white text-[13px] font-semibold rounded-xl hover:from-primary-700 hover:to-primary-800 transition-all duration-150 shadow-sm shadow-primary-600/20"
            >
              <Plus className="w-4 h-4" />
              Add Service
            </button>
          )
        }
      />

      <div className="mb-6 relative">
        <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-surface-400 pointer-events-none" />
        <input
          type="text"
          placeholder="Search services..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2.5 border border-surface-200 bg-white rounded-xl text-sm text-surface-800 placeholder:text-surface-300 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150 shadow-card"
          aria-label="Search services"
        />
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          icon={Wrench}
          title="No services found"
          description={search ? "Try a different search term" : "Get started by adding your first service"}
          action={
            !search && canManage && (
              <button onClick={openCreate} className="px-4 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white text-[13px] font-semibold rounded-xl hover:from-primary-700 hover:to-primary-800 shadow-sm shadow-primary-600/20">
                Add Service
              </button>
            )
          }
        />
      ) : (
        <DataTable columns={columns} data={filtered} />
      )}

      <ServiceModal
        isOpen={modalOpen}
        onClose={() => { setModalOpen(false); setEditing(null); }}
        editing={editing}
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
        title="Delete Service"
        message={`Are you sure you want to delete "${deleteTarget?.name}"? This action cannot be undone.`}
        loading={deleteMutation.isPending}
      />
    </div>
  );
}

function ServiceModal({ isOpen, onClose, editing, onSubmit, loading }) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(serviceSchema),
    values: editing
      ? {
          name: editing.name || "",
          description: editing.description || "",
          price: editing.price ?? "",
          duration_days: editing.duration_days ?? "",
          status: editing.status || "active",
        }
      : {
          name: "",
          description: "",
          price: "",
          duration_days: "",
          status: "active",
        },
  });

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={editing ? "Edit Service" : "New Service"}>
      <form
        onSubmit={handleSubmit((data) => {
          onSubmit(data);
          reset();
        })}
        className="space-y-5"
      >
        <div>
          <label className={LABEL_CLASS}>Service Name *</label>
          <input type="text" {...register("name")} placeholder="e.g. POS System Setup" className={INPUT_CLASS} />
          {errors.name && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.name.message}</p>}
        </div>

        <div>
          <label className={LABEL_CLASS}>Description</label>
          <textarea {...register("description")} rows={3} placeholder="Brief description of the service" className={INPUT_CLASS + " resize-none"} />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>Price (EGP)</label>
            <input type="number" step="0.01" {...register("price")} placeholder="0.00" className={INPUT_CLASS} />
            {errors.price && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.price.message}</p>}
          </div>
          <div>
            <label className={LABEL_CLASS}>Duration (days)</label>
            <input type="number" {...register("duration_days")} placeholder="30" className={INPUT_CLASS} />
            {errors.duration_days && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.duration_days.message}</p>}
          </div>
        </div>

        <div>
          <label className={LABEL_CLASS}>Status</label>
          <select {...register("status")} className={SELECT_CLASS}>
            {STATUS_OPTIONS.map((s) => (
              <option key={s} value={s}>{s.charAt(0).toUpperCase() + s.slice(1)}</option>
            ))}
          </select>
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
