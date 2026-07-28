"""Dashboard service for aggregating data across repositories."""

from typing import Dict, Any, List

from backend.modules.users.repository import UserRepository
from backend.modules.clients.repository import ClientRepository
from backend.modules.services.repository import ServiceRepository
from backend.modules.service_categories.repository import ServiceCategoryRepository


class DashboardService:
    """Service for dashboard statistics and aggregation.

    Collects information from multiple repositories and returns
    aggregated data suitable for dashboard display.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        client_repository: ClientRepository,
        service_repository: ServiceRepository,
        category_repository: ServiceCategoryRepository
    ) -> None:
        """Initialize DashboardService with required repositories.

        Args:
            user_repository: Repository for user database operations.
            client_repository: Repository for client database operations.
            service_repository: Repository for service database operations.
            category_repository: Repository for service category database operations.
        """
        self._user_repository = user_repository
        self._client_repository = client_repository
        self._service_repository = service_repository
        self._category_repository = category_repository

    def get_dashboard_statistics(self) -> Dict[str, Any]:
        """Collect and return aggregated dashboard statistics.

        Returns:
            Dictionary containing total counts and recent records.
        """
        users = self._user_repository.get_all()
        clients = self._client_repository.get_all()
        services = self._service_repository.get_all()
        categories = self._category_repository.get_all()

        recent_clients = clients[:5] if clients else []
        recent_services = services[:5] if services else []

        return {
            "total_users": len(users),
            "total_clients": len(clients),
            "total_services": len(services),
            "total_categories": len(categories),
            "recent_clients": [client.to_dict() for client in recent_clients],
            "recent_services": [service.to_dict() for service in recent_services]
        }
