"""Business development service for aggregated statistics business logic."""

from typing import Dict, Any

from backend.modules.business_development.repository import BusinessDevelopmentRepository


class BusinessDevelopmentService:
    """Service for business development statistics.

    Delegates aggregation to BusinessDevelopmentRepository and exposes
    the statistics used by the business development dashboard endpoint.
    """

    def __init__(self, business_development_repository: BusinessDevelopmentRepository) -> None:
        """Initialize BusinessDevelopmentService with a repository.

        Args:
            business_development_repository: Repository for business development statistics.
        """
        self._business_development_repository = business_development_repository

    def get_statistics(self) -> Dict[str, Any]:
        """Collect all business development statistics.

        Returns:
            Dictionary with total counts, status breakdowns, and recent records.
        """
        return self._business_development_repository.get_statistics()
