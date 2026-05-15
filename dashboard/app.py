import pandas as pd
import streamlit as st
import cliente_grpc
from componentes import graficos, monitor_red

st.set_page_config(
    page_title="Seguridad Nacional — Dashboard",
    page_icon="🔍",
    layout="wide",
)

ANIOS_DEFECTO = (2014, 2025)
VARIABLES     = ["Provincia", "Tipo de arma"]

# ------------------------------------------------------------------
# Pre-carga eagerly al iniciar la sesión (mientras servicios están activos)
# ------------------------------------------------------------------
def _precarga_cache():
    """Carga todas las combinaciones posibles al inicio de sesión."""
    if st.session_state.get("cache_precargado"):
        return
    try:
        anios = cliente_grpc.get_anios_disponibles()
        st.session_state.anios = anios
        anio_min, anio_max = min(anios), max(anios)

        for variable in VARIABLES:
            clave = f"datos_{variable}_{anio_min}_{anio_max}"
            if clave not in st.session_state:
                if variable == "Provincia":
                    st.session_state[clave] = cliente_grpc.get_distribucion_por_provincia(anio_min, anio_max)
                else:
                    st.session_state[clave] = cliente_grpc.get_frecuencia_por_arma(anio_min, anio_max)

        if "conteo_categorias" not in st.session_state:
            st.session_state.conteo_categorias = cliente_grpc.get_conteo_por_categoria()

        st.session_state.cache_precargado = True
    except Exception:
        pass  # Si los servicios no están listos aún, se intentará en cada request


_precarga_cache()

# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def _indicador(activo: bool, nombre: str) -> str:
    icono = "🟢" if activo else "🔴"
    estado = "En línea" if activo else "Sin conexión"
    return f"{icono} **{nombre}**: {estado}"


def _intentar_cargar_anios() -> list[int]:
    if "anios" in st.session_state:
        return st.session_state.anios
    try:
        anios = cliente_grpc.get_anios_disponibles()
        st.session_state.anios = anios
        return anios
    except Exception:
        return []


def _intentar_obtener_datos(variable: str, anio_inicio: int, anio_fin: int):
    cache_key = f"datos_{variable}_{anio_inicio}_{anio_fin}"
    desde_cache = False

    try:
        if variable == "Provincia":
            datos = cliente_grpc.get_distribucion_por_provincia(anio_inicio, anio_fin)
        else:
            datos = cliente_grpc.get_frecuencia_por_arma(anio_inicio, anio_fin)
        st.session_state[cache_key] = datos
    except Exception:
        datos = st.session_state.get(cache_key)
        if datos is None:
            datos = []
        else:
            desde_cache = True

    if variable == "Provincia":
        titulo   = f"Distribución por provincia ({anio_inicio}–{anio_fin})"
        etiqueta = "Provincia"
    else:
        titulo   = f"Frecuencia por tipo de arma ({anio_inicio}–{anio_fin})"
        etiqueta = "Tipo de arma"
    return datos, etiqueta, titulo, desde_cache


# ------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------
with st.sidebar:
    st.title("Estado de servicios")
    maestro_ok   = monitor_red.estado_nodo_maestro()
    analitica_ok = monitor_red.estado_nodo_analitica()
    st.markdown(_indicador(maestro_ok,   "Nodo Maestro (Pyro4)"))
    st.markdown(_indicador(analitica_ok, "Nodo Analítica (gRPC)"))

    if not maestro_ok:
        st.warning("Nodo Maestro caído.")
    if not analitica_ok:
        st.warning("Nodo Analítica caído.")

    st.divider()

    anios = _intentar_cargar_anios()
    anio_min, anio_max = (min(anios), max(anios)) if anios else ANIOS_DEFECTO

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
    variable = st.radio("Variable de análisis", options=VARIABLES)
    tipo_grafico = st.radio("Tipo de gráfico", options=["Barras", "Pastel"])

# ------------------------------------------------------------------
# Contenido principal
# ------------------------------------------------------------------
st.title("Homicidios — Análisis exploratorio")
anio_inicio, anio_fin = rango

# KPIs — conteo por categoría
try:
    if "conteo_categorias" not in st.session_state:
        st.session_state.conteo_categorias = cliente_grpc.get_conteo_por_categoria()
    conteo = st.session_state.conteo_categorias
except Exception:
    conteo = st.session_state.get("conteo_categorias", {})

if conteo:
    iconos = {"Homicidio": "🔫", "Asesinato": "⚔️", "Sicariato": "🎯", "Femicidio": "🚨"}
    cols = st.columns(len(conteo))
    for col, (cat, total) in zip(cols, conteo.items()):
        col.metric(label=f"{iconos.get(cat, '')} {cat}", value=f"{total:,}")
    st.divider()

# Gráfico principal
datos, etiqueta, titulo, desde_cache = _intentar_obtener_datos(variable, anio_inicio, anio_fin)
servicios_caidos = not maestro_ok or not analitica_ok

if servicios_caidos and desde_cache:
    st.warning("⚠️ Uno o más nodos no disponibles. Mostrando últimos datos en caché.")
elif servicios_caidos and not datos:
    st.error("⚠️ Servicios caídos sin datos en caché. Levanta los nodos y recarga la página.")

if not datos:
    st.info("Sin datos para mostrar. Verifica que los nodos estén activos.")
else:
    if desde_cache:
        st.caption("📦 Datos en caché — se actualizarán cuando los servicios vuelvan en línea.")
    fig = graficos.grafico_barras(datos, titulo, etiqueta) if tipo_grafico == "Barras" \
          else graficos.grafico_pastel(datos, titulo)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Ver tabla de datos"):
        st.dataframe(
            pd.DataFrame(datos).rename(columns={"nombre": etiqueta, "frecuencia": "Casos"})
        )
