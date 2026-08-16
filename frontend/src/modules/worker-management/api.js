import api from "../../shared/services/axios";
import { createCrudService } from "../../shared/services/crud";

export const workerService = createCrudService("/worker-management/workers");

export const attendanceService = createCrudService("/worker-management/attendance");

export const salaryService = {
  ...createCrudService("/worker-management/salaries"),
  markPaid: (id, paymentDate) =>
    api.post(`/worker-management/salaries/${id}/pay`, paymentDate ? { payment_date: paymentDate } : {}),
};

export const advanceService = createCrudService("/worker-management/advances");

export const workerManagementService = {
  getStatistics: () => api.get("/worker-management/statistics"),
  getAttendanceReport: (params) => api.get("/worker-management/reports/attendance", { params }),
  getSalaryReport: (params) => api.get("/worker-management/reports/salaries", { params }),
};

export const WORKER_STATUSES = ["active", "inactive"];
export const ATTENDANCE_STATUSES = ["present", "absent", "late", "half_day", "leave"];
export const SALARY_STATUSES = ["paid", "pending", "partial"];
export const ADVANCE_STATUSES = ["pending", "paid", "settled"];
