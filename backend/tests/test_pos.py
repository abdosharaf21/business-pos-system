"""Tests for POS checkout endpoints and payment method validation.

Uses mocked repositories/services so no real database is needed.
Follows the same pattern as other module tests.
"""

from unittest.mock import MagicMock, patch

from backend.modules.pos.service import PosService


def _sale_dict():
    """Build a sale dict in the shape returned by checkout."""
    return {
        "id": 10,
        "invoice_number": "INV-20260804-00010",
        "total_amount": 120.0,
        "payment_method": "cash",
        "status": "completed",
        "items": [],
    }


class TestPosCheckoutRoute:
    """Tests for POST /api/pos/checkout."""

    def test_checkout_accepts_vodafone_cash(self, client, admin_headers):
        """Test checkout succeeds when payment_method is vodafone_cash."""
        sale = _sale_dict()
        sale["payment_method"] = "vodafone_cash"
        with patch("backend.modules.pos.service.PosService.checkout") as mock:
            mock.return_value = sale
            response = client.post(
                "/api/pos/checkout",
                json={
                    "items": [{"product_id": 1, "quantity": 2, "unit_price": 60}],
                    "payment_method": "vodafone_cash",
                },
                headers=admin_headers,
            )
            assert response.status_code == 201
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["payment_method"] == "vodafone_cash"

    def test_checkout_forwards_payment_method(self, client, employee_headers):
        """Test employees can checkout and the payment method is forwarded."""
        with patch("backend.modules.pos.service.PosService.checkout") as mock:
            mock.return_value = _sale_dict()
            client.post(
                "/api/pos/checkout",
                json={
                    "items": [{"product_id": 1, "quantity": 1, "unit_price": 50}],
                    "payment_method": "vodafone_cash",
                },
                headers=employee_headers,
            )
            args, _ = mock.call_args
            assert args[0]["payment_method"] == "vodafone_cash"
            assert args[1] == 3

    def test_checkout_requires_auth(self, client):
        """Test unauthenticated checkout is rejected."""
        response = client.post(
            "/api/pos/checkout",
            json={"items": [{"product_id": 1, "quantity": 1, "unit_price": 50}]},
        )
        assert response.status_code == 401

    def test_checkout_no_data(self, client, admin_headers):
        """Test checkout with an empty body returns 400."""
        response = client.post("/api/pos/checkout", json={}, headers=admin_headers)
        assert response.status_code == 400
        assert response.get_json()["success"] is False


class TestPosServiceValidation:
    """Unit tests for PosService payment method validation."""

    def _service(self):
        """Build a PosService backed by a mocked repository."""
        repo = MagicMock()
        sale = _sale_dict()
        sale["payment_method"] = "vodafone_cash"
        repo.create_checkout.return_value = sale
        return PosService(repo)

    def test_checkout_accepts_vodafone_cash(self):
        """Test the service accepts vodafone_cash as a payment method."""
        service = self._service()
        data = {
            "items": [{"product_id": 1, "quantity": 1, "unit_price": 50}],
            "payment_method": "vodafone_cash",
        }
        result = service.checkout(data, user_id=1)
        service._pos_repository.create_checkout.assert_called_once_with(
            user_id=1,
            items_data=[{"product_id": 1, "quantity": 1, "unit_price": 50.0}],
            customer_id=None,
            payment_method="vodafone_cash",
            discount=0.0,
        )
        assert result["payment_method"] == "vodafone_cash"

    def test_checkout_defaults_to_cash(self):
        """Test checkout without payment_method defaults to cash."""
        service = self._service()
        data = {"items": [{"product_id": 1, "quantity": 1, "unit_price": 50}]}
        service.checkout(data, user_id=1)
        service._pos_repository.create_checkout.assert_called_once_with(
            user_id=1,
            items_data=[{"product_id": 1, "quantity": 1, "unit_price": 50.0}],
            customer_id=None,
            payment_method="cash",
            discount=0.0,
        )

    def test_checkout_rejects_invalid_payment_method(self):
        """Test an unsupported payment method raises ValueError."""
        service = self._service()
        data = {
            "items": [{"product_id": 1, "quantity": 1, "unit_price": 50}],
            "payment_method": "bitcoin",
        }
        try:
            service.checkout(data, user_id=1)
            assert False, "Expected ValueError for invalid payment method"
        except ValueError as exc:
            assert "Invalid payment method" in str(exc)
        service._pos_repository.create_checkout.assert_not_called()

    def test_checkout_rejects_unknown_method_via_api(self, client, admin_headers):
        """Test the API rejects an unknown payment method with 400."""
        with patch("backend.modules.pos.service.PosService.checkout") as mock:
            mock.side_effect = ValueError("Invalid payment method: bitcoin")
            response = client.post(
                "/api/pos/checkout",
                json={
                    "items": [{"product_id": 1, "quantity": 1, "unit_price": 50}],
                    "payment_method": "bitcoin",
                },
                headers=admin_headers,
            )
            assert response.status_code == 400
            assert response.get_json()["success"] is False
