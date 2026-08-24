"""Client services module for client-service assignment operations."""

from backend.modules.client_services.model import ClientService
from backend.modules.client_services.repository import ClientServiceRepository
from backend.modules.client_services.service import ClientServiceAssignmentService

__all__ = ["ClientService", "ClientServiceRepository", "ClientServiceAssignmentService"]
