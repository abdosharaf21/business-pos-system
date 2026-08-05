import {
  LayoutDashboard,
  CreditCard,
  Package,
  ShoppingCart,
  BarChart3,
  Settings,
  ShoppingBag,
  FolderOpen,
  Boxes,
  ClipboardList,
  History,
  Contact2,
  Truck,
  Wallet,
  Store,
  UserCog,
  Plus,
  Printer,
  RefreshCw,
  Download,
  DatabaseBackup,
} from "lucide-react";

const MANAGE_ROLES = ["admin", "manager"];

const QUICK_ACTIONS = {
  dashboard: [
    { id: "new-sale", labelKey: "quickActions.newSale", icon: CreditCard, to: "/pos" },
    { id: "new-purchase", labelKey: "quickActions.newPurchase", icon: Plus, to: "/purchases?new=1", roles: MANAGE_ROLES },
    { id: "products", labelKey: "quickActions.products", icon: ShoppingBag, to: "/products" },
    { id: "customers", labelKey: "quickActions.customers", icon: Contact2, to: "/customers" },
  ],
  inventory: [
    { id: "products", labelKey: "quickActions.products", icon: ShoppingBag, to: "/products" },
    { id: "categories", labelKey: "quickActions.categories", icon: FolderOpen, to: "/categories" },
    { id: "audits", labelKey: "quickActions.audits", icon: ClipboardList, to: "/inventory/audits" },
  ],
  purchases: [
    { id: "new-purchase", labelKey: "quickActions.newPurchase", icon: Plus, to: "/purchases?new=1", roles: MANAGE_ROLES },
    { id: "suppliers", labelKey: "quickActions.suppliers", icon: Truck, to: "/suppliers" },
  ],
  reports: [
    { id: "print", labelKey: "quickActions.print", icon: Printer, kind: "print" },
    { id: "refresh", labelKey: "quickActions.refresh", icon: RefreshCw, kind: "refresh" },
    { id: "export", labelKey: "quickActions.export", icon: Download, kind: "disabled" },
  ],
  settings: [
    { id: "users", labelKey: "quickActions.users", icon: UserCog, to: "/users" },
    { id: "store-settings", labelKey: "quickActions.storeSettings", icon: Store, to: "/store-settings" },
    { id: "backup", labelKey: "quickActions.backup", icon: DatabaseBackup, kind: "disabled" },
  ],
  pos: [],
};

export const MODULES = [
  { id: "dashboard", labelKey: "nav.dashboard", to: "/dashboard", icon: LayoutDashboard },
  { id: "pos", labelKey: "nav.pos", to: "/pos", icon: CreditCard },
  { id: "inventory", labelKey: "nav.inventory", to: "/inventory", icon: Package },
  { id: "purchases", labelKey: "nav.purchases", to: "/purchases", icon: ShoppingCart },
  { id: "reports", labelKey: "nav.reports", to: "/reports", icon: BarChart3 },
  { id: "settings", labelKey: "nav.settings", to: "/store-settings", icon: Settings, roles: ["admin"] },
];

export const MODULE_SIDEBARS = {
  dashboard: [
    {
      labelKey: "nav.overview",
      items: [{ to: "/dashboard", labelKey: "nav.dashboardOverview", icon: LayoutDashboard }],
    },
  ],
  pos: [
    {
      labelKey: "nav.pos",
      items: [
        { to: "/pos", labelKey: "nav.newSale", icon: CreditCard },
        { to: "/customers", labelKey: "nav.customers", icon: Contact2 },
      ],
    },
  ],
  inventory: [
    {
      labelKey: "nav.inventory",
      items: [
        { to: "/products", labelKey: "nav.products", icon: ShoppingBag },
        { to: "/categories", labelKey: "nav.categories", icon: FolderOpen },
        { to: "/inventory", labelKey: "nav.stock", icon: Boxes },
        { to: "/inventory/audits", labelKey: "nav.inventoryAudits", icon: ClipboardList },
        { to: "/inventory/movements", labelKey: "nav.movementHistory", icon: History },
      ],
    },
  ],
  purchases: [
    {
      labelKey: "nav.purchases",
      items: [
        { to: "/purchases", labelKey: "nav.purchases", icon: ShoppingCart },
        { to: "/suppliers", labelKey: "nav.suppliers", icon: Truck },
      ],
    },
  ],
  reports: [
    {
      labelKey: "nav.reports",
      items: [
        { to: "/reports", labelKey: "nav.overview", icon: BarChart3 },
        { to: "/expenses", labelKey: "nav.expenses", icon: Wallet },
      ],
    },
  ],
  settings: [
    {
      labelKey: "nav.administration",
      items: [
        { to: "/store-settings", labelKey: "nav.storeSettings", icon: Store, roles: ["admin"] },
        { to: "/users", labelKey: "nav.users", icon: UserCog, roles: ["admin"] },
      ],
    },
  ],
};

const MODULE_PATHS = (() => {
  const map = {};
  for (const module of MODULES) {
    map[module.id] = [module.to];
  }
  for (const [moduleId, groups] of Object.entries(MODULE_SIDEBARS)) {
    for (const group of groups) {
      for (const item of group.items) {
        if (!map[moduleId].includes(item.to)) {
          map[moduleId].push(item.to);
        }
      }
    }
  }
  return map;
})();

export function getActiveModule(pathname) {
  let best = "dashboard";
  let bestLength = -1;
  for (const [moduleId, paths] of Object.entries(MODULE_PATHS)) {
    for (const path of paths) {
      if (
        (pathname === path || pathname.startsWith(`${path}/`)) &&
        path.length > bestLength
      ) {
        best = moduleId;
        bestLength = path.length;
      }
    }
  }
  return best;
}

export function getVisibleModules(role) {
  return MODULES.filter((module) => !module.roles || module.roles.includes(role));
}

export function getVisibleSidebarGroups(moduleId, role) {
  const groups = MODULE_SIDEBARS[moduleId] || [];
  return groups
    .map((group) => ({
      labelKey: group.labelKey,
      items: (group.items || []).filter((item) => !item.roles || item.roles.includes(role)),
    }))
    .filter((group) => group.items.length > 0);
}

export function getQuickActions(moduleId, role) {
  const actions = QUICK_ACTIONS[moduleId] || [];
  return actions.filter((action) => !action.roles || action.roles.includes(role));
}

export function getBreadcrumb(pathname) {
  const moduleId = getActiveModule(pathname);
  const module = MODULES.find((m) => m.id === moduleId);
  const groups = MODULE_SIDEBARS[moduleId] || [];
  let section = null;
  for (const group of groups) {
    for (const item of group.items) {
      if (pathname === item.to || pathname.startsWith(`${item.to}/`)) {
        section = item;
        break;
      }
    }
    if (section) break;
  }
  return {
    moduleId,
    moduleLabelKey: module?.labelKey || "nav.dashboard",
    sectionLabelKey: section?.labelKey || module?.labelKey || "nav.dashboard",
  };
}
