"""Dashboard service for aggregating data across repositories."""

from typing import Dict, Any

from backend.modules.dashboard.repository import DashboardRepository


class DashboardService:
    """Service for dashboard statistics and aggregation.

    Collects information from the dashboard repository and returns
    aggregated data suitable for POS dashboard display.
    """

    def __init__(
        self,
        dashboard_repository: DashboardRepository,
    ) -> None:
        """Initialize DashboardService.

        Args:
            dashboard_repository: Repository for dashboard statistics queries.
        """
        self._dashboard_repository = dashboard_repository

    def get_dashboard_statistics(self) -> Dict[str, Any]:
        """Collect and return aggregated dashboard statistics.

        Returns:
            Dictionary containing POS dashboard statistics.
        """
        return self._dashboard_repository.get_statistics()
