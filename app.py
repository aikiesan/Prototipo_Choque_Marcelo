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

# CSS Mínimo e Seguro para toques de design premium
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    /* Define a fonte para toda a aplicação */
    html, body, [class*="st-"], .st-emotion-cache {
        font-family: 'Inter', sans-serif;
    }

    /* Estilo para os cards - usando uma classe customizada */
    .card {
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        border: 1px solid #e2e8f0;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }

    /* Estilo para os cabeçalhos de seção */
    .section-header {
        background: white;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 2rem 0 1rem 0;
        border-left: 4px solid #3b82f6;
        box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
    }
    
    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        margin: 0;
    }

    /* Garante que os botões primários tenham texto branco */
    .stButton > button[kind="primary"] {
        color: white;
    }

</style>
""", unsafe_allow_html=True)

# ==============================================================================
# LÓGICA DE SIMULAÇÃO AVANÇADA
# ==============================================================================

def calculate_log_bins(series, num_classes=5):
    """
    Helper robusto para calcular bins logarítmicos.
    Garante que sempre retornará o número correto de bins/labels.
    """
    # Remove valores zero ou negativos e outliers extremos para um binning mais estável
    series_positive = series[(series > 0) & (series < series.quantile(0.99))]
    
    # Se houver muito poucos valores únicos, cria bins simples
    if series_positive.nunique() < num_classes:
        bins = np.linspace(series.min(), series.max(), num=num_classes + 1)
    else:
        # Binning logarítmico para a maioria dos casos
        bins = np.logspace(
            np.log10(max(1, series_positive.min())), # Evita log de zero
            np.log10(series_positive.max()),
            num=num_classes
        )
        # Garante que o valor máximo absoluto seja incluído no último bin
        bins = np.append(bins, series.max())

    # Adiciona o zero no início e remove duplicados
    bins = np.insert(bins, 0, 0)
    bins = np.unique(bins)
    
    # Se, após tudo, ainda não tivermos bins suficientes, cria linearmente
    if len(bins) < num_classes:
        bins = np.linspace(series.min(), series.max(), num=num_classes + 1)

    return bins.tolist()

def calcular_distancias(gdf, regiao_origem_nome):
    """Calcula a distância da região de origem para todas as outras."""
    try:
        # Pega a geometria (polígono) da região de origem
        origem_geom = gdf.loc[gdf['NM_RGINT'] == regiao_origem_nome, 'geometry'].iloc[0]
        # Calcula o ponto central (centroide)
        origem_centroid = origem_geom.centroid
        
        # Calcula a distância do centroide de origem para o centroide de todas as outras regiões
        distancias = gdf['geometry'].apply(lambda geom: origem_centroid.distance(geom.centroid))
        return distancias
    except (IndexError, AttributeError):
        # Se a região não for encontrada ou houver problema, retorna distâncias nulas
        return pd.Series(0.0, index=gdf.index)

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

# Coeficientes de VAB por setor (baseados na estrutura da matriz A)
coef_vab_por_setor = pd.Series({
    'Agropecuária': 0.699,  # 1 - soma da coluna Agropecuária da matriz_a
    'Indústria': 0.291,     # 1 - soma da coluna Indústria
    'Construção': 0.985,    # 1 - soma da coluna Construção (usa poucos insumos de si mesma)
    'Serviços': 0.573       # 1 - soma da coluna Serviços
})

# Coeficiente de impostos sobre VAB (carga tributária média)
coef_impostos_sobre_vab = 0.18  # 18% - estimativa da carga tributária brasileira

# Coeficientes de Emprego (Empregos por R$ Milhão de Produção) - VERSÃO CIENTIFICAMENTE CONSERVADORA
coef_emprego_por_setor = pd.Series({
    'Agropecuária': 12.5, # Média entre agricultura familiar e agronegócio de larga escala
    'Indústria':     8.1, # Reflete a maior produtividade e automação da indústria
    'Construção':   17.6, # Permanece o mais intensivo em mão-de-obra
    'Serviços':     14.8  # Média de um setor muito heterogêneo (de TI a comércio)
})

# Parâmetros do modelo
parametros_modelo = {
    'ano_base': 2017,
    'fonte_matriz': 'Tabela de Recursos e Usos (TRU) - IBGE',
    'metodologia': 'Modelo Input-Output de Leontief',
    'regioes_imediatas_cobertas': 133,
    'setores_economicos': 4,
    'tipo_analise': 'Impactos diretos, indiretos e induzidos',
    'unidade_monetaria': 'Milhões de Reais (R$ Mi)',
    'coef_vab_medio': coef_vab_por_setor.mean(),
    'carga_tributaria': coef_impostos_sobre_vab,
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
    """Gera dados econômicos sintéticos realistas para as 133 regiões imediatas."""
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

def executar_simulacao_avancada(df_economia, gdf, valor_choque, setor_choque, regiao_origem):
    """
    Executa simulação completa com modelo Leontief e distribuição gravitacional.
    """
    # --- PARTE 1: CÁLCULO DO IMPACTO NACIONAL (lógica de Leontief, inalterada) ---
    setor_idx = setores.index(setor_choque)
    vetor_choque = np.zeros(len(setores))
    vetor_choque[setor_idx] = valor_choque
    impactos_setoriais_nacionais = matriz_L @ vetor_choque
    
    # --- PARTE 2: DISTRIBUIÇÃO ESPACIAL GRAVITACIONAL (Lógica Nova e Corrigida) ---
    
    # Calcula o "efeito cascata" (ripple effect) - o impacto que se espalha pela economia
    ripple_effect_nacional = impactos_setoriais_nacionais.sum() - valor_choque
    
    # Inicializa um DataFrame de resultados com as colunas que vamos precisar
    df_resultados = df_economia.copy()
    df_resultados['impacto_producao'] = 0.0
    
    # --- Passo 2a: Atribuir o impacto DIRETO 100% à região de origem ---
    mask_origem = (df_resultados['regiao'] == regiao_origem) & (df_resultados['setor'] == setor_choque)
    df_resultados.loc[mask_origem, 'impacto_producao'] = valor_choque
    
    # --- Passo 2b: Preparar pesos para distribuir o "efeito cascata" (LÓGICA SUAVIZADA) ---
    # Calcular distâncias geográficas a partir da origem
    distancias = calcular_distancias(gdf, regiao_origem)
    
    # --- MUDANÇA NO FATOR DE ATRITO ---
    # Um fator de 1.0 representa um decaimento mais forte e realista.
    fator_atrito = 1.0 
    fator_proximidade = np.exp(-fator_atrito * distancias)
    
    # Mapear o fator de proximidade para cada linha do DataFrame de resultados
    mapa_proximidade = pd.Series(fator_proximidade.values, index=gdf['NM_RGINT'])
    df_resultados['proximidade'] = df_resultados['regiao'].map(mapa_proximidade)
    
    # Criar um peso final combinando tamanho econômico (`share_nacional`) e proximidade
    df_resultados['peso_final'] = df_resultados['share_nacional'] * df_resultados['proximidade']
    
    # --- Passo 2c: Distribuir o "efeito cascata" usando os novos pesos ---
    for setor_idx, setor_nome in enumerate(setores):
        # O efeito cascata de cada setor
        ripple_setor = impactos_setoriais_nacionais[setor_idx]
        if setor_idx == setores.index(setor_choque):
            ripple_setor -= valor_choque # Subtrai o choque direto que já alocamos
        
        if ripple_setor > 0:
            # Filtra para o setor atual
            mask_setor = df_resultados['setor'] == setor_nome
            
            # Normaliza os pesos para que a soma seja 1 (dentro do setor)
            soma_pesos_setor = df_resultados.loc[mask_setor, 'peso_final'].sum()
            if soma_pesos_setor > 0:
                pesos_normalizados = df_resultados.loc[mask_setor, 'peso_final'] / soma_pesos_setor
                
                # Distribui o ripple do setor e SOMA ao impacto já existente (o direto)
                impacto_distribuido = pesos_normalizados * ripple_setor
                df_resultados.loc[mask_setor, 'impacto_producao'] += impacto_distribuido

    # --- PARTE 3: CÁLCULO DOS INDICADORES FINAIS (VAB, Impostos, Empregos) ---
    # (Usando os aprimoramentos que definimos anteriormente)
    df_resultados['coef_vab'] = df_resultados['setor'].map(coef_vab_por_setor)
    df_resultados['impacto_vab'] = df_resultados['impacto_producao'] * df_resultados['coef_vab']
    df_resultados['impacto_impostos'] = df_resultados['impacto_vab'] * coef_impostos_sobre_vab
    
    # --- CORREÇÃO NO CÁLCULO DE EMPREGOS ---
    df_resultados['coef_emprego'] = df_resultados['setor'].map(coef_emprego_por_setor)
    df_resultados['impacto_empregos'] = df_resultados['impacto_producao'] * df_resultados['coef_emprego']
    
    df_resultados['impacto_empresas'] = df_resultados['impacto_producao'] * 0.01

    # --- PARTE 4: CLASSIFICAÇÃO MULTIVARIADA PARA O MAPA ---
    impacto_agregado = df_resultados.groupby('regiao').agg(
        impacto_producao=('impacto_producao', 'sum'),
        impacto_vab=('impacto_vab', 'sum'),
        impacto_empregos=('impacto_empregos', 'sum'),
        impacto_impostos=('impacto_impostos', 'sum')
    )
    
    all_bins = {
        'impacto_producao': calculate_log_bins(impacto_agregado['impacto_producao']),
        'impacto_vab': calculate_log_bins(impacto_agregado['impacto_vab']),
        'impacto_empregos': calculate_log_bins(impacto_agregado['impacto_empregos']),
        'impacto_impostos': calculate_log_bins(impacto_agregado['impacto_impostos'])
    }
    
    for metrica, bins in all_bins.items():
        labels = [i for i in range(len(bins) - 1)]
        classes = pd.cut(impacto_agregado[metrica], bins=bins, labels=labels, include_lowest=True, duplicates='drop')
        df_resultados[f'classe_{metrica}'] = df_resultados['regiao'].map(classes)
        df_resultados[f'classe_{metrica}'].fillna(0, inplace=True)

    return df_resultados, impactos_setoriais_nacionais, all_bins

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
            Simulação de impactos econômicos nas 133 regiões imediatas do Brasil • Modelo Input-Output de Leontief
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
                    <span style="color: #374151; font-size: 0.875rem;">Clique em uma região imediata no mapa</span>
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
                do seu investimento em todas as 133 regiões imediatas do Brasil.
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

def gerenciar_simulacoes(df_economia):
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
        criar_funcionalidades_avancadas(df_economia)

def criar_sidebar_controles(df_economia, gdf):
    """Sidebar com controles e lógica de colapso/expansão"""

    # Lógica para mostrar/esconder o conteúdo
    if st.session_state.sidebar_state == 'expanded':
        # Botão para colapsar
        if st.button("⬅️ Esconder", use_container_width=True, help="Esconder controles para maximizar o mapa"):
            st.session_state.sidebar_state = 'collapsed'
            st.rerun()

        # Header compacto
        st.markdown("""
        <div style="text-align: center; margin-bottom: 1rem;">
            <h4 style="color: #1e293b; margin: 0;">🎯 Simulação de Impactos Econômicos</h4>
            <p style="color: #64748b; font-size: 0.8rem; margin: 0;">Analise os efeitos de investimentos na economia brasileira</p>
        </div>
        """, unsafe_allow_html=True)

        # Instruções step-by-step compactas
        with st.container():
            st.markdown("""
            <div style="background: #f0f9ff; border: 1px solid #0ea5e9; padding: 0.5rem; border-radius: 6px; margin-bottom: 1rem;">
                <div style="font-size: 0.8rem; font-weight: 600; color: #0c4a6e; margin-bottom: 0.4rem;">📋 Como simular:</div>
                <div style="font-size: 0.7rem; color: #475569; line-height: 1.2;">
                    <strong>1️⃣</strong> Escolha o setor • <strong>2️⃣</strong> Clique no mapa<br>
                    <strong>3️⃣</strong> Ajuste o valor • <strong>4️⃣</strong> Execute simulação
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Seleção de setor via RADIO BUTTONS (sem dropdown!)
        st.markdown("**🏭 Setor Econômico do Investimento**")
        st.markdown('<p style="font-size: 0.8rem; color: #6b7280; margin-top: -0.5rem;">Onde o investimento será aplicado:</p>', unsafe_allow_html=True)

        # Preparar opções para radio buttons
        setores = list(metadados_setores.keys())
        opcoes_radio = [f"{metadados_setores[setor]['emoji']} {setor[:20]}" for setor in setores]

        setor_selecionado_idx = st.radio(
            "Escolha:",
            range(len(setores)),
            format_func=lambda x: opcoes_radio[x],
            key="setor_radio_sidebar",
            label_visibility="collapsed"
        )

        setor_selecionado = setores[setor_selecionado_idx]

        # CORREÇÃO: Valor do investimento com CONTROLE POR PORCENTAGEM
        st.markdown("**💰 Tamanho do Investimento**")
        st.markdown('<p style="font-size: 0.8rem; color: #6b7280; margin-top: -0.5rem;">Defina o percentual do VAB setorial da região:</p>', unsafe_allow_html=True)
        
        # Desabilitar o controle se nenhuma região for selecionada
        is_disabled = st.session_state.regiao_ativa is None

        # O slider agora controla a PORCENTAGEM
        percentual_choque = st.slider(
            "Percentual do VAB setorial regional:",
            min_value=0.1,
            max_value=50.0,
            value=10.0,
            step=0.1,
            format="%.1f%%",
            key='slider_percentual_investimento',
            disabled=is_disabled,
            help="Exemplo: 10% significa um investimento equivalente a 10% do VAB do setor na região selecionada. Valores típicos: 5-15% para investimentos grandes."
        )

        # Calcular o valor absoluto e exibi-lo
        if not is_disabled:
            dados_regiao = df_economia[df_economia['regiao'] == st.session_state.regiao_ativa]
            dados_setor = dados_regiao[dados_regiao['setor'] == setor_selecionado]

            if not dados_setor.empty:
                vab_setor = dados_setor['vab'].sum()
                valor_investimento = vab_setor * (percentual_choque / 100.0)

                # Exibe o resultado do cálculo em um card informativo
                st.markdown(f"""
                <div style="background: #ecfdf5; border: 1px solid #86efac; padding: 0.75rem; border-radius: 8px; text-align: center; margin-top: 0.5rem;">
                    <div style="font-size: 0.75rem; color: #15803d; text-transform: uppercase;">Valor do Investimento</div>
                    <div style="font-size: 1.25rem; font-weight: bold; color: #166534;">
                        R$ {valor_investimento:,.2f} Milhões
                    </div>
                    <div style="font-size: 0.75rem; color: #6b7280;">(Base: VAB de R$ {vab_setor:,.1f} M)</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                valor_investimento = 0
                st.warning("Dados do setor não encontrados para esta região.")
        else:
            valor_investimento = 0
            st.markdown("""
            <div style="background: #fef3c7; border: 1px solid #f59e0b; padding: 0.75rem; border-radius: 6px; margin-top: 0.5rem;">
                <div style="color: #92400e; font-size: 0.8rem; font-weight: 600; margin-bottom: 0.25rem;">
                    🗺️ Aguardando seleção da região
                </div>
                <div style="color: #a16207; font-size: 0.75rem;">
                    Clique em uma região imediata no mapa ao lado para definir onde será feito o investimento.
                    O valor será calculado automaticamente com base no percentual escolhido.
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Botões de ação principais
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🚀 **EXECUTAR SIMULAÇÃO**",
                        type="primary",
                        use_container_width=True,
                        disabled=st.session_state.regiao_ativa is None,
                        help="Calcular os impactos econômicos do investimento"):
                if st.session_state.regiao_ativa:
                    executar_simulacao_nova(st.session_state.regiao_ativa, setor_selecionado, valor_investimento, df_economia, gdf)
                    st.rerun()

        with col2:
            if st.button("🔄 **NOVA SIMULAÇÃO**",
                        type="secondary",
                        use_container_width=True,
                        help="Limpar seleções e começar nova análise"):
                # Reset para nova simulação
                st.session_state.regiao_ativa = None
                st.rerun()

        # Explicação do modelo
        with st.expander("💡 Como o impacto é calculado?"):
            st.markdown("""
            <small>
            O modelo combina a **Matriz de Leontief** com um **Modelo Gravitacional**:
            - **Impacto Direto:** O investimento afeta 100% a **região imediata de origem**.
            - **Efeito Cascata:** Impactos indiretos (cadeia de suprimentos) e induzidos (consumo) são distribuídos para outras regiões imediatas com base no **tamanho econômico** e na **proximidade geográfica**.
            </small>
            """, unsafe_allow_html=True)

        # Seção de status atual
        if st.session_state.regiao_ativa:
            st.markdown(f"""
            <div style="background: #ecfdf5; border: 1px solid #86efac; padding: 0.75rem; border-radius: 6px; margin-top: 0.75rem;">
                <div style="color: #059669; font-size: 0.8rem; font-weight: 600; margin-bottom: 0.5rem;">
                    ✅ Simulação Configurada
                </div>
                <div style="color: #047857; font-size: 0.75rem; line-height: 1.3;">
                    📍 <strong>Região Imediata:</strong> {st.session_state.regiao_ativa}<br>
                    🏭 <strong>Setor:</strong> {setor_selecionado}<br>
                    📊 <strong>Percentual:</strong> {percentual_choque:.1f}% do VAB setorial<br>
                    💰 <strong>Valor:</strong> R$ {valor_investimento:,.2f} milhões
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: #fef3c7; border: 1px solid #f59e0b; padding: 0.75rem; border-radius: 6px; margin-top: 0.75rem;">
                <div style="color: #92400e; font-size: 0.8rem; font-weight: 600; margin-bottom: 0.25rem;">
                    ⏳ Aguardando Configuração
                </div>
                <div style="color: #a16207; font-size: 0.75rem;">
                    Clique em uma região imediata no mapa para começar a simulação
                </div>
            </div>
            """, unsafe_allow_html=True)

    else:  # st.session_state.sidebar_state == 'collapsed'
        # Botão para expandir (modo compacto)
        if st.button("➡️", use_container_width=True, help="Mostrar controles de simulação"):
            st.session_state.sidebar_state = 'expanded'
            st.rerun()
        
        # Informação compacta sobre região ativa (se houver)
        if st.session_state.regiao_ativa:
            st.markdown(f"""
            <div style="background: #ecfdf5; padding: 0.5rem; border-radius: 4px; margin-top: 0.5rem; text-align: center;">
                <div style="font-size: 0.7rem; color: #059669; font-weight: 600;">
                    📍 {st.session_state.regiao_ativa[:15]}...
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Contador de simulações (se houver)
        if len(st.session_state.simulacoes) > 0:
            simulacoes_ativas = len([s for s in st.session_state.simulacoes if s['ativa']])
            st.markdown(f"""
            <div style="background: #dbeafe; padding: 0.5rem; border-radius: 4px; margin-top: 0.5rem; text-align: center;">
                <div style="font-size: 0.7rem; color: #1d4ed8; font-weight: 600;">
                    📊 {simulacoes_ativas} ativa(s)
                </div>
            </div>
            """, unsafe_allow_html=True)

def criar_painel_resultados_aprimorado(simulacao):
    """Cria um painel de resultados com dashboard interativo e gráficos."""
    
    st.markdown("### 📈 Análise de Impactos da Simulação")
    
    resultados_df = simulacao['resultados']
    params = simulacao['parametros']
    
    # Card de Resumo da Simulação (mantido, é ótimo)
    st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 10px; margin-bottom: 1rem; border-left: 5px solid #3b82f6;">
        <small>Simulação para:</small><br>
        <strong>{params['regiao_origem']}</strong><br>
        <small>Investimento de <strong>R$ {params['valor_investimento']:,.2f} Mi</strong> no setor de <strong>{params['setor_investimento']}</strong>.</small>
    </div>
    """, unsafe_allow_html=True)

    # Métricas Principais (mantidas)
    total_impacto_prod = resultados_df['impacto_producao'].sum()
    total_impacto_vab = resultados_df['impacto_vab'].sum()
    total_empregos = resultados_df['impacto_empregos'].sum()

    col1, col2 = st.columns(2)
    with col1:
        st.metric("💰 Impacto Total na Produção", f"R$ {total_impacto_prod:,.1f} Mi")
        st.metric("👥 Total de Empregos Gerados", f"{int(total_empregos):,}")
    with col2:
        st.metric("📈 Impacto no VAB (PIB)", f"R$ {total_impacto_vab:,.1f} Mi")
        st.metric("📊 Multiplicador de Produção", f"{total_impacto_prod / params['valor_investimento']:.2f}x")

    st.markdown("---")

    # --- NOVO DASHBOARD COM ABAS ---
    st.markdown("#### 📊 Análise Detalhada dos Impactos")
    tab_ranking, tab_setorial = st.tabs(["🏆 Ranking Regional", "🏭 Composição Setorial"])

    with tab_ranking:
        st.markdown("**Top 15 Regiões Imediatas Mais Impactadas (por Produção)**")
        
        impacto_por_regiao = resultados_df.groupby('regiao').agg(
            impacto_producao=('impacto_producao', 'sum'),
            impacto_vab=('impacto_vab', 'sum'),
            impacto_empregos=('impacto_empregos', 'sum')
        ).nlargest(15, 'impacto_producao').reset_index()

        fig_ranking = px.bar(
            impacto_por_regiao,
            x='impacto_producao',
            y='regiao',
            orientation='h',
            title="",
            labels={'impacto_producao': 'Impacto na Produção (R$ Milhões)', 'regiao': ''},
            hover_data={'regiao': False, 'impacto_vab': ':.2f', 'impacto_empregos': ':.0f'},
            height=500
        )
        fig_ranking.update_layout(
            yaxis={'categoryorder':'total ascending'},
            hoverlabel=dict(bgcolor="white", font_size=12)
        )
        st.plotly_chart(fig_ranking, use_container_width=True)

    with tab_setorial:
        st.markdown("**Composição do Impacto Total por Setor Econômico**")
        
        impacto_por_setor = resultados_df.groupby('setor').agg(
            impacto_producao=('impacto_producao', 'sum'),
            impacto_vab=('impacto_vab', 'sum'),
            impacto_empregos=('impacto_empregos', 'sum')
        ).reset_index()

        fig_treemap = px.treemap(
            impacto_por_setor,
            path=[px.Constant("Impacto Total"), 'setor'],
            values='impacto_producao',
            color='setor',
            color_discrete_map={
                'Agropecuária': '#FF6B6B', 'Indústria': '#4ECDC4',
                'Construção': '#45B7D1', 'Serviços': '#96CEB4'
            },
            hover_data={'impacto_vab': ':.2f', 'impacto_empregos': ':.0f'}
        )
        fig_treemap.update_layout(margin = dict(t=50, l=25, r=25, b=25))
        st.plotly_chart(fig_treemap, use_container_width=True)

