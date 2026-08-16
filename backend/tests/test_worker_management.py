"""Tests for Worker Management API endpoints.

Tests the /api/worker-management/* endpoints including CRUD operations
for workers, attendance, salaries and advances, statistics, reports,
role-based access control, and error handling.
"""

from unittest.mock import patch

from backend.modules.worker_management.model import Advance, Attendance, Salary, Worker


def _worker(**kw):
    """Return a Worker instance with sensible defaults."""
    defaults = dict(
        id=1,
        full_name="Ahmed Ali",
        phone="+201000000001",
        email="ahmed@pos.com",
        job_title="Cashier",
        department="Sales",
        hire_date="2025-01-15",
        base_salary=5000.0,
        status="active",
        notes=None,
    )
    defaults.update(kw)
    return Worker(**defaults)


def _attendance(**kw):
    """Return an Attendance instance with sensible defaults."""
    defaults = dict(
        id=1,
        worker_id=1,
        worker_name="Ahmed Ali",
        attendance_date="2026-08-01",
        status="present",
        check_in="09:00:00",
        check_out="17:00:00",
        notes=None,
    )
    defaults.update(kw)
    return Attendance(**defaults)


def _salary(**kw):
    """Return a Salary instance with sensible defaults."""
    defaults = dict(
        id=1,
        worker_id=1,
        worker_name="Ahmed Ali",
        salary_period="2026-07",
        base_salary=5000.0,
        bonuses=200.0,
        deductions=0.0,
        advances_deduction=300.0,
        net_amount=4900.0,
        payment_status="pending",
        payment_date=None,
        notes=None,
    )
    defaults.update(kw)
    return Salary(**defaults)


def _advance(**kw):
    """Return an Advance instance with sensible defaults."""
    defaults = dict(
        id=1,
        worker_id=1,
        worker_name="Ahmed Ali",
        amount=300.0,
        advance_date="2026-07-10",
        status="paid",
        notes=None,
    )
    defaults.update(kw)
    return Advance(**defaults)


