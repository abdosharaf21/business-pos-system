import { Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { AuthProvider } from "../shared/context/AuthContext";
import ProtectedRoute from "./ProtectedRoute";
import AppLayout from "../shared/layouts/AppLayout";
import LoginPage from "../shared/pages/LoginPage";
import DashboardPage from "../modules/dashboard/page";
import ReportsPage from "../modules/reports/page";
import CategoriesPage from "../modules/categories/page";
import InventoryPage from "../modules/inventory/page";
import InventoryHistoryPage from "../modules/inventory/history";
import InventoryAuditsPage from "../modules/inventory_audits/page";
import ProductsPage from "../modules/products/page";
import CustomersPage from "../modules/customers/page";
import SuppliersPage from "../modules/suppliers/page";
import PurchasesPage from "../modules/purchases/page";
import PurchaseInvoicePage from "../modules/purchases/invoice";
import ExpensesPage from "../modules/expenses/page";
import UsersPage from "../modules/users/page";
import StoreSettingsPage from "../modules/store-settings/page";
import PosPage from "../modules/pos/page";
import InvoicePage from "../modules/pos/invoice";
import ClientsPage from "../modules/clients/page";
import ServicesPage from "../modules/services/page";
import ClientServicesPage from "../modules/client_services/page";
import ServiceCategoriesPage from "../modules/service_categories/page";
import WarehousesPage from "../modules/warehouses/page";
import TransfersPage from "../modules/transfers/page";
import BusinessDashboardPage from "../modules/business/dashboard/page";
import BusinessReportsPage from "../modules/business/reports/page";
import ApplicationsPage from "../modules/applications/page";
import DealsPage from "../modules/deals/page";

export default function AppRoutes() {
  return (
    <AuthProvider>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            borderRadius: "12px",
            background: "#0f172a",
            color: "#f1f5f9",
            fontSize: "13px",
            fontWeight: "500",
            padding: "12px 16px",
            boxShadow: "0 10px 15px -3px rgb(0 0 0 / 0.1)",
          },
          success: { iconTheme: { primary: "#10b981", secondary: "#fff" } },
          error: { iconTheme: { primary: "#ef4444", secondary: "#fff" } },
        }}
      />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          element={
            <ProtectedRoute>
              <AppLayout />
            </ProtectedRoute>
          }
        >
          {/* ── Business Development Application ── */}
          <Route path="/business">
            <Route index element={<Navigate to="dashboard" replace />} />
            <Route path="dashboard" element={<BusinessDashboardPage />} />
            <Route path="clients" element={<ClientsPage />} />
            <Route path="applications" element={<ApplicationsPage />} />
            <Route path="services" element={<ServicesPage />} />
            <Route path="deals" element={<DealsPage />} />
            <Route path="reports" element={<BusinessReportsPage />} />
            <Route path="service-categories" element={<ServiceCategoriesPage />} />
            <Route path="client-services" element={<ClientServicesPage />} />
          </Route>

          {/* Legacy flat BD routes (backward compatibility) */}
          <Route path="/clients" element={<Navigate to="/business/clients" replace />} />
          <Route path="/services" element={<Navigate to="/business/services" replace />} />
          <Route path="/service-categories" element={<Navigate to="/business/service-categories" replace />} />
          <Route path="/client-services" element={<Navigate to="/business/client-services" replace />} />

          {/* ── POS Application ── */}
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/categories" element={<CategoriesPage />} />
          <Route path="/products" element={<ProductsPage />} />
          <Route path="/customers" element={<CustomersPage />} />
          <Route path="/suppliers" element={<SuppliersPage />} />
          <Route path="/purchases" element={<PurchasesPage />} />
          <Route path="/purchases/:purchaseId" element={<PurchaseInvoicePage />} />
          <Route path="/pos" element={<PosPage />} />
          <Route path="/pos/invoice/:saleId" element={<InvoicePage />} />

          {/* ── Inventory Application ── */}
          <Route path="/inventory" element={<InventoryPage />} />
          <Route path="/inventory/movements" element={<InventoryHistoryPage />} />
          <Route path="/inventory/audits" element={<InventoryAuditsPage />} />
          <Route path="/warehouses" element={<WarehousesPage />} />
          <Route path="/transfers" element={<TransfersPage />} />

          {/* ── Expenses Application ── */}
          <Route path="/expenses" element={<ExpensesPage />} />

          {/* ── Settings Application ── */}
          <Route path="/users" element={<UsersPage />} />
          <Route path="/store-settings" element={<StoreSettingsPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/business/dashboard" replace />} />
      </Routes>
    </AuthProvider>
  );
}