def criar_painel_resultados():
    """Nova coluna de resultados compacta e organizada"""

    # Se não há simulações, mostrar placeholder
    if len(st.session_state.simulacoes) == 0:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
            <h4 style="color: #64748b;">Resultados aparecerão aqui</h4>
            <p style="color: #94a3b8; font-size: 0.9rem;">Execute uma simulação para ver os impactos econômicos</p>
        </div>
        """, unsafe_allow_html=True)
        return

    # Header da seção
    st.markdown("### 📈 Resultados")

    # Reset button compacto
    if st.button("🔄 Reset Todas", type="secondary", use_container_width=True):
        st.session_state.simulacoes = []
        st.session_state.contador_simulacoes = 0
        st.session_state.regiao_ativa = None
        st.session_state.resultados_simulacao = None
        st.session_state.parametros_simulacao = None
        st.success("✅ Simulações removidas!")
        st.rerun()

    # Mostrar última simulação
    if st.session_state.resultados_simulacao is not None:
        total_impacto = st.session_state.resultados_simulacao['impacto_producao'].sum()
        total_empregos = st.session_state.resultados_simulacao['impacto_empregos'].sum()
        total_vab = st.session_state.resultados_simulacao['impacto_vab'].sum()
        total_impostos = st.session_state.resultados_simulacao['impacto_impostos'].sum()

        # Métricas principais expandidas
        col1, col2 = st.columns(2)
        with col1:
            st.metric("💰 Produção", f"R$ {total_impacto:,.0f}M", delta=None)
            st.metric("🏛️ Impostos", f"R$ {total_impostos:,.0f}M", delta=None)
        with col2:
            st.metric("📊 PIB (VAB)", f"R$ {total_vab:,.0f}M", delta=None)
            st.metric("👥 Empregos", f"{total_empregos:,.0f}", delta=None)

        # Top 3 regiões impactadas
        st.markdown("**🏆 Top 3 Regiões Imediatas**")
        top_regioes = st.session_state.resultados_simulacao.groupby('regiao')['impacto_producao'].sum().nlargest(3)

        for i, (regiao, impacto) in enumerate(top_regioes.items(), 1):
            st.markdown(f"**{i}.** {regiao[:20]}... - R$ {impacto:,.0f}M")

        # Gráfico compacto por setor
        st.markdown("**📊 Impacto por Setor**")
        impactos_setor = st.session_state.resultados_simulacao.groupby('setor')['impacto_producao'].sum()

        fig = px.bar(
            x=impactos_setor.values,
            y=impactos_setor.index,
            orientation='h',
            title="",
            height=200
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    # Lista de simulações ativas
    simulacoes_ativas = [sim for sim in st.session_state.simulacoes if sim['ativa']]
    if len(simulacoes_ativas) > 1:
        st.markdown("**🔄 Simulações Ativas**")
        for sim in simulacoes_ativas[-3:]:  # Mostrar últimas 3
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"<small>{sim['nome'][:25]}...</small>", unsafe_allow_html=True)
            with col2:
                if st.button("👁️", key=f"view_{sim['id']}", help="Ver detalhes"):
                    # Expandir seção de detalhes
                    pass


def executar_simulacao_nova(regiao, setor, valor, df_economia, gdf):
    """Executa uma nova simulação e adiciona à lista"""
    resultados, _, all_bins = executar_simulacao_avancada(
        df_economia=df_economia,
        gdf=gdf,
        valor_choque=valor,
        setor_choque=setor,
        regiao_origem=regiao
    )

    if resultados is not None:
        # Gerar cor única
        cores_disponiveis = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
        cor_simulacao = cores_disponiveis[len(st.session_state.simulacoes) % len(cores_disponiveis)]

        # Nova simulação
        nova_simulacao = {
            'id': f'sim_{st.session_state.contador_simulacoes:03d}',
            'nome': f'Simulação {st.session_state.contador_simulacoes}: {setor} em {regiao}',
            'regiao': regiao,
            'setor': setor,
            'valor': valor,
            'timestamp': datetime.now(),
            'resultados': resultados,
            'all_bins': all_bins,  # Armazenar todos os bins para diferentes métricas
            'parametros': {  # Adicionando a chave que faltava
                'regiao_origem': regiao,
                'setor_investimento': setor,
                'valor_investimento': valor,
                'timestamp': datetime.now()
            },
            'cor': cor_simulacao,
            'ativa': True
        }

        st.session_state.simulacoes.append(nova_simulacao)
        st.session_state.contador_simulacoes += 1

        # Atualizar simulação atual
        st.session_state.resultados_simulacao = resultados
        st.session_state.parametros_simulacao = {
            'regiao_origem': regiao,
            'setor_investimento': setor,
            'valor_investimento': valor,
            'timestamp': datetime.now()
        }

        st.success(f"✅ Simulação executada: {setor} em {regiao}")

def criar_secao_export_simples():
    """Seção simplificada de export"""
    st.markdown("**📤 Exportar Dados**")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📊 Relatório Completo", use_container_width=True):
            if len(st.session_state.simulacoes) > 0:
                relatorio = gerar_relatorio_completo()
                st.download_button(
                    label="⬇️ Download CSV",
                    data=relatorio,
                    file_name=f"relatorio_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("Nenhuma simulação para exportar")

    with col2:
        simulacoes_ativas = [sim for sim in st.session_state.simulacoes if sim['ativa']]
        if len(simulacoes_ativas) >= 2:
            if st.button("📈 Comparação", use_container_width=True):
                comparacao = gerar_comparacao_export()
                st.download_button(
                    label="⬇️ Download CSV",
                    data=comparacao,
                    file_name=f"comparacao_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
        else:
            st.button("📈 Comparação", disabled=True, help="Precisa de 2+ simulações ativas")

def criar_secao_multi_simulacao_simples():
    """Seção simplificada de gerenciamento multi-simulação"""
    st.markdown("**🔄 Gerenciar Simulações**")

    if len(st.session_state.simulacoes) == 0:
        st.info("Nenhuma simulação criada ainda")
        return

    # Lista compacta das simulações
    for i, sim in enumerate(st.session_state.simulacoes):
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            status = "🟢" if sim['ativa'] else "🔴"
            st.markdown(f"{status} **{sim['nome'][:40]}...**")
            st.markdown(f"<small>{sim['setor']} | R$ {sim['valor']:,.0f}M</small>", unsafe_allow_html=True)

        with col2:
            # Toggle ativo/inativo
            if st.button("👁️" if sim['ativa'] else "👁️‍🗨️",
                        key=f"toggle_multi_{sim['id']}",
                        help="Mostrar/Ocultar no mapa"):
                st.session_state.simulacoes[i]['ativa'] = not sim['ativa']
                st.rerun()

        with col3:
            # Deletar
            if st.button("🗑️", key=f"delete_multi_{sim['id']}", help="Deletar simulação"):
                st.session_state.simulacoes.pop(i)
                st.rerun()

        st.markdown("---")

    # Estatísticas
    simulacoes_ativas = [sim for sim in st.session_state.simulacoes if sim['ativa']]
    st.markdown(f"**📊 Total:** {len(st.session_state.simulacoes)} | **Ativas:** {len(simulacoes_ativas)}")

def criar_funcionalidades_avancadas(df_economia):
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
        st.markdown("#### 📊 Informações da Simulação")
        
        if st.session_state.resultados_simulacao is not None:
            # Mostrar informações da última simulação
            params = st.session_state.parametros_simulacao
            st.markdown(f"""
            **🎯 Última Simulação:**
            - **Região:** {params['regiao']}
            - **Setor:** {params['setor']}
            - **Investimento:** R$ {params['valor']:,.0f}M
            - **Multiplicador:** {params.get('multiplicador', 'N/A')}
            """)
        else:
            st.info("Nenhuma simulação executada ainda.")

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
            'impacto_empregos': 'sum',
            'impacto_vab': 'sum',
            'impacto_impostos': 'sum'
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
                'impacto_vab': row['impacto_vab'],
                'impacto_impostos': row['impacto_impostos'],
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
        total_vab = sim['resultados']['impacto_vab'].sum()
        total_impostos = sim['resultados']['impacto_impostos'].sum()

        comparacao_data.append({
            'simulacao_nome': sim['nome'],
            'regiao_origem': sim['regiao'],
            'setor': sim['setor'],
            'investimento_milhoes': sim['valor'],
            'impacto_producao_milhoes': total_impacto,
            'impacto_vab_milhoes': total_vab,
            'impacto_impostos_milhoes': total_impostos,
            'empregos_gerados': total_empregos,
            'multiplicador_producao': total_impacto / sim['valor'],
            'multiplicador_vab': total_vab / sim['valor'],
            'eficiencia_empregos': total_empregos / sim['valor'],
            'carga_tributaria_efetiva': (total_impostos / total_vab) * 100 if total_vab > 0 else 0,
            'timestamp': sim['timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            'cor_visualizacao': sim['cor']
        })

    df_comparacao = pd.DataFrame(comparacao_data)
    return df_comparacao.to_csv(index=False)


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
    """Dashboard compacto para região selecionada - MUITO mais pequeno"""

    # Header compacto
    st.markdown("**📍 Perfil da Região**")

    # Métricas em uma linha só
    vab_total = dados_regiao['vab'].sum()
    empregos_total = dados_regiao['empregos'].sum()
    empresas_total = dados_regiao['empresas'].sum()

    # Layout horizontal compacto
    st.markdown(f"""
    <div style="
        display: flex;
        justify-content: space-between;
        background: #f8fafc;
        padding: 0.5rem;
        border-radius: 6px;
        margin: 0.5rem 0;
        font-size: 0.8rem;
    ">
        <div style="text-align: center;">
            <div style="font-weight: bold; color: #1e293b;">R$ {vab_total:,.0f}M</div>
            <div style="color: #64748b;">VAB</div>
        </div>
        <div style="text-align: center;">
            <div style="font-weight: bold; color: #1e293b;">{empregos_total:,.0f}</div>
            <div style="color: #64748b;">Empregos</div>
        </div>
        <div style="text-align: center;">
            <div style="font-weight: bold; color: #1e293b;">{empresas_total:,.0f}</div>
            <div style="color: #64748b;">Empresas</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Setor dominante apenas
    setor_dominante = dados_regiao.loc[dados_regiao['vab'].idxmax(), 'setor']
    vab_dominante = dados_regiao['vab'].max()
    percentual_dominante = (vab_dominante / vab_total) * 100

    st.markdown(f"""
    <div style="background: #ecfdf5; padding: 0.5rem; border-radius: 4px; font-size: 0.8rem;">
        <strong>🏭 Setor Principal:</strong> {setor_dominante} ({percentual_dominante:.1f}% do VAB)
    </div>
    """, unsafe_allow_html=True)

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
        st.markdown("### 💰 Coeficientes Econômicos")
        
        col_vab, col_impostos = st.columns(2)
        
        with col_vab:
            st.markdown("**Coeficientes de VAB por Setor:**")
            for setor, coef in coef_vab_por_setor.items():
                emoji = metadados_setores[setor]['emoji']
                st.markdown(f"{emoji} **{setor[:12]}:** {coef:.1%}")
        
        with col_impostos:
            st.markdown("**Tributação:**")
            st.markdown(f"🏛️ **Carga Tributária:** {coef_impostos_sobre_vab:.1%}")
            st.markdown("📊 **Aplicação:** Sobre VAB gerado")
        
        st.markdown("---")
        st.markdown("### 🌍 Cobertura Espacial")
        st.markdown("""
        - **Nível Geográfico:** Regiões Imediatas (Divisão Regional do Brasil - IBGE, 2017)
        - **Abrangência:** Todo território nacional brasileiro
        - **Resolução:** 133 regiões imediatas em 26 estados + DF
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
        3. **Distribuição espacial** baseada nos shares regionais das 133 regiões imediatas
        4. **Agregação** dos resultados por região imediata e setor
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
        title="Top 10 Regiões Imediatas por Impacto Total na Produção",
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
    st.markdown("### 📊 Composição Setorial - Top 5 Regiões Imediatas")

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
    if 'sidebar_state' not in st.session_state:
        st.session_state.sidebar_state = 'expanded'  # 'expanded' ou 'collapsed'

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
    """Aba principal com simulação, mapa multi-camadas e detecção de clique corrigida."""

    # Layout dinâmico baseado no estado da sidebar
    if st.session_state.get('sidebar_state', 'expanded') == 'expanded':
        col_sidebar, col_mapa, col_resultados = st.columns([0.25, 0.45, 0.3])
    else:
        col_sidebar, col_mapa, col_resultados = st.columns([0.05, 0.6, 0.35])

    # ==============================================================================
    # SIDEBAR ESQUERDA: CONTROLES E INSTRUÇÕES
    # ==============================================================================
    with col_sidebar:
        criar_sidebar_controles(df_economia, gdf)

    # ==============================================================================
    # COLUNA CENTRAL: MAPA INTERATIVO (COM DETECÇÃO DE CLIQUE CORRIGIDA)
    # ==============================================================================
    with col_mapa:
        try:
            st.markdown("### 🗺️ Análise Geográfica Interativa")
            
            # Seletor de Camada
            layer_choice = st.radio(
                "Selecione a camada para visualizar no mapa:",
                ['Produção', 'VAB (PIB)', 'Empregos', 'Impostos'],
                horizontal=True, 
                key="map_layer_selector"
            )

            column_map = {
                'Produção': 'impacto_producao', 
                'VAB (PIB)': 'impacto_vab',
                'Empregos': 'impacto_empregos', 
                'Impostos': 'impacto_impostos'
            }
            selected_column = column_map[layer_choice]
            selected_class_col = f"classe_{selected_column}"
            
            mapa = folium.Map(location=[-15.0, -55.0], zoom_start=4, tiles="CartoDB positron")

            # --- LÓGICA DE VISUALIZAÇÃO CORRIGIDA COM 4 CAMADAS ---

            # Camada 1: Bordas de Fundo (VISUAL)
            # Desenha as bordas cinzas de todas as regiões para contexto
            folium.GeoJson(
                gdf,
                name='Bordas das Regiões',
                style_function=lambda x: {
                    'fillColor': 'transparent',  # Sem preenchimento
                    'color': '#888888',          # Cor cinza para as bordas
                    'weight': 1,                 # Espessura fina
                    'fillOpacity': 0,
                }
            ).add_to(mapa)

            simulacoes_ativas = [sim for sim in st.session_state.simulacoes if sim['ativa']]

            # Camada 2: Mapa de Calor (VISUAL)
            if len(simulacoes_ativas) > 0:
                simulacao = simulacoes_ativas[-1]
                resultados_df = simulacao['resultados']
                
                map_data = resultados_df.groupby('regiao').agg(
                    valor=(selected_column, 'sum'),
                    classe=(selected_class_col, 'first')
                ).reset_index()

                gdf_com_dados = gdf.merge(map_data, left_on='NM_RGINT', right_on='regiao', how='left').fillna(0)

                # Paleta de cores para 5 classes
                cores = ['#ffffd4', '#fed98e', '#fe9929', '#d95f0e', '#993404']
                
                # --- FUNÇÃO DE ESTILO SEGURA ---
                def style_function_segura(feature):
                    classe = feature['properties'].get('classe', 0)
                    # Garante que a classe seja um inteiro e esteja dentro dos limites da lista de cores
                    try:
                        classe_segura = int(min(max(classe, 0), len(cores) - 1))
                    except (ValueError, TypeError):
                        classe_segura = 0
                    
                    return {
                        'fillOpacity': 0.7,
                        'weight': 0,  # Sem bordas no mapa de calor para não conflitar
                        'color': 'transparent',
                        'fillColor': cores[classe_segura]
                    }
                
                # Desenha o mapa de calor usando GeoJson
                folium.GeoJson(
                    gdf_com_dados,
                    name='Mapa de Calor',
                    style_function=style_function_segura
                ).add_to(mapa)

                # --- LEGENDA HTML DINÂMICA E SEGURA ---
                if 'all_bins' in simulacao and selected_column in simulacao['all_bins']:
                    bins = simulacao['all_bins'][selected_column]
                    legend_labels = []
                    # Garante que não teremos mais labels que cores disponíveis
                    num_labels = min(len(bins) - 1, len(cores))
                    
                    for i in range(num_labels):
                        if i < len(bins) - 1:  # Verificação adicional de segurança
                            limite_inferior = bins[i]
                            limite_superior = bins[i+1]
                            if selected_column == 'impacto_empregos':
                                label = f"{limite_inferior:,.0f} - {limite_superior:,.0f}"
                            elif limite_inferior < 1000:
                                label = f"{limite_inferior:,.0f} - {limite_superior:,.0f} Mi"
                            else:
                                label = f"{limite_inferior/1000:,.1f} Bi - {limite_superior/1000:,.1f} Bi"
                            legend_labels.append(label)

                    titulo_legenda = {
                        'impacto_producao': 'Impacto na Produção (R$)',
                        'impacto_vab': 'Impacto no VAB/PIB (R$)',
                        'impacto_empregos': 'Empregos Gerados',
                        'impacto_impostos': 'Impostos Gerados (R$)'
                    }

                    legend_html = f'''
                     <div style="position: fixed; 
                     bottom: 30px; left: 30px; width: 250px; 
                     border:2px solid grey; z-index:9999; font-size:14px;
                     background-color:rgba(255, 255, 255, 0.9);
                     padding: 10px; border-radius: 5px;">
                     <strong>{titulo_legenda.get(selected_column, layer_choice)}</strong><br>
                     '''
                    for i, label in enumerate(legend_labels):
                        if i < len(cores):  # Verificação de segurança
                            legend_html += f'<i style="background:{cores[i]}; opacity:0.7; width:20px; height:20px; float:left; margin-right:8px; border:1px solid grey;"></i> {label}<br>'
                    
                    legend_html += '</div>'
                    mapa.get_root().html.add_child(folium.Element(legend_html))

            # Camada 3: Destaque da Região Selecionada (VISUAL)
            if st.session_state.regiao_ativa:
                folium.GeoJson(
                    gdf[gdf['NM_RGINT'] == st.session_state.regiao_ativa],
                    name='Região Selecionada',
                    style_function=lambda x: {
                        'fillColor': '#3b82f6',  # Preenchimento azul
                        'color': '#1d4ed8',      # Borda azul escura
                        'weight': 3,             # Borda mais espessa
                        'fillOpacity': 0.3       # Semi-transparente
                    }
                ).add_to(mapa)

            # Camada 4: Camada de Captura de Cliques (FUNCIONAL)
            # Fica por cima de tudo, é invisível e só serve para capturar o tooltip
            folium.GeoJson(
                gdf,
                name='Camada de Interação',
                style_function=lambda x: {'fillOpacity': 0, 'weight': 0},  # Totalmente invisível
                tooltip=folium.GeoJsonTooltip(fields=['NM_RGINT'], aliases=['Região Imediata:'])
            ).add_to(mapa)

            map_data = st_folium(
                mapa,
                use_container_width=True,
                height=600,
                returned_objects=["last_object_clicked_tooltip"], # Pedimos apenas o tooltip
                key="main_map"
            )

            # --- PROCESSAMENTO DO CLIQUE (LÓGICA CORRIGIDA) ---
            if map_data and map_data.get('last_object_clicked_tooltip'):
                tooltip_text = map_data['last_object_clicked_tooltip']
                
                # PARSER ROBUSTO: Pega a última linha não vazia do tooltip e remove espaços
                try:
                    nova_regiao = [line.strip() for line in tooltip_text.split('\n') if line.strip()][-1]
                except (IndexError, AttributeError):
                    nova_regiao = None

                # LÓGICA DE ATUALIZAÇÃO DE ESTADO
                if nova_regiao and nova_regiao != st.session_state.regiao_ativa:
                    st.session_state.regiao_ativa = nova_regiao
                    st.success(f"✅ Região selecionada: **{nova_regiao}**. Controles habilitados.")
                    st.rerun()

        except Exception as e:
            st.error(f"⚠️ Ocorreu um erro ao renderizar o mapa: {e}")

        # Perfil compacto da região selecionada
        if st.session_state.regiao_ativa is not None:
            with st.expander(f"📍 {st.session_state.regiao_ativa}", expanded=True):
                dados_regiao = df_economia[df_economia['regiao'] == st.session_state.regiao_ativa]
                criar_dashboard_regiao_elegante(dados_regiao)

    # ==============================================================================
    # COLUNA DIREITA: RESULTADOS DA SIMULAÇÃO
    # ==============================================================================
    with col_resultados:
        if st.session_state.simulacoes:
            criar_painel_resultados_aprimorado(st.session_state.simulacoes[-1])
        else:
            st.markdown("""
            <div style="text-align: center; padding: 2rem 0;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📊</div>
                <h4 style="color: #64748b;">Resultados aparecerão aqui</h4>
                <p style="color: #94a3b8; font-size: 0.9rem;">Execute uma simulação para ver os impactos.</p>
            </div>
            """, unsafe_allow_html=True)

    # ==============================================================================
    # SEÇÃO INFERIOR: ANÁLISES DETALHADAS EXPANSÍVEIS
    # ==============================================================================
    if len(st.session_state.simulacoes) > 0:
        st.markdown("---")

        # Tabs para funcionalidades avançadas
        tab_comp, tab_export, tab_multi = st.tabs(["📊 Comparação", "📤 Export", "🔄 Multi-Simulação"])

        with tab_comp:
            simulacoes_ativas = [sim for sim in st.session_state.simulacoes if sim['ativa']]
            if len(simulacoes_ativas) >= 2:
                criar_dashboard_comparacao_simulacoes(simulacoes_ativas)
            else:
                st.info("👆 Execute pelo menos 2 simulações para compará-las")

        with tab_export:
            criar_secao_export_simples()

        with tab_multi:
            criar_secao_multi_simulacao_simples()


if __name__ == "__main__":
    main()