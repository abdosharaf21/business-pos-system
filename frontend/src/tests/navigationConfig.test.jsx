import { describe, it, expect } from "vitest";
import {
  MODULES,
  APPLICATION_LAUNCH_ROUTES,
  getActiveModule,
  getVisibleModules,
  getVisibleSidebarGroups,
  getQuickActions,
  getContextBack,
  getBreadcrumb,
} from "../shared/layouts/navigationConfig";

describe("navigationConfig", () => {
  it("exposes exactly the four applications", () => {
    expect(MODULES.map((m) => m.id)).toEqual([
      "business",
      "pos",
      "inventory",
      "expenses",
    ]);
  });

  it("derives the active module for every existing route", () => {
    const cases = [
      ["/business", "business"],
      ["/business/reports", "business"],
      ["/clients", "business"],
      ["/services", "business"],
      ["/service-categories", "business"],
      ["/client-services", "business"],
      ["/deals", "business"],
      ["/dashboard", "pos"],
      ["/pos", "pos"],
      ["/pos/invoice/42", "pos"],
      ["/products", "pos"],
      ["/categories", "pos"],
      ["/purchases", "pos"],
      ["/purchases/7", "pos"],
      ["/suppliers", "pos"],
      ["/inventory/overview", "inventory"],
      ["/inventory", "inventory"],
      ["/inventory/movements", "inventory"],
      ["/inventory/audits", "inventory"],
      ["/inventory/warehouses", "inventory"],
      ["/inventory/transfers", "inventory"],
      ["/inventory/reorder", "inventory"],
      ["/inventory/expiration", "inventory"],
      ["/inventory/reports", "inventory"],
      ["/expenses/dashboard", "expenses"],
      ["/expenses", "expenses"],
      ["/expenses/categories", "expenses"],
      ["/expenses/reports", "expenses"],
      ["/store-settings", "admin"],
      ["/users", "admin"],
    ];
    cases.forEach(([path, moduleId]) => {
      expect(getActiveModule(path), path).toBe(moduleId);
    });
  });

  it("falls back to the business module for unknown paths", () => {
    expect(getActiveModule("/definitely/not/a/route")).toBe("business");
  });

  it("appends the Administration group only for admins", () => {
    for (const moduleId of ["business", "pos", "inventory", "expenses"]) {
      const employeeLabels = getVisibleSidebarGroups(moduleId, "employee").map(
        (g) => g.labelKey
      );
      expect(employeeLabels, moduleId).not.toContain("nav.administration");

      const adminLabels = getVisibleSidebarGroups(moduleId, "admin").map(
        (g) => g.labelKey
      );
      expect(adminLabels, moduleId).toContain("nav.administration");
    }
  });

  it("keeps Administration items restricted to admins", () => {
    const adminGroups = getVisibleSidebarGroups("pos", "admin");
    const adminGroup = adminGroups.find((g) => g.labelKey === "nav.administration");
    expect(adminGroup.items.map((i) => i.to)).toEqual([
      "/store-settings",
      "/users",
    ]);

    const employeeAdmin = getVisibleSidebarGroups("admin", "employee");
    expect(employeeAdmin.map((g) => g.labelKey)).not.toContain("nav.administration");
  });

  it("keeps every application sidebar populated for a regular employee", () => {
    const modules = getVisibleModules("employee");
    expect(modules).toHaveLength(4);
    modules.forEach((module) => {
      const groups = getVisibleSidebarGroups(module.id, "employee");
      expect(groups.length).toBeGreaterThan(0);
    });
  });

  it("provides quick actions per application and filters by role", () => {
    expect(getQuickActions("business", "employee").length).toBeGreaterThan(0);
    expect(getQuickActions("pos", "employee").length).toBeGreaterThan(0);
    expect(getQuickActions("inventory", "employee").length).toBeGreaterThan(0);
    expect(getQuickActions("expenses", "employee").length).toBeGreaterThan(0);
  });

  it("offers a back-to-services context only inside POS, Inventory and Expenses", () => {
    const backPaths = [
      "/dashboard",
      "/pos",
      "/products",
      "/purchases",
      "/suppliers",
      "/inventory",
      "/inventory/warehouses",
      "/inventory/transfers",
      "/inventory/overview",
      "/expenses",
      "/expenses/dashboard",
      "/expenses/reports",
    ];
    backPaths.forEach((path) => {
      const back = getContextBack(path);
      expect(back, path).not.toBeNull();
      expect(back.to).toBe("/services");
    });

    const noBackPaths = [
      "/business",
      "/services",
      "/clients",
      "/deals",
      "/client-services",
      "/service-categories",
      "/business/reports",
      "/store-settings",
      "/users",
    ];
    noBackPaths.forEach((path) => {
      expect(getContextBack(path), path).toBeNull();
    });
  });

  it("resolves breadcrumbs including administration pages", () => {
    expect(getBreadcrumb("/deals").moduleId).toBe("business");
    expect(getBreadcrumb("/deals").sectionLabelKey).toBe("nav.deals");
    expect(getBreadcrumb("/inventory/transfers").sectionLabelKey).toBe(
      "nav.transfers"
    );
    const settingsCrumb = getBreadcrumb("/store-settings");
    expect(settingsCrumb.moduleId).toBe("admin");
    expect(settingsCrumb.sectionLabelKey).toBe("nav.storeSettings");
  });

  it("keeps the application catalog and sellable service records inside Business Development", () => {
    expect(getActiveModule("/services")).toBe("business");
    expect(getActiveModule("/business/services")).toBe("business");

    const businessItems = getVisibleSidebarGroups(
      "business",
      "employee"
    )[0].items.map((item) => item.to);
    expect(businessItems).toContain("/services");
    expect(businessItems).toContain("/business/services");
  });

  it("distinguishes the catalog breadcrumb from the service records breadcrumb", () => {
    expect(getBreadcrumb("/services").sectionLabelKey).toBe(
      "nav.servicesCatalog"
    );
    expect(getBreadcrumb("/business/services").sectionLabelKey).toBe(
      "nav.serviceRecords"
    );
    expect(getContextBack("/services")).toBeNull();
    expect(getContextBack("/business/services")).toBeNull();
  });

  it("launches every application from the catalog onto its dashboard", () => {
    expect(APPLICATION_LAUNCH_ROUTES).toEqual({
      business: "/business",
      pos: "/dashboard",
      inventory: "/inventory/overview",
      expenses: "/expenses/dashboard",
    });
  });
});
