# La inicialización del cliente HTTP se realiza en server.py (lifespan).
# Las dependencias inyectables se encuentran en core/dependencies.py.
#
# Este módulo se mantiene por compatibilidad de importaciones existentes.
from core.dependencies import get_http_client

__all__ = ["get_http_client"]
