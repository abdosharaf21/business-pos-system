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
