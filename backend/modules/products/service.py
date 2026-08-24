"""Product service for product-related business logic."""

from typing import Optional, List

from backend.config import Config
from backend.modules.products.model import Product
from backend.modules.products.repository import ProductRepository
from backend.modules.products.validator import ProductValidator
from backend.modules.categories.repository import CategoryRepository
from backend.shared.expiration import classify_expiration


class ProductService:
    """Service for product business operations.

    Handles all product-related business logic including creation,
    updates, and deletion. Communicates only with repositories
    for data access.
    """

    def __init__(
        self,
        product_repository: ProductRepository,
        category_repository: CategoryRepository,
    ) -> None:
        """Initialize ProductService with repositories.

        Args:
            product_repository: Repository for product database operations.
            category_repository: Repository for category database operations.
        """
        self._product_repository = product_repository
        self._category_repository = category_repository

    def create_product(self, data: dict) -> Product:
        """Create a new product.

        Args:
            data: Dictionary containing product information.

        Returns:
            Created Product instance.

        Raises:
            ValueError: If validation fails or business rules are violated.
        """
        validated = ProductValidator.validate_create_product(data)

        if self._product_repository.exists_by_name(validated["name"]):
            raise ValueError("A product with this name already exists")

        if self._product_repository.exists_by_barcode(validated["barcode"]):
            raise ValueError("A product with this barcode already exists")

        sku = validated.get("sku")
        if sku and self._product_repository.exists_by_sku(sku):
            raise ValueError("A product with this SKU already exists")

        category = self._category_repository.get_by_id(validated["category_id"])
        if category is None:
            raise ValueError("Category not found")

        product = Product(
            category_id=validated["category_id"],
            name=validated["name"],
            sku=validated.get("sku"),
            barcode=validated["barcode"],
            description=validated.get("description"),
            purchase_price=validated["purchase_price"],
            selling_price=validated["selling_price"],
            quantity=0,
            minimum_stock=validated["minimum_stock"],
            status=validated["status"],
        )

        created = self._product_repository.create(product)
        created.category_name = category.name
        return created

    def get_product(self, product_id: int) -> Product:
        """Retrieve a product by its unique identifier.

        Args:
            product_id: The unique identifier of the product.

        Returns:
            Product instance if found.

        Raises:
            ValueError: If product not found.
        """
        product = self._product_repository.get_by_id(product_id)
        if product is None:
            raise ValueError("Product not found")

        expiration_date = self._product_repository.get_oldest_expiration(product_id)
        if expiration_date is not None:
            product.expiration_date = expiration_date
            product.expiration_status = classify_expiration(
                expiration_date, expiring_soon_days=Config.EXPIRING_SOON_DAYS
            )
        return product

    def get_all_products(
        self,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> List[Product]:
        """Retrieve all products with optional filtering.

        Args:
            search: Optional search term for name or barcode.
            category_id: Optional category filter.
            status: Optional status filter.

        Returns:
            List of Product instances with expiration classification.
        """
        products = self._product_repository.get_all(
            search=search, category_id=category_id, status=status
        )

        for product in products:
            if product.expiration_date is not None:
                product.expiration_status = classify_expiration(
                    product.expiration_date,
                    expiring_soon_days=Config.EXPIRING_SOON_DAYS,
                )

        return products

    def update_product(self, product_id: int, data: dict) -> Product:
        """Update an existing product.

        Args:
            product_id: The unique identifier of the product.
            data: Dictionary containing fields to update.

        Returns:
            Updated Product instance.

        Raises:
            ValueError: If product not found or validation fails.
        """
        validated = ProductValidator.validate_update_product(data)

        product = self._product_repository.get_by_id(product_id)
        if product is None:
            raise ValueError("Product not found")

        if "name" in validated:
            existing = self._product_repository.exists_by_name(validated["name"])
            if existing and validated["name"] != product.name:
                raise ValueError("A product with this name already exists")
            product.name = validated["name"]

        if "barcode" in validated:
            existing = self._product_repository.exists_by_barcode(validated["barcode"])
            if existing and validated["barcode"] != product.barcode:
                raise ValueError("A product with this barcode already exists")
            product.barcode = validated["barcode"]

        if "sku" in validated:
            sku = validated["sku"]
            if sku:
                existing = self._product_repository.exists_by_sku(sku)
                if existing and sku != product.sku:
                    raise ValueError("A product with this SKU already exists")
            product.sku = sku

        if "category_id" in validated:
            category = self._category_repository.get_by_id(validated["category_id"])
            if category is None:
                raise ValueError("Category not found")
            product.category_id = validated["category_id"]

        if "description" in validated:
            product.description = validated["description"]

        if "purchase_price" in validated:
            product.purchase_price = validated["purchase_price"]

        if "selling_price" in validated:
            product.selling_price = validated["selling_price"]

        if "minimum_stock" in validated:
            product.minimum_stock = validated["minimum_stock"]

        if "status" in validated:
            product.status = validated["status"]

        updated = self._product_repository.update(product)
        if updated is None:
            raise ValueError("Failed to update product")
        return updated

    def delete_product(self, product_id: int) -> bool:
        """Delete a product.

        Args:
            product_id: The unique identifier of the product.

        Returns:
            True if product was deleted successfully.

        Raises:
            ValueError: If product not found.
        """
        deleted = self._product_repository.delete(product_id)
        if not deleted:
            raise ValueError("Product not found")
        return True
