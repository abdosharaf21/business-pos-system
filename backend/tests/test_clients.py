"""Tests for Client API endpoints."""

from unittest.mock import patch

from backend.modules.clients.model import Client


def _client(**kw):
    defaults = dict(id=1, company_name="Test Co", contact_person="John", email="j@t.com",
                    phone="1234567890", address="Addr", status="lead")
    defaults.update(kw)
    return Client(**defaults)


class TestGetAllClients:
    """Tests for GET /api/clients/ endpoint."""

    def test_get_all_clients_success(self, client, admin_headers):
        """Test get all clients as admin."""
        clients = [_client(id=1, company_name="A"), _client(id=2, company_name="B")]
        with patch("backend.modules.clients.service.ClientService.get_all_clients") as mock_get:
            mock_get.return_value = clients
            response = client.get("/api/clients/", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert len(data["data"]) == 2

    def test_get_all_clients_employee(self, client, employee_headers):
        """Test get all clients as employee."""
        clients = [_client(id=1)]
        with patch("backend.modules.clients.service.ClientService.get_all_clients") as mock_get:
            mock_get.return_value = clients
            response = client.get("/api/clients/", headers=employee_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True

    def test_get_all_clients_no_token(self, client):
        """Test get all clients without token."""
        response = client.get("/api/clients/")
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False


class TestGetClientById:
    """Tests for GET /api/clients/<id> endpoint."""

    def test_get_client_by_id_success(self, client, admin_headers):
        """Test get client by ID success."""
        c = _client(id=1, company_name="Test Company")
        with patch("backend.modules.clients.service.ClientService.get_client") as mock_get:
            mock_get.return_value = c
            response = client.get("/api/clients/1", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["company_name"] == "Test Company"

    def test_get_client_by_id_not_found(self, client, admin_headers):
        """Test get client by ID not found."""
        with patch("backend.modules.clients.service.ClientService.get_client") as mock_get:
            mock_get.side_effect = ValueError("Client not found")
            response = client.get("/api/clients/999", headers=admin_headers)
            assert response.status_code == 404
            data = response.get_json()
            assert data["success"] is False

    def test_get_client_by_id_no_token(self, client):
        """Test get client by ID without token."""
        response = client.get("/api/clients/1")
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False


class TestCreateClient:
    """Tests for POST /api/clients/ endpoint."""

    def test_create_client_success(self, client, admin_headers):
        """Test create client success."""
        c = _client(id=1, company_name="New Company")
        with patch("backend.modules.clients.service.ClientService.create_client") as mock_create:
            mock_create.return_value = c
            response = client.post("/api/clients/", headers=admin_headers, json={
                "company_name": "New Company", "contact_person": "John Doe"
            })
            assert response.status_code == 201
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["company_name"] == "New Company"

    def test_create_client_missing_company_name(self, client, admin_headers):
        """Test create client with missing company_name."""
        response = client.post("/api/clients/", headers=admin_headers, json={
            "contact_person": "John Doe"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_create_client_missing_contact_person(self, client, admin_headers):
        """Test create client with missing contact_person."""
        response = client.post("/api/clients/", headers=admin_headers, json={
            "company_name": "New Company"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_create_client_invalid_status(self, client, admin_headers):
        """Test create client with invalid status."""
        response = client.post("/api/clients/", headers=admin_headers, json={
            "company_name": "New Company", "contact_person": "John Doe",
            "status": "invalid_status"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_create_client_employee_forbidden(self, client, employee_headers):
        """Test create client as employee (forbidden)."""
        response = client.post("/api/clients/", headers=employee_headers, json={
            "company_name": "New Company", "contact_person": "John Doe"
        })
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False

    def test_create_client_manager(self, client, manager_headers):
        """Test manager can create a client."""
        c = _client(id=2, company_name="Manager Co")
        with patch("backend.modules.clients.service.ClientService.create_client") as mock_create:
            mock_create.return_value = c
            response = client.post("/api/clients/", headers=manager_headers, json={
                "company_name": "Manager Co", "contact_person": "Jane"
            })
            assert response.status_code == 201
            data = response.get_json()
            assert data["success"] is True

    def test_create_client_duplicate_company(self, client, admin_headers):
        """Test create client with duplicate company name."""
        with patch("backend.modules.clients.service.ClientService.create_client") as mock_create:
            mock_create.side_effect = ValueError("Client with this company name already exists")
            response = client.post("/api/clients/", headers=admin_headers, json={
                "company_name": "Existing Company", "contact_person": "John Doe"
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False


class TestUpdateClient:
    """Tests for PUT /api/clients/<id> endpoint."""

    def test_update_client_success(self, client, admin_headers):
        """Test update client success."""
        c = _client(id=1, company_name="Updated Company")
        with patch("backend.modules.clients.service.ClientService.update_client") as mock_update:
            mock_update.return_value = c
            response = client.put("/api/clients/1", headers=admin_headers, json={
                "company_name": "Updated Company"
            })
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["company_name"] == "Updated Company"

    def test_update_client_not_found(self, client, admin_headers):
        """Test update client not found."""
        with patch("backend.modules.clients.service.ClientService.update_client") as mock_update:
            mock_update.side_effect = ValueError("Client not found")
            response = client.put("/api/clients/999", headers=admin_headers, json={
                "company_name": "Updated"
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_update_client_invalid_status(self, client, admin_headers):
        """Test update client with invalid status."""
        response = client.put("/api/clients/1", headers=admin_headers, json={
            "status": "bad_status"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_update_client_employee_forbidden(self, client, employee_headers):
        """Test update client as employee (forbidden)."""
        response = client.put("/api/clients/1", headers=employee_headers, json={
            "company_name": "Updated"
        })
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False

    def test_update_client_manager(self, client, manager_headers):
        """Test manager can update a client."""
        c = _client(id=1, company_name="Mgr Updated")
        with patch("backend.modules.clients.service.ClientService.update_client") as mock_update:
            mock_update.return_value = c
            response = client.put("/api/clients/1", headers=manager_headers, json={
                "company_name": "Mgr Updated"
            })
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True


class TestDeleteClient:
    """Tests for DELETE /api/clients/<id> endpoint."""

    def test_delete_client_success(self, client, admin_headers):
        """Test delete client success."""
        with patch("backend.modules.clients.service.ClientService.delete_client") as mock_delete:
            mock_delete.return_value = True
            response = client.delete("/api/clients/1", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["message"] == "Client deleted successfully"

    def test_delete_client_not_found(self, client, admin_headers):
        """Test delete client not found."""
        with patch("backend.modules.clients.service.ClientService.delete_client") as mock_delete:
            mock_delete.side_effect = ValueError("Client not found")
            response = client.delete("/api/clients/999", headers=admin_headers)
            assert response.status_code == 404
            data = response.get_json()
            assert data["success"] is False

    def test_delete_client_manager(self, client, manager_headers):
        """Test manager can now delete a client."""
        with patch("backend.modules.clients.service.ClientService.delete_client") as mock_delete:
            mock_delete.return_value = True
            response = client.delete("/api/clients/1", headers=manager_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True

    def test_delete_client_employee_forbidden(self, client, employee_headers):
        """Test employee cannot delete a client."""
        response = client.delete("/api/clients/1", headers=employee_headers)
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False


class TestUpdateClientStatus:
    """Tests for PUT /api/clients/<id>/status endpoint."""

    def test_update_client_status_success(self, client, admin_headers):
        """Test update client status success."""
        c = _client(id=1, status="customer")
        with patch("backend.modules.clients.service.ClientService.change_status") as mock_update:
            mock_update.return_value = c
            response = client.put("/api/clients/1/status", headers=admin_headers, json={
                "status": "customer"
            })
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["status"] == "customer"

    def test_update_client_status_missing(self, client, admin_headers):
        """Test update client status with missing status."""
        response = client.put("/api/clients/1/status", headers=admin_headers, json={})
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_update_client_status_invalid(self, client, admin_headers):
        """Test update client status with invalid status."""
        response = client.put("/api/clients/1/status", headers=admin_headers, json={
            "status": "invalid"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_update_client_status_not_found(self, client, admin_headers):
        """Test update client status not found."""
        with patch("backend.modules.clients.service.ClientService.change_status") as mock_update:
            mock_update.side_effect = ValueError("Client not found")
            response = client.put("/api/clients/999/status", headers=admin_headers, json={
                "status": "customer"
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_update_client_status_employee_forbidden(self, client, employee_headers):
        """Test employee cannot update client status."""
        response = client.put("/api/clients/1/status", headers=employee_headers, json={
            "status": "customer"
        })
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False

    def test_update_client_status_manager(self, client, manager_headers):
        """Test manager can update client status."""
        c = _client(id=1, status="prospect")
        with patch("backend.modules.clients.service.ClientService.change_status") as mock_update:
            mock_update.return_value = c
            response = client.put("/api/clients/1/status", headers=manager_headers, json={
                "status": "prospect"
            })
            assert response.status_code == 200
            assert response.get_json()["success"] is True
