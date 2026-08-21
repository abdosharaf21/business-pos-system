"""Tests for Deal API endpoints."""

from unittest.mock import patch

from backend.modules.deals.model import Deal


def _deal(**kw):
    defaults = dict(
        id=1, deal_number="DEAL-000001", client_id=1, service_id=1,
        package_name="Basic Package", sale_date="2026-08-20",
        price=1000.00, discount=0.00, tax=0.00, final_amount=1000.00,
        payment_status="pending", deal_status="draft", notes=None,
        created_by=1,
    )
    defaults.update(kw)
    return Deal(**defaults)


class TestGetAllDeals:
    """Tests for GET /api/deals/ endpoint."""

    def test_get_all_deals_success(self, client, admin_headers):
        """Test get all deals as admin."""
        deals = [_deal(id=1, deal_number="DEAL-000001"), _deal(id=2, deal_number="DEAL-000002")]
        with patch("backend.modules.deals.service.DealService.get_all_deals") as mock_get:
            mock_get.return_value = deals
            response = client.get("/api/deals/", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert len(data["data"]) == 2

    def test_get_all_deals_employee(self, client, employee_headers):
        """Test get all deals as employee."""
        deals = [_deal(id=1)]
        with patch("backend.modules.deals.service.DealService.get_all_deals") as mock_get:
            mock_get.return_value = deals
            response = client.get("/api/deals/", headers=employee_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True

    def test_get_all_deals_no_token(self, client):
        """Test get all deals without token."""
        response = client.get("/api/deals/")
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False


class TestGetDealById:
    """Tests for GET /api/deals/<id> endpoint."""

    def test_get_deal_by_id_success(self, client, admin_headers):
        """Test get deal by ID success."""
        d = _deal(id=1, deal_number="DEAL-000001")
        with patch("backend.modules.deals.service.DealService.get_deal") as mock_get:
            mock_get.return_value = d
            response = client.get("/api/deals/1", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["deal_number"] == "DEAL-000001"

    def test_get_deal_by_id_not_found(self, client, admin_headers):
        """Test get deal by ID not found."""
        with patch("backend.modules.deals.service.DealService.get_deal") as mock_get:
            mock_get.side_effect = ValueError("Deal not found")
            response = client.get("/api/deals/999", headers=admin_headers)
            assert response.status_code == 404
            data = response.get_json()
            assert data["success"] is False

    def test_get_deal_by_id_no_token(self, client):
        """Test get deal by ID without token."""
        response = client.get("/api/deals/1")
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False


class TestCreateDeal:
    """Tests for POST /api/deals/ endpoint."""

    def test_create_deal_success(self, client, admin_headers):
        """Test create deal success."""
        d = _deal(id=1, deal_number="DEAL-000001", client_id=1, service_id=1)
        with patch("backend.modules.deals.service.DealService.create_deal") as mock_create:
            mock_create.return_value = d
            response = client.post("/api/deals/", headers=admin_headers, json={
                "client_id": 1, "service_id": 1, "price": 1000,
                "sale_date": "2026-08-20",
            })
            assert response.status_code == 201
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["deal_number"] == "DEAL-000001"

    def test_create_deal_missing_client_id(self, client, admin_headers):
        """Test create deal with missing client_id."""
        with patch("backend.modules.deals.service.DealService.create_deal") as mock_create:
            mock_create.side_effect = ValueError("Client ID is required")
            response = client.post("/api/deals/", headers=admin_headers, json={
                "service_id": 1, "price": 1000,
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_create_deal_missing_service_id(self, client, admin_headers):
        """Test create deal with missing service_id."""
        with patch("backend.modules.deals.service.DealService.create_deal") as mock_create:
            mock_create.side_effect = ValueError("Service ID is required")
            response = client.post("/api/deals/", headers=admin_headers, json={
                "client_id": 1, "price": 1000,
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_create_deal_invalid_status(self, client, admin_headers):
        """Test create deal with invalid deal_status."""
        with patch("backend.modules.deals.service.DealService.create_deal") as mock_create:
            mock_create.side_effect = ValueError("Invalid deal status")
            response = client.post("/api/deals/", headers=admin_headers, json={
                "client_id": 1, "service_id": 1, "price": 1000,
                "deal_status": "invalid",
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_create_deal_employee_forbidden(self, client, employee_headers):
        """Test create deal as employee (forbidden)."""
        response = client.post("/api/deals/", headers=employee_headers, json={
            "client_id": 1, "service_id": 1, "price": 1000,
        })
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False

    def test_create_deal_manager(self, client, manager_headers):
        """Test manager can create a deal."""
        d = _deal(id=2, deal_number="DEAL-000002", client_id=1, service_id=1)
        with patch("backend.modules.deals.service.DealService.create_deal") as mock_create:
            mock_create.return_value = d
            response = client.post("/api/deals/", headers=manager_headers, json={
                "client_id": 1, "service_id": 1, "price": 500,
                "sale_date": "2026-08-20",
            })
            assert response.status_code == 201
            data = response.get_json()
            assert data["success"] is True


class TestUpdateDeal:
    """Tests for PUT /api/deals/<id> endpoint."""

    def test_update_deal_success(self, client, admin_headers):
        """Test update deal success."""
        d = _deal(id=1, deal_number="DEAL-000001", deal_status="confirmed")
        with patch("backend.modules.deals.service.DealService.update_deal") as mock_update:
            mock_update.return_value = d
            response = client.put("/api/deals/1", headers=admin_headers, json={
                "deal_status": "confirmed"
            })
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["deal_status"] == "confirmed"

    def test_update_deal_not_found(self, client, admin_headers):
        """Test update deal not found."""
        with patch("backend.modules.deals.service.DealService.update_deal") as mock_update:
            mock_update.side_effect = ValueError("Deal not found")
            response = client.put("/api/deals/999", headers=admin_headers, json={
                "deal_status": "confirmed"
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_update_deal_invalid_status(self, client, admin_headers):
        """Test update deal with invalid status."""
        with patch("backend.modules.deals.service.DealService.update_deal") as mock_update:
            mock_update.side_effect = ValueError("Invalid deal status")
            response = client.put("/api/deals/1", headers=admin_headers, json={
                "deal_status": "bad_status"
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_update_deal_employee_forbidden(self, client, employee_headers):
        """Test update deal as employee (forbidden)."""
        response = client.put("/api/deals/1", headers=employee_headers, json={
            "deal_status": "confirmed"
        })
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False

    def test_update_deal_manager(self, client, manager_headers):
        """Test manager can update a deal."""
        d = _deal(id=1, deal_number="DEAL-000001", deal_status="confirmed")
        with patch("backend.modules.deals.service.DealService.update_deal") as mock_update:
            mock_update.return_value = d
            response = client.put("/api/deals/1", headers=manager_headers, json={
                "deal_status": "confirmed"
            })
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True


class TestDeleteDeal:
    """Tests for DELETE /api/deals/<id> endpoint."""

    def test_delete_deal_success(self, client, admin_headers):
        """Test delete deal success."""
        with patch("backend.modules.deals.service.DealService.delete_deal") as mock_delete:
            mock_delete.return_value = True
            response = client.delete("/api/deals/1", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["message"] == "Deal deleted successfully"

    def test_delete_deal_not_found(self, client, admin_headers):
        """Test delete deal not found."""
        with patch("backend.modules.deals.service.DealService.delete_deal") as mock_delete:
            mock_delete.side_effect = ValueError("Deal not found")
            response = client.delete("/api/deals/999", headers=admin_headers)
            assert response.status_code == 404
            data = response.get_json()
            assert data["success"] is False

    def test_delete_deal_manager(self, client, manager_headers):
        """Test manager can delete a deal."""
        with patch("backend.modules.deals.service.DealService.delete_deal") as mock_delete:
            mock_delete.return_value = True
            response = client.delete("/api/deals/1", headers=manager_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True

    def test_delete_deal_employee_forbidden(self, client, employee_headers):
        """Test employee cannot delete a deal."""
        response = client.delete("/api/deals/1", headers=employee_headers)
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False


class TestChangeDealStatus:
    """Tests for PUT /api/deals/<id>/status endpoint."""

    def test_change_deal_status_success(self, client, admin_headers):
        """Test change deal status success."""
        d = _deal(id=1, deal_status="confirmed")
        with patch("backend.modules.deals.service.DealService.change_deal_status") as mock_update:
            mock_update.return_value = d
            response = client.put("/api/deals/1/status", headers=admin_headers, json={
                "status": "confirmed"
            })
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["deal_status"] == "confirmed"

    def test_change_deal_status_invalid(self, client, admin_headers):
        """Test change deal status with invalid status."""
        with patch("backend.modules.deals.service.DealService.change_deal_status") as mock_update:
            mock_update.side_effect = ValueError("Invalid deal status")
            response = client.put("/api/deals/1/status", headers=admin_headers, json={
                "status": "invalid"
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_change_deal_status_not_found(self, client, admin_headers):
        """Test change deal status not found."""
        with patch("backend.modules.deals.service.DealService.change_deal_status") as mock_update:
            mock_update.side_effect = ValueError("Deal not found")
            response = client.put("/api/deals/999/status", headers=admin_headers, json={
                "status": "confirmed"
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_change_deal_status_employee_forbidden(self, client, employee_headers):
        """Test employee cannot change deal status."""
        response = client.put("/api/deals/1/status", headers=employee_headers, json={
            "status": "confirmed"
        })
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False

    def test_change_deal_status_manager(self, client, manager_headers):
        """Test manager can change deal status."""
        d = _deal(id=1, deal_status="delivered")
        with patch("backend.modules.deals.service.DealService.change_deal_status") as mock_update:
            mock_update.return_value = d
            response = client.put("/api/deals/1/status", headers=manager_headers, json={
                "status": "delivered"
            })
            assert response.status_code == 200
            assert response.get_json()["success"] is True


class TestChangePaymentStatus:
    """Tests for PUT /api/deals/<id>/payment-status endpoint."""

    def test_change_payment_status_success(self, client, admin_headers):
        """Test change payment status success."""
        d = _deal(id=1, payment_status="paid")
        with patch("backend.modules.deals.service.DealService.change_payment_status") as mock_update:
            mock_update.return_value = d
            response = client.put("/api/deals/1/payment-status", headers=admin_headers, json={
                "status": "paid"
            })
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["payment_status"] == "paid"

    def test_change_payment_status_invalid(self, client, admin_headers):
        """Test change payment status with invalid status."""
        with patch("backend.modules.deals.service.DealService.change_payment_status") as mock_update:
            mock_update.side_effect = ValueError("Invalid payment status")
            response = client.put("/api/deals/1/payment-status", headers=admin_headers, json={
                "status": "invalid"
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_change_payment_status_employee_forbidden(self, client, employee_headers):
        """Test employee cannot change payment status."""
        response = client.put("/api/deals/1/payment-status", headers=employee_headers, json={
            "status": "paid"
        })
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False


class TestGetStatistics:
    """Tests for GET /api/deals/statistics endpoint."""

    def test_get_statistics_success(self, client, admin_headers):
        """Test get statistics success."""
        stats = {"total_deals": 10, "total_revenue": 5000.00}
        with patch("backend.modules.deals.service.DealService.get_statistics") as mock_stats:
            mock_stats.return_value = stats
            response = client.get("/api/deals/statistics", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["total_deals"] == 10

    def test_get_statistics_employee(self, client, employee_headers):
        """Test employee can get statistics."""
        stats = {"total_deals": 0, "total_revenue": 0}
        with patch("backend.modules.deals.service.DealService.get_statistics") as mock_stats:
            mock_stats.return_value = stats
            response = client.get("/api/deals/statistics", headers=employee_headers)
            assert response.status_code == 200
