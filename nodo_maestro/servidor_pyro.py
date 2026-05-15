import Pyro4
from gestor_datos import GestorDatos

NOMBRE_SERVICIO = "seguridad.nodo_maestro"


@Pyro4.expose
class NodoMaestro:
    def __init__(self):
        self._gestor = GestorDatos()

    def filtrar_por_anios(self, anio_inicio: int, anio_fin: int) -> str:
        return self._gestor.filtrar_por_anios(anio_inicio, anio_fin)

    def conteo_por_categoria(self) -> dict:
        return self._gestor.conteo_por_categoria()

    def anios_disponibles(self) -> list:
        return self._gestor.anios_disponibles()


def main():
    daemon = Pyro4.Daemon()
    ns = Pyro4.locateNS()
    uri = daemon.register(NodoMaestro)
    ns.register(NOMBRE_SERVICIO, uri)
    print(f"[NodoMaestro] Registrado como '{NOMBRE_SERVICIO}' → {uri}")
    print("[NodoMaestro] Esperando llamadas remotas...")
    daemon.requestLoop()


if __name__ == "__main__":
    main()
