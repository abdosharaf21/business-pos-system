import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { customerService } from "./api";
import { useAuth } from "../../shared/context/AuthContext";
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
import { Plus, Pencil, Trash2, Search, Users } from "lucide-react";
import toast from "react-hot-toast";

const customerSchema = z.object({
  name: z.string().min(1, "Name is required"),
  phone: z.string().min(1, "Phone is required"),
  email: z.string().optional(),
  address: z.string().optional(),
});

const INPUT_CLASS = "w-full px-3.5 py-2.5 border border-surface-200 bg-surface-50 rounded-xl text-sm text-surface-800 placeholder:text-surface-300 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150";
const LABEL_CLASS = "block text-[13px] font-semibold text-surface-700 mb-1.5";

export default function CustomersPage() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const canManage = ["admin", "manager"].includes(user?.role);
  const [search, setSearch] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const { data: customers = [], isLoading, error, refetch } = useQuery({
    queryKey: ["customers"],
    queryFn: async () => {
      const res = await customerService.getAll();
      return res.data.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: (data) => customerService.create(data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["customers"] }); toast.success("Customer created"); setModalOpen(false); },
    onError: (err) => toast.error(err.response?.data?.message || "Failed to create customer"),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => customerService.update(id, data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["customers"] }); toast.success("Customer updated"); setModalOpen(false); setEditing(null); },
    onError: (err) => toast.error(err.response?.data?.message || "Failed to update customer"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => customerService.delete(id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["customers"] }); toast.success("Customer deleted"); setDeleteTarget(null); },
    onError: (err) => toast.error(err.response?.data?.message || "Failed to delete customer"),
  });

  const filtered = customers.filter((c) => {
    const term = search.toLowerCase();
    return !search ||
      c.name?.toLowerCase().includes(term) ||
      c.phone?.toLowerCase().includes(term);
  });

  const columns = [
    {
      key: "name",
      label: "Name",
      render: (val) => <span className="text-[13px] font-semibold text-surface-800">{val}</span>,
    },
    {
      key: "phone",
      label: "Phone",
      render: (val) => <span className="text-[13px] text-surface-600">{val || "-"}</span>,
    },
    {
      key: "email",
      label: "Email",
      render: (val) => <span className="text-[13px] text-surface-500">{val || "-"}</span>,
    },
    {
      key: "address",
      label: "Address",
      render: (val) => <span className="text-[13px] text-surface-500 truncate max-w-[200px] inline-block">{val || "-"}</span>,
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
        title="Customers"
        description="Manage your customer directory"
        actions={
          canManage && (
            <button onClick={() => { setEditing(null); setModalOpen(true); }} className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white text-[13px] font-semibold rounded-xl hover:from-primary-700 hover:to-primary-800 transition-all duration-150 shadow-sm shadow-primary-600/20">
              <Plus className="w-4 h-4" />
              New Customer
            </button>
          )
        }
      />

      <div className="mb-6 relative">
        <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-surface-400 pointer-events-none" />
        <input type="text" placeholder="Search by name or phone..." value={search} onChange={(e) => setSearch(e.target.value)} className="w-full pl-10 pr-4 py-2.5 border border-surface-200 bg-white rounded-xl text-sm text-surface-800 placeholder:text-surface-300 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150 shadow-card" aria-label="Search customers" />
      </div>

      {filtered.length === 0 ? (
        <EmptyState icon={Users} title="No customers found" description={search ? "Try a different search" : "Add your first customer"} action={!search && canManage && <button onClick={() => { setEditing(null); setModalOpen(true); }} className="px-4 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white text-[13px] font-semibold rounded-xl hover:from-primary-700 hover:to-primary-800 shadow-sm shadow-primary-600/20">Add Customer</button>} />
      ) : (
        <DataTable columns={columns} data={filtered} />
      )}

      <CustomerModal isOpen={modalOpen} onClose={() => { setModalOpen(false); setEditing(null); }} editing={editing} onSubmit={(data) => editing ? updateMutation.mutate({ id: editing.id, data }) : createMutation.mutate(data)} loading={createMutation.isPending || updateMutation.isPending} />

      <ConfirmDialog isOpen={!!deleteTarget} onClose={() => setDeleteTarget(null)} onConfirm={() => deleteMutation.mutate(deleteTarget.id)} title="Delete Customer" message={`Delete "${deleteTarget?.name}"? This action cannot be undone.`} loading={deleteMutation.isPending} />
    </div>
  );
}

function CustomerModal({ isOpen, onClose, editing, onSubmit, loading }) {
  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: zodResolver(customerSchema),
    values: editing ? {
      name: editing.name || "",
      phone: editing.phone || "",
      email: editing.email || "",
      address: editing.address || "",
    } : {
      name: "",
      phone: "",
      email: "",
      address: "",
    },
  });

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={editing ? "Edit Customer" : "New Customer"}>
      <form onSubmit={handleSubmit((data) => { onSubmit(data); reset(); })} className="space-y-5">
        <div>
          <label className={LABEL_CLASS}>Name</label>
          <input {...register("name")} placeholder="Full name" className={INPUT_CLASS} />
          {errors.name && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.name.message}</p>}
        </div>
        <div>
          <label className={LABEL_CLASS}>Phone</label>
          <input {...register("phone")} placeholder="Phone number" className={INPUT_CLASS} />
          {errors.phone && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.phone.message}</p>}
        </div>
        <div>
          <label className={LABEL_CLASS}>Email</label>
          <input {...register("email")} type="email" placeholder="Email address (optional)" className={INPUT_CLASS} />
          {errors.email && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.email.message}</p>}
        </div>
        <div>
          <label className={LABEL_CLASS}>Address</label>
          <textarea {...register("address")} rows={2} placeholder="Address (optional)" className={`${INPUT_CLASS} resize-none`} />
          {errors.address && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.address.message}</p>}
        </div>
        <div className="flex justify-end gap-3 pt-5 border-t border-surface-100">
          <button type="button" onClick={onClose} className="px-4 py-2.5 text-[13px] font-semibold text-surface-600 bg-white border border-surface-200 rounded-xl hover:bg-surface-50 transition-all duration-150">Cancel</button>
          <button type="submit" disabled={loading} className="px-4 py-2.5 text-[13px] font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl hover:from-primary-700 hover:to-primary-800 disabled:opacity-50 transition-all duration-150 shadow-sm shadow-primary-600/20">{loading ? "Saving..." : editing ? "Update" : "Create"}</button>
        </div>
      </form>
    </Modal>
  );
}
