"""Deal repository for database operations on the deals table."""

from datetime import date
from typing import Optional, List

import mysql.connector

from backend.database import Database
from backend.modules.deals.model import Deal


class DealRepository:
    """Repository for deal database operations.

    Handles all CRUD operations and aggregation queries for the deals table
    using parameterized queries and a shared connection pool.
    """

    def __init__(self, database: Database) -> None:
        """Initialize DealRepository with a Database instance.

        Args:
            database: Database connection pool manager.
        """
        self._database = database

    def _row_to_deal(self, row: tuple) -> Deal:
        """Convert a database row tuple to a Deal instance.

        Args:
            row: Database row as a tuple.

        Returns:
            Deal instance populated from the row data.
        """
        return Deal(
            id=row[0],
            deal_number=row[1],
            client_id=row[2],
            service_id=row[3],
            package_name=row[4],
            sale_date=row[5],
            price=row[6],
            discount=row[7],
            tax=row[8],
            final_amount=row[9],
            payment_status=row[10],
            deal_status=row[11],
            notes=row[12],
            created_by=row[13],
            created_at=row[14],
            updated_at=row[15],
        )

    def create(self, deal: Deal) -> Deal:
        """Insert a new deal record into the database.

        Args:
            deal: Deal instance to insert.

        Returns:
            Deal instance with the generated id populated.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = """
                    INSERT INTO deals (deal_number, client_id, service_id, package_name,
                        sale_date, price, discount, tax, final_amount,
                        payment_status, deal_status, notes, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    deal.deal_number,
                    deal.client_id,
                    deal.service_id,
                    deal.package_name,
                    deal.sale_date,
                    deal.price,
                    deal.discount,
                    deal.tax,
                    deal.final_amount,
                    deal.payment_status,
                    deal.deal_status,
                    deal.notes,
                    deal.created_by,
                ))
                conn.commit()
                deal.id = cursor.lastrowid
                return deal
            except mysql.connector.Error:
                conn.rollback()
                raise
            finally:
                cursor.close()

    def get_by_id(self, deal_id: int) -> Optional[Deal]:
        """Retrieve a deal by its unique identifier.

        Args:
            deal_id: The unique identifier of the deal.

        Returns:
            Deal instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = "SELECT * FROM deals WHERE id = %s"
                cursor.execute(query, (deal_id,))
                row = cursor.fetchone()
                if row:
                    return self._row_to_deal(row)
                return None
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_all(self) -> List[Deal]:
        """Retrieve all deal records from the database.

        Returns:
            List of Deal instances.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = "SELECT * FROM deals ORDER BY created_at DESC"
                cursor.execute(query)
                rows = cursor.fetchall()
                return [self._row_to_deal(row) for row in rows]
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def update(self, deal: Deal) -> Optional[Deal]:
        """Update an existing deal record in the database.

        Args:
            deal: Deal instance with updated fields.

        Returns:
            Updated Deal instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = """
                    UPDATE deals
                    SET package_name = %s, sale_date = %s, price = %s,
                        discount = %s, tax = %s, final_amount = %s,
                        payment_status = %s, deal_status = %s, notes = %s
                    WHERE id = %s
                """
                cursor.execute(query, (
                    deal.package_name,
                    deal.sale_date,
                    deal.price,
                    deal.discount,
                    deal.tax,
                    deal.final_amount,
                    deal.payment_status,
                    deal.deal_status,
                    deal.notes,
                    deal.id,
                ))
                conn.commit()
                if cursor.rowcount > 0:
                    cursor.execute("SELECT * FROM deals WHERE id = %s", (deal.id,))
                    row = cursor.fetchone()
                    if row:
                        return self._row_to_deal(row)
                return None
            except mysql.connector.Error:
                conn.rollback()
                raise
            finally:
                cursor.close()

    def delete(self, deal_id: int) -> bool:
        """Delete a deal record from the database.

        Args:
            deal_id: The unique identifier of the deal to delete.

        Returns:
            True if the deal was deleted, False if not found.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = "DELETE FROM deals WHERE id = %s"
                cursor.execute(query, (deal_id,))
                conn.commit()
                return cursor.rowcount > 0
            except mysql.connector.Error:
                conn.rollback()
                raise
            finally:
                cursor.close()

    def get_next_deal_number(self) -> str:
        """Generate the next sequential deal number.

        Returns:
            Next deal number string (e.g., DEAL-000001).
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "SELECT deal_number FROM deals ORDER BY id DESC LIMIT 1"
                )
                row = cursor.fetchone()
                if row and row[0]:
                    last_num = int(row[0].split("-")[1])
                    return f"DEAL-{last_num + 1:06d}"
                return "DEAL-000001"
            except mysql.connector.Error:
                return "DEAL-000001"
            finally:
                cursor.close()

    def get_deals_by_client(self, client_id: int) -> List[Deal]:
        """Retrieve all deals for a specific client.

        Args:
            client_id: The unique identifier of the client.

        Returns:
            List of Deal instances for the client.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = "SELECT * FROM deals WHERE client_id = %s ORDER BY created_at DESC"
                cursor.execute(query, (client_id,))
                rows = cursor.fetchall()
                return [self._row_to_deal(row) for row in rows]
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_deals_by_service(self, service_id: int) -> List[Deal]:
        """Retrieve all deals for a specific service.

        Args:
            service_id: The unique identifier of the service.

        Returns:
            List of Deal instances for the service.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = "SELECT * FROM deals WHERE service_id = %s ORDER BY created_at DESC"
                cursor.execute(query, (service_id,))
                rows = cursor.fetchall()
                return [self._row_to_deal(row) for row in rows]
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()

    def get_statistics(self) -> dict:
        """Return aggregated deal statistics for the dashboard.

        Returns:
            Dictionary with total_deals, total_revenue, payment_status_breakdown,
            deal_status_breakdown, recent_deals, best_services, revenue_by_service.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor(dictionary=True)
            try:
                stats: dict = {}

                cursor.execute("SELECT COUNT(*) AS total FROM deals")
                stats["total_deals"] = cursor.fetchone()["total"]

                cursor.execute(
                    "SELECT COALESCE(SUM(final_amount), 0) AS total FROM deals "
                    "WHERE deal_status != 'cancelled'"
                )
                stats["total_revenue"] = float(cursor.fetchone()["total"])

                cursor.execute(
                    "SELECT COALESCE(SUM(final_amount), 0) AS total FROM deals "
                    "WHERE deal_status != 'cancelled' "
                    "AND sale_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)"
                )
                stats["monthly_revenue"] = float(cursor.fetchone()["total"])

                cursor.execute(
                    "SELECT payment_status, COUNT(*) AS count, "
                    "COALESCE(SUM(final_amount), 0) AS total "
                    "FROM deals GROUP BY payment_status"
                )
                stats["payment_status_breakdown"] = {
                    row["payment_status"]: {"count": row["count"], "total": float(row["total"])}
                    for row in cursor.fetchall()
                }

                cursor.execute(
                    "SELECT deal_status, COUNT(*) AS count "
                    "FROM deals GROUP BY deal_status"
                )
                stats["deal_status_breakdown"] = {
                    row["deal_status"]: row["count"] for row in cursor.fetchall()
                }

                cursor.execute(
                    "SELECT d.id, d.deal_number, d.client_id, d.service_id, "
                    "d.package_name, d.sale_date, d.final_amount, "
                    "d.payment_status, d.deal_status, "
                    "c.company_name, s.name AS service_name "
                    "FROM deals d "
                    "JOIN clients c ON c.id = d.client_id "
                    "JOIN services s ON s.id = d.service_id "
                    "ORDER BY d.created_at DESC LIMIT 10"
                )
                stats["recent_deals"] = cursor.fetchall()

                cursor.execute(
                    "SELECT s.id, s.name, COUNT(d.id) AS deal_count, "
                    "COALESCE(SUM(d.final_amount), 0) AS total_revenue "
                    "FROM deals d "
                    "JOIN services s ON s.id = d.service_id "
                    "WHERE d.deal_status != 'cancelled' "
                    "GROUP BY s.id, s.name "
                    "ORDER BY total_revenue DESC LIMIT 10"
                )
                stats["best_services"] = cursor.fetchall()

                return stats
            finally:
                cursor.close()

    def search_deals(self, search_term: str) -> List[Deal]:
        """Search deals by deal number, package name, or client company name.

        Args:
            search_term: The search string.

        Returns:
            List of matching Deal instances.
        """
        with self._database.connection() as conn:
            cursor = conn.cursor()
            try:
                query = """
                    SELECT d.* FROM deals d
                    JOIN clients c ON c.id = d.client_id
                    WHERE d.deal_number LIKE %s
                       OR d.package_name LIKE %s
                       OR c.company_name LIKE %s
                    ORDER BY d.created_at DESC
                """
                pattern = f"%{search_term}%"
                cursor.execute(query, (pattern, pattern, pattern))
                rows = cursor.fetchall()
                return [self._row_to_deal(row) for row in rows]
            except mysql.connector.Error:
                raise
            finally:
                cursor.close()
