import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { userService } from "./api";
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
import { Plus, Pencil, Trash2, Search, UserCog, Key, Shield } from "lucide-react";
import toast from "react-hot-toast";

const userSchema = z.object({
  full_name: z.string().min(1, "Name is required").max(100, "Name too long"),
  email: z.string().min(1, "Email is required").email("Invalid email"),
  password: z.string().min(8, "Password must be at least 8 characters").optional().or(z.literal("")),
  phone: z.string().regex(/^\+?[0-9]{10,15}$/, "Phone must be 10-15 digits (optional +)").optional().or(z.literal("")),
  role: z.enum(["admin", "manager", "employee"]),
  status: z.enum(["active", "inactive"]),
});

const editUserSchema = z.object({
  full_name: z.string().min(1, "Name is required").max(100, "Name too long"),
  email: z.string().min(1, "Email is required").email("Invalid email"),
  phone: z.string().regex(/^\+?[0-9]{10,15}$/, "Phone must be 10-15 digits (optional +)").optional().or(z.literal("")),
  role: z.enum(["admin", "manager", "employee"]),
  status: z.enum(["active", "inactive"]),
});

const resetPasswordSchema = z.object({
  new_password: z.string().min(8, "Password must be at least 8 characters"),
});

const ROLE_LABELS = { admin: "Admin", manager: "Manager", employee: "Employee" };

const ROLE_COLORS = {
  admin: "bg-violet-50 text-violet-700 ring-violet-200/60",
  manager: "bg-sky-50 text-sky-700 ring-sky-200/60",
  employee: "bg-surface-100 text-surface-600 ring-surface-200/60",
};

const INPUT_CLASS = "w-full px-3.5 py-2.5 border border-surface-200 bg-surface-50 rounded-xl text-sm text-surface-800 placeholder:text-surface-300 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150";
const LABEL_CLASS = "block text-[13px] font-semibold text-surface-700 mb-1.5";
const SELECT_CLASS = INPUT_CLASS;

