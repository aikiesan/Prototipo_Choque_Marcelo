#!/usr/bin/env python3
"""
🗺️ SIMULADOR GEO-ECONÔMICO NACIONAL - VERSÃO ELEGANT
Interface profissional com design premium, validação técnica e UX excepcional
Layout 50/50 com seção de validação de modelo e parâmetros técnicos
"""

import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    layout="wide",
    page_title="🗺️ Simulador de Choque - Marcelo CP2B",
    page_icon="🗺️",
    initial_sidebar_state="collapsed"
)

# Modern CSS Design System
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* === CSS VARIABLES & DESIGN TOKENS === */
    :root {
        --primary-50: #eff6ff;
        --primary-100: #dbeafe;
        --primary-500: #3b82f6;
        --primary-600: #2563eb;
        --primary-700: #1d4ed8;
        --primary-900: #1e3a8a;

        --gray-50: #f8fafc;
        --gray-100: #f1f5f9;
        --gray-200: #e2e8f0;
        --gray-300: #cbd5e1;
        --gray-400: #94a3b8;
        --gray-500: #64748b;
        --gray-600: #475569;
        --gray-700: #334155;
        --gray-800: #1e293b;
        --gray-900: #0f172a;

        --success-500: #10b981;
        --warning-500: #f59e0b;
        --error-500: #ef4444;

        --radius-sm: 6px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --radius-xl: 16px;

        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);

        --transition-fast: 150ms ease-in-out;
        --transition-normal: 250ms ease-in-out;
    }

    /* === GLOBAL STYLES === */
    .stApp {
        background: linear-gradient(135deg, var(--gray-50) 0%, var(--primary-50) 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .main .block-container {
        background-color: transparent;
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: none;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    /* === TYPOGRAPHY === */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        color: var(--gray-900) !important;
        letter-spacing: -0.025em;
    }

    /* Force dark text for all Streamlit elements */
    .stMarkdown, .stMarkdown p, .stMarkdown div,
    .stText, p, span, div,
    .streamlit-container, .block-container,
    [data-testid="stMarkdownContainer"],
    [data-testid="stText"] {
        color: var(--gray-900) !important;
    }

    /* Ensure main content has dark text */
    .main .block-container * {
        color: var(--gray-900) !important;
    }

    /* Override any white text */
    .main * {
        color: var(--gray-900) !important;
    }

    /* Specific fixes for Streamlit components */
    [data-testid="metric-container"],
    [data-testid="metric-container"] *,
    .streamlit-expanderHeader,
    .streamlit-expander *,
    .stSelectbox label,
    .stNumberInput label,
    .stSlider label,
    .element-container *,
    .row-widget *,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
    .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: var(--gray-900) !important;
    }

    .app-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary-600), var(--primary-700));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
    }

    .app-subtitle {
        font-size: 1.125rem;
        color: var(--gray-600);
        text-align: center;
        margin-bottom: 2rem;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
        line-height: 1.6;
    }

    /* === CARD SYSTEM === */
    .card {
        background: white;
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-md);
        border: 1px solid var(--gray-200);
        transition: all var(--transition-normal);
        overflow: hidden;
    }

    .card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
    }

    .card-header {
        background: linear-gradient(135deg, var(--primary-500), var(--primary-600));
        color: white !important;
        padding: 1.5rem;
        font-weight: 600;
        font-size: 1.125rem;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .card-header * {
        color: white !important;
    }

    .card-body {
        padding: 1.5rem;
        color: var(--gray-900) !important;
    }

    .card-body * {
        color: var(--gray-900) !important;
    }

    .card-compact {
        padding: 1rem;
        color: var(--gray-900) !important;
    }

    /* === METRIC CARDS === */
    .metric-card {
        background: white;
        border-radius: var(--radius-lg);
        padding: 1.5rem;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--gray-200);
        transition: all var(--transition-normal);
        text-align: center;
        position: relative;
        overflow: hidden;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-500), var(--primary-600));
    }

    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-xl);
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--gray-900);
        margin-bottom: 0.25rem;
    }

    .metric-label {
        font-size: 0.875rem;
        color: var(--gray-600);
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .metric-icon {
        font-size: 1.5rem;
        margin-bottom: 0.75rem;
        opacity: 0.8;
    }

    /* === SECTION STYLING === */
    .section-header {
        background: white;
        border-radius: var(--radius-lg);
        padding: 1.25rem 1.5rem;
        margin: 2rem 0 1rem 0;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--gray-200);
        border-left: 4px solid var(--primary-500);
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--gray-900);
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    /* === STREAMLIT COMPONENT OVERRIDES === */
    .stSelectbox > div > div {
        background-color: white !important;
        border: 2px solid var(--gray-200);
        border-radius: var(--radius-md);
        transition: all var(--transition-fast);
    }

    .stSelectbox > div > div:focus-within {
        border-color: var(--primary-500);
        box-shadow: 0 0 0 3px var(--primary-50);
    }

    /* Fix dropdown styling - Force white background always */
    .stSelectbox div[data-baseweb="select"],
    .stSelectbox div[data-baseweb="select"] > div,
    .stSelectbox div[data-baseweb="select"] > div > div,
    .stSelectbox div[data-baseweb="select"] > div > div > div,
    .stSelectbox [data-baseweb="select"] .css-1uccc91-singleValue,
    .stSelectbox [data-baseweb="select"] .css-1wa3eu0-placeholder,
    .stSelectbox [data-baseweb="select"] .css-1dimb5e-singleValue,
    .stSelectbox [data-baseweb="select"] .css-1n7v3ny-option,
    .stSelectbox [data-baseweb="select"] > div[data-baseweb="select-value"],
    .stSelectbox [data-baseweb="select"] [data-baseweb="select-value"],
    .stSelectbox [data-baseweb="select"] span {
        background-color: white !important;
        color: #1e293b !important;
        background: white !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 8px !important;
    }

    /* Dropdown container - super specific */
    .stSelectbox div[data-baseweb="select"] {
        background-color: white !important;
        background: white !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 8px !important;
    }

    /* Value display area */
    .stSelectbox [data-baseweb="select"] > div[data-baseweb="select-value"],
    .stSelectbox [data-baseweb="select"] > div[data-baseweb="select-value"] > div {
        background-color: white !important;
        background: white !important;
        color: #1e293b !important;
    }

    /* All possible text elements */
    .stSelectbox [data-baseweb="select"] span,
    .stSelectbox [data-baseweb="select"] div,
    .stSelectbox [data-baseweb="select"] p {
        color: #1e293b !important;
        background-color: transparent !important;
    }

    /* Fix dropdown options list */
    div[role="listbox"],
    .stSelectbox div[data-baseweb="popover"] > div,
    .stSelectbox div[data-baseweb="popover"] > div > div {
        background-color: white !important;
        background: white !important;
        color: #1e293b !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 8px !important;
        box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1) !important;
    }

    /* Individual options */
    div[role="option"],
    .stSelectbox li[role="option"],
    .stSelectbox div[role="option"] {
        background-color: white !important;
        background: white !important;
        color: #1e293b !important;
        padding: 0.75rem 1rem !important;
    }

    /* Hover state for options */
    div[role="option"]:hover,
    .stSelectbox li[role="option"]:hover,
    .stSelectbox div[role="option"]:hover {
        background-color: #f1f5f9 !important;
        background: #f1f5f9 !important;
        color: #1e293b !important;
    }

    /* Selected option */
    div[role="option"][aria-selected="true"],
    .stSelectbox li[role="option"][aria-selected="true"] {
        background-color: #dbeafe !important;
        background: #dbeafe !important;
        color: #1e40af !important;
    }

    /* Force override for all selectbox states */
    .stSelectbox * {
        background-color: white !important;
        color: #1e293b !important;
    }

    /* Exception for icons and hover states */
    .stSelectbox *:hover {
        background-color: #f1f5f9 !important;
        color: #1e293b !important;
    }

    .stNumberInput > div > div > input {
        background-color: white;
        border: 2px solid var(--gray-200);
        border-radius: var(--radius-md);
        transition: all var(--transition-fast);
    }

    .stNumberInput > div > div > input:focus {
        border-color: var(--primary-500);
        box-shadow: 0 0 0 3px var(--primary-50);
    }

    .stButton > button {
        background: linear-gradient(135deg, var(--primary-500), var(--primary-600));
        color: white;
        border: none;
        border-radius: var(--radius-md);
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: all var(--transition-fast);
        box-shadow: var(--shadow-sm);
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, var(--primary-600), var(--primary-700));
        box-shadow: var(--shadow-md);
        transform: translateY(-1px);
    }

    .stTabs [data-baseweb="tab-list"] {
        background: white;
        border-radius: 12px;
        padding: 0.75rem;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #64748b;
        font-weight: 500;
        font-size: 1rem;
        transition: all 0.2s ease;
        padding: 0.75rem 1.5rem;
        min-width: 200px;
        text-align: center;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: #f1f5f9;
        color: #334155;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        box-shadow: 0 2px 4px -1px rgb(59 130 246 / 0.3);
    }

    /* === RESPONSIVE DESIGN === */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .app-title {
            font-size: 2rem;
        }

        .metric-card {
            padding: 1rem;
        }

        .card-header, .card-body {
            padding: 1rem;
        }
    }

    /* === ACCESSIBILITY === */
    .stButton > button:focus,
    .stSelectbox > div > div:focus-within,
    .stNumberInput > div > div > input:focus {
        outline: 2px solid var(--primary-500);
        outline-offset: 2px;
    }

    /* === ANIMATIONS === */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }

    .animate-fade-in {
        animation: fadeIn 0.5s ease-out;
    }

    .animate-slide-in {
        animation: slideIn 0.4s ease-out;
    }

    /* === LOADING STATES === */
    .loading-skeleton {
        background: linear-gradient(90deg, var(--gray-200) 25%, var(--gray-100) 50%, var(--gray-200) 75%);
        background-size: 200% 100%;
        animation: loading 1.5s infinite;
    }

    @keyframes loading {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }

    /* === ENHANCED VISUAL ELEMENTS === */
    .stExpander {
        border: 1px solid var(--gray-200);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-sm);
        margin: 1rem 0;
    }

    .stExpander > details > summary {
        background: var(--gray-50);
        border-radius: var(--radius-lg) var(--radius-lg) 0 0;
        padding: 1rem 1.5rem;
        font-weight: 500;
        color: var(--gray-700);
    }

    .stExpander[data-testid="expanderContainer"] {
        background: white;
    }

    /* Success/Warning/Error styling */
    .stSuccess {
        background: var(--success-500);
        color: white;
        border-radius: var(--radius-md);
        border: none;
    }

    .stWarning {
        background: var(--warning-500);
        color: white;
        border-radius: var(--radius-md);
        border: none;
    }

    .stError {
        background: var(--error-500);
        color: white;
        border-radius: var(--radius-md);
        border: none;
    }

    .stInfo {
        background: linear-gradient(135deg, var(--primary-50), var(--primary-100));
        border: 1px solid var(--primary-200);
        border-radius: var(--radius-md);
        color: var(--primary-800);
    }

    /* Map container styling */
    .folium-map {
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-lg);
        border: 1px solid var(--gray-200);
        overflow: hidden;
    }

    /* Progress indicators */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--primary-500), var(--primary-600));
        border-radius: var(--radius-sm);
    }

    /* Data frame styling */
    .stDataFrame {
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow-md);
        border: 1px solid var(--gray-200);
        overflow: hidden;
    }

    /* Balloons animation enhancement */
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }

    .floating {
        animation: float 2s ease-in-out infinite;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# MODELO ECONÔMICO AVANÇADO (LEONTIEF INPUT-OUTPUT)
# ==============================================================================

# Definição dos setores e metadados
setores = ['Agropecuária', 'Indústria', 'Construção', 'Serviços']
metadados_setores = {
    'Agropecuária': {
        'emoji': '🌾',
        'descricao': 'Agricultura, pecuária, silvicultura e pesca',
        'multiplicador_base': 1.52,
        'cor': '#FF6B6B'
    },
    'Indústria': {
        'emoji': '🏭',
        'descricao': 'Manufatura, transformação e indústria extrativa',
        'multiplicador_base': 2.18,
        'cor': '#4ECDC4'
    },
    'Construção': {
        'emoji': '🏗️',
        'descricao': 'Construção civil, infraestrutura e obras',
        'multiplicador_base': 1.84,
        'cor': '#45B7D1'
    },
    'Serviços': {
        'emoji': '🏪',
        'descricao': 'Comércio, transportes, serviços e administração',
        'multiplicador_base': 1.67,
        'cor': '#96CEB4'
    }
}

# Matriz de coeficientes técnicos (baseada em dados reais do Brasil - TRU 2017)
matriz_a = pd.DataFrame({
    'Agropecuária': [0.201, 0.155, 0.002, 0.117],
    'Indústria': [0.085, 0.351, 0.004, 0.160],
    'Construção': [0.003, 0.298, 0.001, 0.145],
    'Serviços': [0.012, 0.105, 0.008, 0.245]
}, index=setores)

# Matriz de impactos L = (I - A)^-1
matriz_identidade = np.identity(len(setores))
matriz_L = np.linalg.inv(matriz_identidade - matriz_a.values)
matriz_L_df = pd.DataFrame(matriz_L, index=setores, columns=setores)

# Parâmetros do modelo
parametros_modelo = {
    'ano_base': 2017,
    'fonte_matriz': 'Tabela de Recursos e Usos (TRU) - IBGE',
    'metodologia': 'Modelo Input-Output de Leontief',
    'regioes_cobertas': 133,
    'setores_economicos': 4,
    'tipo_analise': 'Impactos diretos, indiretos e induzidos',
    'unidade_monetaria': 'Milhões de Reais (R$ Mi)',
    'data_processamento': datetime.now().strftime('%d/%m/%Y %H:%M')
}

# ==============================================================================
# CARREGAMENTO E PROCESSAMENTO DE DADOS (CACHEADO)
# ==============================================================================

@st.cache_data(show_spinner="⚡ Carregando geometrias ultra-leves...")
def carregar_dados_geograficos():
    """Carrega geometrias ultra-leves e as prepara."""
    try:
        gdf = gpd.read_parquet('shapefiles/brasil_regions_ultra_light.parquet')
        gdf['NM_RGINT'] = gdf['NM_RGINT'].astype(str).str.strip()
        return gdf
    except FileNotFoundError:
        # Fallback para geometrias originais
        try:
            gdf = gpd.read_parquet(
                'shapefiles/BR_RG_Imediatas_2024_optimized.parquet',
                columns=['NM_RGINT', 'geometry']
            )
            gdf_regioes = gdf.dissolve(by='NM_RGINT').reset_index()
            gdf_regioes['NM_RGINT'] = gdf_regioes['NM_RGINT'].astype(str).str.strip()
            return gdf_regioes
        except Exception as e:
            st.error(f"Erro ao carregar dados geográficos: {e}")
            return None

@st.cache_data(show_spinner="📊 Construindo base econômica sintética...")
def gerar_dados_economicos(_gdf):
    """Gera dados econômicos sintéticos realistas para as 133 regiões."""
    np.random.seed(42)  # Resultados consistentes
    regioes = _gdf['NM_RGINT'].tolist()

    dados = []
    for regiao in regioes:
        # VAB base por setor com variação regional realística
        vab_base = {
            'Agropecuária': np.random.lognormal(10, 0.8),  # Mais variável
            'Indústria': np.random.lognormal(10.5, 1.0),
            'Construção': np.random.lognormal(9.5, 0.6),
            'Serviços': np.random.lognormal(11, 0.7)  # Maior VAB médio
        }

        for setor in setores:
            dados.append({
                'regiao': regiao,
                'setor': setor,
                'vab': vab_base[setor],
                'empregos': vab_base[setor] * np.random.uniform(15, 25),  # Empregos por R$ milhão
                'empresas': int(vab_base[setor] * np.random.uniform(0.5, 2.0))  # Número de empresas
            })

    df = pd.DataFrame(dados)

    # Calcular shares (participação de cada região no VAB setorial nacional)
    df['share_nacional'] = df.groupby('setor')['vab'].transform(lambda x: x / x.sum())

    return df

# ==============================================================================
# LÓGICA DE SIMULAÇÃO AVANÇADA
# ==============================================================================

def executar_simulacao_avancada(df_economia, valor_choque, setor_choque):
    """
    Executa simulação completa com modelo Leontief
    Retorna impactos desagregados por setor e região
    """
    # 1. Vetor de choque inicial
    setor_idx = setores.index(setor_choque)
    vetor_choque = np.zeros(len(setores))
    vetor_choque[setor_idx] = valor_choque

    # 2. Calcular impactos setoriais nacionais usando matriz Leontief
    impactos_setoriais = matriz_L @ vetor_choque

    # 3. Distribuir impactos entre regiões por setor
    resultados = []
    for i, setor in enumerate(setores):
        impacto_setor_nacional = impactos_setoriais[i]

        # Filtrar dados do setor
        dados_setor = df_economia[df_economia['setor'] == setor].copy()

        # Distribuir o impacto nacional entre as regiões
        dados_setor['impacto_producao'] = dados_setor['share_nacional'] * impacto_setor_nacional
        dados_setor['impacto_empregos'] = dados_setor['impacto_producao'] * 0.02  # Aproximação empregos
        dados_setor['impacto_empresas'] = dados_setor['impacto_producao'] * 0.01  # Aproximação empresas

        resultados.append(dados_setor)

    df_resultados = pd.concat(resultados, ignore_index=True)

    return df_resultados, impactos_setoriais

# ==============================================================================
# COMPONENTES DE INTERFACE ELEGANTES
# ==============================================================================

def criar_cabecalho_elegante():
    """Cria cabeçalho compacto e discreto"""
    st.markdown("""
    <div style="
        text-align: center;
        margin: 0.5rem 0 1rem 0;
        padding: 0.75rem;
    ">
        <h1 style="
            font-size: 1.75rem;
            font-weight: 600;
            color: #1e293b;
            margin: 0 0 0.25rem 0;
            line-height: 1.3;
        ">
            🗺️ Simulador de Choque - Marcelo CP2B
        </h1>
        <p style="
            font-size: 0.875rem;
            color: #64748b;
            margin: 0;
            line-height: 1.4;
        ">
            Simulação de impactos econômicos nas 133 regiões do Brasil • Modelo Input-Output de Leontief
        </p>
    </div>
    """, unsafe_allow_html=True)

def criar_controles_simulacao_sidebar(df_economia):
    """Cria controles de simulação elegantes e compactos para sidebar"""

    # Verificar se uma região foi selecionada
    if st.session_state.regiao_ativa is None:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #f8fafc, #e2e8f0);
            border-radius: 12px;
            padding: 2rem;
            border: 2px dashed #94a3b8;
            text-align: center;
            margin-bottom: 1rem;
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem; animation: pulse 2s infinite;">👆</div>
            <h3 style="color: #1e293b; margin-bottom: 1rem;">Como começar sua simulação</h3>
            <div style="text-align: left; max-width: 280px; margin: 0 auto;">
                <div style="display: flex; align-items: center; margin-bottom: 0.75rem;">
                    <span style="background: #3b82f6; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; margin-right: 0.75rem; font-weight: bold;">1</span>
                    <span style="color: #374151; font-size: 0.875rem;">Clique em uma região no mapa</span>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 0.75rem;">
                    <span style="background: #10b981; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; margin-right: 0.75rem; font-weight: bold;">2</span>
                    <span style="color: #374151; font-size: 0.875rem;">Escolha o setor econômico</span>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 0.75rem;">
                    <span style="background: #f59e0b; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; margin-right: 0.75rem; font-weight: bold;">3</span>
                    <span style="color: #374151; font-size: 0.875rem;">Defina o valor do investimento</span>
                </div>
                <div style="display: flex; align-items: center;">
                    <span style="background: #8b5cf6; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; margin-right: 0.75rem; font-weight: bold;">4</span>
                    <span style="color: #374151; font-size: 0.875rem;">Execute e veja os resultados</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Informações adicionais sobre o modelo
        st.markdown("""
        <div style="
            background: white;
            border-radius: 8px;
            padding: 1rem;
            border-left: 4px solid #3b82f6;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px -1px rgb(0 0 0 / 0.1);
        ">
            <h4 style="color: #1e293b; margin: 0 0 0.5rem 0; font-size: 0.9rem;">💡 Sobre o modelo</h4>
            <p style="color: #64748b; margin: 0; font-size: 0.8rem; line-height: 1.4;">
                Utilizamos o modelo Input-Output de Leontief para calcular os <strong>impactos econômicos diretos, indiretos e induzidos</strong>
                do seu investimento em todas as 133 regiões intermediárias do Brasil.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Dados da região selecionada
    dados_regiao = df_economia[df_economia['regiao'] == st.session_state.regiao_ativa].copy()

    # Cabeçalho elegante da simulação
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px 12px 0 0;
        margin-bottom: 0;
        font-weight: 600;
    ">
        🚀 Simulação: {st.session_state.regiao_ativa}
    </div>
    <div style="
        background: white;
        border: 1px solid #e2e8f0;
        border-top: none;
        border-radius: 0 0 12px 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    ">
    """, unsafe_allow_html=True)

    # Seleção do setor - mais compacta
    st.markdown("**🏭 Setor do Investimento**")
    opcoes_setores = [f"{metadados_setores[setor]['emoji']} {setor}"
                     for setor in setores]

    setor_idx = st.selectbox(
        "Escolha o setor:",
        options=range(len(setores)),
        format_func=lambda x: opcoes_setores[x],
        key='setor_simulacao_sidebar',
        label_visibility="collapsed"
    )

    setor_selecionado = setores[setor_idx]
    multiplicador = matriz_L_df.sum(axis=0)[setor_selecionado]

    # Info compacta do multiplicador
    st.markdown(f"""
    <div style="
        background: #f1f5f9;
        padding: 0.5rem 0.75rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        font-size: 0.875rem;
        color: #334155;
    ">
        <strong>Multiplicador:</strong> {multiplicador:.2f}x
    </div>
    """, unsafe_allow_html=True)

    # Valor do investimento - layout refinado
    st.markdown("**💰 Valor do Investimento**")
    vab_setor = dados_regiao[dados_regiao['setor'] == setor_selecionado]['vab'].iloc[0]

    percentual_choque = st.slider(
        "% do VAB setorial:",
        min_value=0.1,
        max_value=50.0,
        value=10.0,
        step=0.1,
        format="%.1f%%",
        key='slider_investimento'
    )

    valor_choque = vab_setor * (percentual_choque / 100.0)

    # Informações de valor em cards compactos
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="
            background: #ecfdf5;
            border: 1px solid #86efac;
            padding: 0.75rem;
            border-radius: 8px;
            text-align: center;
        ">
            <div style="font-size: 1.25rem; font-weight: bold; color: #166534;">R$ {valor_choque:,.1f}M</div>
            <div style="font-size: 0.75rem; color: #15803d;">Investimento</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="
            background: #fef3c7;
            border: 1px solid #fcd34d;
            padding: 0.75rem;
            border-radius: 8px;
            text-align: center;
        ">
            <div style="font-size: 1.25rem; font-weight: bold; color: #92400e;">R$ {vab_setor:,.1f}M</div>
            <div style="font-size: 0.75rem; color: #a16207;">VAB Base</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Botão de simulação elegante
    if st.button("🚀 **EXECUTAR SIMULAÇÃO**", type="primary", use_container_width=True):
        with st.spinner("🔄 Calculando impactos..."):
            resultados, impactos_setoriais = executar_simulacao_avancada(
                df_economia, valor_choque, setor_selecionado
            )

            # Incrementar contador de simulações
            st.session_state.contador_simulacoes += 1

            # Cores para diferentes simulações
            cores_simulacao = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF', '#5F27CD']
            cor_simulacao = cores_simulacao[(st.session_state.contador_simulacoes - 1) % len(cores_simulacao)]

            # Criar nova simulação
            nova_simulacao = {
                'id': f'sim_{st.session_state.contador_simulacoes:03d}',
                'nome': f'Simulação {st.session_state.contador_simulacoes}: {metadados_setores[setor_selecionado]["emoji"]} {setor_selecionado} em {st.session_state.regiao_ativa}',
                'regiao': st.session_state.regiao_ativa,
                'setor': setor_selecionado,
                'valor': valor_choque,
                'percentual_vab': percentual_choque,
                'timestamp': datetime.now(),
                'resultados': resultados,
                'parametros': {
                    'regiao_origem': st.session_state.regiao_ativa,
                    'setor_investimento': setor_selecionado,
                    'valor_investimento': valor_choque,
                    'percentual_vab': percentual_choque,
                    'multiplicador_usado': multiplicador,
                    'timestamp': datetime.now()
                },
                'cor': cor_simulacao,
                'ativa': True
            }

            # Adicionar à lista de simulações
            st.session_state.simulacoes.append(nova_simulacao)

            st.success(f"✅ Simulação {st.session_state.contador_simulacoes} executada!")
            st.balloons()
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def gerenciar_simulacoes():
    """Interface para gerenciar múltiplas simulações"""
    if len(st.session_state.simulacoes) == 0:
        return

    st.markdown("### 📊 Minhas Simulações")

    # Estatísticas gerais
    total_investimento = sum(sim['valor'] for sim in st.session_state.simulacoes if sim['ativa'])
    simulacoes_ativas = sum(1 for sim in st.session_state.simulacoes if sim['ativa'])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="
            background: #ecfdf5;
            border: 1px solid #86efac;
            padding: 0.5rem;
            border-radius: 6px;
            text-align: center;
        ">
            <div style="font-size: 1rem; font-weight: bold; color: #166534;">{len(st.session_state.simulacoes)}</div>
            <div style="font-size: 0.7rem; color: #15803d;">Total</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="
            background: #dbeafe;
            border: 1px solid #60a5fa;
            padding: 0.5rem;
            border-radius: 6px;
            text-align: center;
        ">
            <div style="font-size: 1rem; font-weight: bold; color: #1d4ed8;">{simulacoes_ativas}</div>
            <div style="font-size: 0.7rem; color: #2563eb;">Ativas</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Lista de simulações
    for i, sim in enumerate(st.session_state.simulacoes):
        with st.expander(f"{'✅' if sim['ativa'] else '❌'} {sim['nome'][:40]}...", expanded=False):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"""
                **📍 Região:** {sim['regiao']}
                **🏭 Setor:** {sim['setor']}
                **💰 Investimento:** R$ {sim['valor']:,.1f} Mi
                **📅 Criada:** {sim['timestamp'].strftime('%H:%M:%S')}
                """)

            with col2:
                # Toggle ativo/inativo
                nova_ativacao = st.checkbox("Mostrar no mapa", value=sim['ativa'], key=f"toggle_{sim['id']}")
                if nova_ativacao != sim['ativa']:
                    st.session_state.simulacoes[i]['ativa'] = nova_ativacao
                    st.rerun()

                # Botão deletar
                if st.button("🗑️", key=f"delete_{sim['id']}", help="Deletar simulação"):
                    st.session_state.simulacoes.pop(i)
                    st.rerun()

    # Dashboard de comparação entre simulações ativas
    simulacoes_ativas = [sim for sim in st.session_state.simulacoes if sim['ativa']]
    if len(simulacoes_ativas) >= 2:
        st.markdown("---")
        criar_dashboard_comparacao_simulacoes(simulacoes_ativas)

    # Funcionalidades avançadas
    if len(st.session_state.simulacoes) > 0:
        st.markdown("---")
        criar_funcionalidades_avancadas()

