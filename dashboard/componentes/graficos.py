import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def _a_dataframe(items: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(items, columns=["nombre", "frecuencia"])


def grafico_barras(items: list[dict], titulo: str, etiqueta_x: str) -> go.Figure:
    df = _a_dataframe(items)
    fig = px.bar(
        df,
        x="nombre",
        y="frecuencia",
        title=titulo,
        labels={"nombre": etiqueta_x, "frecuencia": "Casos"},
        color="frecuencia",
        color_continuous_scale="Reds",
    )
    fig.update_layout(xaxis_tickangle=-45, showlegend=False)
    return fig


def grafico_pastel(items: list[dict], titulo: str) -> go.Figure:
    df = _a_dataframe(items)
    fig = px.pie(
        df,
        names="nombre",
        values="frecuencia",
        title=titulo,
        hole=0.3,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return fig