export default function UsersPage() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const isAdmin = user?.role === "admin";
  const [search, setSearch] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [resetTarget, setResetTarget] = useState(null);

  const { data: users = [], isLoading, error, refetch } = useQuery({
    queryKey: ["users"],
    queryFn: async () => {
      const res = await userService.getAll();
      return res.data.data;
    },
  });

  const createMutation = useMutation({
    mutationFn: (data) => userService.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      toast.success("User created");
      setModalOpen(false);
    },
    onError: (err) => toast.error(err.response?.data?.message || "Failed to create"),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => userService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      toast.success("User updated");
      setModalOpen(false);
      setEditing(null);
    },
    onError: (err) => toast.error(err.response?.data?.message || "Failed to update"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => userService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      toast.success("User deleted");
      setDeleteTarget(null);
    },
    onError: (err) => toast.error(err.response?.data?.message || "Failed to delete"),
  });

  const resetMutation = useMutation({
    mutationFn: ({ id, new_password }) => userService.changePassword(id, new_password),
    onSuccess: () => {
      toast.success("Password reset successfully");
      setResetTarget(null);
    },
    onError: (err) => toast.error(err.response?.data?.message || "Failed to reset password"),
  });

  const filtered = users.filter(
    (u) =>
      u.full_name?.toLowerCase().includes(search.toLowerCase()) ||
      u.email?.toLowerCase().includes(search.toLowerCase()) ||
      u.role?.toLowerCase().includes(search.toLowerCase())
  );

  const columns = [
    {
      key: "full_name",
      label: "Name",
      render: (val, row) => (
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-[11px] font-bold text-white shrink-0 shadow-sm shadow-primary-500/20">
            {val?.charAt(0)?.toUpperCase() || "?"}
          </div>
          <div className="min-w-0">
            <p className="text-[13px] font-semibold text-surface-800 truncate">{val}</p>
            <p className="text-[11px] text-surface-400 truncate">{row.email}</p>
          </div>
        </div>
      ),
    },
    {
      key: "role",
      label: "Role",
      render: (val) => (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold ring-1 ring-inset ${ROLE_COLORS[val] || "bg-surface-100 text-surface-600 ring-surface-200/60"}`}>
          <Shield className="w-3 h-3" />
          {ROLE_LABELS[val] || val}
        </span>
      ),
    },
    {
      key: "phone",
      label: "Phone",
      render: (val) => val || <span className="text-surface-300">-</span>,
    },
    {
      key: "status",
      label: "Status",
      render: (val) => <Badge variant={statusBadge(val)}>{val}</Badge>,
    },
    ...(isAdmin
      ? [
          {
            key: "id",
            label: "Actions",
            render: (_, row) => (
              <div className="flex items-center gap-1">
                <button onClick={() => openEdit(row)} className="p-2 text-surface-400 hover:text-primary-600 hover:bg-primary-50 rounded-xl transition-all duration-150" title="Edit">
                  <Pencil className="w-4 h-4" />
                </button>
                <button onClick={() => setResetTarget(row)} className="p-2 text-surface-400 hover:text-amber-600 hover:bg-amber-50 rounded-xl transition-all duration-150" title="Reset password">
                  <Key className="w-4 h-4" />
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

  const openEdit = (user) => {
    setEditing(user);
    setModalOpen(true);
  };

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay message={error.response?.data?.message || error.message} onRetry={refetch} />;

  return (
    <div>
      <PageHeader
        title="Users"
        description="Manage system users and roles"
        actions={
          isAdmin && (
            <button
              onClick={openCreate}
              className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white text-[13px] font-semibold rounded-xl hover:from-primary-700 hover:to-primary-800 transition-all duration-150 shadow-sm shadow-primary-600/20"
            >
              <Plus className="w-4 h-4" />
              Add User
            </button>
          )
        }
      />

      <div className="mb-6 relative">
        <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-surface-400 pointer-events-none" />
        <input
          type="text"
          placeholder="Search users..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full pl-10 pr-4 py-2.5 border border-surface-200 bg-white rounded-xl text-sm text-surface-800 placeholder:text-surface-300 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150 shadow-card"
          aria-label="Search users"
        />
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          icon={UserCog}
          title="No users found"
          description={search ? "Try a different search term" : "Get started by adding your first user"}
          action={
            !search && isAdmin && (
              <button onClick={openCreate} className="px-4 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white text-[13px] font-semibold rounded-xl hover:from-primary-700 hover:to-primary-800 shadow-sm shadow-primary-600/20">
                Add User
              </button>
            )
          }
        />
      ) : (
        <DataTable columns={columns} data={filtered} />
      )}

      {editing ? (
        <EditUserModal
          isOpen={modalOpen}
          onClose={() => { setModalOpen(false); setEditing(null); }}
          editing={editing}
          onSubmit={(data) => updateMutation.mutate({ id: editing.id, data })}
          loading={updateMutation.isPending}
        />
      ) : (
        <CreateUserModal
          isOpen={modalOpen}
          onClose={() => setModalOpen(false)}
          onSubmit={(data) => createMutation.mutate(data)}
          loading={createMutation.isPending}
        />
      )}

      <ConfirmDialog
        isOpen={!!deleteTarget}
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => deleteMutation.mutate(deleteTarget.id)}
        title="Delete User"
        message={`Are you sure you want to delete "${deleteTarget?.full_name}"? This action cannot be undone.`}
        loading={deleteMutation.isPending}
      />

      <ResetPasswordModal
        isOpen={!!resetTarget}
        onClose={() => setResetTarget(null)}
        user={resetTarget}
        onSubmit={(newPassword) => resetMutation.mutate({ id: resetTarget.id, new_password: newPassword })}
        loading={resetMutation.isPending}
      />
    </div>
  );
}

function CreateUserModal({ isOpen, onClose, onSubmit, loading }) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(userSchema),
    defaultValues: { full_name: "", email: "", password: "", phone: "", role: "employee", status: "active" },
  });

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create User">
      <form
        onSubmit={handleSubmit((data) => {
          const payload = { ...data };
          if (!payload.password) delete payload.password;
          if (!payload.phone) delete payload.phone;
          onSubmit(payload);
          reset();
        })}
        className="space-y-5"
      >
        {[
          { name: "full_name", label: "Full Name", placeholder: "John Doe" },
          { name: "email", label: "Email", type: "email", placeholder: "john@company.com" },
          { name: "password", label: "Password", type: "password", placeholder: "Min 8 characters", hint: "Min 8 characters" },
          { name: "phone", label: "Phone", type: "tel", placeholder: "+1234567890", hint: "Optional" },
        ].map(({ name, label, type = "text", placeholder, hint }) => (
          <div key={name}>
            <label className={LABEL_CLASS}>{label}</label>
            <input type={type} {...register(name)} placeholder={placeholder} className={INPUT_CLASS} />
            {hint && !errors[name] && <p className="text-[11px] text-surface-400 mt-1">{hint}</p>}
            {errors[name] && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors[name].message}</p>}
          </div>
        ))}

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>Role</label>
            <select {...register("role")} className={SELECT_CLASS}>
              <option value="employee">Employee</option>
              <option value="manager">Manager</option>
              <option value="admin">Admin</option>
            </select>
            {errors.role && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.role.message}</p>}
          </div>
          <div>
            <label className={LABEL_CLASS}>Status</label>
            <select {...register("status")} className={SELECT_CLASS}>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
            {errors.status && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.status.message}</p>}
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-5 border-t border-surface-100">
          <button type="button" onClick={onClose} className="px-4 py-2.5 text-[13px] font-semibold text-surface-600 bg-white border border-surface-200 rounded-xl hover:bg-surface-50 transition-all duration-150">
            Cancel
          </button>
          <button type="submit" disabled={loading} className="px-4 py-2.5 text-[13px] font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl hover:from-primary-700 hover:to-primary-800 disabled:opacity-50 transition-all duration-150 shadow-sm shadow-primary-600/20">
            {loading ? "Creating..." : "Create User"}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function EditUserModal({ isOpen, onClose, editing, onSubmit, loading }) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(editUserSchema),
    values: {
      full_name: editing.full_name,
      email: editing.email,
      phone: editing.phone || "",
      role: editing.role,
      status: editing.status,
    },
  });

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Edit User">
      <form onSubmit={handleSubmit((data) => onSubmit(data))} className="space-y-5">
        {[
          { name: "full_name", label: "Full Name", placeholder: "John Doe" },
          { name: "email", label: "Email", type: "email", placeholder: "john@company.com" },
          { name: "phone", label: "Phone", type: "tel", placeholder: "+1234567890" },
        ].map(({ name, label, type = "text", placeholder }) => (
          <div key={name}>
            <label className={LABEL_CLASS}>{label}</label>
            <input type={type} {...register(name)} placeholder={placeholder} className={INPUT_CLASS} />
            {errors[name] && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors[name].message}</p>}
          </div>
        ))}

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>Role</label>
            <select {...register("role")} className={SELECT_CLASS}>
              <option value="employee">Employee</option>
              <option value="manager">Manager</option>
              <option value="admin">Admin</option>
            </select>
            {errors.role && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.role.message}</p>}
          </div>
          <div>
            <label className={LABEL_CLASS}>Status</label>
            <select {...register("status")} className={SELECT_CLASS}>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
            {errors.status && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.status.message}</p>}
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-5 border-t border-surface-100">
          <button type="button" onClick={onClose} className="px-4 py-2.5 text-[13px] font-semibold text-surface-600 bg-white border border-surface-200 rounded-xl hover:bg-surface-50 transition-all duration-150">
            Cancel
          </button>
          <button type="submit" disabled={loading} className="px-4 py-2.5 text-[13px] font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl hover:from-primary-700 hover:to-primary-800 disabled:opacity-50 transition-all duration-150 shadow-sm shadow-primary-600/20">
            {loading ? "Saving..." : "Update"}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function ResetPasswordModal({ isOpen, onClose, user, onSubmit, loading }) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: { new_password: "" },
  });

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Reset Password — ${user?.full_name || ""}`}>
      <form
        onSubmit={handleSubmit((data) => {
          onSubmit(data.new_password);
          reset();
        })}
        className="space-y-5"
      >
        <div>
          <label className={LABEL_CLASS}>New Password</label>
          <input
            type="password"
            {...register("new_password")}
            className={INPUT_CLASS}
            placeholder="Min 8 characters"
          />
          {errors.new_password && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.new_password.message}</p>}
        </div>

        <div className="flex justify-end gap-3 pt-5 border-t border-surface-100">
          <button type="button" onClick={onClose} className="px-4 py-2.5 text-[13px] font-semibold text-surface-600 bg-white border border-surface-200 rounded-xl hover:bg-surface-50 transition-all duration-150">
            Cancel
          </button>
          <button type="submit" disabled={loading} className="px-4 py-2.5 text-[13px] font-semibold text-white bg-gradient-to-r from-amber-500 to-amber-600 rounded-xl hover:from-amber-600 hover:to-amber-700 disabled:opacity-50 transition-all duration-150 shadow-sm shadow-amber-500/20">
            {loading ? "Resetting..." : "Reset Password"}
          </button>
        </div>
      </form>
    </Modal>
  );
}
