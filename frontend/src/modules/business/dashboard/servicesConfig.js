import {
  CreditCard,
  Package,
  Wallet,
  Briefcase,
  Users,
} from "lucide-react";

/**
 * Centralized service/application metadata for the Business Development
 * Service Hub dashboard.
 *
 * This is the single source of truth for all services, features, and
 * package/edition definitions shown in the dashboard.
 *
 * When backend endpoints for services and packages become available,
 * replace this static config with API data.
 */

export const SERVICES = [
  {
    id: "pos",
    nameKey: "bdDashboard.services.pos.name",
    nameFallback: "POS System",
    descriptionKey: "bdDashboard.services.pos.description",
    descriptionFallback: "Core point-of-sale system for daily sales operations",
    icon: CreditCard,
    color: "blue",
    status: "active",
    features: [
      { nameKey: "bdDashboard.services.pos.features.sales", nameFallback: "Sales" },
      { nameKey: "bdDashboard.services.pos.features.products", nameFallback: "Products" },
      { nameKey: "bdDashboard.services.pos.features.basicInventory", nameFallback: "Basic Inventory" },
      { nameKey: "bdDashboard.services.pos.features.purchases", nameFallback: "Purchases" },
      { nameKey: "bdDashboard.services.pos.features.basicReports", nameFallback: "Basic Reports" },
    ],
    route: "/pos",
    packageIds: ["basic-pos", "pos-pro", "business-suite"],
  },
  {
    id: "inventory",
    nameKey: "bdDashboard.services.inventory.name",
    nameFallback: "Advanced Inventory",
    descriptionKey: "bdDashboard.services.inventory.description",
    descriptionFallback: "Advanced inventory management with warehouses, audits, and reorder",
    icon: Package,
    color: "green",
    status: "active",
    features: [
      { nameKey: "bdDashboard.services.inventory.features.warehouses", nameFallback: "Warehouses" },
      { nameKey: "bdDashboard.services.inventory.features.transfers", nameFallback: "Transfers" },
      { nameKey: "bdDashboard.services.inventory.features.audits", nameFallback: "Audits" },
      { nameKey: "bdDashboard.services.inventory.features.reorder", nameFallback: "Reorder" },
      { nameKey: "bdDashboard.services.inventory.features.expiration", nameFallback: "Expiration" },
      { nameKey: "bdDashboard.services.inventory.features.advancedReports", nameFallback: "Advanced Reports" },
    ],
    route: "/inventory",
    packageIds: ["pos-pro", "business-suite"],
  },
  {
    id: "expenses",
    nameKey: "bdDashboard.services.expenses.name",
    nameFallback: "Expenses",
    descriptionKey: "bdDashboard.services.expenses.description",
    descriptionFallback: "Expense tracking and reporting",
    icon: Wallet,
    color: "orange",
    status: "active",
    features: [
      { nameKey: "bdDashboard.services.expenses.features.expenses", nameFallback: "Expenses" },
      { nameKey: "bdDashboard.services.expenses.features.categories", nameFallback: "Categories" },
      { nameKey: "bdDashboard.services.expenses.features.reports", nameFallback: "Reports" },
    ],
    route: "/expenses",
    packageIds: ["business-suite"],
  },
  {
    id: "business",
    nameKey: "bdDashboard.services.business.name",
    nameFallback: "Business Development",
    descriptionKey: "bdDashboard.services.business.description",
    descriptionFallback: "Manage clients, services, and client-service relationships",
    icon: Briefcase,
    color: "purple",
    status: "active",
    features: [
      { nameKey: "bdDashboard.services.business.features.clients", nameFallback: "Clients" },
      { nameKey: "bdDashboard.services.business.features.services", nameFallback: "Services" },
      { nameKey: "bdDashboard.services.business.features.serviceCategories", nameFallback: "Service Categories" },
      { nameKey: "bdDashboard.services.business.features.clientServices", nameFallback: "Client Services" },
    ],
    route: "/business/dashboard",
    packageIds: ["business-suite"],
  },
  {
    id: "worker-management",
    nameKey: "bdDashboard.services.workerManagement.name",
    nameFallback: "Worker Management",
    descriptionKey: "bdDashboard.services.workerManagement.description",
    descriptionFallback: "Employee and workforce management — separate standalone application",
    icon: Users,
    color: "default",
    status: "external",
    features: [],
    route: null,
    packageIds: [],
  },
];

export const PACKAGES = [
  {
    id: "basic-pos",
    nameKey: "bdDashboard.packages.basicPos.name",
    nameFallback: "Basic POS",
    descriptionKey: "bdDashboard.packages.basicPos.description",
    descriptionFallback: "Essential point-of-sale features for small businesses",
    serviceIds: ["pos"],
    color: "blue",
  },
  {
    id: "pos-pro",
    nameKey: "bdDashboard.packages.posPro.name",
    nameFallback: "POS Pro",
    descriptionKey: "bdDashboard.packages.posPro.description",
    descriptionFallback: "Full POS with advanced inventory management",
    serviceIds: ["pos", "inventory"],
    color: "purple",
  },
  {
    id: "business-suite",
    nameKey: "bdDashboard.packages.businessSuite.name",
    nameFallback: "Business Suite",
    descriptionKey: "bdDashboard.packages.businessSuite.description",
    descriptionFallback: "Complete business management suite with all services",
    serviceIds: ["pos", "inventory", "expenses", "business"],
    color: "green",
  },
];

export const SERVICE_HUB_STATS = (() => {
  const internal = SERVICES.filter((s) => s.status !== "external");
  const active = SERVICES.filter((s) => s.status === "active");
  const totalFeatures = SERVICES.reduce((sum, s) => sum + s.features.length, 0);

  return {
    totalServices: internal.length,
    activeServices: active.length,
    totalPackages: PACKAGES.length,
    totalFeatures,
  };
})();
