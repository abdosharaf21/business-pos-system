"""Worker Management models representing the worker_management tables.

Only database table representations live here: constructors, properties,
``to_dict()``, ``from_dict()``, ``__str__()`` and ``__repr__()``. No SQL,
business logic, or authentication code is allowed in this module.
"""

from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional


def _to_decimal(value) -> Optional[float]:
    """Coerce a value to a float, tolerating None and Decimal inputs.

    Args:
        value: Numeric value, Decimal, or None.

    Returns:
        Float representation, or None if the value is None.
    """
    if value is None:
        return None
    return float(value)


def _to_date(value) -> Optional[date]:
    """Coerce a value to a date, tolerating None, date and datetime inputs.

    Args:
        value: Date-like value or None.

    Returns:
        Date instance, or None if the value is None.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value[:10])
        except ValueError:
            return None
    return None


def _to_time(value) -> Optional[str]:
    """Coerce a value to a TIME string, tolerating None.

    Args:
        value: Time-like value (time, timedelta, str) or None.

    Returns:
        ``HH:MM:SS`` string, or None if the value is None.
    """
    if value is None:
        return None
    if isinstance(value, time):
        return value.strftime("%H:%M:%S")
    return str(value)[:8]


def _to_datetime(value) -> Optional[datetime]:
    """Coerce a value to a datetime, tolerating None.

    Args:
        value: Datetime-like value or None.

    Returns:
        Datetime instance, or None if the value is None.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    return None


