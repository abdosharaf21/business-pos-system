import {
  CreditCard,
  Package,
  BarChart3,
  ShoppingBag,
  FolderOpen,
  Boxes,
  ClipboardList,
  History,
  Wallet,
  Store,
  UserCog,
  Handshake,
  Contact2,
  BriefcaseBusiness,
  FolderTree,
  Link2,
  ArrowLeftRight,
  Warehouse as WarehouseIcon,
  CalendarClock,
  LayoutDashboard,
  ShoppingCart,
  LayoutGrid,
} from "lucide-react";

const QUICK_ACTIONS = {
  business: [
    { id: "clients", labelKey: "quickActions.clients", icon: Contact2, to: "/clients" },
    { id: "services", labelKey: "quickActions.services", icon: BriefcaseBusiness, to: "/business/services" },
    { id: "deals", labelKey: "quickActions.deals", icon: Handshake, to: "/deals" },
    { id: "reports", labelKey: "nav.reports", icon: BarChart3, to: "/business/reports" },
  ],
  pos: [
    { id: "new-sale", labelKey: "quickActions.newSale", icon: CreditCard, to: "/pos" },
    { id: "products", labelKey: "quickActions.products", icon: ShoppingBag, to: "/products" },
    { id: "customers", labelKey: "quickActions.customers", icon: Contact2, to: "/customers" },
  ],
  inventory: [
    { id: "stock", labelKey: "nav.stock", icon: Boxes, to: "/inventory" },
    { id: "audits", labelKey: "quickActions.audits", icon: ClipboardList, to: "/inventory/audits" },
    { id: "transfers", labelKey: "nav.transfers", icon: ArrowLeftRight, to: "/inventory/transfers" },
  ],
  expenses: [
    { id: "expenses", labelKey: "nav.expensesList", icon: Wallet, to: "/expenses" },
    { id: "categories", labelKey: "quickActions.categories", icon: FolderOpen, to: "/expenses/categories" },
    { id: "reports", labelKey: "nav.reports", icon: BarChart3, to: "/expenses/reports" },
  ],
};

export const MODULES = [
  { id: "business", labelKey: "nav.businessDevelopment", to: "/business", icon: Handshake },
  { id: "pos", labelKey: "nav.pos", to: "/pos", icon: CreditCard },
  { id: "inventory", labelKey: "nav.inventory", to: "/inventory/overview", icon: Package },
  { id: "expenses", labelKey: "nav.expenses", to: "/expenses/dashboard", icon: Wallet },
];

/**
 * Route opened when an application is launched from the Services
 * application catalog. Every target is the application's dashboard so the
 * active context switches through the single canonical URL mapping.
 */
export const APPLICATION_LAUNCH_ROUTES = {
  business: "/business",
  pos: "/dashboard",
  inventory: "/inventory/overview",
  expenses: "/expenses/dashboard",
};

const ADMIN_GROUP = {
  labelKey: "nav.administration",
  items: [
    { to: "/store-settings", labelKey: "nav.storeSettings", icon: Store },
    { to: "/users", labelKey: "nav.users", icon: UserCog },
  ],
};

