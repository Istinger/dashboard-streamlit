import os
import json
import pandas as pd

RUTA_XLSX = os.path.join(os.path.dirname(__file__), "datos", "mdi_homicidiosintencionales_pm_2014_2025.xlsx")
RUTA_CSV  = os.path.join(os.path.dirname(__file__), "datos", "homicidios.csv")

HOJA_XLSX       = "1. Homicidios Intencionales"
COLUMNA_TIPO    = "tipo_muerte"
COLUMNA_PROV    = "provincia"
COLUMNA_ARMA    = "tipo_arma"
COLUMNA_FECHA   = "fecha_infraccion"

# Los valores en el xlsx vienen en MAYÚSCULAS
CATEGORIAS = {"HOMICIDIO", "ASESINATO", "SICARIATO", "FEMICIDIO"}
CATEGORIAS_LABEL = {k: k.capitalize() for k in CATEGORIAS}


class GestorDatos:
    def __init__(self):
        self._df = self._cargar()

    # ------------------------------------------------------------------
    # Inicialización
    # ------------------------------------------------------------------
    def _cargar(self) -> pd.DataFrame:
        if not os.path.exists(RUTA_CSV):
            self._convertir_xlsx_a_csv()
        df = pd.read_csv(RUTA_CSV, sep=";", encoding="utf-8")
        df.columns = df.columns.str.strip()
        df[COLUMNA_FECHA] = pd.to_datetime(df[COLUMNA_FECHA], dayfirst=True, errors="coerce")
        df["anio"] = df[COLUMNA_FECHA].dt.year
        return df

    def _convertir_xlsx_a_csv(self) -> None:
        df = pd.read_excel(RUTA_XLSX, sheet_name=HOJA_XLSX, parse_dates=False)
        df.columns = df.columns.str.strip()
        os.makedirs(os.path.dirname(RUTA_CSV), exist_ok=True)
        df.to_csv(RUTA_CSV, sep=";", index=False, encoding="utf-8")

    # ------------------------------------------------------------------
    # Métodos remotos expuestos via Pyro4
    # ------------------------------------------------------------------
    def filtrar_por_anios(self, anio_inicio: int, anio_fin: int) -> str:
        mascara = (self._df["anio"] >= anio_inicio) & (self._df["anio"] <= anio_fin)
        resultado = self._df[mascara].copy()
        resultado[COLUMNA_FECHA] = resultado[COLUMNA_FECHA].dt.strftime("%Y-%m-%d")
        return resultado.to_json(orient="records", force_ascii=False)

    def conteo_por_categoria(self) -> dict:
        conteos = (
            self._df[COLUMNA_TIPO]
            .str.strip()
            .str.upper()
            .value_counts()
            .to_dict()
        )
        return {
            CATEGORIAS_LABEL[cat]: int(conteos.get(cat, 0))
            for cat in CATEGORIAS
        }

    def anios_disponibles(self) -> list:
        return sorted(self._df["anio"].dropna().unique().astype(int).tolist())
