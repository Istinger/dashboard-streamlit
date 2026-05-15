import sys
import os
from unittest.mock import patch, MagicMock
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dashboard"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "nodo_analitica"))

import cliente_grpc
from componentes import monitor_red
from conftest import requiere_analitica, requiere_sistema_completo

# ------------------------------------------------------------------
# cliente_grpc — integración real
# ------------------------------------------------------------------
class TestClienteGrpcIntegracion:
    @requiere_sistema_completo
    def test_get_distribucion_por_provincia_retorna_lista(self):
        datos = cliente_grpc.get_distribucion_por_provincia(2014, 2025)
        assert isinstance(datos, list)
        assert len(datos) > 0

    @requiere_sistema_completo
    def test_items_tienen_claves_correctas(self):
        datos = cliente_grpc.get_distribucion_por_provincia(2014, 2025)
        for item in datos:
            assert "nombre" in item
            assert "frecuencia" in item

    @requiere_sistema_completo
    def test_get_frecuencia_por_arma_retorna_lista(self):
        datos = cliente_grpc.get_frecuencia_por_arma(2014, 2025)
        assert isinstance(datos, list)
        assert len(datos) > 0

    @requiere_sistema_completo
    def test_get_anios_disponibles_retorna_lista_de_enteros(self):
        anios = cliente_grpc.get_anios_disponibles()
        assert isinstance(anios, list)
        assert all(isinstance(a, int) for a in anios)


# ------------------------------------------------------------------
# monitor_red — detección de caídas (sin servicios reales)
# ------------------------------------------------------------------
class TestMonitorRedCaidas:
    def test_maestro_inaccesible_retorna_false(self):
        proxy_mock = MagicMock()
        proxy_mock.__enter__ = MagicMock(return_value=proxy_mock)
        proxy_mock.__exit__ = MagicMock(return_value=False)
        proxy_mock._pyroBind.side_effect = Exception("sin conexión")
        with patch("componentes.monitor_red.Pyro4.Proxy", return_value=proxy_mock):
            assert monitor_red.estado_nodo_maestro() is False

    def test_maestro_accesible_retorna_true(self):
        proxy_mock = MagicMock()
        proxy_mock.__enter__ = MagicMock(return_value=proxy_mock)
        proxy_mock.__exit__ = MagicMock(return_value=False)
        proxy_mock._pyroBind.return_value = None
        with patch("componentes.monitor_red.Pyro4.Proxy", return_value=proxy_mock):
            assert monitor_red.estado_nodo_maestro() is True

    def test_analitica_puerto_cerrado_retorna_false(self):
        with patch("componentes.monitor_red._tcp_abierto", return_value=False):
            assert monitor_red.estado_nodo_analitica() is False

    def test_analitica_puerto_abierto_retorna_true(self):
        with patch("componentes.monitor_red._tcp_abierto", return_value=True):
            assert monitor_red.estado_nodo_analitica() is True
