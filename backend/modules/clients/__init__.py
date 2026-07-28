"""Clients module for client management operations."""

from backend.modules.clients.model import Client
from backend.modules.clients.repository import ClientRepository
from backend.modules.clients.service import ClientService

__all__ = ["Client", "ClientRepository", "ClientService"]
