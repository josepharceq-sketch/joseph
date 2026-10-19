# =============================================================
# app.py — Interfaz principal Streamlit (UI y navegacion).
# Importa calculos desde data_utils.py y graficos desde charts.py.
# =============================================================

import io
import hashlib
import datetime

import streamlit as st
import numpy as np
import streamlit.components.v1 as components

from data_utils import (
    VALORES_PREDETERMINADOS,
    ALIAS_PARAMETROS,
    leer_archivo_parametros,
    parsear_entradas,
    validar_entradas,
    calcular_parametros_espectrales,
    calcular_factores_participacion,
    calcular_respuestas_modales,
    calcular_combinacion_modal,
    generar_dataframe_resultados,
    estilar_dataframe,
    generar_excel_bytes,
)
from charts import (
    graficar_modelo_estructural,
    graficar_perfiles_modales,
    graficar_combinaciones_modales,
    generar_animacion_modos,
)

# =============================================================
# CONFIGURACION DE PAGINA
# =============================================================
st.set_page_config(
    page_title="Analisis Sismico Modal Espectral (E.030) - 2018",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================
# SESSION STATE: historial
# =============================================================
if "historial_calculos" not in st.session_state:
    st.session_state.historial_calculos = []

# =============================================================
# SELECTOR DE TEMA
# =============================================================
with st.sidebar.container(border=True):
    modo_tema = st.segmented_control(
        label="Modo de Interfaz",
        options=["🌙 Oscuro", "☀️ Claro"],
        default="☀️ Claro",
        selection_mode="single",
        label_visibility="collapsed",
    )

if not modo_tema:
    modo_tema = "☀️ Claro"
es_oscuro = modo_tema.startswith("🌙")

# =============================================================
# PALETA DE COLORES
# =============================================================
if es_oscuro:
    text_color = "#f8fafc"; bg_sidebar = "#1e293b"
    bg_app = "linear-gradient(135deg, #0f172a 0%, #1e1e2e 100%)"
    text_primary = "#f8fafc"; text_secondary = "#94a3b8"
    sidebar_bg = "#1e293b"; card_bg = "#1e293b"; card_border = "rgba(255, 255, 255, 0.15)"
    input_bg = "#0f172a"; input_border = "rgba(255, 255, 255, 0.25)"; input_text = "#ffffff"
    select_bg = "#0f172a"; select_border = "rgba(255, 255, 255, 0.25)"
    select_text = "#ffffff"; select_svg = "#94a3b8"
    popover_bg = "#1e293b"; popover_border = "rgba(255, 255, 255, 0.2)"
    popover_text = "#f8fafc"; popover_hover = "#0284c7"
    metric_color = "#38bdf8"
    tab_bg_inactive = "#1e293b"; tab_border_inactive = "rgba(255, 255, 255, 0.2)"
    tab_text_inactive = "#f8fafc"
    tab_bg_active = "#0284c7"; tab_border_active = "#38bdf8"; tab_text_active = "#ffffff"
    btn_bg = "#0284c7"; btn_text = "#ffffff"
else:
    text_color = "#0f172a"; bg_sidebar = "#ffffff"
    bg_app = "linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)"
    text_primary = "#0f172a"; text_secondary = "#334155"
    sidebar_bg = "#ffffff"; card_bg = "#ffffff"; card_border = "#cbd5e1"
    input_bg = "#ffffff"; input_border = "#cbd5e1"; input_text = "#0f172a"
    select_bg = "#f0f4f8"; select_border = "#94a3b8"
    select_text = "#0f172a"; select_svg = "#475569"
    popover_bg = "#ffffff"; popover_border = "#cbd5e1"
    popover_text = "#0f172a"; popover_hover = "#e0f2fe"
    metric_color = "#0284c7"
    tab_bg_inactive = "#ffffff"; tab_border_inactive = "#cbd5e1"
    tab_text_inactive = "#0f172a"
    tab_bg_active = "#0284c7"; tab_border_active = "#0284c7"; tab_text_active = "#ffffff"
    btn_bg = "#0284c7"; btn_text = "#ffffff"

# =============================================================
# ESTILOS CSS GLOBALES
# =============================================================
st.markdown(f"""
<style>
    .stApp {{
        background: {bg_app} !important;
        color: {text_primary} !important;
    }}
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"] {{
        background: {sidebar_bg} !important;
        color: {text_primary} !important;
    }}
    [data-testid="stHeader"] {{
        border-bottom: 1px solid {card_border} !important;
    }}
    [data-testid="stHeader"] button,
    [data-testid="stHeader"] svg,
    [data-testid="stToolbar"] button,
    [data-testid="stToolbar"] svg {{
        color: {text_primary} !important;
        fill: {text_primary} !important;
    }}
    [data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
    }}
    [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stForm"] {{
        background-color: {card_bg} !important;
        border: 1px solid {card_border} !important;
    }}
    [data-testid="stSidebar"] input,
    div[data-baseweb="input"] > div {{
        background-color: {input_bg} !important;
        border-color: {input_border} !important;
        color: {input_text} !important;
    }}
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {{
        background-color: {select_bg} !important;
        border: 1px solid {select_border} !important;
        color: {select_text} !important;
        border-radius: 6px !important;
    }}
    [data-testid="stSidebar"] div[data-baseweb="select"] * {{
        background-color: transparent !important;
        color: {select_text} !important;
        fill: {select_svg} !important;
    }}
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li,
    div[data-baseweb="menu"] {{
        background-color: {popover_bg} !important;
        border-color: {popover_border} !important;
        color: {popover_text} !important;
    }}
    div[data-baseweb="popover"] li:hover,
    div[data-baseweb="menu"] [aria-selected="true"] {{
        background-color: {popover_hover} !important;
        color: {popover_text} !important;
    }}
    button[data-baseweb="tab"] {{
        background-color: {tab_bg_inactive} !important;
        border: 1px solid {tab_border_inactive} !important;
        color: {tab_text_inactive} !important;
    }}
    button[data-baseweb="tab"][aria-selected="true"] {{
        background-color: {tab_bg_active} !important;
        border-color: {tab_border_active} !important;
        color: {tab_text_active} !important;
    }}
    .stButton > button {{
        background-color: {btn_bg} !important;
        color: {btn_text} !important;
        border: none !important;
    }}
    div[data-testid="stSegmentedControl"] {{
        width: 100% !important;
    }}
    div[data-testid="stSegmentedControl"] > div {{
        width: 100% !important;
        display: flex !important;
    }}
    div[data-testid="stSegmentedControl"] button {{
        flex: 1 !important;
        justify-content: center !important;
        background-color: {select_bg} !important;
        color: {select_text} !important;
        border: 1px solid {select_border} !important;
        font-weight: 600 !important;
    }}
    div[data-testid="stSegmentedControl"] button[aria-selected="true"] {{
        background-color: #0284c7 !important;
        color: #ffffff !important;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<style>
    html, body, p, h1, h2, h3, h4, label, input, select, button,
    .stMarkdown, [data-testid="stMarkdownContainer"] p {{
        font-family: 'Times New Roman', Times, serif !important;
    }}
    .stApp {{ background: {bg_app}; color: {text_primary} !important; }}
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        border-right: 1px solid {card_border};
    }}
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: {text_primary} !important;
        font-weight: 700 !important;
    }}
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] > div > div {{
        background-color: {select_bg} !important;
        color: {select_text} !important;
        border: 1.5px solid {select_border} !important;
        border-radius: 10px !important;
    }}
    div[data-baseweb="select"] * {{ color: {select_text} !important; }}
    div[data-baseweb="select"] svg {{
        fill: {select_svg} !important;
        color: {select_svg} !important;
    }}
    body div[data-baseweb="popover"],
    body div[data-baseweb="popover"] > div,
    body div[data-baseweb="menu"],
    body ul[role="listbox"] {{
        background-color: {popover_bg} !important;
        border: 1.5px solid {popover_border} !important;
        border-radius: 12px !important;
        color: {popover_text} !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.12) !important;
    }}
    body li[role="option"],
    body div[data-baseweb="menu"] li,
    body div[data-baseweb="menu"] div {{
        background-color: {popover_bg} !important;
        color: {popover_text} !important;
        font-size: 1rem !important;
    }}
    body li[role="option"]:hover,
    body li[role="option"][aria-selected="true"],
    body div[data-baseweb="menu"] li:hover {{
        background-color: {popover_hover} !important;
        color: {metric_color} !important;
        font-weight: bold !important;
    }}
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: {card_bg} !important;
        border: 1.5px solid {card_border} !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04) !important;
        margin-bottom: 20px !important;
    }}
    .mac-card-header {{
        background: {card_bg};
        border-radius: 16px;
        padding: 24px;
        border: 1px solid {card_border};
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.06);
        margin-bottom: 24px;
    }}
    .mac-dots {{ display: flex; gap: 8px; margin-bottom: 12px; }}
    .dot {{ width: 12px; height: 12px; border-radius: 50%; display: inline-block; }}
    .dot-red {{ background-color: #ff5f56; }}
    .dot-yellow {{ background-color: #ffbd2e; }}
    .dot-green {{ background-color: #27c93f; }}
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
    div[data-testid="stTabs"] [data-baseweb="tab-border"],
    div[data-baseweb="tab-highlight"],
    div[data-baseweb="tab-border"] {{
        display: none !important;
        height: 0px !important;
        visibility: hidden !important;
        background-color: transparent !important;
        border: none !important;
    }}
    div[data-testid="stTabs"] [role="tablist"] {{
        display: flex !important;
        flex-wrap: wrap !important;
        gap: 10px !important;
        padding: 8px 0 16px 0 !important;
        border: 0 !important;
        background: transparent !important;
    }}
    div[data-testid="stTabs"] [role="tab"] {{
        box-sizing: border-box !important;
        min-height: 44px !important;
        height: auto !important;
        max-width: 100% !important;
        padding: 10px 18px !important;
        border: 1.5px solid {tab_border_inactive} !important;
        border-radius: 12px !important;
        background: {tab_bg_inactive} !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.2s ease-in-out !important;
        white-space: normal !important;
        overflow-wrap: anywhere !important;
    }}
    div[data-testid="stTabs"] [role="tab"] *,
    div[data-testid="stTabs"] [role="tab"] p,
    div[data-testid="stTabs"] [role="tab"] span {{
        color: {tab_text_inactive} !important;
        font-family: 'Times New Roman', Times, serif !important;
        font-size: 1.0rem !important;
        font-weight: 700 !important;
        white-space: normal !important;
        overflow-wrap: anywhere !important;
        line-height: 1.25 !important;
    }}
    div[data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
        background: {tab_bg_active} !important;
        border: 1.5px solid {tab_border_active} !important;
        box-shadow: 0 6px 16px rgba(2, 132, 199, 0.3) !important;
        transform: translateY(-2px) !important;
    }}
    div[data-testid="stTabs"] [role="tab"][aria-selected="true"] * {{
        color: {tab_text_active} !important;
        font-weight: 800 !important;
    }}
    div[data-testid="stExpander"],
    details[data-testid="stExpander"] {{
        background-color: {card_bg} !important;
        border: 1.5px solid {card_border} !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
        margin-bottom: 16px !important;
        overflow: hidden !important;
    }}
    div[data-testid="stExpander"] summary,
    details[data-testid="stExpander"] summary {{
        box-sizing: border-box !important;
        background-color: {card_bg} !important;
        color: {text_primary} !important;
        padding: 14px 18px !important;
        border-radius: 14px !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: flex-start !important;
        gap: 12px !important;
        min-width: 0 !important;
        width: 100% !important;
        height: auto !important;
        min-height: 54px !important;
        overflow: hidden !important;
    }}
    div[data-testid="stExpander"] summary > div,
    details[data-testid="stExpander"] summary > div,
    div[data-testid="stExpander"] summary [data-testid="stMarkdownContainer"],
    details[data-testid="stExpander"] summary [data-testid="stMarkdownContainer"] {{
        flex: 1 1 auto !important;
        min-width: 0 !important;
        width: auto !important;
        max-width: 100% !important;
        overflow-wrap: anywhere !important;
        word-break: normal !important;
    }}
    div[data-testid="stExpander"] summary p,
    details[data-testid="stExpander"] summary p {{
        color: {text_primary} !important;
        font-family: 'Times New Roman', Times, serif !important;
        font-size: 1rem !important;
        line-height: 1.45 !important;
        font-weight: bold !important;
        margin: 0 !important;
        padding: 0 !important;
        white-space: normal !important;
        overflow-wrap: anywhere !important;
        word-break: normal !important;
    }}
    div[data-testid="stExpander"] summary svg,
    details[data-testid="stExpander"] summary svg {{
        position: static !important;
        display: block !important;
        flex: 0 0 1.25rem !important;
        width: 1.25rem !important;
        height: 1.25rem !important;
        margin: 0 !important;
        fill: {text_primary} !important;
        color: {text_primary} !important;
    }}
    div[data-testid="stExpander"] summary:hover {{
        background-color: {popover_hover} !important;
    }}
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"],
    details[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {{
        box-sizing: border-box !important;
        background-color: {card_bg} !important;
        color: {text_primary} !important;
        padding: 18px !important;
        border-top: 1px solid {card_border} !important;
        min-width: 0 !important;
        overflow-x: auto !important;
    }}
    [data-testid="stMetric"] {{
        background: {card_bg};
        padding: 16px 20px;
        border-radius: 14px;
        border: 1px solid {card_border};
        box-shadow: 0 4px 15px rgba(0,0,0,0.04);
    }}
    [data-testid="stMetricValue"] {{
        font-size: 2.1rem !important;
        font-weight: 800 !important;
        color: {metric_color} !important;
    }}
    [data-testid="stMetricLabel"] p {{
        color: {text_primary} !important;
        font-size: 1.15rem !important;
        font-weight: 700 !important;
    }}
    div.stButton > button,
    div[data-testid="stDownloadButton"] > button {{
        background-color: {btn_bg} !important;
        color: {btn_text} !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 10px 20px !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3) !important;
    }}
    div[data-testid="stDataFrame"],
    div[data-testid="stTable"] {{
        background: #ffffff !important;
        border-radius: 10px !important;
        border: 1px solid #e2e8f0 !important;
        padding: 6px !important;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important;
    }}
    .badge-mac {{
        background-color: rgba(56, 189, 248, 0.15);
        color: {metric_color} !important;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.95rem;
        font-weight: 700;
        border: 1px solid rgba(56, 189, 248, 0.3);
    }}
</style>
""", unsafe_allow_html=True)

# =============================================================
# ENCABEZADO
# =============================================================
st.markdown(f"""
<div class="mac-card-header">
    <div class="mac-dots">
        <span class="dot dot-red"></span>
        <span class="dot dot-yellow"></span>
        <span class="dot dot-green"></span>
    </div>
    <span class="badge-mac">NORMA TECNICA PERUANA E.030</span>
    <h1 style='margin-top: 10px; font-weight: 800; font-size: 2.2rem;
               color: {text_primary};'>
        🏢 Sistema de Analisis Sismico Modal Espectral
    </h1>
    <p style='color: {text_secondary}; font-size: 1.1rem;'>
        Plataforma interactiva con soporte de temas dinamicos,
        calculo y visualizacion en tiempo real.
    </p>
</div>
""", unsafe_allow_html=True)

# =============================================================
# BARRA LATERAL: PARAMETROS NORMA E.030
# =============================================================
st.sidebar.markdown("---")
st.sidebar.markdown("### Parametros Norma E.030")

dic_zonas = {
    "Zona 4 (Z = 0.45) - Alta Sismicidad (Costa)": 0.45,
    "Zona 3 (Z = 0.35) - Sismicidad Media-Alta (Sierra)": 0.35,
    "Zona 2 (Z = 0.25) - Sismicidad Media (Ceja de Selva)": 0.25,
    "Zona 1 (Z = 0.10) - Sismicidad Baja (Selva Baja)": 0.10,
}
opcion_z = st.sidebar.selectbox("Factor de Zona (Z):", list(dic_zonas.keys()), index=0)
Z = dic_zonas[opcion_z]

dic_suelos = {
    "S0: Roca Dura (S = 0.80, Tp = 0.3s, TL = 3.0s)":              {"S": 0.80, "Tp": 0.3, "TL": 3.0},
    "S1: Roca o Suelos Muy Rigidos (S = 1.00, Tp = 0.4s, TL = 2.5s)": {"S": 1.00, "Tp": 0.4, "TL": 2.5},
    "S2: Suelos Intermedios (S = 1.05, Tp = 0.6s, TL = 2.0s)":      {"S": 1.05, "Tp": 0.6, "TL": 2.0},
    "S3: Suelos Blandos (S = 1.20, Tp = 1.0s, TL = 1.6s)":          {"S": 1.20, "Tp": 1.0, "TL": 1.6},
}
opcion_s = st.sidebar.selectbox("Perfil de Suelo (S):", list(dic_suelos.keys()), index=1)
S  = dic_suelos[opcion_s]["S"]
Tp = dic_suelos[opcion_s]["Tp"]
TL = dic_suelos[opcion_s]["TL"]

dic_usos = {
    "Categoria A1/A2: Edificaciones Esenciales (U = 1.5)": 1.5,
    "Categoria B: Edificaciones Importantes (U = 1.3)":    1.3,
    "Categoria C: Edificaciones Comunes (U = 1.0)":        1.0,
}
opcion_u = st.sidebar.selectbox("Categoria de Uso e Importancia (U):",
                                list(dic_usos.keys()), index=2)
U = dic_usos[opcion_u]

dic_sistemas_r = {
    "Porticos de Concreto Armado (R = 8)":       8.0,
    "Sistema Dual de Concreto Armado (R = 7)":   7.0,
    "Muros de Concreto Armado / MDU (R = 6)":    6.0,
    "Albanileria Confinada (R = 3)":             3.0,
    "Porticos de Acero SMF (R = 8)":             8.0,
}
opcion_r = st.sidebar.selectbox("Sistema Estructural (R):",
                                list(dic_sistemas_r.keys()), index=0)
R = dic_sistemas_r[opcion_r]

dic_ct = {
    "Porticos de C.A. sin muros / Acero ductil (Ct = 35)": 35.0,
    "Porticos de C.A. con cajas de ascensor (Ct = 45)":    45.0,
    "Albanileria / Muros de C.A. (Ct = 60)":              60.0,
}
opcion_ct = st.sidebar.selectbox("Coeficiente de Periodo (Ct):",
                                 list(dic_ct.keys()), index=0)
Ct = dic_ct[opcion_ct]

# =============================================================
# CARGADOR DE ARCHIVO DE PARAMETROS
# =============================================================
st.sidebar.markdown("---")
st.sidebar.markdown("### Datos de la Estructura")

if es_oscuro:
    uploader_bg = "#172554"; uploader_border = "#60a5fa"
    uploader_text = "#eff6ff"; uploader_hint = "#bfdbfe"
else:
    uploader_bg = "#eaf4ff"; uploader_border = "#60a5fa"
    uploader_text = "#16325c"; uploader_hint = "#315b86"

st.markdown(f"""
<style>
  [data-testid="stFileUploaderDropzone"] {{
      background: {uploader_bg} !important;
      border: 2px dashed {uploader_border} !important;
      border-radius: 12px !important;
  }}
  [data-testid="stFileUploaderDropzone"] p,
  [data-testid="stFileUploaderDropzone"] span,
  [data-testid="stFileUploaderDropzone"] small,
  [data-testid="stFileUploaderDropzone"] [data-testid="stMarkdownContainer"] {{
      color: {uploader_text} !important;
  }}
  [data-testid="stFileUploaderDropzone"] button {{
      background: #dbeafe !important;
      color: #12345a !important;
      border: 1px solid #60a5fa !important;
      border-radius: 8px !important;
      font-size: 14px !important;
      min-width: 78px !important;
      position: relative !important;
  }}
  [data-testid="stFileUploaderDropzone"] button span,
  [data-testid="stFileUploaderDropzone"] button [data-testid="stMarkdownContainer"],
  [data-testid="stFileUploaderDropzone"] button p {{ display: none !important; }}
  [data-testid="stFileUploaderDropzone"] button::after {{
      content: "Subir" !important;
      display: inline-block !important;
      font-size: 14px !important;
      font-weight: 600 !important;
      color: #12345a !important;
  }}
  [data-testid="stFileUploader"] section {{
      background: {uploader_bg} !important;
      border-radius: 12px !important;
  }}
  [data-testid="stFileUploaderFile"] {{
      background: #1e293b !important;
      border: 1px solid #64748b !important;
      border-radius: 8px !important;
  }}
  [data-testid="stFileUploaderFile"] *,
  [data-testid="stFileUploaderFileName"],
  [data-testid="stFileUploaderFile"] small,
  [data-testid="stFileUploaderFile"] span,
  [data-testid="stFileUploaderFile"] p {{
      color: #ffffff !important;
      fill: #ffffff !important;
  }}
  [data-testid="stFileUploader"] small,
  [data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] {{
      color: {uploader_hint} !important;
  }}
</style>
""", unsafe_allow_html=True)

# Inicializar session state con valores predeterminados
for clave, valor in VALORES_PREDETERMINADOS.items():
    st.session_state.setdefault(clave, valor)

archivo_datos = st.sidebar.file_uploader(
    "📂 Cargar parametros (Excel, CSV o TXT)",
    type=["xlsx", "xls", "csv", "txt"],
    help="Una fila por parametro y sus valores en la segunda columna.",
)

if archivo_datos is not None:
    bytes_archivo  = archivo_datos.getvalue()
    id_archivo     = hashlib.sha256(bytes_archivo).hexdigest()
    if st.session_state.get("archivo_parametros_cargado") != id_archivo:
        try:
            resultado = leer_archivo_parametros(bytes_archivo, archivo_datos.name)
            if resultado:
                for clave, texto in resultado.items():
                    st.session_state[clave] = texto
                st.session_state["archivo_parametros_cargado"] = id_archivo
                st.sidebar.success(
                    f"Se actualizaron {len(resultado)} parametros. "
                    "Revisa los campos antes de calcular."
                )
            else:
                st.sidebar.error(
                    "No se encontraron parametros reconocibles. "
                    "Usa la plantilla CSV: columnas 'Parametro' y 'Valores'."
                )
        except Exception as e:
            st.sidebar.error(f"No se pudo leer el archivo: {e}")

# Campos de texto de entrada
alturas_input  = st.sidebar.text_input("Alturas entrepiso (m)",           key="alturas_input")
periodos_input = st.sidebar.text_input("Periodos Modales (s)",             key="periodos_input")
masas_input    = st.sidebar.text_input("Masas de Pisos (tonf.s2/m)",      key="masas_input")
f1_input       = st.sidebar.text_input("Forma Modal 1",                    key="f1_input")
f2_input       = st.sidebar.text_input("Forma Modal 2",                    key="f2_input")
f3_input       = st.sidebar.text_input("Forma Modal 3",                    key="f3_input")

# =============================================================
# PARSEO Y VALIDACION DE ENTRADAS
# =============================================================
try:
    (alturas_entrepiso, periodos_modales, vector_masas_piso,
     forma_modal_1, forma_modal_2, forma_modal_3,
     matriz_masas, matriz_formas_modales,
     num_pisos, lista_pisos, Ht) = parsear_entradas(
        alturas_input, periodos_input, masas_input,
        f1_input, f2_input, f3_input
    )
except Exception as e:
    st.error(f"Error en los datos ingresados: {e}")
    st.stop()

errores = validar_entradas(periodos_modales, vector_masas_piso,
                           num_pisos, alturas_entrepiso, matriz_formas_modales)
for msg in errores:
    st.error(msg)
if errores:
    st.stop()

# =============================================================
# CALCULOS PRINCIPALES
# =============================================================
T_fund, C_modo, Sa_modo, w_modo, Sd_modo = calcular_parametros_espectrales(
    Z, U, S, R, Tp, TL, Ht, Ct, periodos_modales
)
gammas = calcular_factores_participacion(
    matriz_masas, vector_masas_piso, matriz_formas_modales
)
F_modales, V_modales = calcular_respuestas_modales(
    vector_masas_piso, matriz_formas_modales, Sa_modo, gammas
)
V_abs, V_srss, V_cqc, V_real = calcular_combinacion_modal(
    V_modales, R, periodos_modales
)
df_resultados = generar_dataframe_resultados(
    lista_pisos, F_modales, V_modales, V_abs, V_srss, V_cqc, V_real
)

# =============================================================
# BOTON GUARDAR HISTORIAL
# =============================================================
st.sidebar.markdown("---")
if st.sidebar.button("💾 Guardar Analisis Actual"):
    registro = {
        "Fecha":          datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Z": Z, "U": U, "S": S, "R": R,
        "V_Base_CQC":     V_cqc[0],
        "V_Base_Diseno": V_real[0],
        "Resultados":     df_resultados.copy(),
    }
    st.session_state.historial_calculos.append(registro)
    st.sidebar.success("Analisis guardado en memoria.")

# =============================================================
# PESTANAS PRINCIPALES
# =============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Parametros y Resultados",
    "📈 Graficos de Respuestas",
    "💾 Historial de Analisis",
    "📥 Exportar resultados",
    "🎬 Animacion Modos",
])