def criar_funcionalidades_avancadas():
    """Implementa funcionalidades avançadas: export, cenários predefinidos, etc."""
    st.markdown("### ⚙️ Funcionalidades Avançadas")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📤 Exportar Resultados")

        if st.button("📊 Exportar Relatório Completo", use_container_width=True):
            relatorio_completo = gerar_relatorio_completo()
            st.download_button(
                label="📥 Download Relatório (CSV)",
                data=relatorio_completo,
                file_name=f"relatorio_simulacoes_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

        if len([sim for sim in st.session_state.simulacoes if sim['ativa']]) >= 2:
            if st.button("📈 Exportar Comparação", use_container_width=True):
                comparacao_data = gerar_comparacao_export()
                st.download_button(
                    label="📥 Download Comparação (CSV)",
                    data=comparacao_data,
                    file_name=f"comparacao_simulacoes_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

    with col2:
        st.markdown("#### 🎯 Cenários Predefinidos")

        cenarios = {
            "Energia Renovável - Nordeste": {
                "regiao": "Recife",
                "setor": "Eletricidade, gás, água e esgoto",
                "valor": 5000.0,
                "descricao": "Investimento em energia renovável no Nordeste"
            },
            "Agronegócio - Centro-Oeste": {
                "regiao": "Campo Grande",
                "setor": "Agropecuária",
                "valor": 3000.0,
                "descricao": "Expansão do agronegócio no Centro-Oeste"
            },
            "Tecnologia - São Paulo": {
                "regiao": "São Paulo",
                "setor": "Serviços",
                "valor": 8000.0,
                "descricao": "Hub tecnológico em São Paulo"
            },
            "Infraestrutura - Norte": {
                "regiao": "Manaus",
                "setor": "Construção",
                "valor": 4000.0,
                "descricao": "Desenvolvimento de infraestrutura na Amazônia"
            }
        }

        cenario_selecionado = st.selectbox(
            "Escolha um cenário:",
            list(cenarios.keys()),
            help="Cenários predefinidos para análise rápida"
        )

        if st.button("🚀 Aplicar Cenário", use_container_width=True):
            cenario = cenarios[cenario_selecionado]

            # Configurar parâmetros do cenário
            st.session_state.regiao_ativa = cenario["regiao"]

            # Simular o cenário
            simular_cenario_predefinido(cenario)
            st.success(f"✅ Cenário '{cenario_selecionado}' aplicado com sucesso!")
            st.rerun()

        # Mostrar detalhes do cenário selecionado
        if cenario_selecionado:
            cenario = cenarios[cenario_selecionado]
            st.markdown(f"""
            <div style="
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                padding: 0.75rem;
                border-radius: 6px;
                margin-top: 0.5rem;
            ">
                <div style="font-size: 0.8rem; font-weight: bold; color: #374151; margin-bottom: 0.25rem;">
                    {cenario['descricao']}
                </div>
                <div style="font-size: 0.7rem; color: #6b7280;">
                    📍 {cenario['regiao']} • 🏭 {cenario['setor']} • 💰 R$ {cenario['valor']:,.1f}M
                </div>
            </div>
            """, unsafe_allow_html=True)

def gerar_relatorio_completo():
    """Gera relatório completo de todas as simulações para export"""
    relatorio_data = []

    for sim in st.session_state.simulacoes:
        resultados = sim['resultados']
        total_impacto = resultados['impacto_producao'].sum()
        total_empregos = resultados['impacto_empregos'].sum()

        # Agregar por região
        impactos_por_regiao = resultados.groupby('regiao').agg({
            'impacto_producao': 'sum',
            'impacto_empregos': 'sum'
        }).reset_index()

        for _, row in impactos_por_regiao.iterrows():
            relatorio_data.append({
                'simulacao_id': sim['id'],
                'simulacao_nome': sim['nome'],
                'regiao_origem': sim['regiao'],
                'setor_investimento': sim['setor'],
                'valor_investimento': sim['valor'],
                'timestamp': sim['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                'regiao_impactada': row['regiao'],
                'impacto_producao': row['impacto_producao'],
                'impacto_empregos': row['impacto_empregos'],
                'multiplicador_efetivo': total_impacto / sim['valor'],
                'participacao_impacto': (row['impacto_producao'] / total_impacto) * 100
            })

    df_relatorio = pd.DataFrame(relatorio_data)
    return df_relatorio.to_csv(index=False)

def gerar_comparacao_export():
    """Gera dados de comparação entre simulações ativas para export"""
    simulacoes_ativas = [sim for sim in st.session_state.simulacoes if sim['ativa']]

    comparacao_data = []
    for sim in simulacoes_ativas:
        total_impacto = sim['resultados']['impacto_producao'].sum()
        total_empregos = sim['resultados']['impacto_empregos'].sum()

        comparacao_data.append({
            'simulacao_nome': sim['nome'],
            'regiao_origem': sim['regiao'],
            'setor': sim['setor'],
            'investimento_milhoes': sim['valor'],
            'impacto_total_milhoes': total_impacto,
            'empregos_gerados': total_empregos,
            'multiplicador_efetivo': total_impacto / sim['valor'],
            'eficiencia_empregos': total_empregos / sim['valor'],
            'timestamp': sim['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            'cor_visualizacao': sim['cor']
        })

    df_comparacao = pd.DataFrame(comparacao_data)
    return df_comparacao.to_csv(index=False)

def simular_cenario_predefinido(cenario):
    """Executa simulação com parâmetros predefinidos do cenário"""
    # Buscar dados da região do cenário
    dados_regiao = df_economia[df_economia['regiao'] == cenario['regiao']].copy()

    if dados_regiao.empty:
        st.error(f"Região '{cenario['regiao']}' não encontrada nos dados.")
        return

    # Encontrar setor mais próximo
    setores_disponiveis = dados_regiao['setor'].unique()
    setor_encontrado = None

    for setor in setores_disponiveis:
        if cenario['setor'].lower() in setor.lower() or setor.lower() in cenario['setor'].lower():
            setor_encontrado = setor
            break

    if not setor_encontrado:
        # Usar primeiro setor disponível como fallback
        setor_encontrado = setores_disponiveis[0]

    # Executar simulação
    resultados = simular_choque_economico(
        regiao_origem=cenario['regiao'],
        setor_investimento=setor_encontrado,
        valor_investimento=cenario['valor']
    )

    if resultados is not None:
        # Gerar cor única para o cenário
        cores_disponiveis = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
        cor_simulacao = cores_disponiveis[len(st.session_state.simulacoes) % len(cores_disponiveis)]

        # Adicionar à lista de simulações
        nova_simulacao = {
            'id': f'cenario_{st.session_state.contador_simulacoes:03d}',
            'nome': f'Cenário {st.session_state.contador_simulacoes}: {setor_encontrado} em {cenario["regiao"]}',
            'regiao': cenario['regiao'],
            'setor': setor_encontrado,
            'valor': cenario['valor'],
            'timestamp': datetime.now(),
            'resultados': resultados,
            'cor': cor_simulacao,
            'ativa': True
        }

        st.session_state.simulacoes.append(nova_simulacao)
        st.session_state.contador_simulacoes += 1

        # Atualizar resultados atuais
        st.session_state.resultados_simulacao = resultados
        st.session_state.parametros_simulacao = {
            'regiao_origem': cenario['regiao'],
            'setor_investimento': setor_encontrado,
            'valor_investimento': cenario['valor'],
            'percentual_vab': (cenario['valor'] / dados_regiao[dados_regiao['setor'] == setor_encontrado]['vab'].sum()) * 100,
            'multiplicador_usado': resultados['impacto_producao'].sum() / cenario['valor'],
            'timestamp': datetime.now()
        }

def criar_dashboard_comparacao_simulacoes(simulacoes_ativas):
    """Cria dashboard de comparação entre múltiplas simulações ativas"""
    st.markdown("### 📊 Comparação entre Simulações")

    # Preparar dados para comparação
    dados_comparacao = []
    for sim in simulacoes_ativas:
        total_impacto = sim['resultados']['impacto_producao'].sum()
        total_empregos = sim['resultados']['impacto_empregos'].sum()
        top_regiao = sim['resultados'].groupby('regiao')['impacto_producao'].sum().idxmax()
        top_impacto_regiao = sim['resultados'].groupby('regiao')['impacto_producao'].sum().max()

        dados_comparacao.append({
            'nome': sim['nome'][:25] + '...' if len(sim['nome']) > 25 else sim['nome'],
            'setor': sim['setor'],
            'regiao_origem': sim['regiao'],
            'investimento': sim['valor'],
            'impacto_total': total_impacto,
            'empregos_total': total_empregos,
            'multiplicador_efetivo': total_impacto / sim['valor'],
            'top_regiao': top_regiao,
            'top_impacto': top_impacto_regiao,
            'cor': sim['cor']
        })

    df_comp = pd.DataFrame(dados_comparacao)

    # Métricas de comparação em cards
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div style="
            background: #f0f9ff;
            border: 1px solid #0ea5e9;
            padding: 0.75rem;
            border-radius: 8px;
            text-align: center;
        ">
            <div style="font-size: 1.1rem; font-weight: bold; color: #0369a1;">
                R$ {df_comp['impacto_total'].sum():,.1f}M
            </div>
            <div style="font-size: 0.8rem; color: #0284c7;">Impacto Total Combinado</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="
            background: #f0fdf4;
            border: 1px solid #22c55e;
            padding: 0.75rem;
            border-radius: 8px;
            text-align: center;
        ">
            <div style="font-size: 1.1rem; font-weight: bold; color: #15803d;">
                {df_comp['empregos_total'].sum():,.0f}
            </div>
            <div style="font-size: 0.8rem; color: #16a34a;">Empregos Combinados</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        mult_medio = df_comp['multiplicador_efetivo'].mean()
        st.markdown(f"""
        <div style="
            background: #fefce8;
            border: 1px solid #eab308;
            padding: 0.75rem;
            border-radius: 8px;
            text-align: center;
        ">
            <div style="font-size: 1.1rem; font-weight: bold; color: #a16207;">
                {mult_medio:.2f}x
            </div>
            <div style="font-size: 0.8rem; color: #ca8a04;">Multiplicador Médio</div>
        </div>
        """, unsafe_allow_html=True)

    # Gráfico de comparação de impactos
    fig_comp = px.bar(
        df_comp,
        x='nome',
        y='impacto_total',
        color='nome',
        title="Comparação de Impactos Totais por Simulação",
        labels={'impacto_total': 'Impacto Total (R$ Mi)', 'nome': 'Simulação'},
        color_discrete_sequence=[sim['cor'] for sim in simulacoes_ativas]
    )

    fig_comp.update_layout(
        height=350,
        showlegend=False,
        xaxis_tickangle=-45
    )

    st.plotly_chart(fig_comp, use_container_width=True)

    # Gráfico de eficiência (multiplicador efetivo)
    fig_mult = px.scatter(
        df_comp,
        x='investimento',
        y='multiplicador_efetivo',
        size='empregos_total',
        color='nome',
        title="Eficiência das Simulações (Multiplicador vs Investimento)",
        labels={
            'investimento': 'Investimento (R$ Mi)',
            'multiplicador_efetivo': 'Multiplicador Efetivo',
            'empregos_total': 'Empregos'
        },
        color_discrete_sequence=[sim['cor'] for sim in simulacoes_ativas],
        hover_data=['setor', 'regiao_origem']
    )

    fig_mult.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig_mult, use_container_width=True)

    # Tabela de comparação detalhada
    st.markdown("#### 📋 Comparação Detalhada")

    df_display = df_comp[['nome', 'setor', 'regiao_origem', 'investimento', 'impacto_total',
                         'empregos_total', 'multiplicador_efetivo', 'top_regiao']].copy()

    df_display.columns = ['Simulação', 'Setor', 'Região Origem', 'Investimento (R$ Mi)',
                         'Impacto Total (R$ Mi)', 'Empregos', 'Multiplicador', 'Top Região Impactada']

    # Formatação da tabela
    styled_df = df_display.style.format({
        'Investimento (R$ Mi)': '{:,.1f}',
        'Impacto Total (R$ Mi)': '{:,.1f}',
        'Empregos': '{:,.0f}',
        'Multiplicador': '{:.2f}x'
    })

    st.dataframe(styled_df, use_container_width=True, hide_index=True)

    # Análise de convergência regional
    if len(simulacoes_ativas) >= 2:
        st.markdown("#### 🎯 Análise de Convergência Regional")

        # Verificar se há simulações na mesma região
        regioes_origem = df_comp['regiao_origem'].tolist()
        regioes_repetidas = [r for r in set(regioes_origem) if regioes_origem.count(r) > 1]

        if regioes_repetidas:
            st.markdown(f"**⚠️ Concentração detectada:** {len(regioes_repetidas)} região(ões) com múltiplas simulações")
            for regiao in regioes_repetidas:
                sims_regiao = [s for s in simulacoes_ativas if s['regiao'] == regiao]
                st.markdown(f"- **{regiao}:** {len(sims_regiao)} simulações")
        else:
            st.markdown("**✅ Distribuição diversificada:** Cada simulação em região diferente")

def criar_dashboard_regiao_elegante(dados_regiao):
    """Cria dashboard econômico elegante para região selecionada"""

    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">
            <span>📊</span>
            <span>Perfil Econômico Regional</span>
        </h2>
    </div>
    """, unsafe_allow_html=True)

    # Métricas principais em cards elegantes
    col1, col2, col3 = st.columns(3)

    vab_total = dados_regiao['vab'].sum()
    empregos_total = dados_regiao['empregos'].sum()
    empresas_total = dados_regiao['empresas'].sum()

    with col1:
        st.markdown(f"""
        <div class="metric-card animate-fade-in">
            <div class="metric-icon">💰</div>
            <div class="metric-value">R$ {vab_total:,.0f}M</div>
            <div class="metric-label">VAB Total</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card animate-fade-in" style="animation-delay: 0.1s;">
            <div class="metric-icon">👥</div>
            <div class="metric-value">{empregos_total:,.0f}</div>
            <div class="metric-label">Empregos</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card animate-fade-in" style="animation-delay: 0.2s;">
            <div class="metric-icon">🏢</div>
            <div class="metric-value">{empresas_total:,.0f}</div>
            <div class="metric-label">Empresas</div>
        </div>
        """, unsafe_allow_html=True)

    # Gráfico de composição setorial elegante
    st.markdown("""
    <div class="section-header" style="margin-top: 2rem;">
        <h3 class="section-title">
            <span>📈</span>
            <span>Composição Setorial por VAB</span>
        </h3>
    </div>
    """, unsafe_allow_html=True)

    cores_setores = [metadados_setores[setor]['cor'] for setor in dados_regiao['setor']]

    fig = px.pie(
        dados_regiao,
        values='vab',
        names='setor',
        title="",
        color_discrete_sequence=cores_setores,
        hover_data=['empregos', 'empresas']
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>' +
                     'VAB: R$ %{value:,.0f} Mi<br>' +
                     'Empregos: %{customdata[0]:,.0f}<br>' +
                     'Empresas: %{customdata[1]:,.0f}<br>' +
                     '<extra></extra>'
    )

    fig.update_layout(
        height=400,
        font=dict(size=13, family="Inter, sans-serif"),
        margin=dict(t=30, b=30, l=30, r=30),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )

    # Wrap the chart in a card
    st.markdown('<div class="card" style="padding: 1rem; margin: 1rem 0;">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

def criar_secao_validacao_modelo():
    """Cria seção de validação e parâmetros do modelo"""

    st.markdown("""
    <div class="section-header">
        <h2 class="section-title">
            <span>🔬</span>
            <span>Validação e Parâmetros do Modelo</span>
        </h2>
    </div>
    """, unsafe_allow_html=True)

    # Tabs para organizar informações técnicas
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Matriz Leontief", "⚙️ Parâmetros", "📈 Multiplicadores", "🎯 Metodologia"])

    with tab1:
        st.markdown("""
        <div class="card">
            <div class="card-header">
                <span>📊</span>
                <span>Matriz de Impactos (I - A)⁻¹</span>
            </div>
            <div class="card-body">
                <p style="color: var(--gray-600); margin-bottom: 1.5rem;">
                    Mostra quanto cada setor produz para atender uma unidade de demanda final
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Exibir matriz L com formatação elegante
        matriz_styled = matriz_L_df.style.format("{:.3f}")
        st.dataframe(matriz_styled, use_container_width=True)

        st.markdown("""
        <div style="background: var(--primary-50); padding: 1rem; border-radius: var(--radius-md); margin-top: 1rem; border-left: 4px solid var(--primary-500);">
            <strong>📝 Interpretação:</strong> Cada célula (i,j) indica quanto o setor i precisa produzir para
            atender R$ 1 de demanda final do setor j, incluindo efeitos diretos e indiretos.
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.markdown("### Parâmetros Técnicos do Modelo")

        col1, col2 = st.columns(2)

        with col1:
            for key, value in list(parametros_modelo.items())[:4]:
                st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")

        with col2:
            for key, value in list(parametros_modelo.items())[4:]:
                st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")

        st.markdown("---")
        st.markdown("### 🌍 Cobertura Espacial")
        st.markdown("""
        - **Nível Geográfico:** Regiões Intermediárias (Divisão Regional do Brasil - IBGE, 2017)
        - **Abrangência:** Todo território nacional brasileiro
        - **Resolução:** 133 regiões intermediárias em 26 estados + DF
        """)

    with tab3:
        st.markdown("### Multiplicadores Setoriais")

        # Calcular multiplicadores reais da matriz
        multiplicadores_reais = matriz_L_df.sum(axis=0)

        # Criar gráfico de multiplicadores
        fig_mult = px.bar(
            x=multiplicadores_reais.index,
            y=multiplicadores_reais.values,
            title="Multiplicadores de Produção por Setor",
            labels={'x': 'Setor', 'y': 'Multiplicador'},
            color=multiplicadores_reais.values,
            color_continuous_scale='viridis'
        )

        fig_mult.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig_mult, use_container_width=True)

        # Tabela de multiplicadores com interpretação
        df_mult = pd.DataFrame({
            'Setor': multiplicadores_reais.index,
            'Multiplicador': multiplicadores_reais.values,
            'Interpretação': [f'R$ {mult:.2f} de produção total para cada R$ 1,00 investido'
                             for mult in multiplicadores_reais.values]
        })

        st.dataframe(df_mult, use_container_width=True, hide_index=True)

    with tab4:
        st.markdown("### 🎯 Metodologia do Modelo Input-Output")

        st.markdown("""
        #### Fundamentos Teóricos
        O modelo utiliza a **metodologia de Leontief** (Prêmio Nobel de Economia 1973) para análise de:

        - **🎯 Impactos Diretos:** Efeitos imediatos do investimento no setor de destino
        - **🔗 Impactos Indiretos:** Efeitos nas cadeias produtivas fornecedoras
        - **💫 Impactos Induzidos:** Efeitos do aumento da renda na economia

        #### Equação Fundamental
        ```
        X = (I - A)⁻¹ × Y
        ```
        Onde:
        - **X** = Vetor de produção total
        - **A** = Matriz de coeficientes técnicos
        - **Y** = Vetor de demanda final (investimento)
        - **(I - A)⁻¹** = Matriz de impactos de Leontief

        #### Processo de Cálculo
        1. **Choque inicial** aplicado no setor selecionado
        2. **Propagação** através da matriz de impactos
        3. **Distribuição espacial** baseada nos shares regionais
        4. **Agregação** dos resultados por região e setor
        """)

def criar_ranking_resultados_elegante(resultados_simulacao):
    """Cria ranking visual elegante de resultados com composição setorial"""

    st.markdown("""
    <div>
        🏆 RANKING DE IMPACTOS REGIONAIS
    </div>
    """, unsafe_allow_html=True)

    # Agregar por região
    resultados_agregados = resultados_simulacao.groupby('regiao')['impacto_producao'].sum().reset_index()
    top_10 = resultados_agregados.nlargest(10, 'impacto_producao')

    # Gráfico de barras horizontal para o top 10
    fig_ranking = px.bar(
        top_10,
        x='impacto_producao',
        y='regiao',
        orientation='h',
        title="Top 10 Regiões por Impacto Total na Produção",
        labels={'impacto_producao': 'Impacto (R$ Mi)', 'regiao': ''},
        color='impacto_producao',
        color_continuous_scale='Reds'
    )

    fig_ranking.update_layout(
        height=400,
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False
    )

    st.plotly_chart(fig_ranking, use_container_width=True)

    # Detalhamento setorial para cada região do top 5
    st.markdown("### 📊 Composição Setorial - Top 5 Regiões")

    top_5 = top_10.head(5)

    for i, row in top_5.iterrows():
        regiao = row['regiao']
        impacto_total = row['impacto_producao']

        # Dados setoriais da região
        dados_regiao = resultados_simulacao[resultados_simulacao['regiao'] == regiao]

        with st.expander(f"🥇 {regiao} - R$ {impacto_total:,.1f} Mi", expanded=(i == 0)):
            col1, col2 = st.columns([2, 1])

            with col1:
                # Gráfico de barras setorial
                cores_setores = [metadados_setores[setor]['cor'] for setor in dados_regiao['setor']]

                fig_setorial = px.bar(
                    dados_regiao,
                    x='setor',
                    y='impacto_producao',
                    title=f"Impacto por Setor - {regiao}",
                    color='setor',
                    color_discrete_sequence=cores_setores
                )

                fig_setorial.update_layout(height=250, showlegend=False)
                st.plotly_chart(fig_setorial, use_container_width=True)

            with col2:
                # Métricas da região
                total_empregos = dados_regiao['impacto_empregos'].sum()
                total_empresas = dados_regiao['impacto_empresas'].sum()

                st.metric("💼 Empregos Gerados", f"{total_empregos:,.0f}")
                st.metric("🏢 Empresas Impactadas", f"{total_empresas:,.0f}")

                # Setor mais impactado
                setor_max = dados_regiao.loc[dados_regiao['impacto_producao'].idxmax(), 'setor']
                st.info(f"**Setor líder:** {metadados_setores[setor_max]['emoji']} {setor_max}")

# ==============================================================================
# INTERFACE PRINCIPAL ELEGANTE
# ==============================================================================

def main():
    # Cabeçalho elegante
    criar_cabecalho_elegante()

    # Carregamento de dados
    gdf = carregar_dados_geograficos()
    if gdf is None:
        st.error("❌ Não foi possível carregar os dados geográficos.")
        st.stop()

    df_economia = gerar_dados_economicos(gdf)

    # Estado da sessão para sistema multi-simulação
    if 'regiao_ativa' not in st.session_state:
        st.session_state.regiao_ativa = None
    if 'simulacoes' not in st.session_state:
        st.session_state.simulacoes = []
    if 'contador_simulacoes' not in st.session_state:
        st.session_state.contador_simulacoes = 0

    # Manter compatibilidade com código existente
    # A simulação "ativa" é a última da lista ou None se não houver
    if len(st.session_state.simulacoes) > 0:
        st.session_state.resultados_simulacao = st.session_state.simulacoes[-1]['resultados']
        st.session_state.parametros_simulacao = st.session_state.simulacoes[-1]['parametros']
    else:
        st.session_state.resultados_simulacao = None
        st.session_state.parametros_simulacao = None

    # ============================================================================
    # NAVEGAÇÃO POR ABAS
    # ============================================================================
    tab1, tab2 = st.tabs(["🗺️ **Simulação Principal**", "🔬 **Validação Técnica**"])

    with tab1:
        # ABA PRINCIPAL - SIMULAÇÃO E MAPA
        simulacao_principal_tab(gdf, df_economia)

    with tab2:
        # ABA TÉCNICA - VALIDAÇÃO E PARÂMETROS
        criar_secao_validacao_modelo()

def simulacao_principal_tab(gdf, df_economia):
    """Aba principal com simulação e mapa"""

    # Layout principal 60/40 (60% mapa, 40% controles)
    col_esquerda, col_direita = st.columns([0.6, 0.4])

    # ==============================================================================
    # COLUNA ESQUERDA: MAPA E REGIÃO
    # ==============================================================================
    with col_esquerda:
        # Título simples do mapa
        st.markdown("### 🗺️ Mapa Interativo do Brasil")

        # Criar mapa
        mapa = folium.Map(
            location=[-15.0, -55.0],
            zoom_start=4,
            tiles="CartoDB positron",
            prefer_canvas=True
        )

        # Camadas de múltiplas simulações
        simulacoes_ativas = [sim for sim in st.session_state.simulacoes if sim['ativa']]

        if len(simulacoes_ativas) > 0:
            for i, simulacao in enumerate(simulacoes_ativas):
                # Agregar resultados por região para esta simulação
                resultados_agregados = simulacao['resultados'].groupby('regiao')['impacto_producao'].sum().reset_index()

                # Merge com geometrias
                gdf_com_dados = gdf.merge(
                    resultados_agregados,
                    left_on='NM_RGINT',
                    right_on='regiao',
                    how='left'
                ).fillna(0)

                # Choropleth para esta simulação com cor específica
                if gdf_com_dados['impacto_producao'].max() > 0:
                    # Converter cor hex para gradiente
                    import colorsys
                    hex_color = simulacao['cor'].lstrip('#')
                    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                    h, s, v = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)

                    # Criar gradiente baseado na cor da simulação
                    color_scale = ['#ffffff', simulacao['cor']]

                    choro = folium.Choropleth(
                        geo_data=gdf_com_dados,
                        data=gdf_com_dados,
                        columns=['NM_RGINT', 'impacto_producao'],
                        key_on='feature.properties.NM_RGINT',
                        fill_color='viridis',
                        fill_opacity=0.6 - (i * 0.1),  # Reduzir opacidade para sobreposições
                        line_opacity=0.4,
                        legend_name=f'{simulacao["nome"][:30]}... (R$ Mi)',
                        name=f'layer_{simulacao["id"]}'
                    )
                    choro.add_to(mapa)

            # Adicionar controle de layers se houver múltiplas simulações
            if len(simulacoes_ativas) > 1:
                folium.LayerControl(collapsed=False).add_to(mapa)

        # Camada de interação
        folium.GeoJson(
            gdf,
            style_function=lambda feature: {
                'fillColor': '#FFD700' if feature['properties']['NM_RGINT'] == st.session_state.regiao_ativa else 'transparent',
                'color': '#FF4500' if feature['properties']['NM_RGINT'] == st.session_state.regiao_ativa else '#333333',
                'weight': 4 if feature['properties']['NM_RGINT'] == st.session_state.regiao_ativa else 1,
                'fillOpacity': 0.7 if feature['properties']['NM_RGINT'] == st.session_state.regiao_ativa else 0,
                'opacity': 1
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['NM_RGINT'],
                aliases=['Região:'],
                localize=True,
                sticky=True,
                labels=True,
                style="background-color: white; border: 2px solid black; border-radius: 3px; box-shadow: 3px;"
            )
        ).add_to(mapa)

        # Renderizar mapa com altura maior para simetria visual
        map_data = st_folium(
            mapa,
            use_container_width=True,
            height=650,
            returned_objects=["last_object_clicked_tooltip"]
        )

        # Detecção de cliques
        if map_data and map_data.get('last_object_clicked_tooltip'):
            tooltip_data = map_data['last_object_clicked_tooltip']
            nova_regiao = None

            if isinstance(tooltip_data, dict):
                nova_regiao = tooltip_data.get('Região:')
            elif isinstance(tooltip_data, str):
                if 'Região:' in tooltip_data:
                    nova_regiao = tooltip_data.split('Região:')[1].strip()
                else:
                    nova_regiao = tooltip_data.strip()

            if nova_regiao and nova_regiao != st.session_state.regiao_ativa:
                st.session_state.regiao_ativa = nova_regiao
                st.rerun()

        # Perfil da região selecionada (se houver) - POSICIONADO ABAIXO DO MAPA
        if st.session_state.regiao_ativa is not None:
            st.markdown("---")
            dados_regiao = df_economia[df_economia['regiao'] == st.session_state.regiao_ativa]
            criar_dashboard_regiao_elegante(dados_regiao)

    # ==============================================================================
    # COLUNA DIREITA: CONTROLES E RESULTADOS
    # ==============================================================================
    with col_direita:
        # Botão Reset Tudo no topo (se houver simulações)
        if len(st.session_state.simulacoes) > 0:
            if st.button("🔄 **RESET TODAS SIMULAÇÕES**", type="secondary", use_container_width=True):
                # Reset sistema completo
                st.session_state.simulacoes = []
                st.session_state.contador_simulacoes = 0
                st.session_state.regiao_ativa = None
                st.session_state.resultados_simulacao = None
                st.session_state.parametros_simulacao = None
                st.success("✅ Todas as simulações foram removidas!")
                st.rerun()
            st.markdown("---")

        # Controles de simulação
        criar_controles_simulacao_sidebar(df_economia)

        # Interface de gerenciamento de simulações
        if len(st.session_state.simulacoes) > 0:
            st.markdown("---")
            gerenciar_simulacoes()

        # Exibição de resultados elegantes (se houver)
        if st.session_state.resultados_simulacao is not None:
            st.markdown("---")

            # Resumo dos parâmetros da simulação
            if st.session_state.parametros_simulacao:
                params = st.session_state.parametros_simulacao

                with st.expander("📋 **Parâmetros da Simulação Atual**", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**🎯 Região Origem:** {params['regiao_origem']}")
                        st.markdown(f"**🏭 Setor:** {params['setor_investimento']}")
                        st.markdown(f"**💰 Valor:** R$ {params['valor_investimento']:,.1f} Mi")
                    with col2:
                        st.markdown(f"**📊 % do VAB:** {params['percentual_vab']:.1f}%")
                        st.markdown(f"**⚡ Multiplicador:** {params['multiplicador_usado']:.2f}x")
                        st.markdown(f"**⏰ Executado:** {params['timestamp'].strftime('%H:%M:%S')}")

            # Métricas principais da simulação
            total_impacto = st.session_state.resultados_simulacao['impacto_producao'].sum()
            total_empregos = st.session_state.resultados_simulacao['impacto_empregos'].sum()

            st.markdown("""
            <div class="section-header">
                <h2 class="section-title">
                    <span>📈</span>
                    <span>Resultados da Simulação</span>
                </h2>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="metric-card animate-fade-in">
                    <div class="metric-icon">💰</div>
                    <div class="metric-value">R$ {total_impacto:,.1f}M</div>
                    <div class="metric-label">Impacto Total</div>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="metric-card animate-fade-in" style="animation-delay: 0.1s;">
                    <div class="metric-icon">👥</div>
                    <div class="metric-value">{total_empregos:,.0f}</div>
                    <div class="metric-label">Empregos Gerados</div>
                </div>
                """, unsafe_allow_html=True)

            # Análise por setor
            impactos_por_setor = st.session_state.resultados_simulacao.groupby('setor')['impacto_producao'].sum()

            st.markdown("### 📊 Distribuição de Impactos por Setor")

            cores_setores = [metadados_setores[setor]['cor'] for setor in impactos_por_setor.index]

            fig_setores = px.bar(
                x=impactos_por_setor.index,
                y=impactos_por_setor.values,
                title="Impacto na Produção por Setor (Brasil)",
                labels={'x': '', 'y': 'Impacto (R$ Mi)'},
                color=impactos_por_setor.index,
                color_discrete_sequence=cores_setores
            )

            fig_setores.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig_setores, use_container_width=True)

            # Ranking elegante
            st.markdown("### 🏆 Ranking de Regiões")
            criar_ranking_resultados_elegante(st.session_state.resultados_simulacao)


if __name__ == "__main__":
    main()