import json
import Pyro4

NOMBRE_SERVICIO = "seguridad.nodo_maestro"


def obtener_proxy() -> Pyro4.Proxy:
    return Pyro4.Proxy(f"PYRONAME:{NOMBRE_SERVICIO}")


def filtrar_por_anios(anio_inicio: int, anio_fin: int) -> list[dict]:
    with obtener_proxy() as nodo:
        datos_json = nodo.filtrar_por_anios(anio_inicio, anio_fin)
    return json.loads(datos_json)


def anios_disponibles() -> list[int]:
    with obtener_proxy() as nodo:
        return nodo.anios_disponibles()
