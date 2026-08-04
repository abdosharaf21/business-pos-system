"""Tests for Purchase history API endpoints.

Uses mocked services so no real database is needed. Follows the same
pattern as other module tests (service patched, routes exercised).
"""

from unittest.mock import patch

from backend.modules.purchases.model import Purchase, PurchaseItem
from backend.modules.purchases.validator import PurchaseValidator


def _purchase(purchase_id=5, invoice_number="PO-20260801-00005", **overrides):
    """Build a Purchase model instance with standard attribute values."""
    data = dict(
        id=purchase_id,
        supplier_id=2,
        supplier_name="Acme Supplies",
        user_id=1,
        user_name="Admin User",
        invoice_number=invoice_number,
        total_amount=1500.0,
        status="completed",
        payment_method="transfer",
        notes="Urgent restock",
        created_at=None,
    )
    data.update(overrides)
    return Purchase(
        id=data["id"],
        supplier_id=data["supplier_id"],
        supplier_name=data["supplier_name"],
        user_id=data["user_id"],
        user_name=data["user_name"],
        invoice_number=data["invoice_number"],
        total_amount=data["total_amount"],
        status=data["status"],
        payment_method=data["payment_method"],
        notes=data["notes"],
        created_at=data["created_at"],
    )


def _purchase_dict(purchase_id=5, invoice_number="PO-20260801-00005", **overrides):
    """Build a purchase dict in the shape returned by to_dict."""
    return _purchase(purchase_id, invoice_number, **overrides).to_dict()


