import sys
import json
from collections import Counter
from concurrent import futures

import grpc
import analitica_pb2
import analitica_pb2_grpc
import cliente_pyro

COLUMNA_PROVINCIA = "provincia"
COLUMNA_ARMA      = "tipo_arma"
PUERTO            = 50051


class AnaliticaServicer(analitica_pb2_grpc.AnaliticaServiceServicer):

    def _conteo_a_items(self, registros: list[dict], columna: str) -> list:
        conteo = Counter(
            str(r.get(columna, "Desconocido")).strip().title()
            for r in registros
            if r.get(columna)
        )
        return [
            analitica_pb2.ItemFrecuencia(nombre=nombre, frecuencia=freq)
            for nombre, freq in sorted(conteo.items(), key=lambda x: -x[1])
        ]

    def GetDistribucionPorProvincia(self, request, context):
        try:
            registros = cliente_pyro.filtrar_por_anios(request.anio_inicio, request.anio_fin)
            items = self._conteo_a_items(registros, COLUMNA_PROVINCIA)
            return analitica_pb2.DistribucionResponse(items=items)
        except Exception as exc:
            context.set_details(str(exc))
            context.set_code(grpc.StatusCode.INTERNAL)
            return analitica_pb2.DistribucionResponse()

    def GetFrecuenciaPorArma(self, request, context):
        try:
            registros = cliente_pyro.filtrar_por_anios(request.anio_inicio, request.anio_fin)
            items = self._conteo_a_items(registros, COLUMNA_ARMA)
            return analitica_pb2.DistribucionResponse(items=items)
        except Exception as exc:
            context.set_details(str(exc))
            context.set_code(grpc.StatusCode.INTERNAL)
            return analitica_pb2.DistribucionResponse()

    def GetAniosDisponibles(self, request, context):
        try:
            anios = cliente_pyro.anios_disponibles()
            return analitica_pb2.AniosResponse(anios=anios)
        except Exception as exc:
            context.set_details(str(exc))
            context.set_code(grpc.StatusCode.INTERNAL)
            return analitica_pb2.AniosResponse()

    def GetConteoPorCategoria(self, request, context):
        try:
            conteo = cliente_pyro.conteo_por_categoria()
            items = [
                analitica_pb2.CategoriaItem(categoria=cat, total=total)
                for cat, total in sorted(conteo.items(), key=lambda x: -x[1])
            ]
            return analitica_pb2.ConteoCategoriasResponse(items=items)
        except Exception as exc:
            context.set_details(str(exc))
            context.set_code(grpc.StatusCode.INTERNAL)
            return analitica_pb2.ConteoCategoriasResponse()


def main():
    servidor = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    analitica_pb2_grpc.add_AnaliticaServiceServicer_to_server(AnaliticaServicer(), servidor)
    servidor.add_insecure_port(f"[::]:{PUERTO}")
    servidor.start()
    print(f"[NodoAnalitica] Servidor gRPC escuchando en puerto {PUERTO}")
    servidor.wait_for_termination()


if __name__ == "__main__":
    main()
