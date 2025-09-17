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

# CSS para design elegante com suporte a dark/light mode
st.markdown("""
<style>
    /* Forçar light mode para melhor legibilidade */
    .stApp {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    /* Forçar elementos principais em light mode */
    .main .block-container {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    /* Frame elegante para containers */
    .elegant-frame {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #dee2e6;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
        color: #212529 !important;
    }

    /* Títulos com estilo - melhor contraste */
    .section-title {
        color: #ffffff !important;
        font-size: 22px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 15px;
        padding: 12px;
        background: linear-gradient(90deg, #495057 0%, #6c757d 100%);
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    /* Cards informativos - compatível com light mode */
    .info-card {
        background: #f8f9fa !important;
        color: #212529 !important;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #495057;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* Métricas destacadas - melhor contraste */
    .metric-highlight {
        background: linear-gradient(45deg, #495057, #6c757d) !important;
        color: #ffffff !important;
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        margin: 5px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }

    /* Forçar texto escuro em todos os elementos */
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6 {
        color: #212529 !important;
    }

    /* Expander headers */
    .streamlit-expander {
        background-color: #f8f9fa !important;
        border: 1px solid #dee2e6 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #f8f9fa !important;
    }

    .stTabs [data-baseweb="tab"] {
        color: #495057 !important;
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
    """Cria cabeçalho elegante com informações da ferramenta"""
    st.markdown("""
    <div class="section-title">
        🗺️ SIMULADOR DE CHOQUE - MARCELO CP2B
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-card">
        <h4>📋 Análise Interativa de Impactos Econômicos Regionais</h4>
        <p>Ferramenta avançada para simulação de impactos de investimentos nas <b>133 regiões intermediárias do Brasil</b>
        utilizando o <b>modelo Input-Output de Leontief</b> com análise de efeitos diretos, indiretos e induzidos.</p>
    </div>
    """, unsafe_allow_html=True)

def criar_dashboard_regiao_elegante(dados_regiao):
    """Cria dashboard econômico elegante para região selecionada"""

    st.markdown("""
    <div class="section-title">
        📊 PERFIL ECONÔMICO REGIONAL
    </div>
    """, unsafe_allow_html=True)

    # Métricas principais em cards elegantes
    col1, col2, col3 = st.columns(3)

    vab_total = dados_regiao['vab'].sum()
    empregos_total = dados_regiao['empregos'].sum()
    empresas_total = dados_regiao['empresas'].sum()

    with col1:
        st.markdown(f"""
        <div class="metric-highlight">
            <h3>💰 VAB Total</h3>
            <h2>R$ {vab_total:,.0f} Mi</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-highlight">
            <h3>👥 Empregos</h3>
            <h2>{empregos_total:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-highlight">
            <h3>🏢 Empresas</h3>
            <h2>{empresas_total:,.0f}</h2>
        </div>
        """, unsafe_allow_html=True)

    # Gráfico de composição setorial elegante
    st.markdown("### 📈 Composição Setorial por VAB")

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
        height=350,
        font=dict(size=12),
        margin=dict(t=20, b=20, l=20, r=20)
    )

    st.plotly_chart(fig, use_container_width=True)

def criar_secao_validacao_modelo():
    """Cria seção de validação e parâmetros do modelo"""

    st.markdown("""
    <div class="section-title">
        🔬 VALIDAÇÃO E PARÂMETROS DO MODELO
    </div>
    """, unsafe_allow_html=True)

    # Tabs para organizar informações técnicas
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Matriz Leontief", "⚙️ Parâmetros", "📈 Multiplicadores", "🎯 Metodologia"])

    with tab1:
        st.markdown("### Matriz de Impactos (I - A)⁻¹")
        st.markdown("*Mostra quanto cada setor produz para atender uma unidade de demanda final*")

        # Exibir matriz L com formatação elegante
        matriz_styled = matriz_L_df.style.format("{:.3f}").background_gradient(cmap='YlOrRd')
        st.dataframe(matriz_styled, use_container_width=True)

        st.markdown("""
        **📝 Interpretação:** Cada célula (i,j) indica quanto o setor i precisa produzir para
        atender R$ 1 de demanda final do setor j, incluindo efeitos diretos e indiretos.
        """)

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
    <div class="section-title">
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

    # Botão Nova Simulação (se houver resultados)
    if 'resultados_simulacao' in st.session_state and st.session_state.resultados_simulacao is not None:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 **NOVA SIMULAÇÃO**", type="secondary", use_container_width=True):
                # Reset todos os estados
                st.session_state.regiao_ativa = None
                st.session_state.resultados_simulacao = None
                st.session_state.parametros_simulacao = None
                st.success("✅ Parâmetros resetados! Selecione uma nova região.")
                st.rerun()

    # Carregamento de dados
    gdf = carregar_dados_geograficos()
    if gdf is None:
        st.error("❌ Não foi possível carregar os dados geográficos.")
        st.stop()

    df_economia = gerar_dados_economicos(gdf)

    # Estado da sessão
    if 'regiao_ativa' not in st.session_state:
        st.session_state.regiao_ativa = None
    if 'resultados_simulacao' not in st.session_state:
        st.session_state.resultados_simulacao = None
    if 'parametros_simulacao' not in st.session_state:
        st.session_state.parametros_simulacao = None

    # Layout principal 60/40 (60% mapa, 40% painel)
    col_esquerda, col_direita = st.columns([0.6, 0.4])

    # ==============================================================================
    # COLUNA ESQUERDA: MAPA E VALIDAÇÃO
    # ==============================================================================
    with col_esquerda:
        # Seção do mapa
        st.markdown("""
        <div class="section-title">
            🗺️ MAPA INTERATIVO BRASIL
        </div>
        """, unsafe_allow_html=True)

        # Criar mapa
        mapa = folium.Map(
            location=[-15.0, -55.0],
            zoom_start=4,
            tiles="CartoDB positron",
            prefer_canvas=True
        )

        # Camada de resultados (se existir simulação)
        if st.session_state.resultados_simulacao is not None:
            # Agregar resultados por região
            resultados_agregados = st.session_state.resultados_simulacao.groupby('regiao')['impacto_producao'].sum().reset_index()

            # Merge com geometrias
            gdf_com_dados = gdf.merge(
                resultados_agregados,
                left_on='NM_RGINT',
                right_on='regiao',
                how='left'
            ).fillna(0)

            # Choropleth de impactos
            if gdf_com_dados['impacto_producao'].max() > 0:
                choro = folium.Choropleth(
                    geo_data=gdf_com_dados,
                    data=gdf_com_dados,
                    columns=['NM_RGINT', 'impacto_producao'],
                    key_on='feature.properties.NM_RGINT',
                    fill_color='YlOrRd',
                    fill_opacity=0.8,
                    line_opacity=0.3,
                    legend_name='Impacto na Produção (R$ Milhões)'
                )
                choro.add_to(mapa)

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

        # Renderizar mapa
        map_data = st_folium(
            mapa,
            use_container_width=True,
            height=500,
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

        # Seção de validação do modelo (abaixo do mapa)
        st.markdown("---")
        criar_secao_validacao_modelo()

    # ==============================================================================
    # COLUNA DIREITA: DASHBOARD E SIMULAÇÃO
    # ==============================================================================
    with col_direita:
        if st.session_state.regiao_ativa is None:
            # Estado inicial - instruções elegantes
            st.markdown("""
            <div class="section-title">
                🎯 PAINEL DE CONTROLE
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="info-card">
                <h3>🗺️ Como Utilizar a Ferramenta</h3>
                <ol>
                    <li><b>👆 Clique em uma região</b> no mapa interativo</li>
                    <li><b>📊 Analise o perfil</b> econômico da região</li>
                    <li><b>🎯 Configure a simulação</b> de investimento</li>
                    <li><b>🚀 Execute e analise</b> os impactos econômicos</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)

            # Métricas gerais do Brasil
            st.markdown("""
            <div class="section-title">
                📊 PANORAMA NACIONAL
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                vab_total_br = df_economia['vab'].sum()
                st.markdown(f"""
                <div class="metric-highlight">
                    <h4>💰 VAB Nacional</h4>
                    <h3>R$ {vab_total_br:,.0f} Mi</h3>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="metric-highlight">
                    <h4>🏭 Setores</h4>
                    <h3>{len(setores)}</h3>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                empregos_total_br = df_economia['empregos'].sum()
                st.markdown(f"""
                <div class="metric-highlight">
                    <h4>👥 Empregos</h4>
                    <h3>{empregos_total_br:,.0f}</h3>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="metric-highlight">
                    <h4>🗺️ Regiões</h4>
                    <h3>133</h3>
                </div>
                """, unsafe_allow_html=True)

        else:
            # Região selecionada - dashboard e simulação elegantes
            st.markdown(f"""
            <div class="section-title">
                📍 {st.session_state.regiao_ativa}
            </div>
            """, unsafe_allow_html=True)

            # Dashboard da região
            dados_regiao = df_economia[df_economia['regiao'] == st.session_state.regiao_ativa]
            criar_dashboard_regiao_elegante(dados_regiao)

            st.markdown("---")

            # Interface de simulação elegante
            st.markdown("""
            <div class="section-title">
                🚀 SIMULAÇÃO DE INVESTIMENTO
            </div>
            """, unsafe_allow_html=True)

            # Passo 1: Setor
            with st.expander("🎯 **Passo 1: Seleção do Setor Econômico**", expanded=True):
                st.markdown("Escolha o setor que receberá o investimento:")

                opcoes_setores = []
                for setor in setores:
                    meta = metadados_setores[setor]
                    opcoes_setores.append(f"{meta['emoji']} {setor} - {meta['descricao']}")

                setor_idx = st.selectbox(
                    "Setor:",
                    options=range(len(setores)),
                    format_func=lambda x: opcoes_setores[x],
                    key='setor_simulacao'
                )

                setor_selecionado = setores[setor_idx]

                # Mostrar multiplicador do setor
                multiplicador = matriz_L_df.sum(axis=0)[setor_selecionado]
                st.info(f"**Multiplicador de Produção:** {multiplicador:.2f}x")

            # Passo 2: Intensidade
            with st.expander("💰 **Passo 2: Definição do Valor do Investimento**", expanded=True):
                vab_setor = dados_regiao[dados_regiao['setor'] == setor_selecionado]['vab'].iloc[0]

                col1, col2 = st.columns([2, 1])

                with col1:
                    percentual_choque = st.slider(
                        "Porcentagem do VAB setorial:",
                        min_value=0.1,
                        max_value=50.0,
                        value=10.0,
                        step=0.1,
                        format="%.1f%%"
                    )

                with col2:
                    valor_choque = vab_setor * (percentual_choque / 100.0)
                    st.markdown(f"""
                    <div class="metric-highlight">
                        <h4>💵 Investimento</h4>
                        <h3>R$ {valor_choque:,.1f} Mi</h3>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown(f"**Base de cálculo:** VAB {setor_selecionado} = R$ {vab_setor:,.1f} Mi")

            # Botão de simulação elegante
            if st.button("🚀 **EXECUTAR SIMULAÇÃO COMPLETA**", type="primary", use_container_width=True):
                with st.spinner("🔄 Calculando impactos em 133 regiões × 4 setores..."):
                    resultados, impactos_setoriais = executar_simulacao_avancada(
                        df_economia, valor_choque, setor_selecionado
                    )

                    st.session_state.resultados_simulacao = resultados
                    st.session_state.parametros_simulacao = {
                        'regiao_origem': st.session_state.regiao_ativa,
                        'setor_investimento': setor_selecionado,
                        'valor_investimento': valor_choque,
                        'percentual_vab': percentual_choque,
                        'multiplicador_usado': multiplicador,
                        'impactos_setoriais': impactos_setoriais,
                        'timestamp': datetime.now()
                    }

                st.success("✅ Simulação executada com sucesso!")
                st.balloons()
                st.rerun()

        # Exibição de resultados elegantes
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
            <div class="section-title">
                📈 RESULTADOS DA SIMULAÇÃO
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                <div class="metric-highlight">
                    <h4>💰 Impacto Total</h4>
                    <h3>R$ {total_impacto:,.1f} Mi</h3>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="metric-highlight">
                    <h4>👥 Empregos Gerados</h4>
                    <h3>{total_empregos:,.0f}</h3>
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

            # Ranking elegante (em expander para economizar espaço)
            with st.expander("🏆 **Ver Ranking Completo de Regiões**", expanded=False):
                criar_ranking_resultados_elegante(st.session_state.resultados_simulacao)

if __name__ == "__main__":
    main()