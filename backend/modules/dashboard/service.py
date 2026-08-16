"""Dashboard service for aggregating data across repositories."""

from typing import Dict, Any, List

from backend.modules.worker_management.repository import WorkerManagementRepository
from backend.modules.expenses.repository import ExpenseRepository


class DashboardService:
    """Service for dashboard statistics and aggregation.

    Collects information from worker management and expenses repositories
    and returns aggregated data suitable for standalone Worker Management + Expenses dashboard.
    """

    def __init__(
        self,
        worker_management_repository: WorkerManagementRepository,
        expense_repository: ExpenseRepository,
    ) -> None:
        """Initialize DashboardService.

        Args:
            worker_management_repository: Repository for worker management statistics.
            expense_repository: Repository for expense statistics.
        """
        self._worker_management_repository = worker_management_repository
        self._expense_repository = expense_repository

    def get_dashboard_statistics(self) -> Dict[str, Any]:
        """Collect and return aggregated dashboard statistics.

        Returns:
            Dictionary containing combined dashboard statistics.
        """
        worker_stats = self._worker_management_repository.get_statistics()
        expense_stats = self._expense_repository.get_summary()

        workers_by_status = {
            "active": worker_stats.get("active_workers", 0),
            "inactive": worker_stats.get("total_workers", 0) - worker_stats.get("active_workers", 0),
        }

        expenses_by_status = {
            "pending": 0,
            "completed": expense_stats.get("total_count", 0),
        }

        recent_workers_raw = worker_stats.get("recent_workers", [])
        recent_workers: List[Dict[str, Any]] = []
        for w in recent_workers_raw:
            if isinstance(w, dict):
                recent_workers.append({
                    "id": w.get("id"),
                    "full_name": w.get("full_name"),
                    "job_title": w.get("job_title"),
                    "department": w.get("department"),
                    "base_salary": w.get("base_salary"),
                    "status": w.get("status"),
                    "created_at": w.get("created_at"),
                })

        return {
            "total_workers": worker_stats.get("total_workers", 0),
            "workers_by_status": workers_by_status,
            "total_expenses": expense_stats.get("total_count", 0),
            "monthly_expenses": expense_stats.get("this_month_total", 0.0),
            "today_expenses": expense_stats.get("today_total", 0.0),
            "month_expenses": expense_stats.get("this_month_total", 0.0),
            "total_advances": worker_stats.get("total_advances", 0),
            "outstanding_advances": worker_stats.get("outstanding_advances", 0.0),
            "recent_workers": recent_workers,
            "recent_expenses": [],
            "expenses_by_status": expenses_by_status,
        }