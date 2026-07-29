"""Tests for Dashboard API endpoints."""

from unittest.mock import patch


class TestGetDashboardStatistics:
    """Tests for GET /api/dashboard/statistics endpoint."""

    def test_get_statistics_success(self, client, admin_headers):
        """Test admin can view statistics."""
        stats = {"total_products": 50, "total_categories": 8, "total_customers": 25, "total_suppliers": 5, "total_sales": 100, "total_purchases": 30, "low_stock_products": 3, "inventory_value": 15000.0, "todays_sales": 5, "todays_revenue": 450.0}
        with patch("backend.modules.dashboard.service.DashboardService.get_dashboard_statistics") as mock_get:
            mock_get.return_value = stats
            response = client.get("/api/dashboard/statistics", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["total_products"] == 50

    def test_get_statistics_manager(self, client, manager_headers):
        """Test manager can view statistics."""
        stats = {"total_products": 30, "total_categories": 5, "total_customers": 10, "total_suppliers": 3, "total_sales": 50, "total_purchases": 15, "low_stock_products": 1, "inventory_value": 8000.0, "todays_sales": 2, "todays_revenue": 200.0}
        with patch("backend.modules.dashboard.service.DashboardService.get_dashboard_statistics") as mock_get:
            mock_get.return_value = stats
            response = client.get("/api/dashboard/statistics", headers=manager_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True

    def test_get_statistics_employee(self, client, employee_headers):
        """Test employee can also view statistics."""
        stats = {"total_products": 30, "total_categories": 5, "total_customers": 10, "total_suppliers": 3, "total_sales": 50, "total_purchases": 15, "low_stock_products": 1, "inventory_value": 8000.0, "todays_sales": 2, "todays_revenue": 200.0}
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
