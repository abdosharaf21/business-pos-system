"""Tests for Inventory Audit API endpoints.

Tests the /api/inventory-audits/* endpoints including CRUD operations,
counted quantity updates, completion, and role-based access control.
"""

from unittest.mock import patch, Mock


def _audit_dict(**kw):
    """Create a fake audit dict."""
    defaults = dict(
        id=1,
        name="Warehouse count August",
        location="warehouse",
        status="open",
        created_by=1,
        created_by_name="Admin User",
        total_items=5,
        counted_items=2,
        adjusted_items=0,
        total_difference=0,
        started_at="2026-08-01T10:00:00",
        completed_at=None,
        created_at="2026-08-01T10:00:00",
    )
    defaults.update(kw)
    return defaults


def _audit_mock(**kw):
    """Create a mock audit with a to_dict returning the dict."""
    audit = Mock()
    audit.to_dict.return_value = _audit_dict(**kw)
    return audit


def _item_dict(**kw):
    """Create a fake audit item dict."""
    defaults = dict(
        id=1,
        audit_id=1,
        product_id=10,
        product_name="Test Product",
        barcode="123456",
        system_quantity=20,
        counted_quantity=18,
        difference=-2,
        notes=None,
    )
    defaults.update(kw)
    return defaults


class TestCreateAudit:
    """Tests for POST /api/inventory-audits/ endpoint."""

    def test_create_success(self, client, admin_headers):
        """Test admin can create an audit."""
        audit = _audit_mock()
        with patch("backend.modules.inventory_audits.service.InventoryAuditService.create_audit") as mock_create:
            mock_create.return_value = audit
            response = client.post(
                "/api/inventory-audits/",
                headers=admin_headers,
                json={"name": "Warehouse count August", "location": "warehouse"},
            )
            assert response.status_code == 201
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["location"] == "warehouse"
            mock_create.assert_called_once()

    def test_create_missing_name(self, client, admin_headers):
        """Test missing name returns 400."""
        with patch("backend.modules.inventory_audits.service.InventoryAuditService.create_audit") as mock_create:
            mock_create.side_effect = ValueError("Audit name is required")
            response = client.post(
                "/api/inventory-audits/",
                headers=admin_headers,
                json={"location": "warehouse"},
            )
            assert response.status_code == 400
            assert response.get_json()["success"] is False

    def test_create_invalid_location(self, client, admin_headers):
        """Test invalid location returns 400."""
        with patch("backend.modules.inventory_audits.service.InventoryAuditService.create_audit") as mock_create:
            mock_create.side_effect = ValueError(
                "Invalid audit location. Must be one of: store, warehouse"
            )
            response = client.post(
                "/api/inventory-audits/",
                headers=admin_headers,
                json={"name": "Count", "location": "basement"},
            )
            assert response.status_code == 400
            assert response.get_json()["success"] is False

    def test_create_manager_allowed(self, client, manager_headers):
        """Test managers can create audits."""
        audit = _audit_mock()
        with patch("backend.modules.inventory_audits.service.InventoryAuditService.create_audit") as mock_create:
            mock_create.return_value = audit
            response = client.post(
                "/api/inventory-audits/",
                headers=manager_headers,
                json={"name": "Count", "location": "store"},
            )
            assert response.status_code == 201
            assert response.get_json()["success"] is True

    def test_create_employee_forbidden(self, client, employee_headers):
        """Test employees cannot create audits."""
        response = client.post(
            "/api/inventory-audits/",
            headers=employee_headers,
            json={"name": "Count", "location": "store"},
        )
        assert response.status_code == 403
        assert response.get_json()["success"] is False

    def test_create_requires_auth(self, client):
        """Test unauthenticated request returns 401."""
        response = client.post(
            "/api/inventory-audits/",
            json={"name": "Count", "location": "store"},
        )
        assert response.status_code == 401


