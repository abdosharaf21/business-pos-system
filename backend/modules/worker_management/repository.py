"""Worker management repository for database operations.

Contains repository classes for the workers, attendance, salaries and
advances tables plus aggregated statistics queries. This is the only
layer allowed to execute SQL, and it does so exclusively through
parameterized queries.
"""

from typing import Any, Dict, List, Optional

import mysql.connector

from backend.database import Database
from backend.modules.worker_management.model import (
    Advance,
    Attendance,
    Salary,
    Worker,
)
from backend.shared.database import db_cursor


class WorkerRepository:
    """Repository for worker CRUD database operations."""

    def __init__(self, database: Database) -> None:
        """Initialize WorkerRepository with a Database instance.

        Args:
            database: Database connection pool manager.
        """
        self._database = database

    @staticmethod
    def _row_to_worker(row: dict) -> Worker:
        """Convert a database row dictionary to a Worker instance.

        Args:
            row: Database row as a dictionary.

        Returns:
            Worker instance populated from the row data.
        """
        return Worker(
            id=row["id"],
            full_name=row["full_name"],
            phone=row["phone"],
            email=row["email"],
            job_title=row["job_title"],
            department=row["department"],
            hire_date=row["hire_date"],
            base_salary=row["base_salary"],
            status=row["status"],
            notes=row["notes"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def create(self, worker: Worker) -> Worker:
        """Insert a new worker record.

        Args:
            worker: Worker instance to insert.

        Returns:
            Worker instance with the generated id populated.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                query = """
                    INSERT INTO workers
                        (full_name, phone, email, job_title, department,
                         hire_date, base_salary, status, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    worker.full_name,
                    worker.phone,
                    worker.email,
                    worker.job_title,
                    worker.department,
                    worker.hire_date,
                    worker.base_salary,
                    worker.status,
                    worker.notes,
                ))
                conn.commit()
                worker.id = cursor.lastrowid
                return worker
            except mysql.connector.Error:
                conn.rollback()
                raise

    def get_by_id(self, worker_id: int) -> Optional[Worker]:
        """Retrieve a worker by its unique identifier.

        Args:
            worker_id: The unique identifier of the worker.

        Returns:
            Worker instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            cursor.execute("SELECT * FROM workers WHERE id = %s", (worker_id,))
            row = cursor.fetchone()
            return self._row_to_worker(row) if row else None

    def get_all(
        self,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Worker]:
        """Retrieve workers with optional search and status filters.

        Args:
            search: Optional search term for name, phone, job title or department.
            status: Optional status filter (active or inactive).

        Returns:
            List of Worker instances.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            query = "SELECT * FROM workers"
            conditions = []
            params: List[Any] = []

            if search:
                conditions.append(
                    "(full_name LIKE %s OR phone LIKE %s OR job_title LIKE %s OR department LIKE %s)"
                )
                like = f"%{search}%"
                params.extend([like, like, like, like])

            if status:
                conditions.append("status = %s")
                params.append(status)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY full_name ASC"

            cursor.execute(query, tuple(params))
            return [self._row_to_worker(row) for row in cursor.fetchall()]

    def update(self, worker: Worker) -> Optional[Worker]:
        """Update an existing worker record.

        Args:
            worker: Worker instance with updated fields.

        Returns:
            Updated Worker instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                query = """
                    UPDATE workers
                    SET full_name = %s, phone = %s, email = %s, job_title = %s,
                        department = %s, hire_date = %s, base_salary = %s,
                        status = %s, notes = %s
                    WHERE id = %s
                """
                cursor.execute(query, (
                    worker.full_name,
                    worker.phone,
                    worker.email,
                    worker.job_title,
                    worker.department,
                    worker.hire_date,
                    worker.base_salary,
                    worker.status,
                    worker.notes,
                    worker.id,
                ))
                conn.commit()
                if cursor.rowcount > 0:
                    cursor.execute("SELECT * FROM workers WHERE id = %s", (worker.id,))
                    row = cursor.fetchone()
                    if row:
                        return self._row_to_worker(row)
                return None
            except mysql.connector.Error:
                conn.rollback()
                raise

    def delete(self, worker_id: int) -> bool:
        """Delete a worker record.

        Args:
            worker_id: The unique identifier of the worker to delete.

        Returns:
            True if the worker was deleted, False otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                cursor.execute("DELETE FROM workers WHERE id = %s", (worker_id,))
                conn.commit()
                return cursor.rowcount > 0
            except mysql.connector.Error:
                conn.rollback()
                raise

    def exists_by_phone(self, phone: str) -> bool:
        """Check whether a worker exists with the given phone number.

        Args:
            phone: The phone number to check.

        Returns:
            True if a worker with this phone exists, False otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            cursor.execute("SELECT COUNT(*) AS count FROM workers WHERE phone = %s", (phone,))
            return cursor.fetchone()["count"] > 0

    def exists_by_email(self, email: str) -> bool:
        """Check whether a worker exists with the given email address.

        Args:
            email: The email address to check.

        Returns:
            True if a worker with this email exists, False otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            cursor.execute("SELECT COUNT(*) AS count FROM workers WHERE email = %s", (email,))
            return cursor.fetchone()["count"] > 0

    def get_active_count(self) -> int:
        """Count workers with status active.

        Returns:
            Number of active workers.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            cursor.execute("SELECT COUNT(*) AS count FROM workers WHERE status = 'active'")
            return cursor.fetchone()["count"]


class AttendanceRepository:
    """Repository for attendance database operations."""

    def __init__(self, database: Database) -> None:
        """Initialize AttendanceRepository with a Database instance.

        Args:
            database: Database connection pool manager.
        """
        self._database = database

    @staticmethod
    def _row_to_attendance(row: dict) -> Attendance:
        """Convert a database row dictionary to an Attendance instance.

        Args:
            row: Database row as a dictionary.

        Returns:
            Attendance instance populated from the row data.
        """
        return Attendance(
            id=row["id"],
            worker_id=row["worker_id"],
            worker_name=row.get("worker_name"),
            attendance_date=row["attendance_date"],
            status=row["status"],
            check_in=row["check_in"],
            check_out=row["check_out"],
            notes=row["notes"],
            created_at=row["created_at"],
        )

    def create(self, attendance: Attendance) -> Attendance:
        """Insert a new attendance record.

        Args:
            attendance: Attendance instance to insert.

        Returns:
            Attendance instance with the generated id populated.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                query = """
                    INSERT INTO attendance
                        (worker_id, attendance_date, status, check_in, check_out, notes)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    attendance.worker_id,
                    attendance.attendance_date,
                    attendance.status,
                    attendance.check_in,
                    attendance.check_out,
                    attendance.notes,
                ))
                conn.commit()
                attendance.id = cursor.lastrowid
                return attendance
            except mysql.connector.Error:
                conn.rollback()
                raise

    def get_by_id(self, attendance_id: int) -> Optional[Attendance]:
        """Retrieve an attendance record by its unique identifier.

        Args:
            attendance_id: The unique identifier of the attendance record.

        Returns:
            Attendance instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT a.*, w.full_name AS worker_name
                FROM attendance a
                JOIN workers w ON w.id = a.worker_id
                WHERE a.id = %s
                """,
                (attendance_id,),
            )
            row = cursor.fetchone()
            return self._row_to_attendance(row) if row else None

    def get_all(
        self,
        worker_id: Optional[int] = None,
        date: Optional[str] = None,
        month: Optional[str] = None,
    ) -> List[Attendance]:
        """Retrieve attendance records with optional filters.

        Args:
            worker_id: Optional worker id filter.
            date: Optional exact date (YYYY-MM-DD) filter.
            month: Optional month (YYYY-MM) filter.

        Returns:
            List of Attendance instances ordered by date descending.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            query = """
                SELECT a.*, w.full_name AS worker_name
                FROM attendance a
                JOIN workers w ON w.id = a.worker_id
            """
            conditions = []
            params: List[Any] = []

            if worker_id:
                conditions.append("a.worker_id = %s")
                params.append(worker_id)

            if date:
                conditions.append("a.attendance_date = %s")
                params.append(date)

            if month:
                conditions.append("DATE_FORMAT(a.attendance_date, '%%Y-%%m') = %s")
                params.append(month)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY a.attendance_date DESC, a.id DESC"

            cursor.execute(query, tuple(params))
            return [self._row_to_attendance(row) for row in cursor.fetchall()]

    def update(self, attendance: Attendance) -> Optional[Attendance]:
        """Update an existing attendance record.

        Args:
            attendance: Attendance instance with updated fields.

        Returns:
            Updated Attendance instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                query = """
                    UPDATE attendance
                    SET worker_id = %s, attendance_date = %s, status = %s,
                        check_in = %s, check_out = %s, notes = %s
                    WHERE id = %s
                """
                cursor.execute(query, (
                    attendance.worker_id,
                    attendance.attendance_date,
                    attendance.status,
                    attendance.check_in,
                    attendance.check_out,
                    attendance.notes,
                    attendance.id,
                ))
                conn.commit()
                if cursor.rowcount > 0:
                    return self.get_by_id(attendance.id)
                return None
            except mysql.connector.Error:
                conn.rollback()
                raise

    def delete(self, attendance_id: int) -> bool:
        """Delete an attendance record.

        Args:
            attendance_id: The unique identifier of the attendance record.

        Returns:
            True if the record was deleted, False otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                cursor.execute("DELETE FROM attendance WHERE id = %s", (attendance_id,))
                conn.commit()
                return cursor.rowcount > 0
            except mysql.connector.Error:
                conn.rollback()
                raise

    def exists(self, worker_id: int, attendance_date: str) -> bool:
        """Check whether an attendance record exists for a worker and date.

        Args:
            worker_id: The unique identifier of the worker.
            attendance_date: The attendance date (YYYY-MM-DD).

        Returns:
            True if a record exists, False otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            cursor.execute(
                "SELECT COUNT(*) AS count FROM attendance WHERE worker_id = %s AND attendance_date = %s",
                (worker_id, attendance_date),
            )
            return cursor.fetchone()["count"] > 0


class SalaryRepository:
    """Repository for salary database operations."""

    def __init__(self, database: Database) -> None:
        """Initialize SalaryRepository with a Database instance.

        Args:
            database: Database connection pool manager.
        """
        self._database = database

    @staticmethod
    def _row_to_salary(row: dict) -> Salary:
        """Convert a database row dictionary to a Salary instance.

        Args:
            row: Database row as a dictionary.

        Returns:
            Salary instance populated from the row data.
        """
        return Salary(
            id=row["id"],
            worker_id=row["worker_id"],
            worker_name=row.get("worker_name"),
            salary_period=row["salary_period"],
            base_salary=row["base_salary"],
            bonuses=row["bonuses"],
            deductions=row["deductions"],
            advances_deduction=row["advances_deduction"],
            net_amount=row["net_amount"],
            payment_status=row["payment_status"],
            payment_date=row["payment_date"],
            notes=row["notes"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def create(self, salary: Salary) -> Salary:
        """Insert a new salary record.

        Args:
            salary: Salary instance to insert.

        Returns:
            Salary instance with the generated id populated.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                query = """
                    INSERT INTO salaries
                        (worker_id, salary_period, base_salary, bonuses, deductions,
                         advances_deduction, net_amount, payment_status, payment_date, notes)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    salary.worker_id,
                    salary.salary_period,
                    salary.base_salary,
                    salary.bonuses,
                    salary.deductions,
                    salary.advances_deduction,
                    salary.net_amount,
                    salary.payment_status,
                    salary.payment_date,
                    salary.notes,
                ))
                conn.commit()
                salary.id = cursor.lastrowid
                return salary
            except mysql.connector.Error:
                conn.rollback()
                raise

    def get_by_id(self, salary_id: int) -> Optional[Salary]:
        """Retrieve a salary record by its unique identifier.

        Args:
            salary_id: The unique identifier of the salary record.

        Returns:
            Salary instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT s.*, w.full_name AS worker_name
                FROM salaries s
                JOIN workers w ON w.id = s.worker_id
                WHERE s.id = %s
                """,
                (salary_id,),
            )
            row = cursor.fetchone()
            return self._row_to_salary(row) if row else None

    def get_all(
        self,
        worker_id: Optional[int] = None,
        period: Optional[str] = None,
        payment_status: Optional[str] = None,
    ) -> List[Salary]:
        """Retrieve salary records with optional filters.

        Args:
            worker_id: Optional worker id filter.
            period: Optional period (YYYY-MM) filter.
            payment_status: Optional payment status filter.

        Returns:
            List of Salary instances ordered by period descending.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            query = """
                SELECT s.*, w.full_name AS worker_name
                FROM salaries s
                JOIN workers w ON w.id = s.worker_id
            """
            conditions = []
            params: List[Any] = []

            if worker_id:
                conditions.append("s.worker_id = %s")
                params.append(worker_id)

            if period:
                conditions.append("s.salary_period = %s")
                params.append(period)

            if payment_status:
                conditions.append("s.payment_status = %s")
                params.append(payment_status)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY s.salary_period DESC, s.id DESC"

            cursor.execute(query, tuple(params))
            return [self._row_to_salary(row) for row in cursor.fetchall()]

    def update(self, salary: Salary) -> Optional[Salary]:
        """Update an existing salary record.

        Args:
            salary: Salary instance with updated fields.

        Returns:
            Updated Salary instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                query = """
                    UPDATE salaries
                    SET worker_id = %s, salary_period = %s, base_salary = %s,
                        bonuses = %s, deductions = %s, advances_deduction = %s,
                        net_amount = %s, payment_status = %s, payment_date = %s, notes = %s
                    WHERE id = %s
                """
                cursor.execute(query, (
                    salary.worker_id,
                    salary.salary_period,
                    salary.base_salary,
                    salary.bonuses,
                    salary.deductions,
                    salary.advances_deduction,
                    salary.net_amount,
                    salary.payment_status,
                    salary.payment_date,
                    salary.notes,
                    salary.id,
                ))
                conn.commit()
                if cursor.rowcount > 0:
                    return self.get_by_id(salary.id)
                return None
            except mysql.connector.Error:
                conn.rollback()
                raise

    def delete(self, salary_id: int) -> bool:
        """Delete a salary record.

        Args:
            salary_id: The unique identifier of the salary record.

        Returns:
            True if the record was deleted, False otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                cursor.execute("DELETE FROM salaries WHERE id = %s", (salary_id,))
                conn.commit()
                return cursor.rowcount > 0
            except mysql.connector.Error:
                conn.rollback()
                raise

    def exists(self, worker_id: int, salary_period: str) -> bool:
        """Check whether a salary record exists for a worker and period.

        Args:
            worker_id: The unique identifier of the worker.
            salary_period: The salary period (YYYY-MM).

        Returns:
            True if a record exists, False otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            cursor.execute(
                "SELECT COUNT(*) AS count FROM salaries WHERE worker_id = %s AND salary_period = %s",
                (worker_id, salary_period),
            )
            return cursor.fetchone()["count"] > 0


class AdvanceRepository:
    """Repository for advance database operations."""

    def __init__(self, database: Database) -> None:
        """Initialize AdvanceRepository with a Database instance.

        Args:
            database: Database connection pool manager.
        """
        self._database = database

    @staticmethod
    def _row_to_advance(row: dict) -> Advance:
        """Convert a database row dictionary to an Advance instance.

        Args:
            row: Database row as a dictionary.

        Returns:
            Advance instance populated from the row data.
        """
        return Advance(
            id=row["id"],
            worker_id=row["worker_id"],
            worker_name=row.get("worker_name"),
            amount=row["amount"],
            advance_date=row["advance_date"],
            status=row["status"],
            notes=row["notes"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    def create(self, advance: Advance) -> Advance:
        """Insert a new advance record.

        Args:
            advance: Advance instance to insert.

        Returns:
            Advance instance with the generated id populated.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                query = """
                    INSERT INTO advances (worker_id, amount, advance_date, status, notes)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    advance.worker_id,
                    advance.amount,
                    advance.advance_date,
                    advance.status,
                    advance.notes,
                ))
                conn.commit()
                advance.id = cursor.lastrowid
                return advance
            except mysql.connector.Error:
                conn.rollback()
                raise

    def get_by_id(self, advance_id: int) -> Optional[Advance]:
        """Retrieve an advance record by its unique identifier.

        Args:
            advance_id: The unique identifier of the advance record.

        Returns:
            Advance instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            cursor.execute(
                """
                SELECT a.*, w.full_name AS worker_name
                FROM advances a
                JOIN workers w ON w.id = a.worker_id
                WHERE a.id = %s
                """,
                (advance_id,),
            )
            row = cursor.fetchone()
            return self._row_to_advance(row) if row else None

    def get_all(
        self,
        worker_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> List[Advance]:
        """Retrieve advance records with optional filters.

        Args:
            worker_id: Optional worker id filter.
            status: Optional status filter.

        Returns:
            List of Advance instances ordered by date descending.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            query = """
                SELECT a.*, w.full_name AS worker_name
                FROM advances a
                JOIN workers w ON w.id = a.worker_id
            """
            conditions = []
            params: List[Any] = []

            if worker_id:
                conditions.append("a.worker_id = %s")
                params.append(worker_id)

            if status:
                conditions.append("a.status = %s")
                params.append(status)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY a.advance_date DESC, a.id DESC"

            cursor.execute(query, tuple(params))
            return [self._row_to_advance(row) for row in cursor.fetchall()]

    def update(self, advance: Advance) -> Optional[Advance]:
        """Update an existing advance record.

        Args:
            advance: Advance instance with updated fields.

        Returns:
            Updated Advance instance if found, None otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            try:
                query = """
                    UPDATE advances
                    SET worker_id = %s, amount = %s, advance_date = %s,
                        status = %s, notes = %s
                    WHERE id = %s
                """
                cursor.execute(query, (
                    advance.worker_id,
                    advance.amount,
                    advance.advance_date,
                    advance.status,
                    advance.notes,
                    advance.id,
                ))
                conn.commit()
                if cursor.rowcount > 0:
                    return self.get_by_id(advance.id)
                return None
            except mysql.connector.Error:
                conn.rollback()
                raise

    def delete(self, advance_id: int) -> bool:
        """Delete an advance record.

        Args:
            advance_id: The unique identifier of the advance record.

        Returns:
            True if the record was deleted, False otherwise.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                cursor.execute("DELETE FROM advances WHERE id = %s", (advance_id,))
                conn.commit()
                return cursor.rowcount > 0
            except mysql.connector.Error:
                conn.rollback()
                raise

    def outstanding_total(self, worker_id: Optional[int] = None) -> float:
        """Sum advance amounts that are not yet settled.

        Args:
            worker_id: Optional worker id to restrict the sum.

        Returns:
            Total outstanding advance amount.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            query = "SELECT COALESCE(SUM(amount), 0) AS total FROM advances WHERE status IN ('pending', 'paid')"
            params: tuple = ()
            if worker_id:
                query += " AND worker_id = %s"
                params = (worker_id,)
            cursor.execute(query, params)
            return float(cursor.fetchone()["total"])

    def settle_all_for_worker(self, worker_id: int) -> None:
        """Mark all outstanding advances of a worker as settled.

        Args:
            worker_id: The unique identifier of the worker.

        Raises:
            mysql.connector.Error: If database operation fails.
        """
        with self._database.connection() as conn, db_cursor(conn) as cursor:
            try:
                cursor.execute(
                    "UPDATE advances SET status = 'settled' WHERE worker_id = %s AND status IN ('pending', 'paid')",
                    (worker_id,),
                )
                conn.commit()
            except mysql.connector.Error:
                conn.rollback()
                raise


class WorkerManagementRepository:
    """Repository for worker management statistics and reports."""

    def __init__(self, database: Database) -> None:
        """Initialize WorkerManagementRepository with a Database instance.

        Args:
            database: Database connection pool manager.
        """
        self._database = database

    def get_statistics(self) -> Dict[str, Any]:
        """Collect all worker management dashboard statistics.

        Returns:
            Dictionary with worker counts, attendance summary, salary and
            advance totals, and recent records.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:

            def count(query: str, params: tuple = ()) -> int:
                cursor.execute(query, params)
                return cursor.fetchone()["count"]

            total_workers = count("SELECT COUNT(*) AS count FROM workers")
            active_workers = count(
                "SELECT COUNT(*) AS count FROM workers WHERE status = 'active'"
            )

            cursor.execute("SELECT status, COUNT(*) AS count FROM attendance GROUP BY status")
            attendance_by_status = {status: 0 for status in ("present", "absent", "late", "half_day", "leave")}
            for row in cursor.fetchall():
                if row["status"] in attendance_by_status:
                    attendance_by_status[row["status"]] = row["count"]

            today_attendance = count(
                "SELECT COUNT(*) AS count FROM attendance WHERE attendance_date = CURDATE()"
            )

            cursor.execute(
                "SELECT payment_status, COUNT(*) AS count, "
                "COALESCE(SUM(net_amount), 0) AS total FROM salaries "
                "WHERE payment_status != 'paid' GROUP BY payment_status"
            )
            pending_salary_count = 0
            pending_salary_total = 0.0
            for row in cursor.fetchall():
                pending_salary_count += row["count"]
                pending_salary_total += float(row["total"])

            total_salaries_paid = count(
                "SELECT COUNT(*) AS count FROM salaries WHERE payment_status = 'paid'"
            )

            total_advances = count("SELECT COUNT(*) AS count FROM advances")
            outstanding_advances = float(
                count(
                    "SELECT COALESCE(SUM(amount), 0) AS count FROM advances "
                    "WHERE status IN ('pending', 'paid')"
                )
            )

            cursor.execute(
                "SELECT id, full_name, phone, job_title, department, base_salary, status "
                "FROM workers ORDER BY created_at DESC LIMIT 5"
            )
            recent_workers = cursor.fetchall()

        for worker in recent_workers:
            if worker["base_salary"] is not None:
                worker["base_salary"] = float(worker["base_salary"])

        return {
            "total_workers": total_workers,
            "active_workers": active_workers,
            "attendance_by_status": attendance_by_status,
            "today_attendance": today_attendance,
            "pending_salary_count": pending_salary_count,
            "pending_salary_total": pending_salary_total,
            "total_salaries_paid": total_salaries_paid,
            "total_advances": total_advances,
            "outstanding_advances": outstanding_advances,
            "recent_workers": recent_workers,
        }

    def get_attendance_report(
        self,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Build an attendance report within an optional date range.

        Args:
            from_date: Optional start date (YYYY-MM-DD).
            to_date: Optional end date (YYYY-MM-DD).

        Returns:
            List of worker attendance summaries ordered by worker name.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            conditions = []
            params: List[Any] = []

            if from_date:
                conditions.append("a.attendance_date >= %s")
                params.append(from_date)

            if to_date:
                conditions.append("a.attendance_date <= %s")
                params.append(to_date)

            where = " WHERE " + " AND ".join(conditions) if conditions else ""

            query = f"""
                SELECT w.id AS worker_id, w.full_name AS worker_name,
                    COUNT(a.id) AS total_days,
                    SUM(a.status = 'present') AS present_days,
                    SUM(a.status = 'late') AS late_days,
                    SUM(a.status = 'half_day') AS half_days,
                    SUM(a.status = 'absent') AS absent_days,
                    SUM(a.status = 'leave') AS leave_days
                FROM workers w
                LEFT JOIN attendance a ON a.worker_id = w.id{where}
                GROUP BY w.id, w.full_name
                ORDER BY w.full_name ASC
            """
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()

        return [
            {
                "worker_id": row["worker_id"],
                "worker_name": row["worker_name"],
                "total_days": row["total_days"],
                "present_days": row["present_days"],
                "late_days": row["late_days"],
                "half_days": row["half_days"],
                "absent_days": row["absent_days"],
                "leave_days": row["leave_days"],
            }
            for row in rows
        ]

    def get_salary_report(
        self,
        from_period: Optional[str] = None,
        to_period: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Build a salary report within an optional period range.

        Args:
            from_period: Optional start period (YYYY-MM).
            to_period: Optional end period (YYYY-MM).

        Returns:
            List of salary report rows ordered by period descending.
        """
        with self._database.connection() as conn, db_cursor(conn, dictionary=True) as cursor:
            conditions = []
            params: List[Any] = []

            if from_period:
                conditions.append("s.salary_period >= %s")
                params.append(from_period)

            if to_period:
                conditions.append("s.salary_period <= %s")
                params.append(to_period)

            where = " WHERE " + " AND ".join(conditions) if conditions else ""

            query = f"""
                SELECT s.id, s.worker_id, w.full_name AS worker_name, s.salary_period,
                    s.base_salary, s.bonuses, s.deductions, s.advances_deduction,
                    s.net_amount, s.payment_status, s.payment_date
                FROM salaries s
                JOIN workers w ON w.id = s.worker_id
                {where}
                ORDER BY s.salary_period DESC, w.full_name ASC
            """
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()

        return [
            {
                "id": row["id"],
                "worker_id": row["worker_id"],
                "worker_name": row["worker_name"],
                "salary_period": row["salary_period"],
                "base_salary": float(row["base_salary"]) if row["base_salary"] is not None else None,
                "bonuses": float(row["bonuses"]) if row["bonuses"] is not None else None,
                "deductions": float(row["deductions"]) if row["deductions"] is not None else None,
                "advances_deduction": float(row["advances_deduction"])
                if row["advances_deduction"] is not None else None,
                "net_amount": float(row["net_amount"]) if row["net_amount"] is not None else None,
                "payment_status": row["payment_status"],
                "payment_date": row["payment_date"].isoformat() if row["payment_date"] else None,
            }
            for row in rows
        ]
