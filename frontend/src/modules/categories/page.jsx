import { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { categoryService } from "./api";
import { flattenCategoryTree } from "./tree";
import { useAuth } from "../../shared/context/AuthContext";
import { useTranslation } from "react-i18next";
import { PageHeader } from "../../shared/components/PageHeader";
import { Modal } from "../../shared/components/Modal";
import { ConfirmDialog } from "../../shared/components/ConfirmDialog";
import { LoadingSpinner } from "../../shared/components/LoadingSpinner";
import { ErrorDisplay } from "../../shared/components/ErrorDisplay";
import { EmptyState } from "../../shared/components/EmptyState";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Plus, Pencil, Trash2, Search, FolderOpen, ChevronDown, ChevronRight, FolderTree } from "lucide-react";
import toast from "react-hot-toast";

const INPUT_CLASS = "w-full px-3.5 py-2.5 border border-surface-200 bg-surface-50 rounded-xl text-sm text-surface-800 placeholder:text-surface-300 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150";
const LABEL_CLASS = "block text-[13px] font-semibold text-surface-700 mb-1.5";
const SELECT_CLASS = "w-full px-3.5 py-2.5 border border-surface-200 bg-surface-50 rounded-xl text-sm text-surface-800 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150 appearance-none cursor-pointer";

function filterTree(nodes, term) {
  const t = term.trim().toLowerCase();
  if (!t) return nodes;
  const result = [];
  nodes.forEach((n) => {
    const selfMatch = (n.name || "").toLowerCase().includes(t) ||
      (n.description || "").toLowerCase().includes(t);
    const children = filterTree(n.children || [], term);
    if (selfMatch || children.length > 0) {
      result.push({ ...n, children: selfMatch ? n.children : children });
    }
  });
  return result;
}

function collectSubtreeIds(nodes, id) {
  for (const n of nodes) {
    if (n.id === id) {
      const ids = new Set([id]);
      const stack = [...(n.children || [])];
      while (stack.length) {
        const cur = stack.pop();
        ids.add(cur.id);
        stack.push(...(cur.children || []));
      }
      return ids;
    }
    const found = collectSubtreeIds(n.children || [], id);
    if (found) return found;
  }
  return null;
}

