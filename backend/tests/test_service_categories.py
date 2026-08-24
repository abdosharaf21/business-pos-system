"""Tests for Service Category API endpoints."""

from unittest.mock import patch

from backend.modules.service_categories.model import ServiceCategory


def _cat(**kw):
    defaults = dict(id=1, name="Test Cat", description="desc")
    defaults.update(kw)
    return ServiceCategory(**defaults)


class TestGetAllCategories:
    """Tests for GET /api/service-categories/ endpoint."""

    def test_get_all_categories_success(self, client, admin_headers):
        """Test get all categories as admin."""
        cats = [_cat(id=1, name="A"), _cat(id=2, name="B")]
        with patch("backend.modules.service_categories.service.ServiceCategoryService.get_all_categories") as mock_get:
            mock_get.return_value = cats
            response = client.get("/api/service-categories/", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert len(data["data"]) == 2

    def test_get_all_categories_employee(self, client, employee_headers):
        """Test get all categories as employee."""
        with patch("backend.modules.service_categories.service.ServiceCategoryService.get_all_categories") as mock_get:
            mock_get.return_value = [_cat(id=1)]
            response = client.get("/api/service-categories/", headers=employee_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True

    def test_get_all_categories_no_token(self, client):
        """Test get all categories without token."""
        response = client.get("/api/service-categories/")
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False


class TestGetCategoryById:
    """Tests for GET /api/service-categories/<id> endpoint."""

    def test_get_category_by_id_success(self, client, admin_headers):
        """Test get category by ID success."""
        c = _cat(id=1, name="Test Category")
        with patch("backend.modules.service_categories.service.ServiceCategoryService.get_category") as mock_get:
            mock_get.return_value = c
            response = client.get("/api/service-categories/1", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["name"] == "Test Category"

    def test_get_category_by_id_not_found(self, client, admin_headers):
        """Test get category by ID not found."""
        with patch("backend.modules.service_categories.service.ServiceCategoryService.get_category") as mock_get:
            mock_get.side_effect = ValueError("Category not found")
            response = client.get("/api/service-categories/999", headers=admin_headers)
            assert response.status_code == 404
            data = response.get_json()
            assert data["success"] is False


class TestCreateCategory:
    """Tests for POST /api/service-categories/ endpoint."""

    def test_create_category_success(self, client, admin_headers):
        """Test create category success."""
        c = _cat(id=1, name="New Category")
        with patch("backend.modules.service_categories.service.ServiceCategoryService.create_category") as mock_create:
            mock_create.return_value = c
            response = client.post("/api/service-categories/", headers=admin_headers, json={"name": "New Category"})
            assert response.status_code == 201
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["name"] == "New Category"

    def test_create_category_missing_name(self, client, admin_headers):
        """Test create category with missing name."""
        response = client.post("/api/service-categories/", headers=admin_headers, json={})
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_create_category_empty_name(self, client, admin_headers):
        """Test create category with empty name."""
        response = client.post("/api/service-categories/", headers=admin_headers, json={"name": ""})
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_create_category_employee_forbidden(self, client, employee_headers):
        """Test create category as employee (forbidden)."""
        response = client.post("/api/service-categories/", headers=employee_headers, json={"name": "New Cat"})
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False

    def test_create_category_manager(self, client, manager_headers):
        """Test manager can create a category."""
        c = _cat(id=2, name="Mgr Cat")
        with patch("backend.modules.service_categories.service.ServiceCategoryService.create_category") as mock_create:
            mock_create.return_value = c
            response = client.post("/api/service-categories/", headers=manager_headers, json={"name": "Mgr Cat"})
            assert response.status_code == 201
            assert response.get_json()["success"] is True

    def test_create_category_duplicate_name(self, client, admin_headers):
        """Test create category with duplicate name."""
        with patch("backend.modules.service_categories.service.ServiceCategoryService.create_category") as mock_create:
            mock_create.side_effect = ValueError("Category with this name already exists")
            response = client.post("/api/service-categories/", headers=admin_headers, json={"name": "Existing"})
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False


class TestUpdateCategory:
    """Tests for PUT /api/service-categories/<id> endpoint."""

    def test_update_category_success(self, client, admin_headers):
        """Test update category success."""
        c = _cat(id=1, name="Updated Category")
        with patch("backend.modules.service_categories.service.ServiceCategoryService.update_category") as mock_update:
            mock_update.return_value = c
            response = client.put("/api/service-categories/1", headers=admin_headers, json={"name": "Updated Category"})
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["name"] == "Updated Category"

    def test_update_category_not_found(self, client, admin_headers):
        """Test update category not found."""
        with patch("backend.modules.service_categories.service.ServiceCategoryService.update_category") as mock_update:
            mock_update.side_effect = ValueError("Category not found")
            response = client.put("/api/service-categories/999", headers=admin_headers, json={"name": "Updated"})
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_update_category_employee_forbidden(self, client, employee_headers):
        """Test update category as employee (forbidden)."""
        response = client.put("/api/service-categories/1", headers=employee_headers, json={"name": "Updated"})
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False

    def test_update_category_manager(self, client, manager_headers):
        """Test manager can update a category."""
        c = _cat(id=1, name="Mgr Updated")
        with patch("backend.modules.service_categories.service.ServiceCategoryService.update_category") as mock_update:
            mock_update.return_value = c
            response = client.put("/api/service-categories/1", headers=manager_headers, json={"name": "Mgr Updated"})
            assert response.status_code == 200
            assert response.get_json()["success"] is True


class TestDeleteCategory:
    """Tests for DELETE /api/service-categories/<id> endpoint."""

    def test_delete_category_success(self, client, admin_headers):
        """Test delete category success."""
        with patch("backend.modules.service_categories.service.ServiceCategoryService.delete_category") as mock_delete:
            mock_delete.return_value = True
            response = client.delete("/api/service-categories/1", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["message"] == "Category deleted successfully"

    def test_delete_category_not_found(self, client, admin_headers):
        """Test delete category not found."""
        with patch("backend.modules.service_categories.service.ServiceCategoryService.delete_category") as mock_delete:
            mock_delete.side_effect = ValueError("Category not found")
            response = client.delete("/api/service-categories/999", headers=admin_headers)
            assert response.status_code == 404
            data = response.get_json()
            assert data["success"] is False

    def test_delete_category_has_services(self, client, admin_headers):
        """Test delete category that has services."""
        with patch("backend.modules.service_categories.service.ServiceCategoryService.delete_category") as mock_delete:
            mock_delete.side_effect = ValueError("Cannot delete category with active services")
            response = client.delete("/api/service-categories/1", headers=admin_headers)
            assert response.status_code == 404
            data = response.get_json()
            assert data["success"] is False

    def test_delete_category_employee_forbidden(self, client, employee_headers):
        """Test delete category as employee (forbidden)."""
        response = client.delete("/api/service-categories/1", headers=employee_headers)
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False

    def test_delete_category_manager(self, client, manager_headers):
        """Test manager can delete a category."""
        with patch("backend.modules.service_categories.service.ServiceCategoryService.delete_category") as mock_delete:
            mock_delete.return_value = True
            response = client.delete("/api/service-categories/1", headers=manager_headers)
            assert response.status_code == 200
            assert response.get_json()["success"] is True
