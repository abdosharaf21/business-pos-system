import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { clientServiceApi } from "./api";
import { clientService } from "../clients/api";
import { serviceService } from "../services/api";
import { useAuth } from "../../shared/context/AuthContext";
import { PageHeader } from "../../shared/components/PageHeader";
import { DataTable } from "../../shared/components/DataTable";
import { Badge, statusBadge } from "../../shared/components/Badge";
import { Modal } from "../../shared/components/Modal";
import { ConfirmDialog } from "../../shared/components/ConfirmDialog";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Plus, Pencil, Trash2, Search, Link2 } from "lucide-react";
import toast from "react-hot-toast";

const assignSchema = z.object({
  client_id: z.coerce.number().min(1, "Client is required"),
  service_id: z.coerce.number().min(1, "Service is required"),
  start_date: z.string().min(1, "Start date is required"),
  end_date: z.string().min(1, "End date is required"),
  status: z.enum(["pending", "in_progress", "completed", "cancelled"]),
});

const editSchema = z.object({
  start_date: z.string().min(1, "Start date is required"),
  end_date: z.string().min(1, "End date is required"),
  status: z.enum(["pending", "in_progress", "completed", "cancelled"]),
});

const INPUT_CLASS = "w-full px-3.5 py-2.5 border border-surface-200 bg-surface-50 rounded-xl text-sm text-surface-800 placeholder:text-surface-300 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150";
const LABEL_CLASS = "block text-[13px] font-semibold text-surface-700 mb-1.5";
const SELECT_CLASS = INPUT_CLASS;

export default function ClientServicesPage() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const canManage = ["admin", "manager"].includes(user?.role);
  const [search, setSearch] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const { data: allClients = [] } = useQuery({
    queryKey: ["clients"],
    queryFn: async () => { const res = await clientService.getAll(); return res.data.data; },
  });

  const { data: allServices = [] } = useQuery({
    queryKey: ["services"],
    queryFn: async () => { const res = await serviceService.getAll(); return res.data.data; },
  });

  const { data: assignments = [], isLoading, error, refetch } = useQuery({
    queryKey: ["client-assignments"],
    queryFn: async () => {
      const all = [];
      const clientsRes = await clientService.getAll();
      for (const c of clientsRes.data.data) {
        const res = await clientServiceApi.getByClient(c.id);
        all.push(...res.data.data);
      }
      return all;
    },
  });

  const clientMap = Object.fromEntries(allClients.map((c) => [c.id, c.company_name]));
  const serviceMap = Object.fromEntries(allServices.map((s) => [s.id, s.name]));

  const filtered = assignments.filter((a) => {
    const cn = clientMap[a.client_id] || "";
    const sn = serviceMap[a.service_id] || "";
    return cn.toLowerCase().includes(search.toLowerCase()) || sn.toLowerCase().includes(search.toLowerCase());
  });

  const createMutation = useMutation({
    mutationFn: ({ clientId, serviceId, data }) => clientServiceApi.assign(clientId, serviceId, data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["client-assignments"] }); toast.success("Service assigned"); setModalOpen(false); },
    onError: (err) => toast.error(err.response?.data?.message || "Failed"),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => clientServiceApi.update(id, data),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["client-assignments"] }); toast.success("Assignment updated"); setModalOpen(false); setEditing(null); },
    onError: (err) => toast.error(err.response?.data?.message || "Failed"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => clientServiceApi.remove(id),
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["client-assignments"] }); toast.success("Assignment removed"); setDeleteTarget(null); },
    onError: (err) => toast.error(err.response?.data?.message || "Failed"),
  });

  const columns = [
    {
      key: "client_id",
      label: "Client",
      render: (val) => <span className="text-[13px] font-semibold text-surface-800">{clientMap[val] || `#${val}`}</span>,
    },
    {
      key: "service_id",
      label: "Service",
      render: (val) => <Badge variant="info">{serviceMap[val] || `#${val}`}</Badge>,
    },
    { key: "start_date", label: "Start Date", render: (val) => <span className="text-surface-600">{val ? new Date(val).toLocaleDateString() : "-"}</span> },
    { key: "end_date", label: "End Date", render: (val) => <span className="text-surface-600">{val ? new Date(val).toLocaleDateString() : "-"}</span> },
    { key: "status", label: "Status", render: (val) => <Badge variant={statusBadge(val)}>{val}</Badge> },
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
        title="Client Services"
        description="Manage service assignments for clients"
        actions={
          canManage && (
            <button onClick={() => { setEditing(null); setModalOpen(true); }} className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white text-[13px] font-semibold rounded-xl hover:from-primary-700 hover:to-primary-800 transition-all duration-150 shadow-sm shadow-primary-600/20">
              <Plus className="w-4 h-4" />
              Assign Service
            </button>
          )
        }
      />

      <div className="mb-6 relative">
        <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-surface-400 pointer-events-none" />
        <input type="text" placeholder="Search assignments..." value={search} onChange={(e) => setSearch(e.target.value)} className="w-full pl-10 pr-4 py-2.5 border border-surface-200 bg-white rounded-xl text-sm text-surface-800 placeholder:text-surface-300 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150 shadow-card" aria-label="Search assignments" />
      </div>

      {filtered.length === 0 ? (
        <EmptyState icon={Link2} title="No assignments found" description={search ? "Try a different search" : "Assign your first service to a client"} action={!search && canManage && <button onClick={() => { setEditing(null); setModalOpen(true); }} className="px-4 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white text-[13px] font-semibold rounded-xl hover:from-primary-700 hover:to-primary-800 shadow-sm shadow-primary-600/20">Assign Service</button>} />
      ) : (
        <DataTable columns={columns} data={filtered} />
      )}

      {editing ? (
        <EditModal isOpen={modalOpen} onClose={() => { setModalOpen(false); setEditing(null); }} editing={editing} onSubmit={(data) => updateMutation.mutate({ id: editing.id, data })} loading={updateMutation.isPending} />
      ) : (
        <AssignModal isOpen={modalOpen} onClose={() => setModalOpen(false)} clients={allClients} services={allServices} onSubmit={(data) => createMutation.mutate({ clientId: data.client_id, serviceId: data.service_id, data: { start_date: data.start_date, end_date: data.end_date, status: data.status } })} loading={createMutation.isPending} />
      )}

      <ConfirmDialog isOpen={!!deleteTarget} onClose={() => setDeleteTarget(null)} onConfirm={() => deleteMutation.mutate(deleteTarget.id)} title="Remove Assignment" message="Are you sure you want to remove this service assignment?" loading={deleteMutation.isPending} />
    </div>
  );
}

