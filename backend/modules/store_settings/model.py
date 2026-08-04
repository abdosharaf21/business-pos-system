"""StoreSettings model representing the single business configuration row."""

from typing import Dict, Any, Optional


class StoreSettings:
    """Model for the store/business configuration.

    Represents the single row in the store_settings table. Contains no
    SQL, validation, or business logic.

    Attributes:
        DEFAULT_CURRENCY: Default currency code used before customization.
    """

    DEFAULT_CURRENCY = "EGP"

    def __init__(
        self,
        id: Optional[int] = None,
        store_name: str = "",
        owner_name: str = "",
        phone: str = "",
        email: str = "",
        address: str = "",
        website: str = "",
        tax_number: str = "",
        currency: str = DEFAULT_CURRENCY,
        receipt_footer: str = "",
        logo_path: str = "",
        login_background_path: str = "",
        login_logo_path: str = "",
        login_title: str = "",
        login_subtitle: str = "",
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
    ) -> None:
        """Initialize a StoreSettings instance.

        Args:
            id: Unique identifier (always 1 for the single row).
            store_name: Business name shown on invoices and receipts.
            owner_name: Business owner name.
            phone: Business phone number.
            email: Business contact email.
            address: Business street address.
            website: Business website URL.
            tax_number: Tax registration number.
            currency: Currency code used across the application.
            receipt_footer: Footer text printed on receipts.
            logo_path: Filename of the uploaded store logo.
            login_background_path: Filename of the login page background image.
            login_logo_path: Filename of the login page logo image.
            login_title: Welcome title shown on the login page.
            login_subtitle: Welcome subtitle shown on the login page.
            created_at: Row creation timestamp.
            updated_at: Row last-updated timestamp.
        """
        self.id = id
        self.store_name = store_name
        self.owner_name = owner_name
        self.phone = phone
        self.email = email
        self.address = address
        self.website = website
        self.tax_number = tax_number
        self.currency = currency or self.DEFAULT_CURRENCY
        self.receipt_footer = receipt_footer
        self.logo_path = logo_path
        self.login_background_path = login_background_path
        self.login_logo_path = login_logo_path
        self.login_title = login_title
        self.login_subtitle = login_subtitle
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(
        self,
        logo_url: Optional[str] = None,
        login_background_url: Optional[str] = None,
        login_logo_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Convert StoreSettings instance to a dictionary.

        Args:
            logo_url: Optional public URL of the store logo.
            login_background_url: Optional public URL of the login background.
            login_logo_url: Optional public URL of the login logo.

        Returns:
            Dictionary representation of the settings.
        """
        result: Dict[str, Any] = {
            "id": self.id,
            "store_name": self.store_name,
            "owner_name": self.owner_name,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "website": self.website,
            "tax_number": self.tax_number,
            "currency": self.currency,
            "receipt_footer": self.receipt_footer,
            "logo_path": self.logo_path or None,
            "login_background_path": self.login_background_path or None,
            "login_logo_path": self.login_logo_path or None,
            "login_title": self.login_title,
            "login_subtitle": self.login_subtitle,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        if logo_url is not None:
            result["logo_url"] = logo_url
        if login_background_url is not None:
            result["login_background_url"] = login_background_url
        if login_logo_url is not None:
            result["login_logo_url"] = login_logo_url
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StoreSettings":
        """Build a StoreSettings instance from a dictionary.

        Args:
            data: Dictionary with store settings fields.

        Returns:
            StoreSettings instance populated from the data.
        """
        return cls(
            id=data.get("id"),
            store_name=data.get("store_name", ""),
            owner_name=data.get("owner_name", ""),
            phone=data.get("phone", ""),
            email=data.get("email", ""),
            address=data.get("address", ""),
            website=data.get("website", ""),
            tax_number=data.get("tax_number", ""),
            currency=data.get("currency", cls.DEFAULT_CURRENCY),
            receipt_footer=data.get("receipt_footer", ""),
            logo_path=data.get("logo_path", ""),
            login_background_path=data.get("login_background_path", ""),
            login_logo_path=data.get("login_logo_path", ""),
            login_title=data.get("login_title", ""),
            login_subtitle=data.get("login_subtitle", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    def __repr__(self) -> str:
        """Return a developer-friendly string representation.

        Returns:
            String describing the settings row.
        """
        return (
            f"StoreSettings(id={self.id!r}, store_name={self.store_name!r}, "
            f"currency={self.currency!r})"
        )
