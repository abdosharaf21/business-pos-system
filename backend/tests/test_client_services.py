"""Tests for Client Service Assignment API endpoints."""

from datetime import datetime
from unittest.mock import patch

from backend.modules.client_services.model import ClientService


def _dt(s: str) -> datetime:
    return datetime.fromisoformat(s)


def _cs(**kw):
    defaults = dict(id=1, client_id=1, service_id=1,
                    start_date=_dt("2024-01-01T00:00:00"),
                    end_date=_dt("2024-01-31T23:59:59"), status="active")
    defaults.update(kw)
    return ClientService(**defaults)


class TestGetClientServices:
    """Tests for GET /api/client-services/client/<client_id> endpoint."""

    def test_get_by_client_success(self, client, admin_headers):
        items = [_cs(id=1)]
        with patch("backend.modules.client_services.service.ClientServiceAssignmentService.get_client_services") as m:
            m.return_value = items
            response = client.get("/api/client-services/client/1", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert len(data["data"]) == 1

    def test_get_by_client_not_found(self, client, admin_headers):
        with patch("backend.modules.client_services.service.ClientServiceAssignmentService.get_client_services") as m:
            m.side_effect = ValueError("Client not found")
            response = client.get("/api/client-services/client/999", headers=admin_headers)
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_get_by_client_no_token(self, client):
        response = client.get("/api/client-services/client/1")
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False

    def test_get_by_client_employee(self, client, employee_headers):
        with patch("backend.modules.client_services.service.ClientServiceAssignmentService.get_client_services") as m:
            m.return_value = []
            response = client.get("/api/client-services/client/1", headers=employee_headers)
            assert response.status_code == 200


class TestGetServiceClients:
    """Tests for GET /api/client-services/service/<service_id> endpoint."""

    def test_get_by_service_success(self, client, admin_headers):
        items = [_cs(id=1)]
        with patch("backend.modules.client_services.service.ClientServiceAssignmentService.get_service_clients") as m:
            m.return_value = items
            response = client.get("/api/client-services/service/1", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True

    def test_get_by_service_not_found(self, client, admin_headers):
        with patch("backend.modules.client_services.service.ClientServiceAssignmentService.get_service_clients") as m:
            m.side_effect = ValueError("Service not found")
            response = client.get("/api/client-services/service/999", headers=admin_headers)
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False


class TestAssignService:
    """Tests for POST /api/client-services/<client_id>/assign/<service_id>."""

    def test_assign_success(self, client, admin_headers):
        a = _cs(id=1)
        with patch("backend.modules.client_services.service.ClientServiceAssignmentService.assign_service") as m:
            m.return_value = a
            response = client.post("/api/client-services/1/assign/1", headers=admin_headers, json={
                "start_date": "2024-01-01T00:00:00", "end_date": "2024-01-31T23:59:59"
            })
            assert response.status_code == 201
            data = response.get_json()
            assert data["success"] is True

    def test_assign_client_not_found(self, client, admin_headers):
        with patch("backend.modules.client_services.service.ClientServiceAssignmentService.assign_service") as m:
            m.side_effect = ValueError("Client not found")
            response = client.post("/api/client-services/999/assign/1", headers=admin_headers, json={
                "start_date": "2024-01-01T00:00:00"
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_assign_service_not_found(self, client, admin_headers):
        with patch("backend.modules.client_services.service.ClientServiceAssignmentService.assign_service") as m:
            m.side_effect = ValueError("Service not found")
            response = client.post("/api/client-services/1/assign/999", headers=admin_headers, json={
                "start_date": "2024-01-01T00:00:00"
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_assign_invalid_dates(self, client, admin_headers):
        with patch("backend.modules.client_services.service.ClientServiceAssignmentService.assign_service") as m:
            m.side_effect = ValueError("End date must be after start date")
            response = client.post("/api/client-services/1/assign/1", headers=admin_headers, json={
                "start_date": "2024-01-31T00:00:00", "end_date": "2024-01-01T00:00:00"
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_assign_invalid_status(self, client, admin_headers):
        response = client.post("/api/client-services/1/assign/1", headers=admin_headers, json={
            "status": "invalid"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_assign_duplicate(self, client, admin_headers):
        with patch("backend.modules.client_services.service.ClientServiceAssignmentService.assign_service") as m:
            m.side_effect = ValueError("Client already has this service assigned")
            response = client.post("/api/client-services/1/assign/1", headers=admin_headers, json={
                "start_date": "2024-01-01T00:00:00"
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_assign_employee_forbidden(self, client, employee_headers):
        response = client.post("/api/client-services/1/assign/1", headers=employee_headers, json={
            "start_date": "2024-01-01T00:00:00"
        })
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False

    def test_assign_manager(self, client, manager_headers):
        a = _cs(id=2)
        with patch("backend.modules.client_services.service.ClientServiceAssignmentService.assign_service") as m:
            m.return_value = a
            response = client.post("/api/client-services/1/assign/1", headers=manager_headers, json={
                "start_date": "2024-01-01T00:00:00"
            })
            assert response.status_code == 201
            assert response.get_json()["success"] is True


class TestUpdateAssignment:
    """Tests for PUT /api/client-services/<assignment_id>."""

    def test_update_success(self, client, admin_headers):
        a = _cs(id=1, status="completed")
        with patch("backend.modules.client_services.service.ClientServiceAssignmentService.update_assignment") as m:
            m.return_value = a
            response = client.put("/api/client-services/1", headers=admin_headers, json={
                "status": "completed"
            })
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["status"] == "completed"

    def test_update_not_found(self, client, admin_headers):
        with patch("backend.modules.client_services.service.ClientServiceAssignmentService.update_assignment") as m:
            m.side_effect = ValueError("Assignment not found")
            response = client.put("/api/client-services/999", headers=admin_headers, json={
                "status": "completed"
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_update_invalid_status(self, client, admin_headers):
        response = client.put("/api/client-services/1", headers=admin_headers, json={
            "status": "bad_status"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_update_employee_forbidden(self, client, employee_headers):
        response = client.put("/api/client-services/1", headers=employee_headers, json={
            "status": "completed"
        })
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False


class TestRemoveAssignment:
    """Tests for DELETE /api/client-services/<assignment_id>."""

    def test_remove_success(self, client, admin_headers):
        with patch("backend.modules.client_services.service.ClientServiceAssignmentService.remove_assignment") as m:
            m.return_value = True
            response = client.delete("/api/client-services/1", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True

    def test_remove_not_found(self, client, admin_headers):
        with patch("backend.modules.client_services.service.ClientServiceAssignmentService.remove_assignment") as m:
            m.side_effect = ValueError("Assignment not found")
            response = client.delete("/api/client-services/999", headers=admin_headers)
            assert response.status_code == 404
            data = response.get_json()
            assert data["success"] is False

    def test_remove_employee_forbidden(self, client, employee_headers):
        response = client.delete("/api/client-services/1", headers=employee_headers)
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False

    def test_remove_manager(self, client, manager_headers):
        with patch("backend.modules.client_services.service.ClientServiceAssignmentService.remove_assignment") as m:
            m.return_value = True
            response = client.delete("/api/client-services/1", headers=manager_headers)
            assert response.status_code == 200
            assert response.get_json()["success"] is True