function AssignModal({ isOpen, onClose, clients, services, onSubmit, loading }) {
  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: zodResolver(assignSchema),
    defaultValues: { client_id: 0, service_id: 0, start_date: "", end_date: "", status: "pending" },
  });

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Assign Service">
      <form onSubmit={handleSubmit((data) => { onSubmit(data); reset(); })} className="space-y-5">
        <div>
          <label className={LABEL_CLASS}>Client</label>
          <select {...register("client_id")} className={SELECT_CLASS}>
            <option value={0}>Select client</option>
            {clients.map((c) => <option key={c.id} value={c.id}>{c.company_name}</option>)}
          </select>
          {errors.client_id && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.client_id.message}</p>}
        </div>
        <div>
          <label className={LABEL_CLASS}>Service</label>
          <select {...register("service_id")} className={SELECT_CLASS}>
            <option value={0}>Select service</option>
            {services.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          {errors.service_id && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.service_id.message}</p>}
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>Start Date</label>
            <input type="date" {...register("start_date")} className={INPUT_CLASS} />
            {errors.start_date && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.start_date.message}</p>}
          </div>
          <div>
            <label className={LABEL_CLASS}>End Date</label>
            <input type="date" {...register("end_date")} className={INPUT_CLASS} />
            {errors.end_date && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.end_date.message}</p>}
          </div>
        </div>
        <div>
          <label className={LABEL_CLASS}>Status</label>
          <select {...register("status")} className={SELECT_CLASS}>
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
        <div className="flex justify-end gap-3 pt-5 border-t border-surface-100">
          <button type="button" onClick={onClose} className="px-4 py-2.5 text-[13px] font-semibold text-surface-600 bg-white border border-surface-200 rounded-xl hover:bg-surface-50 transition-all duration-150">Cancel</button>
          <button type="submit" disabled={loading} className="px-4 py-2.5 text-[13px] font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl hover:from-primary-700 hover:to-primary-800 disabled:opacity-50 transition-all duration-150 shadow-sm shadow-primary-600/20">{loading ? "Assigning..." : "Assign"}</button>
        </div>
      </form>
    </Modal>
  );
}

function EditModal({ isOpen, onClose, editing, onSubmit, loading }) {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(editSchema),
    values: { start_date: editing.start_date ? editing.start_date.split("T")[0] : "", end_date: editing.end_date ? editing.end_date.split("T")[0] : "", status: editing.status },
  });

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Edit Assignment">
      <form onSubmit={handleSubmit((data) => { onSubmit(data); })} className="space-y-5">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>Start Date</label>
            <input type="date" {...register("start_date")} className={INPUT_CLASS} />
            {errors.start_date && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.start_date.message}</p>}
          </div>
          <div>
            <label className={LABEL_CLASS}>End Date</label>
            <input type="date" {...register("end_date")} className={INPUT_CLASS} />
            {errors.end_date && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.end_date.message}</p>}
          </div>
        </div>
        <div>
          <label className={LABEL_CLASS}>Status</label>
          <select {...register("status")} className={SELECT_CLASS}>
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
        <div className="flex justify-end gap-3 pt-5 border-t border-surface-100">
          <button type="button" onClick={onClose} className="px-4 py-2.5 text-[13px] font-semibold text-surface-600 bg-white border border-surface-200 rounded-xl hover:bg-surface-50 transition-all duration-150">Cancel</button>
          <button type="submit" disabled={loading} className="px-4 py-2.5 text-[13px] font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl hover:from-primary-700 hover:to-primary-800 disabled:opacity-50 transition-all duration-150 shadow-sm shadow-primary-600/20">{loading ? "Saving..." : "Update"}</button>
        </div>
      </form>
    </Modal>
  );
}
