import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {
  LayoutDashboard,
  BarChart3,
  Users,
  Briefcase,
  FolderOpen,
  Package,
  Link2,
  UserCog,
  LogOut,
  X,
  Building2,
  ShoppingBag,
  Contact2,
  ShoppingCart,
  CreditCard,
} from "lucide-react";

const navGroups = [
  {
    label: "Overview",
    items: [{ to: "/dashboard", label: "Dashboard", icon: LayoutDashboard }],
  },
  {
    label: "Management",
    items: [
      { to: "/pos", label: "POS", icon: CreditCard },
      { to: "/reports", label: "Reports", icon: BarChart3 },
      { to: "/clients", label: "Clients", icon: Users },
      { to: "/services", label: "Services", icon: Briefcase },
      { to: "/products", label: "Products", icon: ShoppingBag },
      { to: "/customers", label: "Customers", icon: Contact2 },
      { to: "/purchases", label: "Purchases", icon: ShoppingCart },
      { to: "/categories", label: "Categories", icon: FolderOpen },
      { to: "/inventory", label: "Inventory", icon: Package },
      { to: "/client-services", label: "Client Services", icon: Link2 },
    ],
  },
  {
    label: "Administration",
    items: [{ to: "/users", label: "Users", icon: UserCog, roles: ["admin"] }],
  },
];

export default function Sidebar({ isOpen, onClose }) {
  const { logout, user } = useAuth();

  const handleLogout = async () => {
    await logout();
  };

  const initials = user?.full_name
    ? user.full_name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    : "?";

  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-surface-900/40 backdrop-blur-sm transition-opacity lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={`fixed top-0 left-0 z-50 h-full w-64 bg-white border-r border-surface-200/80 flex flex-col transition-transform duration-300 ease-out
          lg:translate-x-0 ${isOpen ? "translate-x-0" : "-translate-x-full"}`}
        role="navigation"
        aria-label="Main navigation"
      >
        {/* Brand */}
        <div className="flex items-center justify-between px-5 py-5 border-b border-surface-100">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-gradient-to-br from-primary-500 to-primary-700 rounded-xl flex items-center justify-center shadow-sm shadow-primary-500/25">
              <Building2 className="w-5 h-5 text-white" strokeWidth={2.2} />
            </div>
            <div>
              <span className="text-[15px] font-bold text-surface-900 tracking-tight">BizDev</span>
              <p className="text-[10px] text-surface-400 font-medium -mt-0.5 tracking-wide uppercase">Management</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="lg:hidden text-surface-400 hover:text-surface-600 p-1.5 rounded-lg hover:bg-surface-100 transition-colors"
            aria-label="Close sidebar"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-5 overflow-y-auto scrollbar-thin" aria-label="Sidebar navigation">
          {navGroups.map((group) => {
            const visibleItems = group.items.filter(
              (item) => !item.roles || item.roles.includes(user?.role)
            );
            if (visibleItems.length === 0) return null;
            return (
              <div key={group.label}>
                <p className="px-3 mb-2 text-[10px] font-semibold text-surface-400 uppercase tracking-wider">
                  {group.label}
                </p>
                <div className="space-y-0.5">
                  {visibleItems.map(({ to, label, icon: Icon }) => (
                  <NavLink
                    key={to}
                    to={to}
                    onClick={onClose}
                    className={({ isActive }) =>
                      `relative flex items-center gap-3 px-3 py-2.5 rounded-xl text-[13px] font-medium transition-all duration-150
                      ${
                        isActive
                          ? "bg-primary-50 text-primary-700 shadow-sm shadow-primary-500/5"
                          : "text-surface-500 hover:bg-surface-50 hover:text-surface-800"
                      }`
                    }
                  >
                    {({ isActive }) => (
                      <>
                        {isActive && (
                          <span className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 bg-primary-600 rounded-r-full" />
                        )}
                        <Icon
                          className={`w-[18px] h-[18px] shrink-0 ${
                            isActive ? "text-primary-600" : "text-surface-400"
                          }`}
                          strokeWidth={isActive ? 2.2 : 1.8}
                        />
                        {label}
                      </>
                    )}
                  </NavLink>
                ))}
              </div>
            </div>
          );
          })}
        </nav>

        {/* User Profile + Logout */}
        <div className="px-3 py-4 border-t border-surface-100">
          {user && (
            <div className="flex items-center gap-3 px-3 mb-3">
              <div className="w-9 h-9 rounded-full bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-xs font-bold text-white shrink-0 shadow-sm shadow-primary-500/20">
                {initials}
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-[13px] font-semibold text-surface-800 truncate">{user.full_name}</p>
                <p className="text-[11px] text-surface-400 truncate">{user.email}</p>
              </div>
            </div>
          )}
          {user?.role && (
            <div className="px-3 mb-3">
              <span className="inline-flex items-center text-[10px] font-semibold px-2.5 py-1 rounded-full bg-surface-100 text-surface-500 uppercase tracking-wider capitalize">
                {user.role}
              </span>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-[13px] font-medium text-surface-500 hover:bg-red-50 hover:text-red-600 transition-all duration-150"
            aria-label="Sign out"
          >
            <LogOut className="w-[18px] h-[18px]" strokeWidth={1.8} />
            Sign out
          </button>
        </div>
      </aside>
    </>
  );
}
