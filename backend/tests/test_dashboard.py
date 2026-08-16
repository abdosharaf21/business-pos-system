"""Tests for Dashboard API endpoints."""

from unittest.mock import patch


class TestGetDashboardStatistics:
    """Tests for GET /api/dashboard/statistics endpoint."""

    def test_get_statistics_success(self, client, admin_headers):
        """Test admin can view statistics."""
        stats = {
            "total_workers": 10,
            "workers_by_status": {"active": 8, "inactive": 2},
            "total_expenses": 150,
            "monthly_expenses": 30000.0,
            "today_expenses": 450.0,
            "month_expenses": 30000.0,
            "total_advances": 5,
            "outstanding_advances": 1250.0,
            "recent_workers": [],
            "recent_expenses": [],
            "expenses_by_status": {"pending": 0, "completed": 150},
        }
        with patch("backend.modules.dashboard.service.DashboardService.get_dashboard_statistics") as mock_get:
            mock_get.return_value = stats
            response = client.get("/api/dashboard/statistics", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["total_workers"] == 10

    def test_get_statistics_manager(self, client, manager_headers):
        """Test manager can view statistics."""
        stats = {
            "total_workers": 5,
            "workers_by_status": {"active": 4, "inactive": 1},
            "total_expenses": 75,
            "monthly_expenses": 15000.0,
            "today_expenses": 200.0,
            "month_expenses": 15000.0,
            "total_advances": 3,
            "outstanding_advances": 750.0,
            "recent_workers": [],
            "recent_expenses": [],
            "expenses_by_status": {"pending": 0, "completed": 75},
        }
        with patch("backend.modules.dashboard.service.DashboardService.get_dashboard_statistics") as mock_get:
            mock_get.return_value = stats
            response = client.get("/api/dashboard/statistics", headers=manager_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True

    def test_get_statistics_employee(self, client, employee_headers):
        """Test employee can also view statistics."""
        stats = {
            "total_workers": 3,
            "workers_by_status": {"active": 2, "inactive": 1},
            "total_expenses": 40,
            "monthly_expenses": 8000.0,
            "today_expenses": 100.0,
            "month_expenses": 8000.0,
            "total_advances": 2,
            "outstanding_advances": 500.0,
            "recent_workers": [],
            "recent_expenses": [],
            "expenses_by_status": {"pending": 0, "completed": 40},
        }
        with patch("backend.modules.dashboard.service.DashboardService.get_dashboard_statistics") as mock_get:
            mock_get.return_value = stats
            response = client.get("/api/dashboard/statistics", headers=employee_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True

    def test_get_statistics_no_token(self, client):
        """Test unauthenticated cannot view statistics."""
        response = client.get("/api/dashboard/statistics")
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False

    def test_get_statistics_db_error(self, client, admin_headers):
        """Test database error returns 500."""
        with patch("backend.modules.dashboard.service.DashboardService.get_dashboard_statistics") as mock_get:
            mock_get.side_effect = Exception("Database connection error")
            response = client.get("/api/dashboard/statistics", headers=admin_headers)
            assert response.status_code == 500
            data = response.get_json()
            assert data["success"] is False