import { describe, it, expect } from "vitest";
import {
  getActiveModule,
  getVisibleModules,
  getVisibleSidebarGroups,
} from "../shared/layouts/navigationConfig";

describe("navigationConfig", () => {
  it("derives the active module for every existing route", () => {
    const cases = [
      ["/dashboard", "dashboard"],
      ["/pos", "pos"],
      ["/pos/invoice/42", "pos"],
      ["/customers", "pos"],
      ["/products", "inventory"],
      ["/categories", "inventory"],
      ["/inventory", "inventory"],
      ["/inventory/movements", "inventory"],
      ["/inventory/audits", "inventory"],
      ["/purchases", "purchases"],
      ["/purchases/7", "purchases"],
      ["/suppliers", "purchases"],
      ["/reports", "reports"],
      ["/expenses", "reports"],
      ["/store-settings", "settings"],
      ["/users", "settings"],
    ];
    cases.forEach(([path, moduleId]) => {
      expect(getActiveModule(path)).toBe(moduleId);
    });
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
});