export default function CategoriesPage() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const canManage = ["admin", "manager"].includes(user?.role);
  const [search, setSearch] = useState("");
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [defaultParentId, setDefaultParentId] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [collapsed, setCollapsed] = useState(() => new Set());

  const { data: categories = [], isLoading, error, refetch } = useQuery({
    queryKey: ["category-tree"],
    queryFn: async () => {
      const res = await categoryService.getTree();
      return res.data.data;
    },
  });

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["category-tree"] });
    queryClient.invalidateQueries({ queryKey: ["categories"] });
  };

  const createMutation = useMutation({
    mutationFn: (data) => categoryService.create(data),
    onSuccess: () => { invalidate(); toast.success(t("categories.toast.created")); setModalOpen(false); },
    onError: (err) => toast.error(err.response?.data?.message || t("categories.toast.createFailed")),
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => categoryService.update(id, data),
    onSuccess: () => { invalidate(); toast.success(t("categories.toast.updated")); setModalOpen(false); setEditing(null); },
    onError: (err) => toast.error(err.response?.data?.message || t("categories.toast.updateFailed")),
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => categoryService.delete(id),
    onSuccess: () => { invalidate(); toast.success(t("categories.toast.deleted")); setDeleteTarget(null); },
    onError: (err) => toast.error(err.response?.data?.message || t("categories.toast.deleteFailed")),
  });

  const parentOptions = useMemo(() => flattenCategoryTree(categories), [categories]);
  const disabledParentIds = useMemo(() => {
    if (!editing) return null;
    return collectSubtreeIds(categories, editing.id);
  }, [categories, editing]);

  const openCreate = (parentId = null) => {
    setEditing(null);
    setDefaultParentId(parentId);
    setModalOpen(true);
  };

  const openEdit = (category) => {
    setEditing(category);
    setDefaultParentId(null);
    setModalOpen(true);
  };

  const visibleTree = useMemo(() => filterTree(categories, search), [categories, search]);
  const toggleCollapsed = (id) => {
    setCollapsed((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorDisplay message={error.response?.data?.message || error.message} onRetry={refetch} />;

  return (
    <div>
      <PageHeader
        title={t("categories.title")}
        description={t("categories.description")}
        actions={
          canManage && (
            <button onClick={() => openCreate()} className="flex items-center gap-2 px-4 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white text-[13px] font-semibold rounded-xl hover:from-primary-700 hover:to-primary-800 transition-all duration-150 shadow-sm shadow-primary-600/20">
              <Plus className="w-4 h-4" />
              {t("categories.newCategory")}
            </button>
          )
        }
      />

      <div className="mb-6 relative">
        <Search className="w-4 h-4 absolute start-3.5 top-1/2 -translate-y-1/2 text-surface-400 pointer-events-none" />
        <input type="text" placeholder={t("categories.searchPlaceholder")} value={search} onChange={(e) => setSearch(e.target.value)} className="w-full ps-10 pe-4 py-2.5 border border-surface-200 bg-white rounded-xl text-sm text-surface-800 placeholder:text-surface-300 focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-500 transition-all duration-150 shadow-card" aria-label={t("categories.searchAriaLabel")} />
      </div>

      {categories.length === 0 ? (
        <EmptyState icon={FolderTree} title={t("categories.empty.noCategoriesDescription")} description={t("categories.empty.noSubcategoriesDescription")} action={canManage && <button onClick={() => openCreate()} className="px-4 py-2.5 bg-gradient-to-r from-primary-600 to-primary-700 text-white text-[13px] font-semibold rounded-xl hover:from-primary-700 hover:to-primary-800 shadow-sm shadow-primary-600/20">{t("categories.empty.addCategory")}</button>} />
      ) : visibleTree.length === 0 ? (
        <EmptyState icon={FolderOpen} title={t("categories.empty.noResultsTitle")} description={t("categories.empty.noResultsDescription")} />
      ) : (
        <div className="bg-white rounded-2xl border border-surface-200 shadow-card p-3">
          {visibleTree.map((node) => (
            <CategoryNode
              key={node.id}
              node={node}
              depth={0}
              collapsed={collapsed}
              onToggle={toggleCollapsed}
              onEdit={openEdit}
              onDelete={setDeleteTarget}
              onAddChild={(p) => openCreate(p.id)}
              canManage={canManage}
            />
          ))}
        </div>
      )}

      <CategoryModal
        isOpen={modalOpen}
        onClose={() => { setModalOpen(false); setEditing(null); setDefaultParentId(null); }}
        editing={editing}
        parentOptions={parentOptions}
        disabledParentIds={disabledParentIds}
        defaultParentId={defaultParentId}
        onSubmit={(data) => editing ? updateMutation.mutate({ id: editing.id, data }) : createMutation.mutate(data)}
        loading={createMutation.isPending || updateMutation.isPending}
      />

      <ConfirmDialog isOpen={!!deleteTarget} onClose={() => setDeleteTarget(null)} onConfirm={() => deleteMutation.mutate(deleteTarget.id)} title={t("categories.confirmDelete.title")} message={t("categories.confirmDelete.message", { name: deleteTarget?.name })} loading={deleteMutation.isPending} />
    </div>
  );
}

function CategoryNode({ node, depth, collapsed, onToggle, onEdit, onDelete, onAddChild, canManage }) {
  const { t } = useTranslation();
  const hasChildren = node.children && node.children.length > 0;
  const isCollapsed = collapsed.has(node.id);

  return (
    <div>
      <div className="flex items-center gap-1.5 rounded-xl px-2 py-2 hover:bg-surface-50 transition-colors duration-150" style={{ paddingInlineStart: 8 + depth * 22 }}>
        <button
          onClick={() => hasChildren && onToggle(node.id)}
          disabled={!hasChildren}
          className={`w-6 h-6 flex items-center justify-center rounded-lg transition-all duration-150 ${hasChildren ? "text-surface-500 hover:bg-surface-100 cursor-pointer" : "cursor-default"}`}
          title={hasChildren ? t("categories.toggle") : ""}
        >
          {hasChildren ? (isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />) : null}
        </button>
        <FolderOpen className="w-4 h-4 text-amber-500 flex-shrink-0" />
        <span className="text-[13px] font-semibold text-surface-800 truncate">{node.name}</span>
        {node.description && (
          <span className="text-xs text-surface-400 truncate hidden sm:inline">{node.description}</span>
        )}
        {hasChildren && (
          <span className="text-[10px] font-semibold text-surface-400 bg-surface-100 rounded-full px-2 py-0.5">
            {node.children.length}
          </span>
        )}
        {canManage && (
          <div className="ms-auto flex items-center gap-1">
            <button onClick={() => onAddChild(node)} className="p-1.5 text-surface-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-all duration-150" title={t("categories.addSubcategory")}>
              <Plus className="w-4 h-4" />
            </button>
            <button onClick={() => onEdit(node)} className="p-1.5 text-surface-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-all duration-150" title={t("categories.edit")}>
              <Pencil className="w-4 h-4" />
            </button>
            <button onClick={() => onDelete(node)} className="p-1.5 text-surface-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all duration-150" title={t("categories.delete")}>
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
      {hasChildren && !isCollapsed && (
        <div>
          {node.children.map((child) => (
            <CategoryNode
              key={child.id}
              node={child}
              depth={depth + 1}
              collapsed={collapsed}
              onToggle={onToggle}
              onEdit={onEdit}
              onDelete={onDelete}
              onAddChild={onAddChild}
              canManage={canManage}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function CategoryModal({ isOpen, onClose, editing, parentOptions, disabledParentIds, defaultParentId, onSubmit, loading }) {
  const { t } = useTranslation();

  const categorySchema = useMemo(() => z.object({
    name: z.string().min(1, t("categories.validation.nameRequired")),
    description: z.string().optional(),
    parent_id: z.string().optional(),
  }), [t]);

  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: zodResolver(categorySchema),
    values: editing
      ? { name: editing.name, description: editing.description || "", parent_id: editing.parent_id ? String(editing.parent_id) : "" }
      : { name: "", description: "", parent_id: defaultParentId ? String(defaultParentId) : "" },
  });

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={editing ? t("categories.form.titleEdit") : t("categories.form.titleCreate")}>
      <form onSubmit={handleSubmit((data) => { onSubmit({ ...data, parent_id: data.parent_id ? Number(data.parent_id) : null }); reset(); })} className="space-y-5">
        <div>
          <label className={LABEL_CLASS}>{t("categories.form.parent")}</label>
          <select {...register("parent_id")} className={SELECT_CLASS}>
            <option value="">{t("categories.form.parentPlaceholder")}</option>
            {parentOptions.map((opt) => (
              <option key={opt.id} value={opt.id} disabled={disabledParentIds?.has(opt.id)}>
                {"\u00A0\u00A0".repeat(opt.depth)}{opt.name}
              </option>
            ))}
          </select>
          {errors.parent_id && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.parent_id.message}</p>}
        </div>
        <div>
          <label className={LABEL_CLASS}>{t("categories.form.name")}</label>
          <input {...register("name")} placeholder={t("categories.form.namePlaceholder")} className={INPUT_CLASS} />
          {errors.name && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.name.message}</p>}
        </div>
        <div>
          <label className={LABEL_CLASS}>{t("categories.form.description")}</label>
          <textarea {...register("description")} rows={3} placeholder={t("categories.form.descriptionPlaceholder")} className={`${INPUT_CLASS} resize-none`} />
          {errors.description && <p className="text-[11px] text-red-500 mt-1 font-medium">{errors.description.message}</p>}
        </div>
        <div className="flex justify-end gap-3 pt-5 border-t border-surface-100">
          <button type="button" onClick={onClose} className="px-4 py-2.5 text-[13px] font-semibold text-surface-600 bg-white border border-surface-200 rounded-xl hover:bg-surface-50 transition-all duration-150">{t("categories.form.cancel")}</button>
          <button type="submit" disabled={loading} className="px-4 py-2.5 text-[13px] font-semibold text-white bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl hover:from-primary-700 hover:to-primary-800 disabled:opacity-50 transition-all duration-150 shadow-sm shadow-primary-600/20">{loading ? t("categories.form.saving") : editing ? t("categories.form.update") : t("categories.form.create")}</button>
        </div>
      </form>
    </Modal>
  );
}
