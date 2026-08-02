"""Expense and expense category models representing database tables."""

from datetime import date, datetime
from typing import Optional


class ExpenseCategory:
    """Represents an expense category record.

    Attributes:
        id: Unique identifier for the category.
        name: Category name (Rent, Salaries, Electricity, ...).
        description: Optional free-text description.
        created_at: Timestamp when the record was created.
    """

    def __init__(
        self,
        id: Optional[int] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        created_at: Optional[datetime] = None,
    ) -> None:
        """Initialize an ExpenseCategory instance.

        Args:
            id: Unique identifier for the category.
            name: Category name.
            description: Optional description.
            created_at: Timestamp when the record was created.
        """
        self.id = id
        self.name = name
        self.description = description
        self.created_at = created_at or datetime.now()

    def to_dict(self) -> dict:
        """Convert ExpenseCategory instance to dictionary.

        Returns:
            Dictionary representation of the category.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __str__(self) -> str:
        """Return string representation of the category.

        Returns:
            String with category id and name.
        """
        return f"ExpenseCategory(id={self.id}, name={self.name})"

    def __repr__(self) -> str:
        """Return developer-friendly string representation.

        Returns:
            Same as __str__.
        """
        return self.__str__()


class Expense:
    """Represents an expense record in the expenses table.

    Attributes:
        id: Unique identifier for the expense.
        title: Short title describing the expense.
        category_id: Foreign key referencing expense_categories.id.
        category_name: Expense category name (from a join).
        amount: Monetary amount of the expense.
        payment_method: How the expense was paid (Cash, Bank, Visa, Other).
        notes: Optional free-text notes.
        expense_date: Date the expense occurred.
        created_by: ID of the user who recorded the expense.
        created_by_name: Optional full name of the creating user (from join).
        created_at: Timestamp when the record was created.
        updated_at: Timestamp when the record was last updated.
    """

    def __init__(
        self,
        id: Optional[int] = None,
        title: Optional[str] = None,
        category_id: Optional[int] = None,
        category_name: Optional[str] = None,
        amount: Optional[float] = None,
        payment_method: Optional[str] = None,
        notes: Optional[str] = None,
        expense_date: Optional[date] = None,
        created_by: Optional[int] = None,
        created_by_name: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        """Initialize an Expense instance.

        Args:
            id: Unique identifier for the expense.
            title: Short title describing the expense.
            category_id: Foreign key referencing expense_categories.id.
            category_name: Expense category name.
            amount: Monetary amount of the expense.
            payment_method: Payment method used.
            notes: Optional free-text notes.
            expense_date: Date the expense occurred.
            created_by: ID of the user who recorded the expense.
            created_by_name: Optional full name of the creating user.
            created_at: Timestamp when the record was created.
            updated_at: Timestamp when the record was last updated.
        """
        self.id = id
        self.title = title
        self.category_id = category_id
        self.category_name = category_name
        self.amount = amount
        self.payment_method = payment_method
        self.notes = notes
        self.expense_date = expense_date
        self.created_by = created_by
        self.created_by_name = created_by_name
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def to_dict(self) -> dict:
        """Convert Expense instance to dictionary.

        Returns:
            Dictionary representation of the expense.
        """
        result = {
            "id": self.id,
            "title": self.title,
            "category_id": self.category_id,
            "amount": float(self.amount) if self.amount is not None else 0.0,
            "payment_method": self.payment_method,
            "notes": self.notes,
            "expense_date": self.expense_date.isoformat() if self.expense_date else None,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
        if self.category_name is not None:
            result["category_name"] = self.category_name
        if self.created_by_name is not None:
            result["created_by_name"] = self.created_by_name
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "Expense":
        """Create an Expense instance from a dictionary.

        Args:
            data: Dictionary containing expense data.

        Returns:
            Expense instance created from the dictionary.
        """
        expense_date = data.get("expense_date")
        if expense_date and isinstance(expense_date, str):
            expense_date = datetime.strptime(expense_date, "%Y-%m-%d").date()

        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)

        updated_at = data.get("updated_at")
        if updated_at and isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)

        return cls(
            id=data.get("id"),
            title=data.get("title"),
            category_id=data.get("category_id"),
            category_name=data.get("category_name"),
            amount=data.get("amount"),
            payment_method=data.get("payment_method"),
            notes=data.get("notes"),
            expense_date=expense_date,
            created_by=data.get("created_by"),
            created_by_name=data.get("created_by_name"),
            created_at=created_at,
            updated_at=updated_at,
        )

    def __str__(self) -> str:
        """Return string representation of the Expense.

        Returns:
            String with expense id and title.
        """
        return f"Expense(id={self.id}, title={self.title}, amount={self.amount})"

    def __repr__(self) -> str:
        """Return developer-friendly string representation.

        Returns:
            Same as __str__.
        """
        return self.__str__()
