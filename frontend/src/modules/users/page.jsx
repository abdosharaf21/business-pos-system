import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { userService } from "./api";
import { inputClass, labelClass, searchInputClass } from "../../shared/components/styles";
import { useAuth } from "../../shared/context/AuthContext";
import { useTranslation } from "react-i18next";
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

const ROLE_COLORS = {
  admin: "bg-violet-50 text-violet-700 ring-violet-200/60 dark:bg-violet-500/10 dark:text-violet-400 dark:ring-violet-500/30",
  manager: "bg-primary-50 text-primary-700 ring-primary-200/60 dark:bg-primary-500/10 dark:text-primary-400 dark:ring-primary-500/30",
  employee: "bg-surface-100 text-surface-600 ring-surface-200/60 dark:bg-surface-700/50 dark:text-surface-300 dark:ring-surface-700/60",
};

const INPUT_CLASS = inputClass;
const LABEL_CLASS = labelClass;
const SELECT_CLASS = INPUT_CLASS;

export default function UsersPage() {
  const { t } = useTranslation();
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
      toast.success(t("users.toast.created"));
      setModalOpen(false);
    },
    onError: (err) => toast.error(err.response?.data?.message || t("users.toast.createFailed")),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => userService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      toast.success(t("users.toast.updated"));
      setModalOpen(false);
      setEditing(null);
    },
    onError: (err) => toast.error(err.response?.data?.message || t("users.toast.updateFailed")),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => userService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      toast.success(t("users.toast.deleted"));
      setDeleteTarget(null);
    },
    onError: (err) => toast.error(err.response?.data?.message || t("users.toast.deleteFailed")),
  });

  const resetMutation = useMutation({
    mutationFn: ({ id, new_password }) => userService.changePassword(id, new_password),
    onSuccess: () => {
      toast.success(t("users.toast.passwordReset"));
      setResetTarget(null);
    },
    onError: (err) => toast.error(err.response?.data?.message || t("users.toast.passwordResetFailed")),
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
      label: t("users.columns.name"),
      render: (val, row) => (
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-[11px] font-bold text-white shrink-0 shadow-sm shadow-primary-500/20">
            {val?.charAt(0)?.toUpperCase() || "?"}
          </div>
          <div className="min-w-0">
            <p className="text-[13px] font-semibold text-surface-800 dark:text-surface-100 truncate">{val}</p>
            <p className="text-[11px] text-surface-400 dark:text-surface-500 truncate">{row.email}</p>
          </div>
        </div>
      ),
    },
    {
      key: "role",
      label: t("users.columns.role"),
      render: (val) => (
        <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold ring-1 ring-inset ${ROLE_COLORS[val] || "bg-surface-100 dark:bg-surface-700/50 text-surface-600 dark:text-surface-300 ring-surface-200/60 dark:ring-surface-700/60"}`}>
          <Shield className="w-3 h-3" />
          {t("users.roles." + val)}
        </span>
      ),
    },
    {
      key: "phone",
      label: t("users.columns.phone"),
      render: (val) => val || <span className="text-surface-300 dark:text-surface-600">-</span>,
    },
    {
      key: "status",
      label: t("users.columns.status"),
      render: (val) => <Badge variant={statusBadge(val)}>{t("users.status." + val)}</Badge>,
    },
    ...(isAdmin
      ? [
          {
            key: "id",
            label: t("users.columns.actions"),
            render: (_, row) => (
              <div className="flex items-center gap-1">
                <button onClick={() => openEdit(row)} className="p-2 text-surface-400 dark:text-surface-500 hover:text-primary-600 dark:hover:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-500/10 rounded-xl transition-all duration-150" title={t("users.edit")}>
                  <Pencil className="w-4 h-4" />
                </button>
                <button onClick={() => setResetTarget(row)} className="p-2 text-surface-400 dark:text-surface-500 hover:text-amber-600 dark:hover:text-amber-400 hover:bg-amber-50 dark:hover:bg-amber-500/10 rounded-xl transition-all duration-150" title={t("users.resetPassword")}>
                  <Key className="w-4 h-4" />
                </button>
                <button onClick={() => setDeleteTarget(row)} className="p-2 text-surface-400 dark:text-surface-500 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-500/10 rounded-xl transition-all duration-150" title={t("users.delete")}>
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
        title={t("users.title")}
        description={t("users.description")}
        actions={
          isAdmin && (
            <button
              onClick={openCreate}
              className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white text-[13px] font-semibold rounded-xl hover:from-primary-700 hover:to-primary-800 transition-all duration-150 shadow-sm shadow-primary-600/20"
            >
              <Plus className="w-4 h-4" />
              {t("users.addUser")}
            </button>
          )
        }
      />

      <div className="mb-6 relative">
        <Search className="w-4 h-4 absolute start-3.5 top-1/2 -translate-y-1/2 text-surface-400 dark:text-surface-500 pointer-events-none" />
        <input
          type="text"
          placeholder={t("users.searchPlaceholder")}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className={searchInputClass}
          aria-label={t("users.searchAriaLabel")}
        />
      </div>

      {filtered.length === 0 ? (
        <EmptyState
          icon={UserCog}
          title={t("users.empty.noResultsTitle")}
          description={search ? t("users.empty.noResultsDescription") : t("users.empty.noUsersDescription")}
          action={
            !search && isAdmin && (
              <button onClick={openCreate} className="px-4 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white text-[13px] font-semibold rounded-xl hover:from-primary-700 hover:to-primary-800 shadow-sm shadow-primary-600/20">
                {t("users.empty.addUser")}
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
        title={t("users.confirmDelete.title")}
        message={t("users.confirmDelete.message", { name: deleteTarget?.full_name })}
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
  const { t } = useTranslation();

  const userSchema = useMemo(() => z.object({
    full_name: z.string().min(1, t("users.validation.nameRequired")).max(100, t("users.validation.nameTooLong")),
    email: z.string().min(1, t("users.validation.emailRequired")).email(t("users.validation.emailInvalid")),
    password: z.string().min(8, t("users.validation.passwordMin")).optional().or(z.literal("")),
    phone: z.string().regex(/^\+?[0-9]{10,15}$/, t("users.validation.phoneInvalid")).optional().or(z.literal("")),
    role: z.enum(["admin", "manager", "employee"]),
    status: z.enum(["active", "inactive"]),
  }), [t]);

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
    <Modal isOpen={isOpen} onClose={onClose} title={t("users.form.createTitle")}>
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
          { name: "full_name", label: t("users.form.fullName"), placeholder: t("users.form.fullNamePlaceholder") },
          { name: "email", label: t("users.form.email"), type: "email", placeholder: t("users.form.emailPlaceholder") },
          { name: "password", label: t("users.form.password"), type: "password", placeholder: t("users.form.passwordPlaceholder"), hint: t("users.form.passwordHint") },
          { name: "phone", label: t("users.form.phone"), type: "tel", placeholder: t("users.form.phonePlaceholder"), hint: t("users.form.phoneHint") },
        ].map(({ name, label, type = "text", placeholder, hint }) => (
          <div key={name}>
            <label className={LABEL_CLASS}>{label}</label>
            <input type={type} {...register(name)} placeholder={placeholder} className={INPUT_CLASS} />
            {hint && !errors[name] && <p className="text-[11px] text-surface-400 dark:text-surface-500 mt-1">{hint}</p>}
            {errors[name] && <p className="text-[11px] text-red-500 dark:text-red-400 mt-1 font-medium">{errors[name].message}</p>}
          </div>
        ))}

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>{t("users.form.role")}</label>
            <select {...register("role")} className={SELECT_CLASS}>
              <option value="employee">{t("users.roles.employee")}</option>
              <option value="manager">{t("users.roles.manager")}</option>
              <option value="admin">{t("users.roles.admin")}</option>
            </select>
            {errors.role && <p className="text-[11px] text-red-500 dark:text-red-400 mt-1 font-medium">{errors.role.message}</p>}
          </div>
          <div>
            <label className={LABEL_CLASS}>{t("users.form.status")}</label>
            <select {...register("status")} className={SELECT_CLASS}>
              <option value="active">{t("users.status.active")}</option>
              <option value="inactive">{t("users.status.inactive")}</option>
            </select>
            {errors.status && <p className="text-[11px] text-red-500 dark:text-red-400 mt-1 font-medium">{errors.status.message}</p>}
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-5 border-t border-surface-100 dark:border-surface-700/60">
          <button type="button" onClick={onClose} className="px-4 py-2.5 text-[13px] font-semibold text-surface-600 dark:text-surface-300 bg-white dark:bg-surface-800 border border-surface-200 dark:border-surface-700/60 rounded-xl hover:bg-surface-50 dark:hover:bg-surface-700 transition-all duration-150">
            {t("users.form.cancel")}
          </button>
          <button type="submit" disabled={loading} className="px-4 py-2.5 text-[13px] font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl hover:from-primary-700 hover:to-primary-800 disabled:opacity-50 transition-all duration-150 shadow-sm shadow-primary-600/20">
            {loading ? t("users.form.creating") : t("users.form.createBtn")}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function EditUserModal({ isOpen, onClose, editing, onSubmit, loading }) {
  const { t } = useTranslation();

  const editUserSchema = useMemo(() => z.object({
    full_name: z.string().min(1, t("users.validation.nameRequired")).max(100, t("users.validation.nameTooLong")),
    email: z.string().min(1, t("users.validation.emailRequired")).email(t("users.validation.emailInvalid")),
    phone: z.string().regex(/^\+?[0-9]{10,15}$/, t("users.validation.phoneInvalid")).optional().or(z.literal("")),
    role: z.enum(["admin", "manager", "employee"]),
    status: z.enum(["active", "inactive"]),
  }), [t]);

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
    <Modal isOpen={isOpen} onClose={onClose} title={t("users.form.editTitle")}>
      <form onSubmit={handleSubmit((data) => onSubmit(data))} className="space-y-5">
        {[
          { name: "full_name", label: t("users.form.fullName"), placeholder: t("users.form.fullNamePlaceholder") },
          { name: "email", label: t("users.form.email"), type: "email", placeholder: t("users.form.emailPlaceholder") },
          { name: "phone", label: t("users.form.phone"), type: "tel", placeholder: t("users.form.phonePlaceholder") },
        ].map(({ name, label, type = "text", placeholder }) => (
          <div key={name}>
            <label className={LABEL_CLASS}>{label}</label>
            <input type={type} {...register(name)} placeholder={placeholder} className={INPUT_CLASS} />
            {errors[name] && <p className="text-[11px] text-red-500 dark:text-red-400 mt-1 font-medium">{errors[name].message}</p>}
          </div>
        ))}

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className={LABEL_CLASS}>{t("users.form.role")}</label>
            <select {...register("role")} className={SELECT_CLASS}>
              <option value="employee">{t("users.roles.employee")}</option>
              <option value="manager">{t("users.roles.manager")}</option>
              <option value="admin">{t("users.roles.admin")}</option>
            </select>
            {errors.role && <p className="text-[11px] text-red-500 dark:text-red-400 mt-1 font-medium">{errors.role.message}</p>}
          </div>
          <div>
            <label className={LABEL_CLASS}>{t("users.form.status")}</label>
            <select {...register("status")} className={SELECT_CLASS}>
              <option value="active">{t("users.status.active")}</option>
              <option value="inactive">{t("users.status.inactive")}</option>
            </select>
            {errors.status && <p className="text-[11px] text-red-500 dark:text-red-400 mt-1 font-medium">{errors.status.message}</p>}
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-5 border-t border-surface-100 dark:border-surface-700/60">
          <button type="button" onClick={onClose} className="px-4 py-2.5 text-[13px] font-semibold text-surface-600 dark:text-surface-300 bg-white dark:bg-surface-800 border border-surface-200 dark:border-surface-700/60 rounded-xl hover:bg-surface-50 dark:hover:bg-surface-700 transition-all duration-150">
            {t("users.form.cancel")}
          </button>
          <button type="submit" disabled={loading} className="px-4 py-2.5 text-[13px] font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl hover:from-primary-700 hover:to-primary-800 disabled:opacity-50 transition-all duration-150 shadow-sm shadow-primary-600/20">
            {loading ? t("users.form.saving") : t("users.form.update")}
          </button>
        </div>
      </form>
    </Modal>
  );
}

function ResetPasswordModal({ isOpen, onClose, user, onSubmit, loading }) {
  const { t } = useTranslation();

  const resetPasswordSchema = useMemo(() => z.object({
    new_password: z.string().min(8, t("users.validation.passwordMin")),
  }), [t]);

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
    <Modal isOpen={isOpen} onClose={onClose} title={t("users.form.resetPasswordTitle", { name: user?.full_name || "" })}>
      <form
        onSubmit={handleSubmit((data) => {
          onSubmit(data.new_password);
          reset();
        })}
        className="space-y-5"
      >
        <div>
          <label className={LABEL_CLASS}>{t("users.form.newPassword")}</label>
          <input
            type="password"
            {...register("new_password")}
            className={INPUT_CLASS}
            placeholder={t("users.form.newPasswordPlaceholder")}
          />
          {errors.new_password && <p className="text-[11px] text-red-500 dark:text-red-400 mt-1 font-medium">{errors.new_password.message}</p>}
        </div>

        <div className="flex justify-end gap-3 pt-5 border-t border-surface-100 dark:border-surface-700/60">
          <button type="button" onClick={onClose} className="px-4 py-2.5 text-[13px] font-semibold text-surface-600 dark:text-surface-300 bg-white dark:bg-surface-800 border border-surface-200 dark:border-surface-700/60 rounded-xl hover:bg-surface-50 dark:hover:bg-surface-700 transition-all duration-150">
            {t("users.form.cancel")}
          </button>
          <button type="submit" disabled={loading} className="px-4 py-2.5 text-[13px] font-semibold text-white bg-gradient-to-r from-amber-500 to-amber-600 rounded-xl hover:from-amber-600 hover:to-amber-700 disabled:opacity-50 transition-all duration-150 shadow-sm shadow-amber-500/20">
            {loading ? t("users.form.resetting") : t("users.form.resetPassword")}
          </button>
        </div>
      </form>
    </Modal>
  );
}
