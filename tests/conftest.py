import socket
import pytest
import Pyro4

PYRO_NS_HOST = "localhost"
PYRO_NS_PORT = 9090
GRPC_HOST    = "localhost"
GRPC_PORT    = 50051


def _tcp_abierto(host: str, puerto: int, timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection((host, puerto), timeout=timeout):
            return True
    except OSError:
        return False


def _nodo_maestro_registrado() -> bool:
    try:
        with Pyro4.Proxy("PYRONAME:seguridad.nodo_maestro") as proxy:
            proxy._pyroBind()
        return True
    except Exception:
        return False


requiere_maestro = pytest.mark.skipif(
    not _nodo_maestro_registrado(),
    reason="NodoMaestro no está disponible (levanta el Name Server y servidor_pyro.py)",
)

requiere_analitica = pytest.mark.skipif(
    not _tcp_abierto(GRPC_HOST, GRPC_PORT),
    reason="NodoAnalitica no está disponible (levanta servidor_grpc.py)",
)

requiere_sistema_completo = pytest.mark.skipif(
    not (_nodo_maestro_registrado() and _tcp_abierto(GRPC_HOST, GRPC_PORT)),
    reason="Sistema incompleto: se necesitan NodoMaestro y NodoAnalitica activos",
)
