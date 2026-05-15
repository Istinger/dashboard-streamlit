import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "nodo_analitica"))

import grpc
import analitica_pb2
import analitica_pb2_grpc
from conftest import requiere_analitica, requiere_sistema_completo

HOST   = "localhost"
PUERTO = 50051


@pytest.fixture(scope="module")
def stub():
    canal = grpc.insecure_channel(f"{HOST}:{PUERTO}")
    return analitica_pb2_grpc.AnaliticaServiceStub(canal)


def _filtro(anio_inicio=2014, anio_fin=2025):
    return analitica_pb2.FiltroRequest(anio_inicio=anio_inicio, anio_fin=anio_fin)


# ------------------------------------------------------------------
# Conexión
# ------------------------------------------------------------------
class TestConexion:
    @requiere_analitica
    def test_canal_grpc_accesible(self):
        canal = grpc.insecure_channel(f"{HOST}:{PUERTO}")
        estado = grpc.channel_ready_future(canal).result(timeout=3)
        assert estado is None  # no lanza excepción → canal listo


# ------------------------------------------------------------------
# GetDistribucionPorProvincia
# ------------------------------------------------------------------
class TestDistribucionPorProvincia:
    @requiere_sistema_completo
    def test_retorna_items(self, stub):
        resp = stub.GetDistribucionPorProvincia(_filtro())
        assert len(resp.items) > 0

    @requiere_sistema_completo
    def test_items_tienen_nombre_y_frecuencia(self, stub):
        resp = stub.GetDistribucionPorProvincia(_filtro())
        for item in resp.items:
            assert item.nombre != ""
            assert item.frecuencia > 0

    @requiere_sistema_completo
    def test_ordenado_por_frecuencia_descendente(self, stub):
        resp = stub.GetDistribucionPorProvincia(_filtro())
        frecuencias = [i.frecuencia for i in resp.items]
        assert frecuencias == sorted(frecuencias, reverse=True)

    @requiere_sistema_completo
    def test_rango_sin_datos_retorna_lista_vacia(self, stub):
        resp = stub.GetDistribucionPorProvincia(_filtro(1800, 1801))
        assert list(resp.items) == []


# ------------------------------------------------------------------
# GetFrecuenciaPorArma
# ------------------------------------------------------------------
class TestFrecuenciaPorArma:
    @requiere_sistema_completo
    def test_retorna_items(self, stub):
        resp = stub.GetFrecuenciaPorArma(_filtro())
        assert len(resp.items) > 0

    @requiere_sistema_completo
    def test_items_tienen_nombre_y_frecuencia(self, stub):
        resp = stub.GetFrecuenciaPorArma(_filtro())
        for item in resp.items:
            assert item.nombre != ""
            assert item.frecuencia > 0

    @requiere_sistema_completo
    def test_ordenado_por_frecuencia_descendente(self, stub):
        resp = stub.GetFrecuenciaPorArma(_filtro())
        frecuencias = [i.frecuencia for i in resp.items]
        assert frecuencias == sorted(frecuencias, reverse=True)


# ------------------------------------------------------------------
# GetAniosDisponibles
# ------------------------------------------------------------------
class TestAniosDisponibles:
    @requiere_sistema_completo
    def test_retorna_anios(self, stub):
        resp = stub.GetAniosDisponibles(_filtro())
        assert len(resp.anios) > 0

    @requiere_sistema_completo
    def test_anios_son_positivos(self, stub):
        resp = stub.GetAniosDisponibles(_filtro())
        for a in resp.anios:
            assert a > 1900
