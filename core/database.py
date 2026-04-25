# La inicialización del cliente MongoDB se realiza en server.py (lifespan).
# Las dependencias inyectables se encuentran en core/dependencies.py.
#
# Este módulo se mantiene por compatibilidad de importaciones existentes.
from core.dependencies import get_db

__all__ = ["get_db"]
