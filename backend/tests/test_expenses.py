"""Tests for Expenses API endpoints.

Tests the /api/expenses/* endpoints including CRUD operations,
filters, pagination, categories, summary, monthly/yearly reports,
category/payment-method reports, and role-based access control.
"""

from unittest.mock import patch, Mock


def _expense_dict(**kw):
    """Create a fake expense dict."""
    defaults = dict(
        id=1,
        title="Office rent",
        category_id=1,
        category_name="Rent",
        amount=5000.0,
        payment_method="Cash",
        notes="Monthly rent",
        expense_date="2026-08-01",
        created_by=1,
        created_by_name="Admin User",
        created_at="2026-08-01T10:00:00",
        updated_at="2026-08-01T10:00:00",
    )
    defaults.update(kw)
    return defaults


def _expense_mock(**kw):
    """Create a mock expense with a to_dict returning the dict."""
    expense = Mock()
    expense.to_dict.return_value = _expense_dict(**kw)
    return expense


class TestCreateExpense:
    """Tests for POST /api/expenses/ endpoint."""

    def test_create_success(self, client, admin_headers):
        """Test admin can create an expense."""
        expense = _expense_mock()
        with patch("backend.modules.expenses.service.ExpenseService.create_expense") as mock_create:
            mock_create.return_value = expense
            response = client.post(
                "/api/expenses/",
                headers=admin_headers,
                json={
                    "title": "Office rent",
                    "category_id": 1,
                    "amount": 5000,
                    "payment_method": "Cash",
                    "expense_date": "2026-08-01",
                },
            )
            assert response.status_code == 201
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["category_id"] == 1
            assert data["data"]["category_name"] == "Rent"
            mock_create.assert_called_once()

    def test_create_amount_negative(self, client, admin_headers):
        """Test negative amount returns 400."""
        with patch("backend.modules.expenses.service.ExpenseService.create_expense") as mock_create:
            mock_create.side_effect = ValueError("Expense amount must be greater than zero")
            response = client.post(
                "/api/expenses/",
                headers=admin_headers,
                json={"title": "Rent", "category_id": 1, "amount": -5, "expense_date": "2026-08-01"},
            )
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_create_missing_title(self, client, admin_headers):
        """Test missing title returns 400."""
        with patch("backend.modules.expenses.service.ExpenseService.create_expense") as mock_create:
            mock_create.side_effect = ValueError("Expense title is required")
            response = client.post(
                "/api/expenses/",
                headers=admin_headers,
                json={"category_id": 1, "amount": 100, "expense_date": "2026-08-01"},
            )
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_create_missing_category(self, client, admin_headers):
        """Test missing category id returns 400."""
        with patch("backend.modules.expenses.service.ExpenseService.create_expense") as mock_create:
            mock_create.side_effect = ValueError("Expense category is required")
            response = client.post(
                "/api/expenses/",
                headers=admin_headers,
                json={"title": "Rent", "amount": 100, "expense_date": "2026-08-01"},
            )
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_create_missing_date(self, client, admin_headers):
        """Test missing expense date returns 400."""
        with patch("backend.modules.expenses.service.ExpenseService.create_expense") as mock_create:
            mock_create.side_effect = ValueError("Expense date is required")
            response = client.post(
                "/api/expenses/",
                headers=admin_headers,
                json={"title": "Rent", "category_id": 1, "amount": 100},
            )
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_create_employee_forbidden(self, client, employee_headers):
        """Test employees cannot create expenses."""
        response = client.post(
            "/api/expenses/",
            headers=employee_headers,
            json={"title": "Rent", "category_id": 1, "amount": 100, "expense_date": "2026-08-01"},
        )
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False

    def test_create_requires_auth(self, client):
        """Test unauthenticated request returns 401."""
        response = client.post(
            "/api/expenses/",
            json={"title": "Rent", "category_id": 1, "amount": 100, "expense_date": "2026-08-01"},
        )
        assert response.status_code == 401


