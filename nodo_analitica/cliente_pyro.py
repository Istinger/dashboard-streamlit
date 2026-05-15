import os
import json
import Pyro4

NOMBRE_SERVICIO = "seguridad.nodo_maestro"
# IP de la máquina donde corre el Name Server de Pyro4
# Puede ser localhost o la IP de otra máquina en la red, ej: 192.168.1.10
NS_HOST = os.environ.get("PYRO_NS_HOST", "localhost")


def obtener_proxy() -> Pyro4.Proxy:
    ns = Pyro4.locateNS(host=NS_HOST)
    uri = ns.lookup(NOMBRE_SERVICIO)
    return Pyro4.Proxy(uri)


def filtrar_por_anios(anio_inicio: int, anio_fin: int) -> list[dict]:
    with obtener_proxy() as nodo:
        datos_json = nodo.filtrar_por_anios(anio_inicio, anio_fin)
    return json.loads(datos_json)


def anios_disponibles() -> list[int]:
    with obtener_proxy() as nodo:
        return nodo.anios_disponibles()


def conteo_por_categoria() -> dict:
    with obtener_proxy() as nodo:
        return nodo.conteo_por_categoria()
