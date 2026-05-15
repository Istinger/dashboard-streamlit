import sys
import os

# Los stubs pb2 viven en nodo_analitica/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "nodo_analitica"))

import grpc
import analitica_pb2
import analitica_pb2_grpc

HOST  = "localhost"
PUERTO = 50051


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
