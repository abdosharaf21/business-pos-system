import { Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "react-hot-toast";
import { AuthProvider } from "../shared/context/AuthContext";
import ProtectedRoute from "./ProtectedRoute";
import AppLayout from "../shared/layouts/ModuleLayout";
import LoginPage from "../shared/pages/LoginPage";
import DashboardPage from "../modules/dashboard/page";
import ExpensesPage from "../modules/expenses/page";
import UsersPage from "../modules/users/page";
import StoreSettingsPage from "../modules/store-settings/page";
import WorkerManagementPage from "../modules/worker-management/page";
import WorkersPage from "../modules/worker-management/workers";
import AttendancePage from "../modules/worker-management/attendance";
import SalariesPage from "../modules/worker-management/salaries";
import AdvancesPage from "../modules/worker-management/advances";
import WorkerReportsPage from "../modules/worker-management/reports";

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
          <Route path="/worker-management" element={<WorkerManagementPage />} />
          <Route path="/worker-management/workers" element={<WorkersPage />} />
          <Route path="/worker-management/attendance" element={<AttendancePage />} />
          <Route path="/worker-management/salaries" element={<SalariesPage />} />
          <Route path="/worker-management/advances" element={<AdvancesPage />} />
          <Route path="/worker-management/reports" element={<WorkerReportsPage />} />
          <Route path="/expenses" element={<ExpensesPage />} />
          <Route path="/users" element={<UsersPage />} />
          <Route path="/store-settings" element={<StoreSettingsPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AuthProvider>
  );
}