class TestWorkers:
    """Tests for worker endpoints."""

    def test_get_all_workers_success(self, client, admin_headers):
        """Test admin can list workers."""
        workers = [_worker(id=1), _worker(id=2, full_name="Sara Hassan")]
        with patch("backend.modules.worker_management.service.WorkerManagementService.get_all_workers") as mock_get:
            mock_get.return_value = workers
            response = client.get("/api/worker-management/workers/", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert len(data["data"]) == 2
            assert data["data"][0]["full_name"] == "Ahmed Ali"

    def test_get_all_workers_no_token(self, client):
        """Test unauthenticated cannot list workers."""
        response = client.get("/api/worker-management/workers/")
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False

    def test_get_worker_success(self, client, employee_headers):
        """Test employee can get a worker by ID."""
        with patch("backend.modules.worker_management.service.WorkerManagementService.get_worker") as mock_get:
            mock_get.return_value = _worker(id=1)
            response = client.get("/api/worker-management/workers/1", headers=employee_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["department"] == "Sales"

    def test_get_worker_not_found(self, client, admin_headers):
        """Test get non-existent worker returns 404."""
        with patch("backend.modules.worker_management.service.WorkerManagementService.get_worker") as mock_get:
            mock_get.side_effect = ValueError("Worker not found")
            response = client.get("/api/worker-management/workers/999", headers=admin_headers)
            assert response.status_code == 404
            data = response.get_json()
            assert data["success"] is False

    def test_create_worker_success(self, client, admin_headers):
        """Test admin can create a worker."""
        with patch("backend.modules.worker_management.service.WorkerManagementService.create_worker") as mock_create:
            mock_create.return_value = _worker(id=1)
            response = client.post("/api/worker-management/workers/", headers=admin_headers, json={
                "full_name": "Ahmed Ali",
                "phone": "+201000000001",
            })
            assert response.status_code == 201
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["id"] == 1

    def test_create_worker_validation_error(self, client, admin_headers):
        """Test create worker returns 400 on validation error."""
        with patch("backend.modules.worker_management.service.WorkerManagementService.create_worker") as mock_create:
            mock_create.side_effect = ValueError("Full name is required")
            response = client.post("/api/worker-management/workers/", headers=admin_headers, json={})
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False
            assert "Full name" in data["message"]

    def test_create_worker_employee_forbidden(self, client, employee_headers):
        """Test employee cannot create a worker."""
        response = client.post("/api/worker-management/workers/", headers=employee_headers, json={
            "full_name": "Ahmed Ali",
            "phone": "+201000000001",
        })
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False

    def test_update_worker_success(self, client, admin_headers):
        """Test admin can update a worker."""
        with patch("backend.modules.worker_management.service.WorkerManagementService.update_worker") as mock_update:
            mock_update.return_value = _worker(id=1, department="Logistics")
            response = client.put("/api/worker-management/workers/1", headers=admin_headers, json={
                "department": "Logistics",
            })
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["department"] == "Logistics"

    def test_delete_worker_success(self, client, admin_headers):
        """Test admin can delete a worker."""
        with patch("backend.modules.worker_management.service.WorkerManagementService.delete_worker") as mock_delete:
            mock_delete.return_value = True
            response = client.delete("/api/worker-management/workers/1", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True

    def test_delete_worker_not_found(self, client, admin_headers):
        """Test delete non-existent worker returns 404."""
        with patch("backend.modules.worker_management.service.WorkerManagementService.delete_worker") as mock_delete:
            mock_delete.side_effect = ValueError("Worker not found")
            response = client.delete("/api/worker-management/workers/999", headers=admin_headers)
            assert response.status_code == 404
            data = response.get_json()
            assert data["success"] is False


class TestAttendance:
    """Tests for attendance endpoints."""

    def test_get_all_attendance_success(self, client, admin_headers):
        """Test admin can list attendance records."""
        records = [_attendance(id=1), _attendance(id=2, status="late", attendance_date="2026-08-02")]
        with patch("backend.modules.worker_management.service.WorkerManagementService.get_all_attendance") as mock_get:
            mock_get.return_value = records
            response = client.get("/api/worker-management/attendance/", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert len(data["data"]) == 2
            assert data["data"][0]["worker_name"] == "Ahmed Ali"

    def test_create_attendance_success(self, client, admin_headers):
        """Test admin can create an attendance record."""
        with patch("backend.modules.worker_management.service.WorkerManagementService.create_attendance") as mock_create:
            mock_create.return_value = _attendance(id=1)
            response = client.post("/api/worker-management/attendance/", headers=admin_headers, json={
                "worker_id": 1,
                "attendance_date": "2026-08-01",
                "status": "present",
            })
            assert response.status_code == 201
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["status"] == "present"

    def test_create_attendance_duplicate(self, client, admin_headers):
        """Test duplicate attendance returns 400."""
        with patch("backend.modules.worker_management.service.WorkerManagementService.create_attendance") as mock_create:
            mock_create.side_effect = ValueError("Attendance already exists for this worker and date")
            response = client.post("/api/worker-management/attendance/", headers=admin_headers, json={
                "worker_id": 1,
                "attendance_date": "2026-08-01",
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_update_attendance_success(self, client, admin_headers):
        """Test admin can update an attendance record."""
        with patch("backend.modules.worker_management.service.WorkerManagementService.update_attendance") as mock_update:
            mock_update.return_value = _attendance(id=1, status="half_day")
            response = client.put("/api/worker-management/attendance/1", headers=admin_headers, json={
                "status": "half_day",
            })
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["status"] == "half_day"

    def test_delete_attendance_success(self, client, admin_headers):
        """Test admin can delete an attendance record."""
        with patch("backend.modules.worker_management.service.WorkerManagementService.delete_attendance") as mock_delete:
            mock_delete.return_value = True
            response = client.delete("/api/worker-management/attendance/1", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True

    def test_attendance_employee_forbidden(self, client, employee_headers):
        """Test employee cannot create attendance."""
        response = client.post("/api/worker-management/attendance/", headers=employee_headers, json={
            "worker_id": 1,
            "attendance_date": "2026-08-01",
        })
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False


class TestSalaries:
    """Tests for salary endpoints."""

    def test_get_all_salaries_success(self, client, admin_headers):
        """Test admin can list salary records."""
        salaries = [_salary(id=1)]
        with patch("backend.modules.worker_management.service.WorkerManagementService.get_all_salaries") as mock_get:
            mock_get.return_value = salaries
            response = client.get("/api/worker-management/salaries/", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"][0]["salary_period"] == "2026-07"

    def test_create_salary_success(self, client, admin_headers):
        """Test admin can create a salary record."""
        with patch("backend.modules.worker_management.service.WorkerManagementService.create_salary") as mock_create:
            mock_create.return_value = _salary(id=1)
            response = client.post("/api/worker-management/salaries/", headers=admin_headers, json={
                "worker_id": 1,
                "salary_period": "2026-07",
                "base_salary": 5000.0,
            })
            assert response.status_code == 201
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["net_amount"] == 4900.0

    def test_create_salary_duplicate(self, client, admin_headers):
        """Test duplicate salary returns 400."""
        with patch("backend.modules.worker_management.service.WorkerManagementService.create_salary") as mock_create:
            mock_create.side_effect = ValueError("Salary already exists for this worker and period")
            response = client.post("/api/worker-management/salaries/", headers=admin_headers, json={
                "worker_id": 1,
                "salary_period": "2026-07",
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_mark_salary_paid_success(self, client, admin_headers):
        """Test admin can mark a salary as paid."""
        with patch("backend.modules.worker_management.service.WorkerManagementService.mark_salary_paid") as mock_pay:
            mock_pay.return_value = _salary(id=1, payment_status="paid", payment_date="2026-08-01")
            response = client.post("/api/worker-management/salaries/1/pay", headers=admin_headers, json={})
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["payment_status"] == "paid"

    def test_update_salary_success(self, client, admin_headers):
        """Test admin can update a salary record."""
        with patch("backend.modules.worker_management.service.WorkerManagementService.update_salary") as mock_update:
            mock_update.return_value = _salary(id=1, bonuses=500.0, net_amount=5200.0)
            response = client.put("/api/worker-management/salaries/1", headers=admin_headers, json={
                "bonuses": 500.0,
            })
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["bonuses"] == 500.0

    def test_delete_salary_success(self, client, admin_headers):
        """Test admin can delete a salary record."""
        with patch("backend.modules.worker_management.service.WorkerManagementService.delete_salary") as mock_delete:
            mock_delete.return_value = True
            response = client.delete("/api/worker-management/salaries/1", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True


class TestAdvances:
    """Tests for advance endpoints."""

    def test_get_all_advances_success(self, client, admin_headers):
        """Test admin can list advance records."""
        advances = [_advance(id=1)]
        with patch("backend.modules.worker_management.service.WorkerManagementService.get_all_advances") as mock_get:
            mock_get.return_value = advances
            response = client.get("/api/worker-management/advances/", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"][0]["amount"] == 300.0

    def test_create_advance_success(self, client, manager_headers):
        """Test manager can create an advance record."""
        with patch("backend.modules.worker_management.service.WorkerManagementService.create_advance") as mock_create:
            mock_create.return_value = _advance(id=1)
            response = client.post("/api/worker-management/advances/", headers=manager_headers, json={
                "worker_id": 1,
                "amount": 300.0,
                "advance_date": "2026-07-10",
            })
            assert response.status_code == 201
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["status"] == "paid"

    def test_create_advance_invalid_amount(self, client, admin_headers):
        """Test create advance returns 400 on invalid amount."""
        with patch("backend.modules.worker_management.service.WorkerManagementService.create_advance") as mock_create:
            mock_create.side_effect = ValueError("Amount must be greater than zero")
            response = client.post("/api/worker-management/advances/", headers=admin_headers, json={
                "worker_id": 1,
                "amount": 0,
                "advance_date": "2026-07-10",
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_update_advance_success(self, client, admin_headers):
        """Test admin can update an advance record."""
        with patch("backend.modules.worker_management.service.WorkerManagementService.update_advance") as mock_update:
            mock_update.return_value = _advance(id=1, status="settled")
            response = client.put("/api/worker-management/advances/1", headers=admin_headers, json={
                "status": "settled",
            })
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["status"] == "settled"

    def test_delete_advance_success(self, client, admin_headers):
        """Test admin can delete an advance record."""
        with patch("backend.modules.worker_management.service.WorkerManagementService.delete_advance") as mock_delete:
            mock_delete.return_value = True
            response = client.delete("/api/worker-management/advances/1", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True


class TestStatistics:
    """Tests for statistics endpoint."""

    def test_statistics_success(self, client, admin_headers):
        """Test admin can retrieve worker management statistics."""
        stats = {
            "total_workers": 8,
            "active_workers": 6,
            "attendance_by_status": {"present": 5, "absent": 1, "late": 1, "half_day": 0, "leave": 1},
            "today_attendance": 3,
            "pending_salary_count": 2,
            "pending_salary_total": 9800.0,
            "total_salaries_paid": 1,
            "total_advances": 3,
            "outstanding_advances": 450.0,
            "recent_workers": [],
        }
        with patch("backend.modules.worker_management.service.WorkerManagementService.get_statistics") as mock_stats:
            mock_stats.return_value = stats
            response = client.get("/api/worker-management/statistics", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["total_workers"] == 8
            assert data["data"]["attendance_by_status"]["present"] == 5
            assert data["data"]["outstanding_advances"] == 450.0

    def test_statistics_no_token(self, client):
        """Test unauthenticated cannot retrieve statistics."""
        response = client.get("/api/worker-management/statistics")
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False


class TestReports:
    """Tests for report endpoints."""

    def test_attendance_report_success(self, client, admin_headers):
        """Test admin can retrieve the attendance report."""
        report = [
            {
                "worker_id": 1,
                "worker_name": "Ahmed Ali",
                "total_days": 20,
                "present_days": 18,
                "late_days": 1,
                "half_days": 0,
                "absent_days": 1,
                "leave_days": 0,
            }
        ]
        with patch("backend.modules.worker_management.service.WorkerManagementService.get_attendance_report") as mock_report:
            mock_report.return_value = report
            response = client.get(
                "/api/worker-management/reports/attendance?from=2026-07-01&to=2026-07-31",
                headers=admin_headers,
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"][0]["worker_name"] == "Ahmed Ali"
            assert data["data"][0]["present_days"] == 18

    def test_salary_report_success(self, client, admin_headers):
        """Test admin can retrieve the salary report."""
        report = [
            {
                "id": 1,
                "worker_id": 1,
                "worker_name": "Ahmed Ali",
                "salary_period": "2026-07",
                "base_salary": 5000.0,
                "bonuses": 200.0,
                "deductions": 0.0,
                "advances_deduction": 300.0,
                "net_amount": 4900.0,
                "payment_status": "pending",
                "payment_date": None,
            }
        ]
        with patch("backend.modules.worker_management.service.WorkerManagementService.get_salary_report") as mock_report:
            mock_report.return_value = report
            response = client.get(
                "/api/worker-management/reports/salaries?from=2026-07&to=2026-07",
                headers=admin_headers,
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"][0]["net_amount"] == 4900.0

    def test_reports_no_token(self, client):
        """Test unauthenticated cannot retrieve reports."""
        response = client.get("/api/worker-management/reports/attendance")
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False
