"""Repository for Business Development dashboard aggregation queries."""

from backend.database import Database


class BusinessDevelopmentRepository:
    """Provides aggregated statistics across BD tables for the dashboard."""

    def __init__(self, database: Database) -> None:
        """Initialize BusinessDevelopmentRepository with a Database instance.

        Args:
            database: Database connection pool manager.
        """
        self._database = database

    def get_statistics(self) -> dict:
        """Return aggregated counts and breakdowns for all BD entities."""
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                stats: dict = {}

                # ── Clients ──
                cursor.execute("SELECT COUNT(*) AS total FROM clients")
                stats["total_clients"] = cursor.fetchone()["total"]

                cursor.execute(
                    "SELECT COUNT(*) AS count FROM clients WHERE status = %s",
                    ("customer",),
                )
                stats["active_clients"] = cursor.fetchone()["count"]

                cursor.execute(
                    "SELECT status, COUNT(*) AS count FROM clients GROUP BY status"
                )
                stats["clients_by_status"] = {
                    row["status"]: row["count"] for row in cursor.fetchall()
                }

                cursor.execute(
                    "SELECT id, company_name, contact_person, status, created_at "
                    "FROM clients ORDER BY created_at DESC LIMIT 5"
                )
                stats["recent_clients"] = cursor.fetchall()

                # ── Services ──
                cursor.execute("SELECT COUNT(*) AS total FROM services")
                stats["total_services"] = cursor.fetchone()["total"]

                cursor.execute(
                    "SELECT COUNT(*) AS count FROM services WHERE status = %s",
                    ("active",),
                )
                stats["active_services"] = cursor.fetchone()["count"]

                cursor.execute(
                    "SELECT status, COUNT(*) AS count FROM services GROUP BY status"
                )
                stats["services_by_status"] = {
                    row["status"]: row["count"] for row in cursor.fetchall()
                }

                # ── Service Categories ──
                cursor.execute("SELECT COUNT(*) AS total FROM service_categories")
                stats["total_service_categories"] = cursor.fetchone()["total"]

                # ── Client Services (assignments) ──
                cursor.execute("SELECT COUNT(*) AS total FROM client_services")
                stats["total_client_services"] = cursor.fetchone()["total"]

                cursor.execute(
                    "SELECT COUNT(*) AS count FROM client_services WHERE status = %s",
                    ("in_progress",),
                )
                stats["active_client_services"] = cursor.fetchone()["count"]

                cursor.execute(
                    "SELECT status, COUNT(*) AS count FROM client_services GROUP BY status"
                )
                stats["client_services_by_status"] = {
                    row["status"]: row["count"] for row in cursor.fetchall()
                }

                cursor.execute(
                    "SELECT cs.id, cs.client_id, cs.service_id, cs.start_date, "
                    "cs.end_date, cs.status, cs.created_at, "
                    "c.company_name, s.name AS service_name "
                    "FROM client_services cs "
                    "JOIN clients c ON c.id = cs.client_id "
                    "JOIN services s ON s.id = cs.service_id "
                    "ORDER BY cs.created_at DESC LIMIT 5"
                )
                stats["recent_client_services"] = cursor.fetchall()

                return stats
            finally:
                cursor.close()
