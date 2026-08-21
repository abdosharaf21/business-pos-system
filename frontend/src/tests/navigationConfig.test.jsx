import { describe, it, expect } from "vitest";
import {
  getActiveModule,
  getActiveApplication,
  getVisibleSidebarGroups,
  getVisibleApplications,
  getApplicationDefaultPath,
  getAppTabs,
  getBackRoute,
  APPS,
} from "../shared/layouts/navigationConfig";

describe("navigationConfig", () => {
  it("derives the active app for every existing route", () => {
    const cases = [
      ["/dashboard", "pos"],
      ["/pos", "pos"],
      ["/pos/invoice/42", "pos"],
      ["/customers", "pos"],
      ["/products", "pos"],
      ["/categories", "pos"],
      ["/inventory", "inventory"],
      ["/inventory/movements", "inventory"],
      ["/inventory/audits", "inventory"],
      ["/warehouses", "inventory"],
      ["/transfers", "inventory"],
      ["/purchases", "pos"],
      ["/purchases/7", "pos"],
      ["/suppliers", "pos"],
      ["/reports", "expenses"],
      ["/expenses", "expenses"],
      ["/business/dashboard", "business"],
      ["/business/clients", "business"],
      ["/business/services", "business"],
      ["/business/applications", "business"],
      ["/business/reports", "business"],
      ["/business/service-categories", "business"],
      ["/business/client-services", "business"],
    ];
    cases.forEach(([path, appId]) => {
      expect(getActiveModule(path)).toBe(appId);
    });
  });

  it("maps routes to the correct application", () => {
    const cases = [
      ["/dashboard", "pos"],
      ["/pos", "pos"],
      ["/products", "pos"],
      ["/warehouses", "inventory"],
      ["/transfers", "inventory"],
      ["/business/dashboard", "business"],
      ["/business/clients", "business"],
      ["/business/services", "business"],
      ["/business/applications", "business"],
      ["/business/reports", "business"],
      ["/reports", "expenses"],
      ["/expenses", "expenses"],
    ];
    cases.forEach(([path, appId]) => {
      expect(getActiveApplication(path)).toBe(appId);
    });
  });

  it("returns default path for each application", () => {
    expect(getApplicationDefaultPath("pos")).toBe("/dashboard");
    expect(getApplicationDefaultPath("business")).toBe("/business/dashboard");
    expect(getApplicationDefaultPath("expenses")).toBe("/expenses");
    expect(getApplicationDefaultPath("inventory")).toBe("/inventory");
  });

  it("keeps every app sidebar populated for a regular employee", () => {
    const employeeApps = getVisibleApplications("employee");
    employeeApps.forEach((app) => {
      const groups = getVisibleSidebarGroups(app.id, "employee");
      expect(groups.length).toBeGreaterThan(0);
    });
  });

  it("has all applications defined", () => {
    expect(APPS.length).toBe(4);
    expect(APPS.map((a) => a.id)).toEqual([
      "business",
      "pos",
      "inventory",
      "expenses",
    ]);
  });

  it("provides sidebar groups for the business app", () => {
    const groups = getVisibleSidebarGroups("business", "admin");
    expect(groups.length).toBeGreaterThan(0);
    const itemTos = groups[0].items.map((i) => i.to);
    expect(itemTos).toContain("/business/dashboard");
    expect(itemTos).toContain("/business/clients");
    expect(itemTos).toContain("/business/services");
    expect(itemTos).toContain("/business/applications");
    expect(itemTos).toContain("/business/reports");
  });

  it("provides app-specific tabs for each application", () => {
    const posTabs = getAppTabs("pos", "admin");
    expect(posTabs.length).toBeGreaterThan(0);
    expect(posTabs.some((t) => t.to === "/dashboard")).toBe(true);

    const invTabs = getAppTabs("inventory", "admin");
    expect(invTabs.length).toBeGreaterThan(0);
    expect(invTabs.some((t) => t.to === "/warehouses")).toBe(true);

    const bdTabs = getAppTabs("business", "admin");
    expect(bdTabs.length).toBe(6);
    expect(bdTabs.some((t) => t.to === "/business/services")).toBe(true);
    expect(bdTabs.some((t) => t.to === "/business/applications")).toBe(true);
    expect(bdTabs.some((t) => t.to === "/business/deals")).toBe(true);
    expect(bdTabs.some((t) => t.to === "/business/reports")).toBe(true);
  });

  it("does NOT include Reports in POS sidebar", () => {
    const groups = getVisibleSidebarGroups("pos", "admin");
    const itemTos = groups.flatMap((g) => g.items.map((i) => i.to));
    expect(itemTos).not.toContain("/reports");
  });

  it("includes Reports in Expenses sidebar", () => {
    const groups = getVisibleSidebarGroups("expenses", "admin");
    const itemTos = groups.flatMap((g) => g.items.map((i) => i.to));
    expect(itemTos).toContain("/reports");
  });

  it("includes Reports in Expenses tabs", () => {
    const expTabs = getAppTabs("expenses", "admin");
    expect(expTabs.some((t) => t.to === "/reports")).toBe(true);
  });

  it("provides a single Administration group as a global section with no duplicates", () => {
    const adminApps = ["business", "pos", "inventory", "expenses"];
    adminApps.forEach((appId) => {
      const groups = getVisibleSidebarGroups(appId, "admin");
      const itemTos = groups.flatMap((g) => g.items.map((i) => i.to));
      expect(itemTos).toContain("/store-settings");
      expect(itemTos).toContain("/users");
      expect(itemTos.filter((t) => t === "/store-settings").length).toBe(1);
      expect(itemTos.filter((t) => t === "/users").length).toBe(1);
    });
  });
});

describe("getBackRoute", () => {
  it("returns null for Business Development pages", () => {
    expect(getBackRoute("/business/dashboard")).toBeNull();
    expect(getBackRoute("/business/services")).toBeNull();
    expect(getBackRoute("/business/clients")).toBeNull();
    expect(getBackRoute("/business/reports")).toBeNull();
  });

  it("returns null for Settings pages", () => {
    expect(getBackRoute("/store-settings")).toBeNull();
    expect(getBackRoute("/users")).toBeNull();
  });

  it("returns /business/applications for all POS routes", () => {
    expect(getBackRoute("/dashboard")).toBe("/business/applications");
    expect(getBackRoute("/products")).toBe("/business/applications");
    expect(getBackRoute("/categories")).toBe("/business/applications");
    expect(getBackRoute("/purchases")).toBe("/business/applications");
    expect(getBackRoute("/pos")).toBe("/business/applications");
    expect(getBackRoute("/customers")).toBe("/business/applications");
    expect(getBackRoute("/suppliers")).toBe("/business/applications");
    expect(getBackRoute("/purchases/42")).toBe("/business/applications");
    expect(getBackRoute("/pos/invoice/7")).toBe("/business/applications");
  });

  it("returns /business/applications for all Inventory routes", () => {
    expect(getBackRoute("/inventory")).toBe("/business/applications");
    expect(getBackRoute("/warehouses")).toBe("/business/applications");
    expect(getBackRoute("/transfers")).toBe("/business/applications");
    expect(getBackRoute("/inventory/movements")).toBe("/business/applications");
    expect(getBackRoute("/inventory/audits")).toBe("/business/applications");
  });

  it("returns /business/applications for all Expenses routes", () => {
    expect(getBackRoute("/expenses")).toBe("/business/applications");
    expect(getBackRoute("/reports")).toBe("/business/applications");
  });
});