# ----------------------------------------------------------
# TAB 1 — Resultados tabulares
# ----------------------------------------------------------
with tab1:
    with st.container(border=True):
        st.subheader("📌 Parametros Principales")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Factor Zona (Z)",  f"{Z:.2f}")
        c2.metric("Factor Uso (U)",   f"{U:.2f}")
        c3.metric("Coef. Suelo (S)", f"{S:.2f}")
        c4.metric("Reduccion (R)",    f"{R:.1f}")

    with st.container(border=True):
        st.subheader("📋 Tabla Resumen por Piso (Fuerzas y Cortantes)")
        st.dataframe(estilar_dataframe(df_resultados, es_oscuro),
                     use_container_width=True)

# ----------------------------------------------------------
# TAB 2 — Graficos
# ----------------------------------------------------------
with tab2:
    with st.container(border=True):
        st.subheader("🏢 Distribucion de Cargas Sismicas Lateralmente Aplicadas")
        fig_est = graficar_modelo_estructural(
            lista_pisos, alturas_entrepiso, V_real, es_oscuro
        )
        st.pyplot(fig_est)

    with st.container(border=True):
        st.subheader("📊 Perfiles Modales de Fuerzas y Cortantes")
        fig1 = graficar_perfiles_modales(
            lista_pisos, F_modales, V_modales, es_oscuro
        )
        st.pyplot(fig1)

    with st.container(border=True):
        st.subheader("📊 Comparacion de cortantes combinados por piso")
        fig_comb = graficar_combinaciones_modales(
            lista_pisos, V_abs, V_srss, V_cqc, V_real
        )
        st.pyplot(fig_comb, use_container_width=True)

