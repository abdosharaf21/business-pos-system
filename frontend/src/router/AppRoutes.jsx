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
import ExpensesDashboardPage from "../modules/expenses/dashboard";
import ExpenseCategoriesPage from "../modules/expenses/categories";
import ExpenseReportsPage from "../modules/expenses/reports";
import BusinessPage from "../modules/business/page";
import BusinessReportsPage from "../modules/business/reports";
import ClientsPage from "../modules/clients/page";
import ServicesPage from "../modules/services/page";
import ApplicationCatalogPage from "../modules/services/catalog";
import ServiceCategoriesPage from "../modules/service_categories/page";
import ClientServicesPage from "../modules/client_services/page";
import DealsPage from "../modules/deals/page";
import WarehousesPage from "../modules/warehouses/page";
import TransfersPage from "../modules/transfers/page";
import InventoryOverviewPage from "../modules/inventory/overview";
import InventoryReorderPage from "../modules/inventory/reorder";
import InventoryExpirationPage from "../modules/inventory/expiration";
import InventoryReportsPage from "../modules/inventory/reports";
import UsersPage from "../modules/users/page";
import StoreSettingsPage from "../modules/store-settings/page";
import PosPage from "../modules/pos/page";
import InvoicePage from "../modules/pos/invoice";

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
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="/categories" element={<CategoriesPage />} />
          <Route path="/inventory" element={<InventoryPage />} />
          <Route path="/inventory/movements" element={<InventoryHistoryPage />} />
          <Route path="/inventory/audits" element={<InventoryAuditsPage />} />
          <Route path="/products" element={<ProductsPage />} />
          <Route path="/customers" element={<CustomersPage />} />
          <Route path="/suppliers" element={<SuppliersPage />} />
          <Route path="/purchases" element={<PurchasesPage />} />
          <Route path="/purchases/:purchaseId" element={<PurchaseInvoicePage />} />
          <Route path="/expenses" element={<ExpensesPage />} />
          <Route path="/expenses/dashboard" element={<ExpensesDashboardPage />} />
          <Route path="/expenses/categories" element={<ExpenseCategoriesPage />} />
          <Route path="/expenses/reports" element={<ExpenseReportsPage />} />
          <Route path="/business" element={<BusinessPage />} />
          <Route path="/business/reports" element={<BusinessReportsPage />} />
          <Route path="/business/services" element={<ServicesPage />} />
          <Route path="/clients" element={<ClientsPage />} />
          <Route path="/services" element={<ApplicationCatalogPage />} />
          <Route path="/service-categories" element={<ServiceCategoriesPage />} />
          <Route path="/client-services" element={<ClientServicesPage />} />
          <Route path="/deals" element={<DealsPage />} />
          <Route path="/inventory/overview" element={<InventoryOverviewPage />} />
          <Route path="/inventory/warehouses" element={<WarehousesPage />} />
          <Route path="/inventory/transfers" element={<TransfersPage />} />
          <Route path="/inventory/reorder" element={<InventoryReorderPage />} />
          <Route path="/inventory/expiration" element={<InventoryExpirationPage />} />
          <Route path="/inventory/reports" element={<InventoryReportsPage />} />
          <Route path="/pos" element={<PosPage />} />
          <Route path="/pos/invoice/:saleId" element={<InvoicePage />} />
          <Route path="/users" element={<UsersPage />} />
          <Route path="/store-settings" element={<StoreSettingsPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AuthProvider>
  );
}
