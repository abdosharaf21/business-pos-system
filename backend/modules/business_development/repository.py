"""Business development repository for aggregated statistics queries."""

from typing import Dict, Any, List

from backend.database import Database
from backend.shared.database import db_cursor


class BusinessDevelopmentRepository:
    """Repository for business development statistics.

    Aggregates data across the clients, service_categories, services
    and client_services tables using raw SQL queries. Returns zero
    values for empty tables instead of raising exceptions.
    """

    def __init__(self, database: Database) -> None:
        """Initialize BusinessDevelopmentRepository.

        Args:
            database: Database instance for connection management.
        """
        self._database = database

    def _count_rows(self, cursor, query: str, params: tuple = ()) -> int:
        """Run a COUNT query and return its result.

        Args:
            cursor: An open database cursor.
            query: Parameterized COUNT query.
            params: Optional query parameters.

        Returns:
            Integer row count.
        """
        cursor.execute(query, params)
        return cursor.fetchone()["count"]

    @staticmethod
    def _status_breakdown(rows: List[Dict[str, Any]], valid_statuses: List[str]) -> Dict[str, int]:
        """Convert GROUP BY status rows into a complete status dictionary.

        Args:
            rows: List of rows with ``status`` and ``count`` keys.
            valid_statuses: All valid statuses to include in the result.

        Returns:
            Dictionary mapping each status to its count (zero if absent).
        """
        counts = {status: 0 for status in valid_statuses}
        for row in rows:
            if row["status"] in counts:
                counts[row["status"]] = row["count"]
        return counts

    def get_statistics(self) -> Dict[str, Any]:
        """Collect all business development statistics.

        Returns:
            Dictionary with total counts, status breakdowns, and
            recent clients and services.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:

            total_clients = self._count_rows(cursor, "SELECT COUNT(*) AS count FROM clients")
            total_categories = self._count_rows(cursor, "SELECT COUNT(*) AS count FROM service_categories")
            total_services = self._count_rows(cursor, "SELECT COUNT(*) AS count FROM services")
            total_assignments = self._count_rows(cursor, "SELECT COUNT(*) AS count FROM client_services")

            cursor.execute(
                "SELECT status, COUNT(*) AS count FROM clients GROUP BY status"
            )
            clients_by_status = self._status_breakdown(
                cursor.fetchall(), ["lead", "prospect", "customer"]
            )

            cursor.execute(
                "SELECT status, COUNT(*) AS count FROM services GROUP BY status"
            )
            services_by_status = self._status_breakdown(
                cursor.fetchall(), ["active", "inactive"]
            )

            cursor.execute(
                "SELECT status, COUNT(*) AS count FROM client_services GROUP BY status"
            )
            assignments_by_status = self._status_breakdown(
                cursor.fetchall(), ["pending", "in_progress", "completed", "cancelled"]
            )

            cursor.execute(
                "SELECT id, company_name, contact_person, email, phone, address, status, "
                "created_at FROM clients ORDER BY created_at DESC LIMIT 5"
            )
            recent_clients = cursor.fetchall()

            cursor.execute(
                "SELECT id, category_id, name, description, price, duration_days, status, "
                "created_at FROM services ORDER BY created_at DESC LIMIT 5"
            )
            recent_services = cursor.fetchall()

        for client in recent_clients:
            client["created_at"] = client["created_at"].isoformat() if client["created_at"] else None

        for service in recent_services:
            service["created_at"] = service["created_at"].isoformat() if service["created_at"] else None
            if service["price"] is not None:
                service["price"] = float(service["price"])

        return {
            "total_clients": total_clients,
            "clients_by_status": clients_by_status,
            "total_categories": total_categories,
            "total_services": total_services,
            "services_by_status": services_by_status,
            "total_assignments": total_assignments,
            "assignments_by_status": assignments_by_status,
            "recent_clients": recent_clients,
            "recent_services": recent_services,
        }
