import {
  LayoutDashboard,
  CreditCard,
  Package,
  ShoppingCart,
  BarChart3,
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
  Briefcase,
  Wrench,
  Users,
  Warehouse,
  ArrowLeftRight,
  Handshake,
} from "lucide-react";

const MANAGE_ROLES = ["admin", "manager"];

// ─── Global sidebar groups (always visible regardless of active app) ──────────
// These appear at the bottom of every application's sidebar.
const GLOBAL_SIDEBAR_GROUPS = [
  {
    labelKey: "nav.administration",
    items: [
      { to: "/store-settings", labelKey: "nav.storeSettings", icon: Store, roles: ["admin"] },
      { to: "/users", labelKey: "nav.users", icon: UserCog, roles: ["admin"] },
    ],
  },
];

// ─── Application definitions (3-level hierarchy) ─────────────────────────────
// Each application has: tabs (top-bar), sidebar (side-nav), paths, defaultPath
// Settings (Store Settings / Users) is NOT an app — it is global system
// functionality rendered via GLOBAL_SIDEBAR_GROUPS.  Its paths must not
// appear in any app's paths array so that getActiveApplication never
// switches context to a "settings" app.
export const APPS = [
  {
    id: "business",
    labelKey: "nav.businessDevelopment",
    icon: Briefcase,
    defaultPath: "/business/dashboard",
    tabs: [
      { id: "bd-dashboard", labelKey: "nav.dashboard", to: "/business/dashboard", icon: LayoutDashboard },
      { id: "bd-deals", labelKey: "nav.deals", to: "/business/deals", icon: Handshake },
      { id: "bd-applications", labelKey: "nav.applications", to: "/business/applications", icon: LayoutDashboard },
      { id: "bd-services", labelKey: "nav.services", to: "/business/services", icon: Wrench },
      { id: "bd-clients", labelKey: "nav.clients", to: "/business/clients", icon: Users },
      { id: "bd-reports", labelKey: "nav.reports", to: "/business/reports", icon: BarChart3 },
    ],
    sidebar: [
      {
        labelKey: "nav.businessDevelopment",
        items: [
          { to: "/business/dashboard", labelKey: "nav.dashboard", icon: LayoutDashboard },
          { to: "/business/deals", labelKey: "nav.deals", icon: Handshake },
          { to: "/business/applications", labelKey: "nav.applications", icon: LayoutDashboard },
          { to: "/business/services", labelKey: "nav.services", icon: Wrench },
          { to: "/business/clients", labelKey: "nav.clients", icon: Users },
          { to: "/business/reports", labelKey: "nav.reports", icon: BarChart3 },
        ],
      },
    ],
    paths: [
      "/business/dashboard", "/business/clients", "/business/applications", "/business/services",
      "/business/deals", "/business/reports", "/business/service-categories", "/business/client-services",
      "/clients", "/services", "/service-categories", "/client-services",
    ],
  },
  {
    id: "pos",
    labelKey: "nav.pos",
    icon: CreditCard,
    defaultPath: "/dashboard",
    tabs: [
      { id: "pos-dashboard", labelKey: "nav.dashboard", to: "/dashboard", icon: LayoutDashboard },
      { id: "pos-products", labelKey: "nav.products", to: "/products", icon: ShoppingBag },
      { id: "pos-categories", labelKey: "nav.categories", to: "/categories", icon: FolderOpen },
      { id: "pos-purchases", labelKey: "nav.purchases", to: "/purchases", icon: ShoppingCart },
    ],
    sidebar: [
      {
        labelKey: "nav.pos",
        items: [
          { to: "/dashboard", labelKey: "nav.dashboard", icon: LayoutDashboard },
          { to: "/pos", labelKey: "nav.newSale", icon: CreditCard },
          { to: "/products", labelKey: "nav.products", icon: ShoppingBag },
          { to: "/categories", labelKey: "nav.categories", icon: FolderOpen },
          { to: "/purchases", labelKey: "nav.purchases", icon: ShoppingCart },
          { to: "/customers", labelKey: "nav.customers", icon: Contact2 },
          { to: "/suppliers", labelKey: "nav.suppliers", icon: Truck },
        ],
      },
    ],
    paths: [
      "/dashboard", "/pos", "/pos/invoice",
      "/customers", "/products", "/categories",
      "/purchases", "/purchases/", "/suppliers",
    ],
  },
  {
    id: "inventory",
    labelKey: "nav.inventory",
    icon: Package,
    defaultPath: "/inventory",
    tabs: [
      { id: "inv-dashboard", labelKey: "nav.dashboard", to: "/inventory", icon: LayoutDashboard },
      { id: "inv-stock", labelKey: "nav.stock", to: "/inventory", icon: Boxes },
      { id: "inv-warehouses", labelKey: "nav.warehouses", to: "/warehouses", icon: Warehouse },
      { id: "inv-transfers", labelKey: "nav.transfers", to: "/transfers", icon: ArrowLeftRight },
      { id: "inv-audits", labelKey: "nav.inventoryAudits", to: "/inventory/audits", icon: ClipboardList },
      { id: "inv-history", labelKey: "nav.movementHistory", to: "/inventory/movements", icon: History },
    ],
    sidebar: [
      {
        labelKey: "nav.inventory",
        items: [
          { to: "/inventory", labelKey: "nav.dashboard", icon: LayoutDashboard },
          { to: "/inventory", labelKey: "nav.stock", icon: Boxes },
          { to: "/warehouses", labelKey: "nav.warehouses", icon: Warehouse },
          { to: "/transfers", labelKey: "nav.transfers", icon: ArrowLeftRight },
          { to: "/inventory/audits", labelKey: "nav.inventoryAudits", icon: ClipboardList },
          { to: "/inventory/movements", labelKey: "nav.movementHistory", icon: History },
        ],
      },
    ],
    paths: [
      "/inventory", "/inventory/movements", "/inventory/audits",
      "/warehouses", "/transfers",
    ],
  },
  {
    id: "expenses",
    labelKey: "nav.expenses",
    icon: Wallet,
    defaultPath: "/expenses",
    tabs: [
      { id: "exp-dashboard", labelKey: "nav.dashboard", to: "/expenses", icon: LayoutDashboard },
      { id: "exp-expenses", labelKey: "nav.expenses", to: "/expenses", icon: Wallet },
      { id: "exp-reports", labelKey: "nav.reports", to: "/reports", icon: BarChart3 },
    ],
    sidebar: [
      {
        labelKey: "nav.expenses",
        items: [
          { to: "/expenses", labelKey: "nav.dashboard", icon: LayoutDashboard },
          { to: "/expenses", labelKey: "nav.expenses", icon: Wallet },
          { to: "/reports", labelKey: "nav.reports", icon: BarChart3 },
        ],
      },
    ],
    paths: ["/expenses", "/reports"],
  },
];

