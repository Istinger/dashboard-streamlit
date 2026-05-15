import socket
import Pyro4

PYRO_HOST  = "localhost"
PYRO_PORT  = 9090
GRPC_HOST  = "localhost"
GRPC_PORT  = 50051


def _tcp_abierto(host: str, puerto: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, puerto), timeout=timeout):
            return True
    except OSError:
        return False


def estado_nodo_maestro() -> bool:
    """Verifica que el nodo maestro responda llamadas remotas (no solo que esté registrado)."""
    try:
        with Pyro4.Proxy("PYRONAME:seguridad.nodo_maestro") as proxy:
            proxy._pyroBind()
        return True
    except Exception:
        return False


def estado_nodo_analitica() -> bool:
    """Verifica que el servidor gRPC esté escuchando."""
    return _tcp_abierto(GRPC_HOST, GRPC_PORT)
