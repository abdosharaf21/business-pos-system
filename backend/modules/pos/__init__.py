"""POS module for cashier interface."""
from backend.modules.pos.model import PosProduct
from backend.modules.pos.repository import PosRepository
from backend.modules.pos.service import PosService

__all__ = ["PosProduct", "PosRepository", "PosService"]
