import os
import socket
import Pyro4

PYRO_HOST  = os.environ.get("PYRO_NS_HOST", "localhost")
PYRO_PORT  = int(os.environ.get("PYRO_NS_PORT", "9090"))
GRPC_HOST  = os.environ.get("GRPC_HOST", "localhost")
GRPC_PORT  = int(os.environ.get("GRPC_PORT", "50051"))


def _tcp_abierto(host: str, puerto: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, puerto), timeout=timeout):
            return True
    except OSError:
        return False


def estado_nodo_maestro() -> bool:
    """Verifica que el nodo maestro responda llamadas remotas (no solo que esté registrado)."""
    try:
        ns = Pyro4.locateNS(host=PYRO_HOST, port=PYRO_PORT)
        uri = ns.lookup("seguridad.nodo_maestro")
        with Pyro4.Proxy(uri) as proxy:
            proxy._pyroBind()
        return True
    except Exception:
        return False


def estado_nodo_analitica() -> bool:
    """Verifica que el servidor gRPC esté escuchando."""
    return _tcp_abierto(GRPC_HOST, GRPC_PORT)
