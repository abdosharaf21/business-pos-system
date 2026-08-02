"""Tests for Category API endpoints.

Tests the /api/categories/* endpoints including CRUD operations,
hierarchical parent relationships, the tree endpoint, role-based
access control, and delete safety rules.
"""

from unittest.mock import patch

from backend.modules.categories.model import Category


def _category(**kw):
    defaults = dict(id=1, parent_id=None, name="Electronics", description="Devices")
    defaults.update(kw)
    return Category(**defaults)


class TestGetCategories:
    """Tests for GET /api/categories/ endpoint."""

    def test_get_all_categories_success(self, client, admin_headers):
        """Test admin can list all categories."""
        categories = [
            _category(id=1, name="Electronics", parent_id=None),
            _category(id=2, name="Phones", parent_id=1),
        ]
        with patch("backend.modules.categories.service.CategoryService.get_all_categories") as mock_get:
            mock_get.return_value = categories
            response = client.get("/api/categories/", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert len(data["data"]) == 2
            assert data["data"][1]["parent_id"] == 1

    def test_get_all_categories_no_token(self, client):
        """Test unauthenticated cannot list categories."""
        response = client.get("/api/categories/")
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False


class TestGetCategoryTree:
    """Tests for GET /api/categories/tree endpoint."""

    def test_tree_success(self, client, admin_headers):
        """Test admin can retrieve the nested category tree."""
        tree = [
            {
                "id": 1,
                "parent_id": None,
                "name": "Electronics",
                "description": "Devices",
                "children": [
                    {
                        "id": 2,
                        "parent_id": 1,
                        "name": "Phones",
                        "description": None,
                        "children": [],
                    }
                ],
            }
        ]
        with patch("backend.modules.categories.service.CategoryService.get_category_tree") as mock_tree:
            mock_tree.return_value = tree
            response = client.get("/api/categories/tree", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"][0]["name"] == "Electronics"
            assert data["data"][0]["children"][0]["name"] == "Phones"
            assert data["data"][0]["children"][0]["children"] == []

    def test_tree_no_token(self, client):
        """Test unauthenticated cannot retrieve the category tree."""
        response = client.get("/api/categories/tree")
        assert response.status_code == 401
        data = response.get_json()
        assert data["success"] is False


class TestGetCategoryById:
    """Tests for GET /api/categories/<id> endpoint."""

    def test_get_category_success(self, client, admin_headers):
        """Test admin can get a category by ID."""
        category = _category(id=1, name="Electronics", parent_id=None)
        with patch("backend.modules.categories.service.CategoryService.get_category") as mock_get:
            mock_get.return_value = category
            response = client.get("/api/categories/1", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["name"] == "Electronics"

    def test_get_category_not_found(self, client, admin_headers):
        """Test get non-existent category returns 404."""
        with patch("backend.modules.categories.service.CategoryService.get_category") as mock_get:
            mock_get.side_effect = ValueError("Category not found")
            response = client.get("/api/categories/999", headers=admin_headers)
            assert response.status_code == 404
            data = response.get_json()
            assert data["success"] is False


class TestCreateCategory:
    """Tests for POST /api/categories/ endpoint."""

    def test_create_root_category(self, client, admin_headers):
        """Test creating a root category."""
        category = _category(id=1, name="Electronics", parent_id=None)
        with patch("backend.modules.categories.service.CategoryService.create_category") as mock_create:
            mock_create.return_value = category
            response = client.post("/api/categories/", headers=admin_headers, json={
                "name": "Electronics", "description": "Devices"
            })
            assert response.status_code == 201
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["parent_id"] is None

    def test_create_child_category(self, client, admin_headers):
        """Test creating a child category with a parent_id."""
        category = _category(id=2, parent_id=1, name="Phones")
        with patch("backend.modules.categories.service.CategoryService.create_category") as mock_create:
            mock_create.return_value = category
            response = client.post("/api/categories/", headers=admin_headers, json={
                "name": "Phones", "description": None, "parent_id": 1
            })
            assert response.status_code == 201
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["parent_id"] == 1

    def test_create_category_duplicate_name(self, client, admin_headers):
        """Test duplicate category name returns 400."""
        with patch("backend.modules.categories.service.CategoryService.create_category") as mock_create:
            mock_create.side_effect = ValueError("A category with this name already exists")
            response = client.post("/api/categories/", headers=admin_headers, json={
                "name": "Electronics"
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_create_category_invalid_parent(self, client, admin_headers):
        """Test invalid parent category returns 400."""
        with patch("backend.modules.categories.service.CategoryService.create_category") as mock_create:
            mock_create.side_effect = ValueError("Parent category not found")
            response = client.post("/api/categories/", headers=admin_headers, json={
                "name": "Phones", "parent_id": 999
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_create_category_missing_name(self, client, admin_headers):
        """Test create category with missing name returns 400."""
        response = client.post("/api/categories/", headers=admin_headers, json={
            "description": "Devices"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False

    def test_create_category_employee_forbidden(self, client, employee_headers):
        """Test employee cannot create a category."""
        response = client.post("/api/categories/", headers=employee_headers, json={
            "name": "Electronics"
        })
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False


class TestUpdateCategory:
    """Tests for PUT /api/categories/<id> endpoint."""

    def test_update_category_success(self, client, admin_headers):
        """Test admin can update a category."""
        category = _category(id=1, name="Consumer Electronics", parent_id=None)
        with patch("backend.modules.categories.service.CategoryService.update_category") as mock_update:
            mock_update.return_value = category
            response = client.put("/api/categories/1", headers=admin_headers, json={
                "name": "Consumer Electronics"
            })
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["name"] == "Consumer Electronics"

    def test_update_category_cycle(self, client, admin_headers):
        """Test moving a category under its own subcategory returns 400."""
        with patch("backend.modules.categories.service.CategoryService.update_category") as mock_update:
            mock_update.side_effect = ValueError("A category cannot be moved under one of its own subcategories")
            response = client.put("/api/categories/1", headers=admin_headers, json={
                "parent_id": 2
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_update_category_not_found(self, client, admin_headers):
        """Test update non-existent category returns 400."""
        with patch("backend.modules.categories.service.CategoryService.update_category") as mock_update:
            mock_update.side_effect = ValueError("Category not found")
            response = client.put("/api/categories/999", headers=admin_headers, json={
                "name": "Updated"
            })
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_update_category_employee_forbidden(self, client, employee_headers):
        """Test employee cannot update a category."""
        response = client.put("/api/categories/1", headers=employee_headers, json={
            "name": "Updated"
        })
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False


class TestDeleteCategory:
    """Tests for DELETE /api/categories/<id> endpoint."""

    def test_delete_category_success(self, client, admin_headers):
        """Test admin can delete a leaf category."""
        with patch("backend.modules.categories.service.CategoryService.delete_category") as mock_delete:
            mock_delete.return_value = True
            response = client.delete("/api/categories/1", headers=admin_headers)
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True

    def test_delete_category_has_subcategories(self, client, admin_headers):
        """Test deleting a category with subcategories returns 400."""
        with patch("backend.modules.categories.service.CategoryService.delete_category") as mock_delete:
            mock_delete.side_effect = ValueError("Cannot delete a category that has subcategories")
            response = client.delete("/api/categories/1", headers=admin_headers)
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_delete_category_has_products(self, client, admin_headers):
        """Test deleting a category assigned to products returns 400."""
        with patch("backend.modules.categories.service.CategoryService.delete_category") as mock_delete:
            mock_delete.side_effect = ValueError("Cannot delete a category that is assigned to products")
            response = client.delete("/api/categories/1", headers=admin_headers)
            assert response.status_code == 400
            data = response.get_json()
            assert data["success"] is False

    def test_delete_category_not_found(self, client, admin_headers):
        """Test delete non-existent category returns 404."""
        with patch("backend.modules.categories.service.CategoryService.delete_category") as mock_delete:
            mock_delete.side_effect = ValueError("Category not found")
            response = client.delete("/api/categories/999", headers=admin_headers)
            assert response.status_code == 404
            data = response.get_json()
            assert data["success"] is False

    def test_delete_category_employee_forbidden(self, client, employee_headers):
        """Test employee cannot delete a category."""
        response = client.delete("/api/categories/1", headers=employee_headers)
        assert response.status_code == 403
        data = response.get_json()
        assert data["success"] is False