// ─── Application switcher (for TopBar AppSwitcher) ──────────────────────────
// Derived from APPS so all apps are always available — no manual maintenance
export const APPLICATIONS = APPS.map((app) => ({
  id: app.id,
  labelKey: app.labelKey,
  icon: app.icon,
  defaultPath: app.defaultPath,
  roles: app.roles,
}));

// ─── Quick actions (per app) ──────────────────────────────────────────────────
const QUICK_ACTIONS = {
  business: [
    { id: "new-deal", labelKey: "quickActions.newDeal", icon: Handshake, to: "/business/deals" },
    { id: "new-client", labelKey: "quickActions.newClient", icon: Users, to: "/business/clients" },
    { id: "services", labelKey: "quickActions.services", icon: Wrench, to: "/business/services" },
    { id: "client-services", labelKey: "quickActions.clientServices", icon: Briefcase, to: "/business/client-services" },
  ],
  pos: [
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
  expenses: [],
};

// ─── Helper: get active application from pathname ─────────────────────────────
// Tracks the last-known app so that global paths (/store-settings, /users)
// never reset the context — the previous app's sidebar and tabs stay active.
let _lastKnownApp = "pos";

export function getActiveApplication(pathname) {
  let best = null;
  let bestLength = -1;
  for (const app of APPS) {
    for (const path of app.paths) {
      if (
        (pathname === path || pathname.startsWith(`${path}/`)) &&
        path.length > bestLength
      ) {
        best = app.id;
        bestLength = path.length;
      }
    }
  }
  if (best) {
    _lastKnownApp = best;
    return best;
  }
  return _lastKnownApp;
}

/**
 * Get the default path for an application.
 */
export function getApplicationDefaultPath(appId) {
  const app = APPS.find((a) => a.id === appId);
  return app?.defaultPath || "/business/dashboard";
}

/**
 * Get visible applications filtered by role.
 */
export function getVisibleApplications(role) {
  return APPS.filter((a) => !a.roles || a.roles.includes(role));
}

/**
 * Get tabs for the active application (used by TopNavigation).
 */
export function getAppTabs(appId, role) {
  const app = APPS.find((a) => a.id === appId);
  if (!app) return [];
  return app.tabs.filter((tab) => !tab.roles || tab.roles.includes(role));
}

/**
 * Get sidebar groups for the active application (used by Sidebar).
 */
export function getAppSidebarGroups(appId, role) {
  const app = APPS.find((a) => a.id === appId);
  const appGroups = app
    ? app.sidebar
        .map((group) => ({
          labelKey: group.labelKey,
          items: (group.items || []).filter((item) => !item.roles || item.roles.includes(role)),
        }))
        .filter((group) => group.items.length > 0)
    : [];

  const globalGroups = GLOBAL_SIDEBAR_GROUPS
    .map((group) => ({
      labelKey: group.labelKey,
      items: (group.items || []).filter((item) => !item.roles || item.roles.includes(role)),
    }))
    .filter((group) => group.items.length > 0);

  return [...appGroups, ...globalGroups];
}

/**
 * Get quick actions for the active application.
 */
export function getQuickActions(appId, role) {
  const actions = QUICK_ACTIONS[appId] || [];
  return actions.filter((action) => !action.roles || action.roles.includes(role));
}

/**
 * Get breadcrumb for the current pathname.
 */
export function getBreadcrumb(pathname) {
  const appId = getActiveApplication(pathname);
  const app = APPS.find((a) => a.id === appId);
  const groups = app?.sidebar || [];
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
    appId,
    appLabelKey: app?.labelKey || "nav.businessDevelopment",
    sectionLabelKey: section?.labelKey || app?.labelKey || "nav.dashboard",
  };
}

