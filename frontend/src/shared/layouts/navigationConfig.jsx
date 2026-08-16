import {
  LayoutDashboard,
  BarChart3,
  Settings,
  Wallet,
  UserCheck,
  HandCoins,
  CalendarCheck,
  ReceiptText,
  FolderOpen,
  Users,
  HardHat,
} from "lucide-react";

const MANAGE_ROLES = ["admin", "manager"];

export const STANDALONE_MODULES = [
  { id: "dashboard", labelKey: "nav.dashboard", to: "/dashboard", icon: LayoutDashboard },
  { id: "worker-management", labelKey: "services.workerManagement", to: "/worker-management", icon: HardHat },
  { id: "expenses", labelKey: "services.expenses", to: "/expenses", icon: Wallet },
  { id: "settings", labelKey: "nav.settings", to: "/store-settings", icon: Settings, roles: ["admin"] },
];

export const MODULE_SIDEBARS = {
  dashboard: [
    {
      labelKey: "nav.overview",
      items: [{ to: "/dashboard", labelKey: "nav.dashboardOverview", icon: LayoutDashboard }],
    },
  ],
  "worker-management": [
    {
      labelKey: "nav.overview",
      items: [
        { to: "/worker-management", labelKey: "nav.dashboard", icon: LayoutDashboard },
      ],
    },
    {
      labelKey: "nav.workforce",
      items: [
        { to: "/worker-management/workers", labelKey: "nav.workers", icon: UserCheck },
        { to: "/worker-management/attendance", labelKey: "nav.attendance", icon: CalendarCheck },
      ],
    },
    {
      labelKey: "nav.finance",
      items: [
        { to: "/worker-management/salaries", labelKey: "nav.salaries", icon: Wallet },
        { to: "/worker-management/advances", labelKey: "nav.advances", icon: HandCoins },
      ],
    },
    {
      labelKey: "nav.reports",
      items: [
        { to: "/worker-management/reports", labelKey: "nav.reports", icon: BarChart3 },
      ],
    },
  ],
  expenses: [
    {
      labelKey: "nav.expenses",
      items: [
        { to: "/expenses", labelKey: "nav.expenses", icon: ReceiptText },
        { to: "/expenses/categories", labelKey: "nav.expenseCategories", icon: FolderOpen },
      ],
    },
    {
      labelKey: "nav.reports",
      items: [
        { to: "/expenses/reports", labelKey: "nav.reports", icon: BarChart3 },
      ],
    },
  ],
  settings: [
    {
      labelKey: "nav.administration",
      items: [
        { to: "/store-settings", labelKey: "nav.storeSettings", icon: Settings, roles: ["admin"] },
        { to: "/users", labelKey: "nav.users", icon: Users, roles: ["admin"] },
      ],
    },
  ],
};

const MODULE_PATHS = {
  dashboard: ["/dashboard"],
  "worker-management": ["/worker-management", "/worker-management/workers", "/worker-management/attendance", "/worker-management/salaries", "/worker-management/advances", "/worker-management/reports"],
  expenses: ["/expenses", "/expenses/categories", "/expenses/reports"],
  settings: ["/store-settings", "/users"],
};

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
  return STANDALONE_MODULES.filter((module) => !module.roles || module.roles.includes(role));
}

function filterGroup(group, role) {
  return {
    labelKey: group.labelKey,
    items: (group.items || []).filter((item) => !item.roles || item.roles.includes(role)),
  };
}

export function getVisibleSidebarGroups(moduleId, role, _pathname) {
  const groups = MODULE_SIDEBARS[moduleId] || [];
  return groups.map((group) => filterGroup(group, role)).filter((group) => group.items.length > 0);
}

export function getBreadcrumb(pathname) {
  const moduleId = getActiveModule(pathname);
  const module = STANDALONE_MODULES.find((m) => m.id === moduleId);
  let sectionLabelKey = module?.labelKey || "nav.dashboard";

  const groups = MODULE_SIDEBARS[moduleId] || [];
  let section = null;
  let sectionLength = -1;
  for (const group of groups) {
    for (const item of group.items) {
      if (pathname === item.to || pathname.startsWith(`${item.to}/`)) {
        const len = item.to.length;
        if (len > sectionLength) {
          section = item;
          sectionLength = len;
        }
      }
    }
  }
  if (section) sectionLabelKey = section.labelKey;

  return {
    moduleId,
    moduleLabelKey: module?.labelKey || "nav.dashboard",
    sectionLabelKey,
  };
}

const QUICK_ACTIONS = {
  dashboard: [
    { id: "new-worker", labelKey: "quickActions.newWorker", icon: UserCheck, to: "/worker-management/workers", roles: MANAGE_ROLES },
    { id: "new-expense", labelKey: "quickActions.newExpense", icon: ReceiptText, to: "/expenses", roles: MANAGE_ROLES },
  ],
  "worker-management": [
    { id: "new-worker", labelKey: "quickActions.newWorker", icon: UserCheck, to: "/worker-management/workers", roles: MANAGE_ROLES },
    { id: "new-attendance", labelKey: "quickActions.newAttendance", icon: CalendarCheck, to: "/worker-management/attendance", roles: MANAGE_ROLES },
    { id: "new-expense", labelKey: "quickActions.newExpense", icon: ReceiptText, to: "/expenses", roles: MANAGE_ROLES },
  ],
  expenses: [
    { id: "new-expense", labelKey: "quickActions.newExpense", icon: ReceiptText, to: "/expenses", roles: MANAGE_ROLES },
    { id: "new-worker", labelKey: "quickActions.newWorker", icon: UserCheck, to: "/worker-management/workers", roles: MANAGE_ROLES },
  ],
};

export function getQuickActions(moduleId, role) {
  const actions = QUICK_ACTIONS[moduleId] || [];
  return actions.filter((action) => !action.roles || action.roles.includes(role));
}