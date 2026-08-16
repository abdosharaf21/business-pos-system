import { describe, it, expect } from "vitest";
import {
  STANDALONE_MODULES,
  getActiveModule,
  getVisibleModules,
  getVisibleSidebarGroups,
  getQuickActions,
  getBreadcrumb,
} from "../shared/layouts/navigationConfig";

describe("navigationConfig (standalone)", () => {
  it("derives the active module for every standalone route", () => {
    const cases = [
      ["/dashboard", "dashboard"],
      ["/worker-management", "worker-management"],
      ["/worker-management/workers", "worker-management"],
      ["/worker-management/attendance", "worker-management"],
      ["/worker-management/salaries", "worker-management"],
      ["/worker-management/advances", "worker-management"],
      ["/worker-management/reports", "worker-management"],
      ["/expenses", "expenses"],
      ["/expenses/categories", "expenses"],
      ["/expenses/reports", "expenses"],
      ["/store-settings", "settings"],
      ["/users", "settings"],
    ];
    cases.forEach(([path, moduleId]) => {
      expect(getActiveModule(path)).toBe(moduleId);
    });
  });

  it("exposes the standalone modules with their destinations", () => {
    const destinations = STANDALONE_MODULES.map((s) => s.to);
    expect(destinations).toContain("/dashboard");
    expect(destinations).toContain("/worker-management");
    expect(destinations).toContain("/expenses");
    expect(destinations).toContain("/store-settings");
  });

  it("hides the Settings module and its items from non-admin roles", () => {
    const adminModules = getVisibleModules("admin").map((m) => m.id);
    expect(adminModules).toContain("settings");

    const employeeModules = getVisibleModules("employee").map((m) => m.id);
    expect(employeeModules).not.toContain("settings");

    expect(getVisibleSidebarGroups("settings", "employee")).toHaveLength(0);
    expect(getVisibleSidebarGroups("settings", "admin")).toHaveLength(1);
  });

  it("keeps every module sidebar populated for a regular employee", () => {
    const employeeModules = getVisibleModules("employee");
    employeeModules.forEach((module) => {
      const groups = getVisibleSidebarGroups(module.id, "employee");
      expect(groups.length).toBeGreaterThan(0);
    });
  });

  it("exposes the worker-management module navigation with real pages", () => {
    const groups = getVisibleSidebarGroups("worker-management", "employee", "/worker-management");
    const allItems = groups.flatMap((g) => g.items);
    const allLabels = allItems.map((i) => i.to);
    expect(allLabels).toContain("/worker-management");
    expect(allLabels).toContain("/worker-management/workers");
    expect(allLabels).toContain("/worker-management/attendance");
    expect(allLabels).toContain("/worker-management/salaries");
    expect(allLabels).toContain("/worker-management/advances");
    expect(allLabels).toContain("/worker-management/reports");
  });

  it("exposes the expenses module navigation", () => {
    const groups = getVisibleSidebarGroups("expenses", "employee", "/expenses");
    const allItems = groups.flatMap((g) => g.items);
    const allLabels = allItems.map((i) => i.to);
    expect(allLabels).toContain("/expenses");
    expect(allLabels).toContain("/expenses/categories");
    expect(allLabels).toContain("/expenses/reports");
  });

  it("exposes the dashboard module navigation", () => {
    const groups = getVisibleSidebarGroups("dashboard", "employee", "/dashboard");
    const allItems = groups.flatMap((g) => g.items);
    const allLabels = allItems.map((i) => i.to);
    expect(allLabels).toContain("/dashboard");
  });

  it("exposes the settings module navigation for admin", () => {
    const groups = getVisibleSidebarGroups("settings", "admin", "/store-settings");
    const allItems = groups.flatMap((g) => g.items);
    const allLabels = allItems.map((i) => i.to);
    expect(allLabels).toContain("/store-settings");
    expect(allLabels).toContain("/users");
  });

  it("restricts Settings module to admin roles", () => {
    const employeeLabels = getVisibleSidebarGroups("settings", "employee", "/store-settings")
      .flatMap((g) => g.items.map((i) => i.to));
    expect(employeeLabels).not.toContain("/store-settings");
    expect(employeeLabels).not.toContain("/users");

    const adminLabels = getVisibleSidebarGroups("settings", "admin", "/store-settings")
      .flatMap((g) => g.items.map((i) => i.to));
    expect(adminLabels).toContain("/store-settings");
    expect(adminLabels).toContain("/users");
  });

  it("returns quick actions for dashboard module", () => {
    const actions = getQuickActions("dashboard", "admin");
    const labels = actions.map((a) => a.to);
    expect(labels).toContain("/worker-management/workers");
    expect(labels).toContain("/expenses");
  });

  it("returns quick actions for worker-management module", () => {
    const actions = getQuickActions("worker-management", "admin");
    const labels = actions.map((a) => a.to);
    expect(labels).toContain("/worker-management/workers");
    expect(labels).toContain("/worker-management/attendance");
    expect(labels).toContain("/expenses");
  });

  it("returns quick actions for expenses module", () => {
    const actions = getQuickActions("expenses", "admin");
    const labels = actions.map((a) => a.to);
    expect(labels).toContain("/expenses");
    expect(labels).toContain("/worker-management/workers");
  });

  it("filters quick actions by role", () => {
    const adminActions = getQuickActions("dashboard", "admin");
    const employeeActions = getQuickActions("dashboard", "employee");
    expect(adminActions.length).toBeGreaterThan(employeeActions.length);
  });

  it("generates breadcrumb for worker-management routes", () => {
    const bc = getBreadcrumb("/worker-management/workers");
    expect(bc.moduleId).toBe("worker-management");
    expect(bc.moduleLabelKey).toBe("services.workerManagement");
    expect(bc.sectionLabelKey).toBe("nav.workers");
  });

  it("generates breadcrumb for expenses routes", () => {
    const bc = getBreadcrumb("/expenses");
    expect(bc.moduleId).toBe("expenses");
    expect(bc.moduleLabelKey).toBe("services.expenses");
    expect(bc.sectionLabelKey).toBe("nav.expenses");
  });

  it("generates breadcrumb for dashboard", () => {
    const bc = getBreadcrumb("/dashboard");
    expect(bc.moduleId).toBe("dashboard");
    expect(bc.moduleLabelKey).toBe("nav.dashboard");
    expect(bc.sectionLabelKey).toBe("nav.dashboardOverview");
  });
});