export const MODULE_SIDEBARS = {
  business: [
    {
      labelKey: "nav.businessDevelopment",
      items: [
        { to: "/business", labelKey: "nav.businessHome", icon: Handshake },
        { to: "/services", labelKey: "nav.servicesCatalog", icon: LayoutGrid },
        { to: "/business/services", labelKey: "nav.serviceRecords", icon: BriefcaseBusiness },
        { to: "/clients", labelKey: "nav.clients", icon: Contact2 },
        { to: "/service-categories", labelKey: "nav.serviceCategories", icon: FolderTree },
        { to: "/client-services", labelKey: "nav.clientServices", icon: Link2 },
        { to: "/deals", labelKey: "nav.deals", icon: Handshake },
        { to: "/business/reports", labelKey: "nav.reports", icon: BarChart3 },
      ],
    },
  ],
  pos: [
    {
      labelKey: "nav.pos",
      items: [
        { to: "/dashboard", labelKey: "nav.dashboard", icon: LayoutDashboard },
        { to: "/pos", labelKey: "nav.newSale", icon: CreditCard },
        { to: "/products", labelKey: "nav.products", icon: ShoppingBag },
        { to: "/categories", labelKey: "nav.categories", icon: FolderOpen },
        { to: "/inventory", labelKey: "nav.stock", icon: Boxes },
        { to: "/purchases", labelKey: "nav.purchases", icon: ShoppingCart },
      ],
    },
  ],
  inventory: [
    {
      labelKey: "nav.inventory",
      items: [
        { to: "/inventory/overview", labelKey: "nav.dashboard", icon: LayoutDashboard },
        { to: "/inventory", labelKey: "nav.stock", icon: Boxes },
        { to: "/inventory/warehouses", labelKey: "nav.warehouses", icon: WarehouseIcon },
        { to: "/inventory/transfers", labelKey: "nav.transfers", icon: ArrowLeftRight },
        { to: "/inventory/audits", labelKey: "nav.inventoryAudits", icon: ClipboardList },
        { to: "/inventory/movements", labelKey: "nav.movementHistory", icon: History },
        { to: "/inventory/reorder", labelKey: "nav.reorder", icon: ShoppingCart },
        { to: "/inventory/expiration", labelKey: "nav.expiration", icon: CalendarClock },
        { to: "/inventory/reports", labelKey: "nav.reports", icon: BarChart3 },
      ],
    },
  ],
  expenses: [
    {
      labelKey: "nav.expenses",
      items: [
        { to: "/expenses/dashboard", labelKey: "nav.dashboard", icon: LayoutDashboard },
        { to: "/expenses", labelKey: "nav.expensesList", icon: Wallet },
        { to: "/expenses/categories", labelKey: "nav.expenseCategories", icon: FolderOpen },
        { to: "/expenses/reports", labelKey: "nav.reports", icon: BarChart3 },
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
  map.pos.push("/suppliers");
  map.pos.push("/customers");
  map.pos.push("/reports");
  return map;
})();

export const BACK_TARGET = { to: "/services", labelKey: "nav.backToServices" };
const BACK_ENABLED_MODULES = ["pos", "inventory", "expenses"];

export function getActiveModule(pathname) {
  if (pathname === "/store-settings" || pathname.startsWith("/store-settings/") || pathname === "/users") {
    return "admin";
  }
  const candidates = [];
  for (const [moduleId, paths] of Object.entries(MODULE_PATHS)) {
    for (const path of paths) {
      const exact = pathname === path;
      if (exact || pathname.startsWith(`${path}/`)) {
        candidates.push({ moduleId, score: (exact ? 100000 : 0) + path.length });
      }
    }
  }
  if (candidates.length === 0) return "business";

  const topScore = Math.max(...candidates.map((c) => c.score));
  const tied = candidates.filter((c) => c.score === topScore);
  if (tied.length === 1) return tied[0].moduleId;

  const homeRoute = (id) => MODULES.find((m) => m.id === id)?.to || "";
  let best = tied[0].moduleId;
  let bestShared = -1;
  for (const candidate of tied) {
    const home = homeRoute(candidate.moduleId);
    let shared = 0;
    while (shared < home.length && home[shared] === pathname[shared]) shared++;
    if (shared > bestShared) {
      bestShared = shared;
      best = candidate.moduleId;
    }
  }
  return best;
}

export function getContextBack(pathname) {
  const moduleId = getActiveModule(pathname);
  return BACK_ENABLED_MODULES.includes(moduleId) ? BACK_TARGET : null;
}

export function getVisibleModules(role) {
  return MODULES.filter((module) => !module.roles || module.roles.includes(role));
}

export function getVisibleSidebarGroups(moduleId, role) {
  const isAdmin = role === "admin";
  if (moduleId === "admin") {
    return isAdmin ? [{ ...ADMIN_GROUP }] : [];
  }
  const baseGroups = (MODULE_SIDEBARS[moduleId] || [])
    .map((group) => ({
      labelKey: group.labelKey,
      items: (group.items || []).filter((item) => !item.roles || item.roles.includes(role)),
    }))
    .filter((group) => group.items.length > 0);

  if (isAdmin) {
    return [...baseGroups, { ...ADMIN_GROUP }];
  }
  return baseGroups;
}

export function getQuickActions(moduleId, role) {
  const actions = QUICK_ACTIONS[moduleId] || [];
  return actions.filter((action) => !action.roles || action.roles.includes(role));
}

export function getBreadcrumb(pathname) {
  const moduleId = getActiveModule(pathname);
  const module = MODULES.find((m) => m.id === moduleId);
  const groups = MODULE_SIDEBARS[moduleId] || [];
  const findSection = (matcher) => {
    for (const group of groups) {
      for (const item of group.items) {
        if (matcher(item.to)) return item;
      }
    }
    return null;
  };
  let section = findSection((to) => pathname === to);
  if (!section) {
    section = findSection((to) => pathname.startsWith(`${to}/`));
  }
  if (!section && moduleId === "admin") {
    section = ADMIN_GROUP.items.find((item) =>
      pathname === item.to || pathname.startsWith(`${item.to}/`)
    );
  }
  return {
    moduleId,
    moduleLabelKey: section?.labelKey || module?.labelKey || "nav.businessHome",
    sectionLabelKey: section?.labelKey || module?.labelKey || "nav.businessHome",
  };
}
