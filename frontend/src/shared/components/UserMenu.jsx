import { useState, useRef, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { ChevronDown, LogOut } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function UserMenu() {
  const { user, logout } = useAuth();
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const menuRef = useRef(null);

  const initials = user?.full_name
    ? user.full_name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    : "?";

  useEffect(() => {
    if (!open) return;
    const handlePointerDown = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setOpen(false);
      }
    };
    const handleKeyDown = (e) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", handlePointerDown);
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("mousedown", handlePointerDown);
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [open]);

  const handleLogout = async () => {
    await logout();
  };

  if (!user) return null;

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setOpen((prev) => !prev)}
        className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-surface-100 transition-colors"
        aria-haspopup="menu"
        aria-expanded={open}
        aria-label={user.full_name}
      >
        <span className="w-8 h-8 rounded-full bg-primary-700 flex items-center justify-center text-[10px] font-bold text-white shrink-0">
          {initials}
        </span>
        <span className="hidden xl:block text-start min-w-0">
          <span className="block text-[13px] font-semibold text-surface-800 leading-tight truncate max-w-[140px]">
            {user.full_name}
          </span>
          <span className="block text-[11px] text-surface-400 leading-tight">
            {t(`common.roles.${user.role}`)}
          </span>
        </span>
        <ChevronDown className="hidden xl:block w-3.5 h-3.5 text-surface-400" />
      </button>

      {open && (
        <div
          className="absolute end-0 top-full mt-2 w-64 rounded-xl bg-white border border-surface-200 shadow-xl shadow-surface-900/10 overflow-hidden z-50 dark:bg-surface-900 dark:border-surface-800 animate-in-fast"
          role="menu"
        >
          <div className="px-4 py-3.5 border-b border-surface-100 dark:border-surface-800">
            <div className="flex items-center gap-3">
              <span className="w-10 h-10 rounded-full bg-primary-700 flex items-center justify-center text-xs font-bold text-white shrink-0">
                {initials}
              </span>
              <div className="min-w-0">
                <p className="text-sm font-bold text-surface-900 truncate dark:text-surface-100">{user.full_name}</p>
                <p className="text-xs text-surface-400 truncate">{user.email}</p>
              </div>
            </div>
            {user.role && (
              <span className="inline-flex mt-3 items-center px-2.5 py-1 rounded-full bg-surface-100 text-surface-500 text-[10px] font-semibold uppercase tracking-wider capitalize">
                {t(`common.roles.${user.role}`)}
              </span>
            )}
          </div>
          <div className="p-1.5">
            <button
              onClick={handleLogout}
              className="flex items-center gap-2.5 w-full px-3 py-2.5 rounded-lg text-[13px] font-medium text-surface-600 hover:bg-red-50 hover:text-red-600 transition-all duration-150"
              role="menuitem"
            >
              <LogOut className="w-4 h-4" />
              {t("common.signOut")}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
