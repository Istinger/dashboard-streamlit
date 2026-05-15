import json
import pytest
import Pyro4
from conftest import requiere_maestro

NOMBRE_SERVICIO = "seguridad.nodo_maestro"
CATEGORIAS_ESPERADAS = {"Homicidio", "Asesinato", "Sicariato", "Femicidio"}


@pytest.fixture(scope="module")
def nodo():
    return Pyro4.Proxy(f"PYRONAME:{NOMBRE_SERVICIO}")


# ------------------------------------------------------------------
# Conexión
# ------------------------------------------------------------------
class TestConexion:
    @requiere_maestro
    def test_name_server_accesible(self):
        ns = Pyro4.locateNS()
        assert ns is not None

    @requiere_maestro
    def test_servicio_registrado_en_ns(self):
        ns = Pyro4.locateNS()
        assert NOMBRE_SERVICIO in ns.list()


# ------------------------------------------------------------------
# filtrar_por_anios
# ------------------------------------------------------------------
class TestFiltrarPorAnios:
    @requiere_maestro
    def test_retorna_json_valido(self, nodo):
        resultado = nodo.filtrar_por_anios(2014, 2025)
        datos = json.loads(resultado)
        assert isinstance(datos, list)

    @requiere_maestro
    def test_registros_dentro_del_rango(self, nodo):
        anio_inicio, anio_fin = 2018, 2020
        datos = json.loads(nodo.filtrar_por_anios(anio_inicio, anio_fin))
        for registro in datos:
            fecha = registro.get("fecha_infraccion", "")
            if fecha:
                anio = int(fecha[:4])
                assert anio_inicio <= anio <= anio_fin

    @requiere_maestro
    def test_rango_sin_datos_retorna_lista_vacia(self, nodo):
        datos = json.loads(nodo.filtrar_por_anios(1800, 1801))
        assert datos == []


# ------------------------------------------------------------------
# conteo_por_categoria
# ------------------------------------------------------------------
class TestConteoPorCategoria:
    @requiere_maestro
    def test_retorna_dict(self, nodo):
        resultado = nodo.conteo_por_categoria()
        assert isinstance(resultado, dict)

    @requiere_maestro
    def test_contiene_todas_las_categorias(self, nodo):
        resultado = nodo.conteo_por_categoria()
        assert CATEGORIAS_ESPERADAS == set(resultado.keys())

    @requiere_maestro
    def test_valores_son_enteros_no_negativos(self, nodo):
        resultado = nodo.conteo_por_categoria()
        for categoria, total in resultado.items():
            assert isinstance(total, int), f"{categoria} no es int"
            assert total >= 0, f"{categoria} tiene valor negativo"


# ------------------------------------------------------------------
# anios_disponibles
# ------------------------------------------------------------------
class TestAniosDisponibles:
    @requiere_maestro
    def test_retorna_lista_no_vacia(self, nodo):
        anios = nodo.anios_disponibles()
        assert isinstance(anios, list)
        assert len(anios) > 0

    @requiere_maestro
    def test_anios_son_enteros_positivos(self, nodo):
        anios = nodo.anios_disponibles()
        for a in anios:
            assert isinstance(a, int)
            assert 2014 <= a <= 2025