class Worker:
    """Represents a worker record in the workers table.

    Attributes:
        id: Unique identifier for the worker.
        full_name: Full name of the worker.
        phone: Contact phone number of the worker.
        email: Optional contact email of the worker.
        job_title: Role or job title of the worker.
        department: Optional department the worker belongs to.
        hire_date: Date the worker was hired.
        base_salary: Base salary of the worker.
        status: Worker status (active or inactive).
        notes: Optional free-text notes about the worker.
        created_at: Timestamp when the worker was created.
        updated_at: Timestamp when the worker was last updated.
    """

    def __init__(
        self,
        id: Optional[int] = None,
        full_name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        job_title: Optional[str] = None,
        department: Optional[str] = None,
        hire_date: Optional[date] = None,
        base_salary: Optional[float] = None,
        status: str = "active",
        notes: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        """Initialize a Worker instance.

        Args:
            id: Unique identifier for the worker.
            full_name: Full name of the worker.
            phone: Contact phone number of the worker.
            email: Optional contact email of the worker.
            job_title: Role or job title of the worker.
            department: Optional department of the worker.
            hire_date: Date the worker was hired.
            base_salary: Base salary of the worker.
            status: Worker status (active or inactive).
            notes: Optional free-text notes about the worker.
            created_at: Timestamp when the worker was created.
            updated_at: Timestamp when the worker was last updated.
        """
        self.id = id
        self.full_name = full_name
        self.phone = phone
        self.email = email
        self.job_title = job_title
        self.department = department
        self.hire_date = _to_date(hire_date)
        self.base_salary = _to_decimal(base_salary)
        self.status = status
        self.notes = notes
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> dict:
        """Convert the Worker instance to a dictionary.

        Returns:
            Dictionary representation of the worker.
        """
        return {
            "id": self.id,
            "full_name": self.full_name,
            "phone": self.phone,
            "email": self.email,
            "job_title": self.job_title,
            "department": self.department,
            "hire_date": self.hire_date.isoformat() if self.hire_date else None,
            "base_salary": self.base_salary,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Worker":
        """Create a Worker instance from a dictionary.

        Args:
            data: Dictionary containing worker data.

        Returns:
            Worker instance created from the dictionary.
        """
        return cls(
            id=data.get("id"),
            full_name=data.get("full_name"),
            phone=data.get("phone"),
            email=data.get("email"),
            job_title=data.get("job_title"),
            department=data.get("department"),
            hire_date=_to_date(data.get("hire_date")),
            base_salary=data.get("base_salary"),
            status=data.get("status", "active"),
            notes=data.get("notes"),
            created_at=_to_datetime(data.get("created_at")),
            updated_at=_to_datetime(data.get("updated_at")),
        )

    def __str__(self) -> str:
        """Return a short string representation.

        Returns:
            String with worker id and full name.
        """
        return f"Worker(id={self.id}, full_name={self.full_name})"

    def __repr__(self) -> str:
        """Return a developer-friendly string representation.

        Returns:
            Same as __str__.
        """
        return self.__str__()


class Attendance:
    """Represents a worker attendance record.

    Attributes:
        id: Unique identifier for the attendance record.
        worker_id: Identifier of the worker.
        worker_name: Optional worker name (joined).
        attendance_date: Date the attendance applies to.
        status: Attendance status (present, absent, late, half_day, leave).
        check_in: Optional check-in time.
        check_out: Optional check-out time.
        notes: Optional free-text notes.
        created_at: Timestamp when the record was created.
    """

    STATUSES = ("present", "absent", "late", "half_day", "leave")

    def __init__(
        self,
        id: Optional[int] = None,
        worker_id: Optional[int] = None,
        worker_name: Optional[str] = None,
        attendance_date: Optional[date] = None,
        status: str = "present",
        check_in: Optional[str] = None,
        check_out: Optional[str] = None,
        notes: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ) -> None:
        """Initialize an Attendance instance.

        Args:
            id: Unique identifier for the attendance record.
            worker_id: Identifier of the worker.
            worker_name: Optional worker name (joined).
            attendance_date: Date the attendance applies to.
            status: Attendance status.
            check_in: Optional check-in time.
            check_out: Optional check-out time.
            notes: Optional free-text notes.
            created_at: Timestamp when the record was created.
        """
        self.id = id
        self.worker_id = worker_id
        self.worker_name = worker_name
        self.attendance_date = _to_date(attendance_date)
        self.status = status
        self.check_in = _to_time(check_in)
        self.check_out = _to_time(check_out)
        self.notes = notes
        self.created_at = created_at

    def to_dict(self) -> dict:
        """Convert the Attendance instance to a dictionary.

        Returns:
            Dictionary representation of the attendance record.
        """
        return {
            "id": self.id,
            "worker_id": self.worker_id,
            "worker_name": self.worker_name,
            "attendance_date": self.attendance_date.isoformat()
            if self.attendance_date
            else None,
            "status": self.status,
            "check_in": self.check_in,
            "check_out": self.check_out,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Attendance":
        """Create an Attendance instance from a dictionary.

        Args:
            data: Dictionary containing attendance data.

        Returns:
            Attendance instance created from the dictionary.
        """
        return cls(
            id=data.get("id"),
            worker_id=data.get("worker_id"),
            worker_name=data.get("worker_name"),
            attendance_date=_to_date(data.get("attendance_date")),
            status=data.get("status", "present"),
            check_in=data.get("check_in"),
            check_out=data.get("check_out"),
            notes=data.get("notes"),
            created_at=_to_datetime(data.get("created_at")),
        )

    def __str__(self) -> str:
        """Return a short string representation.

        Returns:
            String with attendance id and worker id.
        """
        return f"Attendance(id={self.id}, worker_id={self.worker_id})"

    def __repr__(self) -> str:
        """Return a developer-friendly string representation.

        Returns:
            Same as __str__.
        """
        return self.__str__()


class Salary:
    """Represents a worker salary record.

    Attributes:
        id: Unique identifier for the salary record.
        worker_id: Identifier of the worker.
        worker_name: Optional worker name (joined).
        salary_period: Salary period in ``YYYY-MM`` format.
        base_salary: Base salary for the period.
        bonuses: Bonus amount for the period.
        deductions: Deduction amount for the period.
        advances_deduction: Amount deducted to repay worker advances.
        net_amount: Computed net salary.
        payment_status: Payment status (paid, pending, partial).
        payment_date: Date the salary was paid.
        notes: Optional free-text notes.
        created_at: Timestamp when the record was created.
        updated_at: Timestamp when the record was last updated.
    """

    STATUSES = ("paid", "pending", "partial")

    def __init__(
        self,
        id: Optional[int] = None,
        worker_id: Optional[int] = None,
        worker_name: Optional[str] = None,
        salary_period: Optional[str] = None,
        base_salary: Optional[float] = None,
        bonuses: Optional[float] = None,
        deductions: Optional[float] = None,
        advances_deduction: Optional[float] = None,
        net_amount: Optional[float] = None,
        payment_status: str = "pending",
        payment_date: Optional[date] = None,
        notes: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        """Initialize a Salary instance.

        Args:
            id: Unique identifier for the salary record.
            worker_id: Identifier of the worker.
            worker_name: Optional worker name (joined).
            salary_period: Salary period in ``YYYY-MM`` format.
            base_salary: Base salary for the period.
            bonuses: Bonus amount for the period.
            deductions: Deduction amount for the period.
            advances_deduction: Amount deducted to repay worker advances.
            net_amount: Computed net salary.
            payment_status: Payment status.
            payment_date: Date the salary was paid.
            notes: Optional free-text notes.
            created_at: Timestamp when the record was created.
            updated_at: Timestamp when the record was last updated.
        """
        self.id = id
        self.worker_id = worker_id
        self.worker_name = worker_name
        self.salary_period = salary_period
        self.base_salary = _to_decimal(base_salary)
        self.bonuses = _to_decimal(bonuses)
        self.deductions = _to_decimal(deductions)
        self.advances_deduction = _to_decimal(advances_deduction)
        self.net_amount = _to_decimal(net_amount)
        self.payment_status = payment_status
        self.payment_date = _to_date(payment_date)
        self.notes = notes
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> dict:
        """Convert the Salary instance to a dictionary.

        Returns:
            Dictionary representation of the salary record.
        """
        return {
            "id": self.id,
            "worker_id": self.worker_id,
            "worker_name": self.worker_name,
            "salary_period": self.salary_period,
            "base_salary": self.base_salary,
            "bonuses": self.bonuses,
            "deductions": self.deductions,
            "advances_deduction": self.advances_deduction,
            "net_amount": self.net_amount,
            "payment_status": self.payment_status,
            "payment_date": self.payment_date.isoformat() if self.payment_date else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Salary":
        """Create a Salary instance from a dictionary.

        Args:
            data: Dictionary containing salary data.

        Returns:
            Salary instance created from the dictionary.
        """
        return cls(
            id=data.get("id"),
            worker_id=data.get("worker_id"),
            worker_name=data.get("worker_name"),
            salary_period=data.get("salary_period"),
            base_salary=data.get("base_salary"),
            bonuses=data.get("bonuses"),
            deductions=data.get("deductions"),
            advances_deduction=data.get("advances_deduction"),
            net_amount=data.get("net_amount"),
            payment_status=data.get("payment_status", "pending"),
            payment_date=_to_date(data.get("payment_date")),
            notes=data.get("notes"),
            created_at=_to_datetime(data.get("created_at")),
            updated_at=_to_datetime(data.get("updated_at")),
        )

    def __str__(self) -> str:
        """Return a short string representation.

        Returns:
            String with salary id and period.
        """
        return f"Salary(id={self.id}, period={self.salary_period})"

    def __repr__(self) -> str:
        """Return a developer-friendly string representation.

        Returns:
            Same as __str__.
        """
        return self.__str__()


class Advance:
    """Represents a worker advance record.

    Attributes:
        id: Unique identifier for the advance record.
        worker_id: Identifier of the worker.
        worker_name: Optional worker name (joined).
        amount: Advance amount.
        advance_date: Date the advance was given.
        status: Advance status (pending, paid, settled).
        notes: Optional free-text notes.
        created_at: Timestamp when the record was created.
        updated_at: Timestamp when the record was last updated.
    """

    STATUSES = ("pending", "paid", "settled")

    def __init__(
        self,
        id: Optional[int] = None,
        worker_id: Optional[int] = None,
        worker_name: Optional[str] = None,
        amount: Optional[float] = None,
        advance_date: Optional[date] = None,
        status: str = "pending",
        notes: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        """Initialize an Advance instance.

        Args:
            id: Unique identifier for the advance record.
            worker_id: Identifier of the worker.
            worker_name: Optional worker name (joined).
            amount: Advance amount.
            advance_date: Date the advance was given.
            status: Advance status.
            notes: Optional free-text notes.
            created_at: Timestamp when the record was created.
            updated_at: Timestamp when the record was last updated.
        """
        self.id = id
        self.worker_id = worker_id
        self.worker_name = worker_name
        self.amount = _to_decimal(amount)
        self.advance_date = _to_date(advance_date)
        self.status = status
        self.notes = notes
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> dict:
        """Convert the Advance instance to a dictionary.

        Returns:
            Dictionary representation of the advance record.
        """
        return {
            "id": self.id,
            "worker_id": self.worker_id,
            "worker_name": self.worker_name,
            "amount": self.amount,
            "advance_date": self.advance_date.isoformat()
            if self.advance_date
            else None,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Advance":
        """Create an Advance instance from a dictionary.

        Args:
            data: Dictionary containing advance data.

        Returns:
            Advance instance created from the dictionary.
        """
        return cls(
            id=data.get("id"),
            worker_id=data.get("worker_id"),
            worker_name=data.get("worker_name"),
            amount=data.get("amount"),
            advance_date=_to_date(data.get("advance_date")),
            status=data.get("status", "pending"),
            notes=data.get("notes"),
            created_at=_to_datetime(data.get("created_at")),
            updated_at=_to_datetime(data.get("updated_at")),
        )

    def __str__(self) -> str:
        """Return a short string representation.

        Returns:
            String with advance id and worker id.
        """
        return f"Advance(id={self.id}, worker_id={self.worker_id})"

    def __repr__(self) -> str:
        """Return a developer-friendly string representation.

        Returns:
            Same as __str__.
        """
        return self.__str__()
