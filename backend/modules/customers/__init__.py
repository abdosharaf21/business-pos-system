"""Customers module for customer management."""

from backend.modules.customers.model import Customer
from backend.modules.customers.repository import CustomerRepository
from backend.modules.customers.service import CustomerService

__all__ = ["Customer", "CustomerRepository", "CustomerService"]
