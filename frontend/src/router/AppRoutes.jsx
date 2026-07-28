import { Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { AuthProvider } from "../shared/context/AuthContext";
import ProtectedRoute from "./ProtectedRoute";
import AppLayout from "../shared/layouts/AppLayout";
import LoginPage from "../shared/pages/LoginPage";
import DashboardPage from "../modules/dashboard/page";
import ClientsPage from "../modules/clients/page";
import ServicesPage from "../modules/services/page";
import CategoriesPage from "../modules/service_categories/page";
import ClientServicesPage from "../modules/client_services/page";
import UsersPage from "../modules/users/page";

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
          <Route path="/clients" element={<ClientsPage />} />
          <Route path="/services" element={<ServicesPage />} />
          <Route path="/categories" element={<CategoriesPage />} />
          <Route path="/client-services" element={<ClientServicesPage />} />
          <Route path="/users" element={<UsersPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AuthProvider>
  );
}