# ----------------------------------------------------------
# TAB 3 — Historial
# ----------------------------------------------------------
with tab3:
    with st.container(border=True):
        st.subheader("📚 Historial de Analisis Guardados")
        if not st.session_state.historial_calculos:
            st.info("No hay analisis guardados. Presiona 'Guardar Analisis Actual'.")
        else:
            for idx, calc in enumerate(st.session_state.historial_calculos):
                with st.expander(
                    f"📌 Analisis N° {idx+1} — {calc['Fecha']} "
                    f"| (Z={calc['Z']}, U={calc['U']}, S={calc['S']}, R={calc['R']})"
                ):
                    ch1, ch2 = st.columns(2)
                    ch1.metric("Cortante Basal CQC",     f"{calc['V_Base_CQC']:.3f} tonf")
                    ch2.metric("Cortante Basal de Diseno", f"{calc['V_Base_Diseno']:.3f} tonf")
                    st.dataframe(estilar_dataframe(calc["Resultados"], es_oscuro),
                                 use_container_width=True)

# ----------------------------------------------------------
# TAB 4 — Exportacion
# ----------------------------------------------------------
with tab4:
    with st.container(border=True):
        st.subheader("📥 Exportacion del Reporte")

        # Excel
        buffer_excel = generar_excel_bytes(df_resultados)
        st.download_button(
            label="📊 Descargar Reporte Excel (.xlsx)",
            data=buffer_excel,
            file_name=f"Reporte_Sismico_{datetime.datetime.now():%Y%m%d_%H%M%S}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        # CSV
        st.download_button(
            label="📄 Descargar resultados en CSV",
            data=df_resultados.to_csv(index=False).encode("utf-8-sig"),
            file_name="Resultados_Analisis_Sismico.csv",
            mime="text/csv",
        )

        # PDF con graficos vectoriales
        def generar_pdf_reporte(df, fig_est, fig1, fig_comb):
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_pdf import PdfPages

            pdf_buf = io.BytesIO()
            with PdfPages(pdf_buf) as pdf:
                # Pagina 1: tabla de resultados
                fig_t, ax_t = plt.subplots(figsize=(11.69, 8.27))
                fig_t.patch.set_facecolor("white")
                ax_t.axis("off")
                ax_t.text(0.5, 0.96,
                          "REPORTE DE ANALISIS SISMICO MODAL ESPECTRAL — NORMA E.030",
                          ha="center", va="top", fontsize=15, fontweight="bold",
                          color="#075985", transform=ax_t.transAxes)
                ax_t.text(0.5, 0.90,
                          f"Fecha de generacion: {datetime.datetime.now():%d/%m/%Y %H:%M}",
                          ha="center", va="top", fontsize=9, color="#334155",
                          transform=ax_t.transAxes)
                tabla = ax_t.table(
                    cellText=df.round(3).astype(str).values,
                    colLabels=[str(c) for c in df.columns],
                    cellLoc="center", colLoc="center", loc="center",
                )
                tabla.auto_set_font_size(False)
                tabla.set_fontsize(8)
                tabla.scale(1, 1.5)
                for (fila, col_), celda in tabla.get_celld().items():
                    celda.set_edgecolor("#cbd5e1")
                    if fila == 0:
                        celda.set_facecolor("#0284c7")
                        celda.get_text().set_color("white")
                        celda.get_text().set_weight("bold")
                    else:
                        celda.set_facecolor("#eff6ff" if fila % 2 == 0 else "white")
                        celda.get_text().set_color("#0f172a")
                pdf.savefig(fig_t, bbox_inches="tight")
                plt.close(fig_t)

                for figura, titulo in [
                    (fig_est,  "Distribucion de cargas sismicas"),
                    (fig1,     "Perfiles modales de fuerzas y cortantes"),
                    (fig_comb, "Comparacion de cortantes combinados — cuatro metodos"),
                ]:
                    if figura is not None:
                        figura.suptitle(titulo, fontsize=14, fontweight="bold",
                                        color="#075985", y=1.02)
                        figura.tight_layout()
                        pdf.savefig(figura, bbox_inches="tight")
                        figura.suptitle("")

            pdf_buf.seek(0)
            return pdf_buf

        pdf_buffer = generar_pdf_reporte(df_resultados, fig_est, fig1, fig_comb)
        st.download_button(
            label="📄 Descargar reporte completo en PDF (graficos vectoriales)",
            data=pdf_buffer,
            file_name=f"Reporte_Sismico_E030_{datetime.datetime.now():%Y%m%d_%H%M%S}.pdf",
            mime="application/pdf",
        )

# ----------------------------------------------------------
# TAB 5 — Animacion dinamica
# ----------------------------------------------------------
with tab5:
    st.subheader("🎬 Animacion Dinamica 2D (Modelo de Masa Concentrada)")
    if st.button("▶️ Generar Animacion de Modos"):
        with st.spinner("Procesando fotogramas dinamicos..."):
            html_code = generar_animacion_modos(
                alturas_entrepiso, periodos_modales,
                matriz_formas_modales, w_modo,
                num_pisos, es_oscuro,
            )
            components.html(html_code, height=520, scrolling=True)

# =============================================================
# PIE DE PAGINA
# =============================================================
st.markdown(f"""
<div class="mac-card-header" style="text-align: center;">
    <h2 style='margin-top: 0; font-weight: 600; font-size: 1.25rem;
               color: {text_primary}; margin-bottom: 10px;'>
        Alumno: Arce Quinteros Joseph Jhordan
    </h2>
    <h2 style='margin-top: 0; font-weight: 600; font-size: 1.25rem;
               color: {text_primary}; margin-bottom: 10px;'>
        Especialidad: Python + IA Aplicada a la Ingenieria Civil | AECODE
    </h2>
</div>
""", unsafe_allow_html=True)
