"""Worker management service for all worker and payroll business logic.

Handles workers, attendance, salaries and advances. Communicates only
with repositories and validators; it never executes raw SQL.
"""

from datetime import date
from typing import Any, Dict, List, Optional

from backend.modules.worker_management.model import (
    Advance,
    Attendance,
    Salary,
    Worker,
)
from backend.modules.worker_management.repository import (
    AdvanceRepository,
    AttendanceRepository,
    SalaryRepository,
    WorkerManagementRepository,
    WorkerRepository,
)
from backend.modules.worker_management.validator import WorkerValidator


class WorkerManagementService:
    """Service for worker management business operations."""

    def __init__(
        self,
        worker_repository: WorkerRepository,
        attendance_repository: AttendanceRepository,
        salary_repository: SalaryRepository,
        advance_repository: AdvanceRepository,
        worker_management_repository: WorkerManagementRepository,
    ) -> None:
        """Initialize WorkerManagementService with its repositories.

        Args:
            worker_repository: Repository for workers table operations.
            attendance_repository: Repository for attendance table operations.
            salary_repository: Repository for salaries table operations.
            advance_repository: Repository for advances table operations.
            worker_management_repository: Repository for statistics and reports.
        """
        self._worker_repository = worker_repository
        self._attendance_repository = attendance_repository
        self._salary_repository = salary_repository
        self._advance_repository = advance_repository
        self._worker_management_repository = worker_management_repository

    # ------------------------------------------------------------------
    # Workers
    # ------------------------------------------------------------------

    def create_worker(self, data: dict) -> Worker:
        """Create a new worker.

        Args:
            data: Dictionary containing worker information.

        Returns:
            Created Worker instance.

        Raises:
            ValueError: If validation fails or business rules are violated.
        """
        validated = WorkerValidator.validate_worker(data)

        if self._worker_repository.exists_by_phone(validated["phone"]):
            raise ValueError("A worker with this phone number already exists")

        if validated["email"] and self._worker_repository.exists_by_email(validated["email"]):
            raise ValueError("A worker with this email already exists")

        worker = Worker(
            full_name=validated["full_name"],
            phone=validated["phone"],
            email=validated["email"],
            job_title=validated["job_title"],
            department=validated["department"],
            hire_date=validated["hire_date"],
            base_salary=validated["base_salary"] or 0.0,
            status=validated["status"],
            notes=validated["notes"],
        )

        return self._worker_repository.create(worker)

    def get_worker(self, worker_id: int) -> Worker:
        """Retrieve a worker by its unique identifier.

        Args:
            worker_id: The unique identifier of the worker.

        Returns:
            Worker instance if found.

        Raises:
            ValueError: If worker not found.
        """
        worker = self._worker_repository.get_by_id(worker_id)
        if worker is None:
            raise ValueError("Worker not found")
        return worker

    def get_all_workers(
        self,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Worker]:
        """Retrieve workers with optional search and status filters.

        Args:
            search: Optional search term for name, phone, job title or department.
            status: Optional status filter.

        Returns:
            List of Worker instances.
        """
        return self._worker_repository.get_all(search=search, status=status)

    def update_worker(self, worker_id: int, data: dict) -> Worker:
        """Update an existing worker.

        Args:
            worker_id: The unique identifier of the worker.
            data: Dictionary containing fields to update.

        Returns:
            Updated Worker instance.

        Raises:
            ValueError: If worker not found or validation fails.
        """
        validated = WorkerValidator.validate_worker(data, partial=True)

        worker = self._worker_repository.get_by_id(worker_id)
        if worker is None:
            raise ValueError("Worker not found")

        if "phone" in validated:
            if validated["phone"] != worker.phone and self._worker_repository.exists_by_phone(
                validated["phone"]
            ):
                raise ValueError("A worker with this phone number already exists")
            worker.phone = validated["phone"]

        if "email" in validated:
            if validated["email"] and validated["email"] != worker.email and (
                self._worker_repository.exists_by_email(validated["email"])
            ):
                raise ValueError("A worker with this email already exists")
            worker.email = validated["email"]

        for field in (
            "full_name",
            "job_title",
            "department",
            "hire_date",
            "status",
            "notes",
        ):
            if field in validated:
                setattr(worker, field, validated[field])

        if "base_salary" in validated:
            worker.base_salary = validated["base_salary"] or 0.0

        updated = self._worker_repository.update(worker)
        if updated is None:
            raise ValueError("Failed to update worker")
        return updated

    def delete_worker(self, worker_id: int) -> bool:
        """Delete a worker.

        Args:
            worker_id: The unique identifier of the worker.

        Returns:
            True if the worker was deleted successfully.

        Raises:
            ValueError: If worker not found.
        """
        deleted = self._worker_repository.delete(worker_id)
        if not deleted:
            raise ValueError("Worker not found")
        return True

    # ------------------------------------------------------------------
    # Attendance
    # ------------------------------------------------------------------

    def create_attendance(self, data: dict) -> Attendance:
        """Create a new attendance record.

        Args:
            data: Dictionary containing attendance information.

        Returns:
            Created Attendance instance.

        Raises:
            ValueError: If validation fails or business rules are violated.
        """
        validated = WorkerValidator.validate_attendance(data)

        self.get_worker(validated["worker_id"])

        if validated["attendance_date"] is None:
            raise ValueError("Attendance date is required")

        if self._attendance_repository.exists(validated["worker_id"], validated["attendance_date"]):
            raise ValueError("Attendance already exists for this worker and date")

        attendance = Attendance(
            worker_id=validated["worker_id"],
            attendance_date=validated["attendance_date"],
            status=validated["status"],
            check_in=validated["check_in"],
            check_out=validated["check_out"],
            notes=validated["notes"],
        )

        return self._attendance_repository.create(attendance)

    def get_attendance(self, attendance_id: int) -> Attendance:
        """Retrieve an attendance record by its unique identifier.

        Args:
            attendance_id: The unique identifier of the attendance record.

        Returns:
            Attendance instance if found.

        Raises:
            ValueError: If attendance record not found.
        """
        attendance = self._attendance_repository.get_by_id(attendance_id)
        if attendance is None:
            raise ValueError("Attendance record not found")
        return attendance

    def get_all_attendance(
        self,
        worker_id: Optional[int] = None,
        date: Optional[str] = None,
        month: Optional[str] = None,
    ) -> List[Attendance]:
        """Retrieve attendance records with optional filters.

        Args:
            worker_id: Optional worker id filter.
            date: Optional exact date filter.
            month: Optional month filter.

        Returns:
            List of Attendance instances.
        """
        return self._attendance_repository.get_all(
            worker_id=worker_id,
            date=date,
            month=month,
        )

    def update_attendance(self, attendance_id: int, data: dict) -> Attendance:
        """Update an existing attendance record.

        Args:
            attendance_id: The unique identifier of the attendance record.
            data: Dictionary containing fields to update.

        Returns:
            Updated Attendance instance.

        Raises:
            ValueError: If record not found or validation fails.
        """
        validated = WorkerValidator.validate_attendance(data, partial=True)

        attendance = self._attendance_repository.get_by_id(attendance_id)
        if attendance is None:
            raise ValueError("Attendance record not found")

        if "worker_id" in validated and validated["worker_id"] != attendance.worker_id:
            self.get_worker(validated["worker_id"])
            attendance.worker_id = validated["worker_id"]

        if "attendance_date" in validated:
            attendance.attendance_date = validated["attendance_date"]

        if self._attendance_repository.exists(attendance.worker_id, attendance.attendance_date):
            existing = self._attendance_repository.get_all(
                worker_id=attendance.worker_id,
                date=attendance.attendance_date,
            )
            if existing and existing[0].id != attendance_id:
                raise ValueError("Attendance already exists for this worker and date")

        for field in ("status", "check_in", "check_out", "notes"):
            if field in validated:
                setattr(attendance, field, validated[field])

        updated = self._attendance_repository.update(attendance)
        if updated is None:
            raise ValueError("Failed to update attendance record")
        return updated

    def delete_attendance(self, attendance_id: int) -> bool:
        """Delete an attendance record.

        Args:
            attendance_id: The unique identifier of the attendance record.

        Returns:
            True if the record was deleted successfully.

        Raises:
            ValueError: If record not found.
        """
        deleted = self._attendance_repository.delete(attendance_id)
        if not deleted:
            raise ValueError("Attendance record not found")
        return True

    # ------------------------------------------------------------------
    # Salaries
    # ------------------------------------------------------------------

    def create_salary(self, data: dict) -> Salary:
        """Create a new salary record.

        Computes the net salary automatically (base + bonuses - deductions
        - advances deduction). When advances deduction is not provided it
        defaults to the worker's total outstanding advances, and those
        advances are marked as settled.

        Args:
            data: Dictionary containing salary information.

        Returns:
            Created Salary instance.

        Raises:
            ValueError: If validation fails or business rules are violated.
        """
        validated = WorkerValidator.validate_salary(data)

        self.get_worker(validated["worker_id"])

        if validated["salary_period"] is None:
            raise ValueError("Salary period is required")

        if self._salary_repository.exists(validated["worker_id"], validated["salary_period"]):
            raise ValueError("Salary already exists for this worker and period")

        advances_deduction = validated.get("advances_deduction")
        if advances_deduction is None:
            advances_deduction = self._advance_repository.outstanding_total(
                validated["worker_id"]
            )

        net_amount = self._compute_net_salary(
            validated["base_salary"] or 0.0,
            validated.get("bonuses") or 0.0,
            validated.get("deductions") or 0.0,
            advances_deduction or 0.0,
        )

        salary = Salary(
            worker_id=validated["worker_id"],
            salary_period=validated["salary_period"],
            base_salary=validated["base_salary"] or 0.0,
            bonuses=validated["bonuses"] or 0.0,
            deductions=validated["deductions"] or 0.0,
            advances_deduction=advances_deduction or 0.0,
            net_amount=net_amount,
            payment_status=validated["payment_status"],
            payment_date=validated["payment_date"],
            notes=validated["notes"],
        )

        created = self._salary_repository.create(salary)

        if (created.advances_deduction or 0) > 0:
            self._advance_repository.settle_all_for_worker(created.worker_id)

        return created

    def get_salary(self, salary_id: int) -> Salary:
        """Retrieve a salary record by its unique identifier.

        Args:
            salary_id: The unique identifier of the salary record.

        Returns:
            Salary instance if found.

        Raises:
            ValueError: If salary record not found.
        """
        salary = self._salary_repository.get_by_id(salary_id)
        if salary is None:
            raise ValueError("Salary record not found")
        return salary

    def get_all_salaries(
        self,
        worker_id: Optional[int] = None,
        period: Optional[str] = None,
        payment_status: Optional[str] = None,
    ) -> List[Salary]:
        """Retrieve salary records with optional filters.

        Args:
            worker_id: Optional worker id filter.
            period: Optional period filter.
            payment_status: Optional payment status filter.

        Returns:
            List of Salary instances.
        """
        return self._salary_repository.get_all(
            worker_id=worker_id,
            period=period,
            payment_status=payment_status,
        )

    def update_salary(self, salary_id: int, data: dict) -> Salary:
        """Update an existing salary record.

        Args:
            salary_id: The unique identifier of the salary record.
            data: Dictionary containing fields to update.

        Returns:
            Updated Salary instance.

        Raises:
            ValueError: If record not found or validation fails.
        """
        validated = WorkerValidator.validate_salary(data, partial=True)

        salary = self._salary_repository.get_by_id(salary_id)
        if salary is None:
            raise ValueError("Salary record not found")

        if "worker_id" in validated and validated["worker_id"] != salary.worker_id:
            self.get_worker(validated["worker_id"])
            salary.worker_id = validated["worker_id"]

        if "salary_period" in validated:
            salary.salary_period = validated["salary_period"]

        if self._salary_repository.exists(salary.worker_id, salary.salary_period):
            existing = self._salary_repository.get_all(
                worker_id=salary.worker_id,
                period=salary.salary_period,
            )
            if existing and existing[0].id != salary_id:
                raise ValueError("Salary already exists for this worker and period")

        for field in (
            "payment_status",
            "payment_date",
            "notes",
        ):
            if field in validated:
                setattr(salary, field, validated[field])

        for field in (
            "base_salary",
            "bonuses",
            "deductions",
            "advances_deduction",
            "net_amount",
        ):
            if field in validated:
                setattr(salary, field, validated[field] or 0.0)

        if "net_amount" not in validated:
            salary.net_amount = self._compute_net_salary(
                salary.base_salary or 0.0,
                salary.bonuses or 0.0,
                salary.deductions or 0.0,
                salary.advances_deduction or 0.0,
            )

        updated = self._salary_repository.update(salary)
        if updated is None:
            raise ValueError("Failed to update salary record")
        return updated

    def mark_salary_paid(self, salary_id: int, data: dict) -> Salary:
        """Mark a salary record as paid.

        Args:
            salary_id: The unique identifier of the salary record.
            data: Dictionary optionally containing the payment date.

        Returns:
            Updated Salary instance.

        Raises:
            ValueError: If salary record not found.
        """
        salary = self.get_salary(salary_id)

        payment_date = data.get("payment_date") if data else None
        if payment_date is None:
            payment_date = date.today().isoformat()

        validated_date = WorkerValidator._optional_date(payment_date, "Payment date")

        salary.payment_status = "paid"
        salary.payment_date = validated_date or date.today().isoformat()

        updated = self._salary_repository.update(salary)
        if updated is None:
            raise ValueError("Failed to update salary record")
        return updated

    def delete_salary(self, salary_id: int) -> bool:
        """Delete a salary record.

        Args:
            salary_id: The unique identifier of the salary record.

        Returns:
            True if the record was deleted successfully.

        Raises:
            ValueError: If record not found.
        """
        deleted = self._salary_repository.delete(salary_id)
        if not deleted:
            raise ValueError("Salary record not found")
        return True

    # ------------------------------------------------------------------
    # Advances
    # ------------------------------------------------------------------

    def create_advance(self, data: dict) -> Advance:
        """Create a new advance record.

        Args:
            data: Dictionary containing advance information.

        Returns:
            Created Advance instance.

        Raises:
            ValueError: If validation fails or business rules are violated.
        """
        validated = WorkerValidator.validate_advance(data)

        self.get_worker(validated["worker_id"])

        if validated["advance_date"] is None:
            raise ValueError("Advance date is required")

        advance = Advance(
            worker_id=validated["worker_id"],
            amount=validated["amount"],
            advance_date=validated["advance_date"],
            status=validated["status"],
            notes=validated["notes"],
        )

        return self._advance_repository.create(advance)

    def get_advance(self, advance_id: int) -> Advance:
        """Retrieve an advance record by its unique identifier.

        Args:
            advance_id: The unique identifier of the advance record.

        Returns:
            Advance instance if found.

        Raises:
            ValueError: If advance record not found.
        """
        advance = self._advance_repository.get_by_id(advance_id)
        if advance is None:
            raise ValueError("Advance record not found")
        return advance

    def get_all_advances(
        self,
        worker_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> List[Advance]:
        """Retrieve advance records with optional filters.

        Args:
            worker_id: Optional worker id filter.
            status: Optional status filter.

        Returns:
            List of Advance instances.
        """
        return self._advance_repository.get_all(worker_id=worker_id, status=status)

    def update_advance(self, advance_id: int, data: dict) -> Advance:
        """Update an existing advance record.

        Args:
            advance_id: The unique identifier of the advance record.
            data: Dictionary containing fields to update.

        Returns:
            Updated Advance instance.

        Raises:
            ValueError: If record not found or validation fails.
        """
        validated = WorkerValidator.validate_advance(data, partial=True)

        advance = self._advance_repository.get_by_id(advance_id)
        if advance is None:
            raise ValueError("Advance record not found")

        if "worker_id" in validated and validated["worker_id"] != advance.worker_id:
            self.get_worker(validated["worker_id"])
            advance.worker_id = validated["worker_id"]

        for field in ("amount", "advance_date", "status", "notes"):
            if field in validated:
                setattr(advance, field, validated[field])

        updated = self._advance_repository.update(advance)
        if updated is None:
            raise ValueError("Failed to update advance record")
        return updated

    def delete_advance(self, advance_id: int) -> bool:
        """Delete an advance record.

        Args:
            advance_id: The unique identifier of the advance record.

        Returns:
            True if the record was deleted successfully.

        Raises:
            ValueError: If record not found.
        """
        deleted = self._advance_repository.delete(advance_id)
        if not deleted:
            raise ValueError("Advance record not found")
        return True

    # ------------------------------------------------------------------
    # Statistics and reports
    # ------------------------------------------------------------------

    def get_statistics(self) -> Dict[str, Any]:
        """Collect all worker management dashboard statistics.

        Returns:
            Dictionary with worker management statistics.
        """
        return self._worker_management_repository.get_statistics()

    def get_attendance_report(
        self,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Build an attendance report within an optional date range.

        Args:
            from_date: Optional start date.
            to_date: Optional end date.

        Returns:
            List of attendance report rows.
        """
        return self._worker_management_repository.get_attendance_report(
            from_date=from_date,
            to_date=to_date,
        )

    def get_salary_report(
        self,
        from_period: Optional[str] = None,
        to_period: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Build a salary report within an optional period range.

        Args:
            from_period: Optional start period.
            to_period: Optional end period.

        Returns:
            List of salary report rows.
        """
        return self._worker_management_repository.get_salary_report(
            from_period=from_period,
            to_period=to_period,
        )

    @staticmethod
    def _compute_net_salary(
        base_salary: float,
        bonuses: float,
        deductions: float,
        advances_deduction: float,
    ) -> float:
        """Compute the net salary for a period.

        Args:
            base_salary: Base salary amount.
            bonuses: Bonus amount.
            deductions: Deduction amount.
            advances_deduction: Advances deduction amount.

        Returns:
            Net salary rounded to two decimal places.
        """
        return round(base_salary + bonuses - deductions - advances_deduction, 2)
