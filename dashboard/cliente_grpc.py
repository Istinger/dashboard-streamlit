import sys
import os

# Los stubs pb2 viven en nodo_analitica/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "nodo_analitica"))

import grpc
import analitica_pb2
import analitica_pb2_grpc

# IP de la máquina donde corre el servidor gRPC (Nodo Analítica)
# Puede ser localhost o la IP de otra máquina en la red, ej: 192.168.1.20
HOST   = os.environ.get("GRPC_HOST", "localhost")
PUERTO = int(os.environ.get("GRPC_PORT", "50051"))


def _canal():
    return grpc.insecure_channel(f"{HOST}:{PUERTO}")


def get_distribucion_por_provincia(anio_inicio: int, anio_fin: int) -> list[dict]:
    with _canal() as canal:
        stub = analitica_pb2_grpc.AnaliticaServiceStub(canal)
        req  = analitica_pb2.FiltroRequest(anio_inicio=anio_inicio, anio_fin=anio_fin)
        resp = stub.GetDistribucionPorProvincia(req)
    return [{"nombre": i.nombre, "frecuencia": i.frecuencia} for i in resp.items]


def get_frecuencia_por_arma(anio_inicio: int, anio_fin: int) -> list[dict]:
    with _canal() as canal:
        stub = analitica_pb2_grpc.AnaliticaServiceStub(canal)
        req  = analitica_pb2.FiltroRequest(anio_inicio=anio_inicio, anio_fin=anio_fin)
        resp = stub.GetFrecuenciaPorArma(req)
    return [{"nombre": i.nombre, "frecuencia": i.frecuencia} for i in resp.items]


def get_anios_disponibles() -> list[int]:
    with _canal() as canal:
        stub = analitica_pb2_grpc.AnaliticaServiceStub(canal)
        req  = analitica_pb2.FiltroRequest(anio_inicio=0, anio_fin=0)
        resp = stub.GetAniosDisponibles(req)
    return list(resp.anios)


def get_conteo_por_categoria() -> dict:
    with _canal() as canal:
        stub = analitica_pb2_grpc.AnaliticaServiceStub(canal)
        req  = analitica_pb2.FiltroRequest(anio_inicio=0, anio_fin=0)
        resp = stub.GetConteoPorCategoria(req)
    return {item.categoria: item.total for item in resp.items}