// ─── Back-button visibility ───────────────────────────────────────────────────
// The Back button only appears inside services/apps opened from the
// Business Development Services catalog (POS, Inventory, Expenses).
// It always returns the user to /business/services.
const SERVICE_APP_IDS = ["pos", "inventory", "expenses"];
const SERVICES_CATALOG_PATH = "/business/applications";
const SETTINGS_PATHS = ["/store-settings", "/users"];

/**
 * Get the back-route for the current pathname.
 * Returns "/business/services" when inside a service app, or null otherwise.
 * Returns null for global settings paths (they are not part of any service app).
 */
export function getBackRoute(pathname) {
  if (SETTINGS_PATHS.includes(pathname)) return null;
  const appId = getActiveApplication(pathname);
  return SERVICE_APP_IDS.includes(appId) ? SERVICES_CATALOG_PATH : null;
}

// ─── Legacy compatibility exports ─────────────────────────────────────────────
// These keep backward compatibility with any code that references the old API

/**
 * @deprecated Use getActiveApplication instead
 */
export function getActiveModule(pathname) {
  return getActiveApplication(pathname);
}

/**
 * @deprecated Use getAppTabs instead
 */
export function getVisibleModules(role) {
  return APPS.map((app) => ({
    id: app.id,
    labelKey: app.labelKey,
    to: app.defaultPath,
    icon: app.icon,
    roles: app.roles,
  })).filter((m) => !m.roles || m.roles.includes(role));
}

/**
 * @deprecated Use getAppSidebarGroups instead
 */
export function getVisibleSidebarGroups(appId, role) {
  return getAppSidebarGroups(appId, role);
}