class TestListPurchases:
    """Tests for GET /api/purchases/ (purchase history list)."""

    def test_list_success_paginated(self, client, admin_headers):
        """Test admin can list purchases in the paginated shape."""
        payload = {
            "items": [_purchase_dict()],
            "total": 1,
            "page": 1,
            "per_page": 20,
            "pages": 1,
        }
        with patch("backend.modules.purchases.service.PurchaseService.list_purchases") as mock:
            mock.return_value = payload
            response = client.get("/api/purchases/", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["items"][0]["payment_method"] == "transfer"
            assert data["data"]["items"][0]["notes"] == "Urgent restock"
            assert data["data"]["total"] == 1

    def test_list_passes_filters(self, client, admin_headers):
        """Test search, date, and date-range params are forwarded."""
        payload = {"items": [], "total": 0, "page": 1, "per_page": 10, "pages": 0}
        with patch("backend.modules.purchases.service.PurchaseService.list_purchases") as mock:
            mock.return_value = payload
            client.get(
                "/api/purchases/?search=acme&date=2026-08-01"
                "&date_from=2026-07-01&date_to=2026-08-31&page=2&per_page=10",
                headers=admin_headers,
            )
            filters = mock.call_args[0][0]
            assert filters["search"] == "acme"
            assert filters["date"] == "2026-08-01"
            assert filters["date_from"] == "2026-07-01"
            assert filters["date_to"] == "2026-08-31"
            assert filters["page"] == 2
            assert filters["per_page"] == 10

    def test_list_legacy_limit_offset(self, client, admin_headers):
        """Test legacy limit/offset params still return a plain array."""
        with patch("backend.modules.purchases.service.PurchaseService.get_all_purchases") as mock:
            mock.return_value = [_purchase()]
            response = client.get("/api/purchases/?limit=50&offset=0", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert isinstance(data["data"], list)
            assert data["data"][0]["payment_method"] == "transfer"

    def test_list_employee_allowed(self, client, employee_headers):
        """Test employees can view purchase history."""
        with patch("backend.modules.purchases.service.PurchaseService.list_purchases") as mock:
            mock.return_value = {"items": [], "total": 0, "page": 1, "per_page": 20, "pages": 0}
            response = client.get("/api/purchases/", headers=employee_headers)
            assert response.status_code == 200

    def test_list_requires_auth(self, client):
        """Test unauthenticated access is rejected."""
        response = client.get("/api/purchases/")
        assert response.status_code == 401


class TestGetPurchase:
    """Tests for GET /api/purchases/<id>."""

    def test_get_purchase_includes_new_fields(self, client, admin_headers):
        """Test purchase details include payment method and notes."""
        with patch("backend.modules.purchases.service.PurchaseService.get_purchase") as mock:
            mock.return_value = _purchase()
            response = client.get("/api/purchases/5", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["payment_method"] == "transfer"
            assert data["notes"] == "Urgent restock"

    def test_get_purchase_not_found(self, client, admin_headers):
        """Test missing purchase returns 404."""
        with patch("backend.modules.purchases.service.PurchaseService.get_purchase") as mock:
            mock.side_effect = ValueError("Purchase not found")
            response = client.get("/api/purchases/999", headers=admin_headers)
            assert response.status_code == 404
            assert response.get_json()["success"] is False


class TestGetPurchaseInvoice:
    """Tests for GET /api/purchases/<id>/invoice."""

    def test_invoice_includes_new_fields(self, client, admin_headers):
        """Test invoice data includes payment method and notes."""
        invoice = {
            "id": 5,
            "invoice_number": "PO-20260801-00005",
            "total_amount": 1500.0,
            "status": "completed",
            "payment_method": "cash",
            "notes": None,
            "created_at": "2026-08-01T10:00:00",
            "supplier_name": "Acme Supplies",
            "supplier_phone": "+123",
            "supplier_email": "acme@example.com",
            "supplier_address": "Warehouse 1",
            "user_name": "Admin User",
            "items": [],
        }
        with patch("backend.modules.purchases.service.PurchaseService.get_purchase_invoice") as mock:
            mock.return_value = invoice
            response = client.get("/api/purchases/5/invoice", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()["data"]
            assert data["payment_method"] == "cash"
            assert data["notes"] is None


class TestCreatePurchase:
    """Tests for POST /api/purchases/."""

    def test_create_with_payment_method_and_notes(self, client, admin_headers):
        """Test creation forwards payment_method and notes."""
        with patch("backend.modules.purchases.service.PurchaseService.create_purchase") as mock:
            mock.return_value = _purchase(payment_method="card", notes="Test note")
            response = client.post(
                "/api/purchases/",
                json={
                    "supplier_id": 2,
                    "payment_method": "card",
                    "notes": "Test note",
                    "items": [{"product_id": 1, "quantity": 2, "cost_price": 50}],
                },
                headers=admin_headers,
            )
            assert response.status_code == 201
            data = response.get_json()["data"]
            assert data["payment_method"] == "card"
            assert data["notes"] == "Test note"

    def test_create_defaults_payment_method(self, client, admin_headers):
        """Test creating without payment_method passes 'cash' through validation."""
        with patch("backend.modules.purchases.service.PurchaseService.create_purchase") as mock:
            mock.return_value = _purchase()
            response = client.post(
                "/api/purchases/",
                json={
                    "supplier_id": 2,
                    "items": [{"product_id": 1, "quantity": 2, "cost_price": 50}],
                },
                headers=admin_headers,
            )
            assert response.status_code == 201
            assert response.get_json()["data"]["payment_method"] == "transfer"

    def test_create_rejects_invalid_payment_method(self, client, admin_headers):
        """Test an unsupported payment method is rejected with 400."""
        response = client.post(
            "/api/purchases/",
            json={
                "supplier_id": 2,
                "payment_method": "bitcoin",
                "items": [{"product_id": 1, "quantity": 1, "cost_price": 10}],
            },
            headers=admin_headers,
        )
        assert response.status_code == 400
        assert response.get_json()["success"] is False

    def test_create_accepts_vodafone_cash(self, client, admin_headers):
        """Test creation accepts vodafone_cash as a payment method."""
        with patch("backend.modules.purchases.service.PurchaseService.create_purchase") as mock:
            mock.return_value = _purchase(payment_method="vodafone_cash", notes=None)
            response = client.post(
                "/api/purchases/",
                json={
                    "supplier_id": 2,
                    "payment_method": "vodafone_cash",
                    "items": [{"product_id": 1, "quantity": 1, "cost_price": 10}],
                },
                headers=admin_headers,
            )
            assert response.status_code == 201
            data = response.get_json()["data"]
            assert data["payment_method"] == "vodafone_cash"

    def test_validator_accepts_vodafone_cash(self):
        """Test the purchase validator accepts vodafone_cash."""
        assert PurchaseValidator.validate_payment_method("vodafone_cash") == "vodafone_cash"

    def test_validator_rejects_unknown_method(self):
        """Test the purchase validator still rejects unknown methods."""
        try:
            PurchaseValidator.validate_payment_method("bitcoin")
            assert False, "Expected ValueError for invalid payment method"
        except ValueError as exc:
            assert "Invalid payment method" in str(exc)

    def test_create_employee_forbidden(self, client, employee_headers):
        """Test employees cannot create purchases."""
        response = client.post(
            "/api/purchases/",
            json={"supplier_id": 2, "items": [{"product_id": 1, "quantity": 1, "cost_price": 10}]},
            headers=employee_headers,
        )
        assert response.status_code == 403


class TestExpiration:
    """Tests for purchase item expiration dates."""

    def test_purchase_item_to_dict_includes_expiration(self):
        """Test PurchaseItem.to_dict returns the expiration_date."""
        item = PurchaseItem(
            id=10,
            purchase_id=5,
            product_id=1,
            product_name="Milk",
            quantity=2,
            cost_price=50,
            subtotal=100,
            expiration_date="2026-12-31",
        )
        data = item.to_dict()
        assert data["expiration_date"] == "2026-12-31"

    def test_purchase_item_to_dict_omits_missing_expiration(self):
        """Test to_dict omits expiration_date when it is None."""
        item = PurchaseItem(
            id=10,
            purchase_id=5,
            product_id=1,
            quantity=1,
            cost_price=10,
            subtotal=10,
        )
        assert item.to_dict()["expiration_date"] is None

    def test_validator_normalizes_expiration_date(self):
        """Test the validator accepts and normalizes a valid date."""
        validated = PurchaseValidator.validate_expiration_date("2026-12-31")
        assert validated == "2026-12-31"

    def test_validator_allows_missing_expiration(self):
        """Test the validator returns None for empty expiration values."""
        assert PurchaseValidator.validate_expiration_date(None) is None
        assert PurchaseValidator.validate_expiration_date("") is None

    def test_validator_rejects_invalid_expiration(self):
        """Test the validator rejects a malformed expiration date."""
        try:
            PurchaseValidator.validate_expiration_date("31-12-2026")
            assert False, "Expected ValueError for invalid date"
        except ValueError as exc:
            assert "Expiration date" in str(exc)

    def test_validator_validate_item_keeps_expiration(self):
        """Test validate_item preserves the expiration_date field."""
        validated = PurchaseValidator.validate_item(
            {
                "product_id": 1,
                "quantity": 2,
                "cost_price": 50,
                "expiration_date": "2026-12-31",
            },
            0,
        )
        assert validated["expiration_date"] == "2026-12-31"

    def test_create_with_expiration_date(self, client, admin_headers):
        """Test creating a purchase forwards the expiration date."""
        with patch("backend.modules.purchases.service.PurchaseService.create_purchase") as mock:
            purchase = _purchase()
            purchase.items = [
                PurchaseItem(
                    id=1,
                    purchase_id=5,
                    product_id=1,
                    product_name="Milk",
                    quantity=2,
                    cost_price=50,
                    subtotal=100,
                    expiration_date="2026-12-31",
                )
            ]
            mock.return_value = purchase
            response = client.post(
                "/api/purchases/",
                json={
                    "supplier_id": 2,
                    "items": [
                        {
                            "product_id": 1,
                            "quantity": 2,
                            "cost_price": 50,
                            "expiration_date": "2026-12-31",
                        }
                    ],
                },
                headers=admin_headers,
            )
            assert response.status_code == 201
            items = response.get_json()["data"]["items"]
            assert items[0]["expiration_date"] == "2026-12-31"

    def test_invoice_includes_expiration_date(self, client, admin_headers):
        """Test invoice items carry the expiration date."""
        invoice = {
            "id": 5,
            "invoice_number": "PO-20260801-00005",
            "total_amount": 100.0,
            "status": "completed",
            "payment_method": "cash",
            "notes": None,
            "created_at": "2026-08-01T10:00:00",
            "supplier_name": "Acme Supplies",
            "supplier_phone": "+123",
            "supplier_email": "acme@example.com",
            "supplier_address": "Warehouse 1",
            "user_name": "Admin User",
            "items": [
                {
                    "quantity": 2,
                    "cost_price": 50,
                    "subtotal": 100,
                    "expiration_date": "2026-12-31",
                    "product_name": "Milk",
                    "barcode": "123",
                    "product_sku": "SKU-1",
                }
            ],
        }
        with patch("backend.modules.purchases.service.PurchaseService.get_purchase_invoice") as mock:
            mock.return_value = invoice
            response = client.get("/api/purchases/5/invoice", headers=admin_headers)
            assert response.status_code == 200
            items = response.get_json()["data"]["items"]
            assert items[0]["expiration_date"] == "2026-12-31"

    def test_get_purchase_includes_item_expiration(self, client, admin_headers):
        """Test purchase details expose item expiration dates."""
        purchase = _purchase()
        purchase.items = [
            PurchaseItem(
                id=1,
                purchase_id=5,
                product_id=1,
                product_name="Milk",
                quantity=2,
                cost_price=50,
                subtotal=100,
                expiration_date="2026-12-31",
            )
        ]
        with patch("backend.modules.purchases.service.PurchaseService.get_purchase") as mock:
            mock.return_value = purchase
            response = client.get("/api/purchases/5", headers=admin_headers)
            assert response.status_code == 200
            items = response.get_json()["data"]["items"]
            assert items[0]["expiration_date"] == "2026-12-31"