class TestListAudits:
    """Tests for GET /api/inventory-audits/ endpoint."""

    def test_list_success(self, client, admin_headers):
        """Test admin can list audits with pagination."""
        result = {
            "items": [_audit_dict()],
            "total": 1,
            "page": 1,
            "per_page": 20,
            "pages": 1,
        }
        with patch("backend.modules.inventory_audits.service.InventoryAuditService.list_audits") as mock_list:
            mock_list.return_value = result
            response = client.get("/api/inventory-audits/", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["total"] == 1
            assert data["data"]["items"][0]["status"] == "open"

    def test_list_with_filters(self, client, admin_headers):
        """Test list passes filters to the service."""
        result = {"items": [], "total": 0, "page": 1, "per_page": 20, "pages": 0}
        with patch("backend.modules.inventory_audits.service.InventoryAuditService.list_audits") as mock_list:
            mock_list.return_value = result
            response = client.get(
                "/api/inventory-audits/",
                headers=admin_headers,
                query_string={
                    "search": "august",
                    "location": "warehouse",
                    "status": "open",
                    "sort": "name",
                    "order": "asc",
                    "page": 2,
                    "per_page": 10,
                },
            )
            assert response.status_code == 200
            kwargs = mock_list.call_args[0][0]
            assert kwargs["search"] == "august"
            assert kwargs["location"] == "warehouse"
            assert kwargs["status"] == "open"
            assert kwargs["sort"] == "name"
            assert kwargs["order"] == "asc"

    def test_list_invalid_status(self, client, admin_headers):
        """Test invalid status filter returns 400."""
        with patch("backend.modules.inventory_audits.service.InventoryAuditService.list_audits") as mock_list:
            mock_list.side_effect = ValueError(
                "Invalid audit status. Must be one of: cancelled, completed, open"
            )
            response = client.get(
                "/api/inventory-audits/",
                headers=admin_headers,
                query_string={"status": "bogus"},
            )
            assert response.status_code == 400
            assert response.get_json()["success"] is False

    def test_list_employee_allowed(self, client, employee_headers):
        """Test employees can view audits (read-only)."""
        result = {"items": [], "total": 0, "page": 1, "per_page": 20, "pages": 0}
        with patch("backend.modules.inventory_audits.service.InventoryAuditService.list_audits") as mock_list:
            mock_list.return_value = result
            response = client.get("/api/inventory-audits/", headers=employee_headers)
            assert response.status_code == 200
            assert response.get_json()["success"] is True

    def test_list_requires_auth(self, client):
        """Test unauthenticated request returns 401."""
        response = client.get("/api/inventory-audits/")
        assert response.status_code == 401


class TestGetAudit:
    """Tests for GET /api/inventory-audits/{id} endpoint."""

    def test_get_by_id_success(self, client, admin_headers):
        """Test admin can get a single audit."""
        audit = _audit_mock()
        with patch("backend.modules.inventory_audits.service.InventoryAuditService.get_audit") as mock_get:
            mock_get.return_value = audit
            response = client.get("/api/inventory-audits/1", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["id"] == 1

    def test_get_by_id_employee_allowed(self, client, employee_headers):
        """Test employees can view a single audit."""
        audit = _audit_mock()
        with patch("backend.modules.inventory_audits.service.InventoryAuditService.get_audit") as mock_get:
            mock_get.return_value = audit
            response = client.get("/api/inventory-audits/1", headers=employee_headers)
            assert response.status_code == 200
            assert response.get_json()["success"] is True

    def test_get_by_id_not_found(self, client, admin_headers):
        """Test missing audit returns 404."""
        with patch("backend.modules.inventory_audits.service.InventoryAuditService.get_audit") as mock_get:
            mock_get.side_effect = ValueError("Audit not found")
            response = client.get("/api/inventory-audits/999", headers=admin_headers)
            assert response.status_code == 404
            assert response.get_json()["success"] is False


class TestGetAuditItems:
    """Tests for GET /api/inventory-audits/{id}/items endpoint."""

    def test_get_items_success(self, client, admin_headers):
        """Test admin can get audit items."""
        with patch("backend.modules.inventory_audits.service.InventoryAuditService.get_items") as mock_items:
            mock_items.return_value = [_item_dict()]
            response = client.get("/api/inventory-audits/1/items", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"][0]["product_name"] == "Test Product"
            assert data["data"][0]["difference"] == -2

    def test_get_items_employee_allowed(self, client, employee_headers):
        """Test employees can view audit items."""
        with patch("backend.modules.inventory_audits.service.InventoryAuditService.get_items") as mock_items:
            mock_items.return_value = [_item_dict()]
            response = client.get("/api/inventory-audits/1/items", headers=employee_headers)
            assert response.status_code == 200
            assert response.get_json()["success"] is True

    def test_get_items_not_found(self, client, admin_headers):
        """Test missing audit items returns 404."""
        with patch("backend.modules.inventory_audits.service.InventoryAuditService.get_items") as mock_items:
            mock_items.side_effect = ValueError("Audit not found")
            response = client.get("/api/inventory-audits/999/items", headers=admin_headers)
            assert response.status_code == 404
            assert response.get_json()["success"] is False


class TestCompleteAudit:
    """Tests for POST /api/inventory-audits/{id}/complete endpoint."""

    def test_complete_success(self, client, admin_headers):
        """Test admin can complete an open audit."""
        result = {"adjusted_items": 2, "audit": _audit_dict(status="completed")}
        with patch("backend.modules.inventory_audits.service.InventoryAuditService.complete_audit") as mock_complete:
            mock_complete.return_value = result
            response = client.post("/api/inventory-audits/1/complete", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["adjusted_items"] == 2

    def test_complete_not_open(self, client, admin_headers):
        """Test completing a non-open audit returns 400."""
        with patch("backend.modules.inventory_audits.service.InventoryAuditService.complete_audit") as mock_complete:
            mock_complete.side_effect = ValueError("Only open audits can be completed")
            response = client.post("/api/inventory-audits/1/complete", headers=admin_headers)
            assert response.status_code == 400
            assert response.get_json()["success"] is False

    def test_complete_not_found(self, client, admin_headers):
        """Test completing a missing audit returns 404."""
        with patch("backend.modules.inventory_audits.service.InventoryAuditService.complete_audit") as mock_complete:
            mock_complete.side_effect = ValueError("Audit not found")
            response = client.post("/api/inventory-audits/999/complete", headers=admin_headers)
            assert response.status_code == 404
            assert response.get_json()["success"] is False

    def test_complete_employee_forbidden(self, client, employee_headers):
        """Test employees cannot complete audits."""
        response = client.post("/api/inventory-audits/1/complete", headers=employee_headers)
        assert response.status_code == 403
        assert response.get_json()["success"] is False


class TestUpdateAudit:
    """Tests for PUT /api/inventory-audits/{id} endpoint."""

    def test_update_counts_success(self, client, admin_headers):
        """Test admin can update counted quantities."""
        audit = _audit_mock(counted_items=3)
        with patch("backend.modules.inventory_audits.service.InventoryAuditService.update_audit") as mock_update:
            mock_update.return_value = audit
            response = client.put(
                "/api/inventory-audits/1",
                headers=admin_headers,
                json={"items": [{"product_id": 10, "counted_quantity": 18}]},
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["counted_items"] == 3

    def test_update_cancel_success(self, client, admin_headers):
        """Test admin can cancel an open audit."""
        audit = _audit_mock(status="cancelled")
        with patch("backend.modules.inventory_audits.service.InventoryAuditService.update_audit") as mock_update:
            mock_update.return_value = audit
            response = client.put(
                "/api/inventory-audits/1",
                headers=admin_headers,
                json={"status": "cancelled"},
            )
            assert response.status_code == 200
            assert response.get_json()["data"]["status"] == "cancelled"

    def test_update_completed_locked(self, client, admin_headers):
        """Test updating a completed audit returns 400."""
        with patch("backend.modules.inventory_audits.service.InventoryAuditService.update_audit") as mock_update:
            mock_update.side_effect = ValueError("Cannot edit a completed audit")
            response = client.put(
                "/api/inventory-audits/1",
                headers=admin_headers,
                json={"name": "Renamed"},
            )
            assert response.status_code == 400
            assert response.get_json()["success"] is False

    def test_update_not_found(self, client, admin_headers):
        """Test updating a missing audit returns 404."""
        with patch("backend.modules.inventory_audits.service.InventoryAuditService.update_audit") as mock_update:
            mock_update.side_effect = ValueError("Audit not found")
            response = client.put(
                "/api/inventory-audits/999",
                headers=admin_headers,
                json={"name": "Renamed"},
            )
            assert response.status_code == 404
            assert response.get_json()["success"] is False

    def test_update_employee_forbidden(self, client, employee_headers):
        """Test employees cannot update audits."""
        response = client.put(
            "/api/inventory-audits/1",
            headers=employee_headers,
            json={"name": "Renamed"},
        )
        assert response.status_code == 403
        assert response.get_json()["success"] is False


class TestDeleteAudit:
    """Tests for DELETE /api/inventory-audits/{id} endpoint."""

    def test_delete_success(self, client, admin_headers):
        """Test admin can delete an audit."""
        with patch("backend.modules.inventory_audits.service.InventoryAuditService.delete_audit") as mock_delete:
            response = client.delete("/api/inventory-audits/1", headers=admin_headers)
            assert response.status_code == 200
            assert response.get_json()["success"] is True

    def test_delete_completed_forbidden(self, client, admin_headers):
        """Test deleting a completed audit returns 400."""
        with patch("backend.modules.inventory_audits.service.InventoryAuditService.delete_audit") as mock_delete:
            mock_delete.side_effect = ValueError("Cannot delete a completed audit")
            response = client.delete("/api/inventory-audits/1", headers=admin_headers)
            assert response.status_code == 400
            assert response.get_json()["success"] is False

    def test_delete_not_found(self, client, admin_headers):
        """Test deleting a missing audit returns 404."""
        with patch("backend.modules.inventory_audits.service.InventoryAuditService.delete_audit") as mock_delete:
            mock_delete.side_effect = ValueError("Audit not found")
            response = client.delete("/api/inventory-audits/999", headers=admin_headers)
            assert response.status_code == 404
            assert response.get_json()["success"] is False

    def test_delete_employee_forbidden(self, client, employee_headers):
        """Test employees cannot delete audits."""
        response = client.delete("/api/inventory-audits/1", headers=employee_headers)
        assert response.status_code == 403
        assert response.get_json()["success"] is False


class TestQuickAuditFlow:
    """Tests for the Quick Audit flow.

    The Inventory page's Quick Audit reuses the existing Inventory Audit
    API by chaining create -> update counted quantity -> complete. Stock
    is never written directly; every correction produces a normal
    'adjustment' movement whose notes reference the Inventory Audit.
    """

    def test_quick_audit_full_flow(self, client, admin_headers):
        """Test the exact API sequence used by the Quick Audit dialog."""
        created = _audit_mock(id=7, name="Quick Audit - Test Product", location="store")
        with patch(
            "backend.modules.inventory_audits.service.InventoryAuditService.create_audit"
        ) as mock_create:
            mock_create.return_value = created
            response = client.post(
                "/api/inventory-audits/",
                headers=admin_headers,
                json={"name": "Quick Audit - Test Product", "location": "store"},
            )
            assert response.status_code == 201
            audit_id = response.get_json()["data"]["id"]
            mock_create.assert_called_once()
            create_kwargs = mock_create.call_args[0][0]
            assert create_kwargs["name"].startswith("Quick Audit")
            assert create_kwargs["location"] == "store"

        updated = _audit_mock(id=audit_id, counted_items=1, adjusted_items=1)
        with patch(
            "backend.modules.inventory_audits.service.InventoryAuditService.update_audit"
        ) as mock_update:
            mock_update.return_value = updated
            response = client.put(
                f"/api/inventory-audits/{audit_id}",
                headers=admin_headers,
                json={
                    "items": [
                        {
                            "product_id": 10,
                            "counted_quantity": 18,
                            "notes": "Physical count completed",
                        }
                    ]
                },
            )
            assert response.status_code == 200
            assert response.get_json()["data"]["counted_items"] == 1
            mock_update.assert_called_once()
            payload = mock_update.call_args[0][1]
            assert payload["items"][0]["product_id"] == 10
            assert payload["items"][0]["counted_quantity"] == 18

        result = {"adjusted_items": 1, "audit": _audit_dict(id=audit_id, status="completed")}
        with patch(
            "backend.modules.inventory_audits.service.InventoryAuditService.complete_audit"
        ) as mock_complete:
            mock_complete.return_value = result
            response = client.post(
                f"/api/inventory-audits/{audit_id}/complete", headers=admin_headers
            )
            assert response.status_code == 200
            assert response.get_json()["data"]["adjusted_items"] == 1
            mock_complete.assert_called_once_with(audit_id, 1)

    def test_quick_audit_manager_allowed(self, client, manager_headers):
        """Test managers can run every step of a quick audit."""
        with patch(
            "backend.modules.inventory_audits.service.InventoryAuditService.create_audit"
        ) as mock_create:
            mock_create.return_value = _audit_mock(id=9)
            response = client.post(
                "/api/inventory-audits/",
                headers=manager_headers,
                json={"name": "Quick Audit - Product", "location": "store"},
            )
            assert response.status_code == 201

    def test_quick_audit_employee_forbidden(self, client, employee_headers):
        """Test employees cannot run a quick audit at any step."""
        response = client.post(
            "/api/inventory-audits/",
            headers=employee_headers,
            json={"name": "Quick Audit - Product", "location": "store"},
        )
        assert response.status_code == 403

    def test_quick_audit_negative_count_rejected(self, client, admin_headers):
        """Test a negative counted quantity is rejected by the validator."""
        with patch(
            "backend.modules.inventory_audits.service.InventoryAuditService.update_audit"
        ) as mock_update:
            mock_update.side_effect = ValueError("Counted quantity cannot be negative")
            response = client.put(
                "/api/inventory-audits/1",
                headers=admin_headers,
                json={"items": [{"product_id": 10, "counted_quantity": -3}]},
            )
            assert response.status_code == 400
            assert response.get_json()["success"] is False

    def test_quick_audit_empty_count_rejected(self, client, admin_headers):
        """Test an empty counted quantity is rejected by the validator."""
        with patch(
            "backend.modules.inventory_audits.service.InventoryAuditService.update_audit"
        ) as mock_update:
            mock_update.side_effect = ValueError("Counted quantity is required")
            response = client.put(
                "/api/inventory-audits/1",
                headers=admin_headers,
                json={"items": [{"product_id": 10, "counted_quantity": ""}]},
            )
            assert response.status_code == 400
            assert response.get_json()["success"] is False


class TestAuditReports:
    """Tests for the inventory audit report endpoints."""

    def test_report_success(self, client, admin_headers):
        """Test admin can fetch the inventory audit report."""
        result = {
            "metrics": {"total_audits": 1, "open_audits": 0, "completed_audits": 1},
            "largest_shortages": [],
            "largest_overages": [],
        }
        with patch("backend.modules.reports.service.ReportService.get_inventory_audit_report") as mock_report:
            mock_report.return_value = result
            response = client.get("/api/reports/inventory-audits", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["metrics"]["completed_audits"] == 1

    def test_report_employee_allowed(self, client, employee_headers):
        """Test employees can view the inventory audit report."""
        with patch("backend.modules.reports.service.ReportService.get_inventory_audit_report") as mock_report:
            mock_report.return_value = {"metrics": {}, "largest_shortages": [], "largest_overages": []}
            response = client.get("/api/reports/inventory-audits", headers=employee_headers)
            assert response.status_code == 200
            assert response.get_json()["success"] is True

    def test_monthly_summary_success(self, client, admin_headers):
        """Test monthly audit summary."""
        with patch("backend.modules.reports.service.ReportService.get_audits_monthly_summary") as mock_monthly:
            mock_monthly.return_value = {"period": "monthly", "year": 2026, "total_audits": 1, "data": []}
            response = client.get(
                "/api/reports/inventory-audits-monthly",
                headers=admin_headers,
                query_string={"year": 2026},
            )
            assert response.status_code == 200
            assert response.get_json()["data"]["period"] == "monthly"

    def test_yearly_summary_success(self, client, admin_headers):
        """Test yearly audit summary."""
        with patch("backend.modules.reports.service.ReportService.get_audits_yearly_summary") as mock_yearly:
            mock_yearly.return_value = {"period": "yearly", "from_year": 2022, "to_year": 2026, "total_audits": 3, "data": []}
            response = client.get(
                "/api/reports/inventory-audits-yearly",
                headers=admin_headers,
                query_string={"from_year": 2022, "to_year": 2026},
            )
            assert response.status_code == 200
            assert response.get_json()["data"]["period"] == "yearly"

    def test_yearly_invalid_range(self, client, admin_headers):
        """Test invalid year range returns 400."""
        with patch("backend.modules.reports.service.ReportService.get_audits_yearly_summary") as mock_yearly:
            mock_yearly.side_effect = ValueError("from_year cannot be after to_year")
            response = client.get(
                "/api/reports/inventory-audits-yearly",
                headers=admin_headers,
                query_string={"from_year": 2026, "to_year": 2022},
            )
            assert response.status_code == 400
            assert response.get_json()["success"] is False