class TestGetExpenses:
    """Tests for GET /api/expenses/ endpoint."""

    def test_list_success(self, client, admin_headers):
        """Test admin can list expenses with pagination."""
        result = {
            "items": [_expense_dict()],
            "total": 1,
            "page": 1,
            "per_page": 20,
            "pages": 1,
        }
        with patch("backend.modules.expenses.service.ExpenseService.list_expenses") as mock_list:
            mock_list.return_value = result
            response = client.get("/api/expenses/", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["total"] == 1
            assert data["data"]["items"][0]["title"] == "Office rent"

    def test_list_with_filters(self, client, admin_headers):
        """Test list passes filters to the service."""
        result = {"items": [], "total": 0, "page": 1, "per_page": 20, "pages": 0}
        with patch("backend.modules.expenses.service.ExpenseService.list_expenses") as mock_list:
            mock_list.return_value = result
            response = client.get(
                "/api/expenses/",
                headers=admin_headers,
                query_string={
                    "category_id": 1,
                    "payment_method": "Cash",
                    "start_date": "2026-01-01",
                    "end_date": "2026-12-31",
                    "search": "office",
                    "sort": "amount",
                    "order": "asc",
                    "page": 2,
                    "per_page": 10,
                },
            )
            assert response.status_code == 200
            kwargs = mock_list.call_args[0][0]
            assert kwargs["category_id"] == "1"
            assert kwargs["payment_method"] == "Cash"
            assert kwargs["start_date"] == "2026-01-01"
            assert kwargs["sort"] == "amount"
            assert kwargs["order"] == "asc"

    def test_list_invalid_date(self, client, admin_headers):
        """Test invalid date filter returns 400."""
        with patch("backend.modules.expenses.service.ExpenseService.list_expenses") as mock_list:
            mock_list.side_effect = ValueError("start_date must be a valid date in YYYY-MM-DD format")
            response = client.get(
                "/api/expenses/",
                headers=admin_headers,
                query_string={"start_date": "bogus"},
            )
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_list_employee_allowed(self, client, employee_headers):
        """Test employees can view expenses (read-only)."""
        result = {"items": [], "total": 0, "page": 1, "per_page": 20, "pages": 0}
        with patch("backend.modules.expenses.service.ExpenseService.list_expenses") as mock_list:
            mock_list.return_value = result
            response = client.get("/api/expenses/", headers=employee_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True

    def test_get_by_id_success(self, client, admin_headers):
        """Test admin can get a single expense."""
        expense = _expense_mock()
        with patch("backend.modules.expenses.service.ExpenseService.get_expense") as mock_get:
            mock_get.return_value = expense
            response = client.get("/api/expenses/1", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["id"] == 1

    def test_get_by_id_employee_allowed(self, client, employee_headers):
        """Test employees can view a single expense."""
        expense = _expense_mock()
        with patch("backend.modules.expenses.service.ExpenseService.get_expense") as mock_get:
            mock_get.return_value = expense
            response = client.get("/api/expenses/1", headers=employee_headers)
            assert response.status_code == 200
            assert response.get_json()["success"] is True

    def test_get_by_id_not_found(self, client, admin_headers):
        """Test missing expense returns 404."""
        with patch("backend.modules.expenses.service.ExpenseService.get_expense") as mock_get:
            mock_get.side_effect = ValueError("Expense not found")
            response = client.get("/api/expenses/999", headers=admin_headers)
            assert response.status_code == 404
            data = response.get_json()
            assert data["success"] is False


class TestExpenseCategories:
    """Tests for GET /api/expenses/categories endpoint."""

    def _category_dict(self, cid, name):
        """Create a fake category dict."""
        return {
            "id": cid,
            "name": name,
            "description": f"{name} description",
            "created_at": "2026-08-01T10:00:00",
        }

    def test_categories_success(self, client, admin_headers):
        """Test admin can list expense categories."""
        category = Mock()
        category.to_dict.return_value = self._category_dict(1, "Rent")
        with patch("backend.modules.expenses.service.ExpenseService.get_categories") as mock_cats:
            mock_cats.return_value = [category]
            response = client.get("/api/expenses/categories", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"][0]["name"] == "Rent"

    def test_categories_employee_allowed(self, client, employee_headers):
        """Test employees can list expense categories."""
        with patch("backend.modules.expenses.service.ExpenseService.get_categories") as mock_cats:
            mock_cats.return_value = []
            response = client.get("/api/expenses/categories", headers=employee_headers)
            assert response.status_code == 200
            assert response.get_json()["success"] is True

    def test_categories_requires_auth(self, client):
        """Test unauthenticated request returns 401."""
        response = client.get("/api/expenses/categories")
        assert response.status_code == 401


class TestUpdateExpense:
    """Tests for PUT /api/expenses/{id} endpoint."""

    def test_update_success(self, client, admin_headers):
        """Test admin can update an expense."""
        expense = _expense_mock(title="Updated rent", amount=6000.0)
        with patch("backend.modules.expenses.service.ExpenseService.update_expense") as mock_update:
            mock_update.return_value = expense
            response = client.put(
                "/api/expenses/1",
                headers=admin_headers,
                json={"title": "Updated rent", "amount": 6000},
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["amount"] == 6000.0

    def test_update_invalid_category(self, client, admin_headers):
        """Test updating with a non-existent category returns 400."""
        with patch("backend.modules.expenses.service.ExpenseService.update_expense") as mock_update:
            mock_update.side_effect = ValueError("Expense category does not exist")
            response = client.put(
                "/api/expenses/1",
                headers=admin_headers,
                json={"category_id": 999},
            )
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_update_not_found(self, client, admin_headers):
        """Test updating missing expense returns 404."""
        with patch("backend.modules.expenses.service.ExpenseService.update_expense") as mock_update:
            mock_update.side_effect = ValueError("Expense not found")
            response = client.put(
                "/api/expenses/999",
                headers=admin_headers,
                json={"title": "Rent"},
            )
            assert response.status_code == 404
            data = response.get_json()
            assert data["success"] is False

    def test_update_employee_forbidden(self, client, employee_headers):
        """Test employees cannot update expenses."""
        response = client.put(
            "/api/expenses/1",
            headers=employee_headers,
            json={"title": "Rent"},
        )
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False


class TestDeleteExpense:
    """Tests for DELETE /api/expenses/{id} endpoint."""

    def test_delete_success(self, client, admin_headers):
        """Test admin can delete an expense."""
        with patch("backend.modules.expenses.service.ExpenseService.delete_expense") as mock_delete:
            mock_delete.return_value = True
            response = client.delete("/api/expenses/1", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True

    def test_delete_not_found(self, client, admin_headers):
        """Test deleting missing expense returns 404."""
        with patch("backend.modules.expenses.service.ExpenseService.delete_expense") as mock_delete:
            mock_delete.side_effect = ValueError("Expense not found")
            response = client.delete("/api/expenses/999", headers=admin_headers)
            assert response.status_code == 404
            data = response.get_json()
            assert data["success"] is False

    def test_delete_employee_forbidden(self, client, employee_headers):
        """Test employees cannot delete expenses."""
        response = client.delete("/api/expenses/1", headers=employee_headers)
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False


class TestExpenseSummary:
    """Tests for GET /api/expenses/summary endpoint."""

    def test_summary_success(self, client, admin_headers):
        """Test summary includes totals and highest category."""
        summary = {
            "total_count": 5,
            "total_expenses": 12000.0,
            "today_count": 1,
            "today_total": 500.0,
            "this_month_count": 3,
            "this_month_total": 7000.0,
            "this_year_count": 5,
            "this_year_total": 12000.0,
            "avg_monthly_total": 4000.0,
            "highest_category": "Rent",
            "highest_category_id": 1,
            "highest_category_total": 5000.0,
        }
        with patch("backend.modules.expenses.service.ExpenseService.get_summary") as mock_summary:
            mock_summary.return_value = summary
            response = client.get("/api/expenses/summary", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["data"]["highest_category"] == "Rent"
            assert data["data"]["highest_category_id"] == 1
            assert data["data"]["total_expenses"] == 12000.0

    def test_summary_employee_allowed(self, client, employee_headers):
        """Test employees can view the expense summary."""
        with patch("backend.modules.expenses.service.ExpenseService.get_summary") as mock_summary:
            mock_summary.return_value = {"total_expenses": 0.0}
            response = client.get("/api/expenses/summary", headers=employee_headers)
            assert response.status_code == 200
            assert response.get_json()["success"] is True


class TestExpenseMonthlyYearly:
    """Tests for GET /api/expenses/monthly and /api/expenses/yearly."""

    def test_monthly_success(self, client, admin_headers):
        """Test monthly report returns daily totals."""
        data = {"period": "monthly", "year": 2026, "month": 8, "data": [{"day": 1, "total": 100.0, "count": 1}]}
        with patch("backend.modules.expenses.service.ExpenseService.get_monthly") as mock_monthly:
            mock_monthly.return_value = data
            response = client.get(
                "/api/expenses/monthly",
                headers=admin_headers,
                query_string={"year": 2026, "month": 8},
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["period"] == "monthly"

    def test_monthly_invalid_month(self, client, admin_headers):
        """Test invalid month returns 400."""
        with patch("backend.modules.expenses.service.ExpenseService.get_monthly") as mock_monthly:
            mock_monthly.side_effect = ValueError("Month must be between 1 and 12")
            response = client.get(
                "/api/expenses/monthly",
                headers=admin_headers,
                query_string={"year": 2026, "month": 13},
            )
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_yearly_success(self, client, admin_headers):
        """Test yearly report returns monthly totals."""
        data = {"period": "yearly", "year": 2026, "data": [{"month": 1, "total": 500.0, "count": 2}]}
        with patch("backend.modules.expenses.service.ExpenseService.get_yearly") as mock_yearly:
            mock_yearly.return_value = data
            response = client.get(
                "/api/expenses/yearly",
                headers=admin_headers,
                query_string={"year": 2026},
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["period"] == "yearly"

    def test_monthly_employee_allowed(self, client, employee_headers):
        """Test employees can view monthly expenses."""
        with patch("backend.modules.expenses.service.ExpenseService.get_monthly") as mock_monthly:
            mock_monthly.return_value = {"period": "monthly", "year": 2026, "month": 8, "data": []}
            response = client.get("/api/expenses/monthly", headers=employee_headers)
            assert response.status_code == 200
            assert response.get_json()["success"] is True


class TestExpenseReports:
    """Tests for GET /api/expenses/by-category and /api/expenses/by-payment."""

    def test_by_category_success(self, client, admin_headers):
        """Test category breakdown report."""
        result = {
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
            "total_expenses": 100.0,
            "data": [{"category_id": 1, "category": "Rent", "total": 100.0, "count": 1}],
        }
        with patch("backend.modules.expenses.service.ExpenseService.get_category_breakdown") as mock_report:
            mock_report.return_value = result
            response = client.get(
                "/api/expenses/by-category",
                headers=admin_headers,
                query_string={"start_date": "2026-01-01", "end_date": "2026-12-31"},
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["data"][0]["category"] == "Rent"

    def test_by_payment_success(self, client, admin_headers):
        """Test payment method breakdown report."""
        result = {
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
            "total_expenses": 100.0,
            "data": [{"payment_method": "Cash", "total": 100.0, "count": 1}],
        }
        with patch("backend.modules.expenses.service.ExpenseService.get_payment_method_breakdown") as mock_report:
            mock_report.return_value = result
            response = client.get(
                "/api/expenses/by-payment",
                headers=admin_headers,
            )
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["data"][0]["payment_method"] == "Cash"

    def test_by_category_invalid_date(self, client, admin_headers):
        """Test invalid date range returns 400."""
        with patch("backend.modules.expenses.service.ExpenseService.get_category_breakdown") as mock_report:
            mock_report.side_effect = ValueError("start_date must be a valid date in YYYY-MM-DD format")
            response = client.get(
                "/api/expenses/by-category",
                headers=admin_headers,
                query_string={"start_date": "bogus"},
            )
            assert response.status_code == 400
            assert response.get_json()["success"] is False

    def test_by_category_employee_allowed(self, client, employee_headers):
        """Test employees can view the category breakdown."""
        with patch("backend.modules.expenses.service.ExpenseService.get_category_breakdown") as mock_report:
            mock_report.return_value = {"data": []}
            response = client.get("/api/expenses/by-category", headers=employee_headers)
            assert response.status_code == 200
            assert response.get_json()["success"] is True
