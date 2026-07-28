"""Tests for Service API endpoints."""

from unittest.mock import patch

from backend.modules.services.model import Service


def _service(**kw):
    defaults = dict(id=1, category_id=1, name="Test Svc", description="desc",
                    price=100.0, duration_days=30, status="active")
    defaults.update(kw)
    return Service(**defaults)


class TestGetAllServices:
    """Tests for GET /api/services/ endpoint."""

    def test_get_all_services_success(self, client, admin_headers):
        """Test get all services as admin."""
        services = [_service(id=1, name="A"), _service(id=2, name="B")]
        with patch("backend.modules.services.service.ServiceService.get_all_services") as mock_get:
            mock_get.return_value = services
            response = client.get("/api/services/", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert len(data["data"]) == 2

    def test_get_all_services_employee(self, client, employee_headers):
        """Test get all services as employee."""
        with patch("backend.modules.services.service.ServiceService.get_all_services") as mock_get:
            mock_get.return_value = [_service(id=1)]
            response = client.get("/api/services/", headers=employee_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True

    def test_get_all_services_no_token(self, client):
        """Test get all services without token."""
        response = client.get("/api/services/")
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False


class TestGetServiceById:
    """Tests for GET /api/services/<id> endpoint."""

    def test_get_service_by_id_success(self, client, admin_headers):
        """Test get service by ID success."""
        s = _service(id=1, name="Test Service")
        with patch("backend.modules.services.service.ServiceService.get_service") as mock_get:
            mock_get.return_value = s
            response = client.get("/api/services/1", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["name"] == "Test Service"

    def test_get_service_by_id_not_found(self, client, admin_headers):
        """Test get service by ID not found."""
        with patch("backend.modules.services.service.ServiceService.get_service") as mock_get:
            mock_get.side_effect = ValueError("Service not found")
            response = client.get("/api/services/999", headers=admin_headers)
            assert response.status_code == 404
            data = response.get_json()
            assert data["success"] is False


class TestGetServicesByCategory:
    """Tests for GET /api/services/category/<category_id> endpoint."""

    def test_get_services_by_category_success(self, client, admin_headers):
        """Test get services by category success."""
        services = [_service(id=1, name="A", category_id=1)]
        with patch("backend.modules.services.service.ServiceService.get_services_by_category") as mock_get:
            mock_get.return_value = services
            response = client.get("/api/services/category/1", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True

    def test_get_services_by_category_not_found(self, client, admin_headers):
        """Test get services by non-existent category."""
        with patch("backend.modules.services.service.ServiceService.get_services_by_category") as mock_get:
            mock_get.side_effect = ValueError("Category not found")
            response = client.get("/api/services/category/999", headers=admin_headers)
            assert response.status_code == 400


class TestCreateService:
    """Tests for POST /api/services/ endpoint."""

    def test_create_service_success(self, client, admin_headers):
        """Test create service success."""
        s = _service(id=1, name="New Service")
        with patch("backend.modules.services.service.ServiceService.create_service") as mock_create:
            mock_create.return_value = s
            response = client.post("/api/services/", headers=admin_headers, json={
                "name": "New Service", "category_id": 1
            })
            assert response.status_code == 201
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["name"] == "New Service"

    def test_create_service_missing_name(self, client, admin_headers):
        """Test create service with missing name."""
        response = client.post("/api/services/", headers=admin_headers, json={"category_id": 1})
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_create_service_missing_category_id(self, client, admin_headers):
        """Test create service with missing category_id."""
        response = client.post("/api/services/", headers=admin_headers, json={"name": "New Service"})
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_create_service_negative_price(self, client, admin_headers):
        """Test create service with negative price."""
        response = client.post("/api/services/", headers=admin_headers, json={
            "name": "New Service", "category_id": 1, "price": -50.00
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_create_service_invalid_status(self, client, admin_headers):
        """Test create service with invalid status."""
        response = client.post("/api/services/", headers=admin_headers, json={
            "name": "New Service", "category_id": 1, "status": "invalid"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_create_service_employee_forbidden(self, client, employee_headers):
        """Test create service as employee (forbidden)."""
        response = client.post("/api/services/", headers=employee_headers, json={
            "name": "New Service", "category_id": 1
        })
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False

    def test_create_service_manager(self, client, manager_headers):
        """Test manager can create a service."""
        s = _service(id=2, name="Mgr Service")
        with patch("backend.modules.services.service.ServiceService.create_service") as mock_create:
            mock_create.return_value = s
            response = client.post("/api/services/", headers=manager_headers, json={
                "name": "Mgr Service", "category_id": 1
            })
            assert response.status_code == 201
            assert response.get_json()["success"] is True

    def test_create_service_duplicate_name(self, client, admin_headers):
        """Test create service with duplicate name."""
        with patch("backend.modules.services.service.ServiceService.create_service") as mock_create:
            mock_create.side_effect = ValueError("Service with this name already exists")
            response = client.post("/api/services/", headers=admin_headers, json={
                "name": "Existing Service", "category_id": 1
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False


class TestUpdateService:
    """Tests for PUT /api/services/<id> endpoint."""

    def test_update_service_success(self, client, admin_headers):
        """Test update service success."""
        s = _service(id=1, name="Updated Service")
        with patch("backend.modules.services.service.ServiceService.update_service") as mock_update:
            mock_update.return_value = s
            response = client.put("/api/services/1", headers=admin_headers, json={
                "name": "Updated Service"
            })
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["name"] == "Updated Service"

    def test_update_service_not_found(self, client, admin_headers):
        """Test update service not found."""
        with patch("backend.modules.services.service.ServiceService.update_service") as mock_update:
            mock_update.side_effect = ValueError("Service not found")
            response = client.put("/api/services/999", headers=admin_headers, json={"name": "Updated"})
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_update_service_negative_price(self, client, admin_headers):
        """Test update service with negative price."""
        response = client.put("/api/services/1", headers=admin_headers, json={"price": -100.00})
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_update_service_employee_forbidden(self, client, employee_headers):
        """Test update service as employee (forbidden)."""
        response = client.put("/api/services/1", headers=employee_headers, json={"name": "Updated"})
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False


class TestDeleteService:
    """Tests for DELETE /api/services/<id> endpoint."""

    def test_delete_service_success(self, client, admin_headers):
        """Test delete service success."""
        with patch("backend.modules.services.service.ServiceService.delete_service") as mock_delete:
            mock_delete.return_value = True
            response = client.delete("/api/services/1", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["message"] == "Service deleted successfully"

    def test_delete_service_not_found(self, client, admin_headers):
        """Test delete service not found."""
        with patch("backend.modules.services.service.ServiceService.delete_service") as mock_delete:
            mock_delete.side_effect = ValueError("Service not found")
            response = client.delete("/api/services/999", headers=admin_headers)
            assert response.status_code == 404
            data = response.get_json()
            assert data["success"] is False

    def test_delete_service_employee_forbidden(self, client, employee_headers):
        """Test delete service as employee (forbidden)."""
        response = client.delete("/api/services/1", headers=employee_headers)
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False

    def test_delete_service_manager(self, client, manager_headers):
        """Test manager can delete a service."""
        with patch("backend.modules.services.service.ServiceService.delete_service") as mock_delete:
            mock_delete.return_value = True
            response = client.delete("/api/services/1", headers=manager_headers)
            assert response.status_code == 200
            assert response.get_json()["success"] is True
