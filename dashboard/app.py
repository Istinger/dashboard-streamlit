import streamlit as st
import cliente_grpc
from componentes import graficos, monitor_red

st.set_page_config(
    page_title="Seguridad Nacional — Dashboard",
    page_icon="🔍",
    layout="wide",
)

# ------------------------------------------------------------------
# Estado de la red
# ------------------------------------------------------------------
def _indicador(activo: bool, nombre: str) -> str:
    icono = "🟢" if activo else "🔴"
    estado = "En línea" if activo else "Sin conexión"
    return f"{icono} **{nombre}**: {estado}"


with st.sidebar:
    st.title("Estado de servicios")
    maestro_ok   = monitor_red.estado_nodo_maestro()
    analitica_ok = monitor_red.estado_nodo_analitica()
    st.markdown(_indicador(maestro_ok,   "Nodo Maestro (Pyro4)"))
    st.markdown(_indicador(analitica_ok, "Nodo Analítica (gRPC)"))
    st.divider()

    if not analitica_ok:
        st.error("El Nodo Analítica no está disponible. Verifica que el servidor gRPC esté corriendo.")
        st.stop()

    # Carga de años disponibles (una vez por sesión)
    if "anios" not in st.session_state:
        try:
            st.session_state.anios = cliente_grpc.get_anios_disponibles()
        except Exception as exc:
            st.error(f"Error al obtener años: {exc}")
            st.stop()

    anios = st.session_state.anios
    anio_min, anio_max = min(anios), max(anios)

    st.subheader("Filtros")
    if anio_min == anio_max:
        st.info(f"Año disponible: {anio_min}")
        rango = (anio_min, anio_max)
    else:
        rango = st.slider(
            "Rango de años",
            min_value=anio_min,
            max_value=anio_max,
            value=(anio_min, anio_max),
        )
    variable = st.radio(
        "Variable de análisis",
        options=["Provincia", "Tipo de arma"],
    )
    tipo_grafico = st.radio(
        "Tipo de gráfico",
        options=["Barras", "Pastel"],
    )

# ------------------------------------------------------------------
# Contenido principal
# ------------------------------------------------------------------
st.title("Homicidios — Análisis exploratorio")
anio_inicio, anio_fin = rango

try:
    if variable == "Provincia":
        datos = cliente_grpc.get_distribucion_por_provincia(anio_inicio, anio_fin)
        titulo    = f"Distribución por provincia ({anio_inicio}–{anio_fin})"
        etiqueta  = "Provincia"
    else:
        datos = cliente_grpc.get_frecuencia_por_arma(anio_inicio, anio_fin)
        titulo    = f"Frecuencia por tipo de arma ({anio_inicio}–{anio_fin})"
        etiqueta  = "Tipo de arma"

    if not datos:
        st.warning("No hay datos para el rango seleccionado.")
        st.stop()

    if tipo_grafico == "Barras":
        fig = graficos.grafico_barras(datos, titulo, etiqueta)
    else:
        fig = graficos.grafico_pastel(datos, titulo)

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Ver tabla de datos"):
        import pandas as pd
        st.dataframe(pd.DataFrame(datos).rename(columns={"nombre": etiqueta, "frecuencia": "Casos"}))

except Exception as exc:
    st.error(f"Error al obtener datos del servidor: {exc}")
