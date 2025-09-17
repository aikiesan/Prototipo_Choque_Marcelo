#!/usr/bin/env python3
"""
SIMULADOR GEO-ECONÔMICO NACIONAL - VERSÃO PREMIUM
Interface UX guiada com análise econômica profunda e modelo Leontief avançado
De Funcional a Excepcional - Experiência Map First Premium
"""

import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    layout="wide",
    page_title="🗺️ Simulador Geo-Econômico Nacional",
    page_icon="🗺️",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# MODELO ECONÔMICO AVANÇADO (LEONTIEF INPUT-OUTPUT)
# ==============================================================================

# Matriz de coeficientes técnicos (baseada em dados reais do Brasil)
setores = ['Agropecuária', 'Indústria', 'Construção', 'Serviços']

# Matriz A (coeficientes técnicos) - quanto cada setor consome dos outros
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

@st.cache_data(show_spinner="📊 Gerando base econômica das 133 regiões...")
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
                'empregos': vab_base[setor] * np.random.uniform(15, 25)  # Empregos por R$ milhão
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

        resultados.append(dados_setor)

    df_resultados = pd.concat(resultados, ignore_index=True)

    return df_resultados

# ==============================================================================
# INTERFACE PREMIUM - COMPONENTES
# ==============================================================================

def criar_dashboard_regiao(dados_regiao):
    """Cria dashboard econômico para região selecionada"""

    # Métricas principais
    col1, col2 = st.columns(2)
    with col1:
        vab_total = dados_regiao['vab'].sum()
        st.metric("💰 VAB Total", f"R$ {vab_total:,.0f} Mi")
    with col2:
        empregos_total = dados_regiao['empregos'].sum()
        st.metric("👥 Empregos", f"{empregos_total:,.0f}")

    # Gráfico de composição setorial
    st.markdown("**📊 Composição Setorial:**")
    fig = px.bar(
        dados_regiao,
        x='setor',
        y='vab',
        title="",
        labels={'vab': 'VAB (R$ Mi)', 'setor': ''},
        color='setor',
        color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    )
    fig.update_layout(
        height=250,
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig, use_container_width=True)

def criar_ranking_resultados(resultados_simulacao):
    """Cria ranking visual de resultados com composição setorial"""

    # Agregar por região
    resultados_agregados = resultados_simulacao.groupby('regiao')['impacto_producao'].sum().reset_index()
    top_10 = resultados_agregados.nlargest(10, 'impacto_producao')

    st.markdown("**🏆 Top 10 Regiões Mais Impactadas:**")

    for i, row in top_10.iterrows():
        regiao = row['regiao']
        impacto_total = row['impacto_producao']

        # Dados setoriais da região
        dados_regiao = resultados_simulacao[resultados_simulacao['regiao'] == regiao]

        with st.container():
            # Header da região
            col1, col2 = st.columns([3, 1])
            with col1:
                posicao = i + 1
                emoji = "🥇" if posicao == 1 else "🥈" if posicao == 2 else "🥉" if posicao == 3 else f"{posicao}º"
                st.write(f"**{emoji} {regiao}**")
            with col2:
                st.write(f"**R$ {impacto_total:,.1f} Mi**")

            # Mini-gráfico de composição setorial
            fig_mini = px.bar(
                dados_regiao,
                x='setor',
                y='impacto_producao',
                color='setor',
                color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
            )
            fig_mini.update_layout(
                height=120,
                showlegend=False,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis_title="",
                yaxis_title=""
            )
            st.plotly_chart(fig_mini, use_container_width=True)

# ==============================================================================
# INTERFACE PRINCIPAL
# ==============================================================================

def main():
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

    # Cabeçalho
    st.title("🗺️ Simulador Geo-Econômico Nacional")
    st.caption("Análise interativa de impactos econômicos nas 133 regiões intermediárias do Brasil usando modelo Input-Output")

    # Layout principal 65/35
    col_mapa, col_painel = st.columns([0.65, 0.35])

    # ==============================================================================
    # MAPA INTERATIVO PREMIUM
    # ==============================================================================
    with col_mapa:
        # Criar mapa base
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

        # Camada de interação (sempre por cima)
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
            ),
            highlight_function=lambda x: {
                'weight': 3,
                'color': '#FFD700',
                'fillOpacity': 0.7
            }
        ).add_to(mapa)

        # Renderizar mapa
        map_data = st_folium(
            mapa,
            use_container_width=True,
            height=700,
            returned_objects=["last_object_clicked_tooltip"]
        )

        # Detecção de cliques aprimorada
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

    # ==============================================================================
    # PAINEL DE CONTROLE E RESULTADOS PREMIUM
    # ==============================================================================
    with col_painel:
        if st.session_state.regiao_ativa is None:
            # Estado inicial - instruções
            st.markdown("""
            ### 🗺️ Bem-vindo ao Simulador!

            **Como usar:**
            1. 👆 **Clique em uma região** no mapa
            2. 🎯 Configure sua simulação
            3. 🚀 Execute e veja os impactos

            ---

            **💡 Sobre a ferramenta:**
            - Modelo **Input-Output Leontief**
            - **133 regiões** intermediárias
            - **4 setores** econômicos
            - Análise de **efeitos indiretos**
            """)

            # Métricas gerais
            st.markdown("### 📊 Brasil em Números")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("🗺️ Regiões", "133")
                st.metric("🏭 Setores", "4")
            with col2:
                vab_total_br = df_economia['vab'].sum()
                st.metric("💰 VAB Total", f"R$ {vab_total_br:,.0f} Mi")
                empregos_total_br = df_economia['empregos'].sum()
                st.metric("👥 Empregos", f"{empregos_total_br:,.0f}")

        else:
            # Região selecionada - dashboard e simulação
            st.header(f"📍 {st.session_state.regiao_ativa}")

            # Dashboard da região
            dados_regiao = df_economia[df_economia['regiao'] == st.session_state.regiao_ativa]
            criar_dashboard_regiao(dados_regiao)

            st.markdown("---")

            # Interface de simulação guiada
            st.subheader("🎯 Simulação de Investimento")

            # Passo 1: Setor
            with st.expander("**📋 Passo 1: Setor do Investimento**", expanded=True):
                setor_info = {
                    'Agropecuária': '🌾 Agricultura, pecuária, silvicultura',
                    'Indústria': '🏭 Manufatura e transformação',
                    'Construção': '🏗️ Construção civil e infraestrutura',
                    'Serviços': '🏪 Comércio, transportes e serviços'
                }

                setor_selecionado = st.selectbox(
                    "Selecione o setor:",
                    options=list(setor_info.keys()),
                    format_func=lambda x: setor_info[x],
                    key='setor_sim'
                )

            # Passo 2: Intensidade
            with st.expander("**💰 Passo 2: Intensidade do Investimento**", expanded=True):
                vab_setor = dados_regiao[dados_regiao['setor'] == setor_selecionado]['vab'].iloc[0]

                percentual_choque = st.slider(
                    "Porcentagem do VAB setorial da região:",
                    min_value=0.1,
                    max_value=50.0,
                    value=10.0,
                    step=0.1,
                    format="%.1f%%"
                )

                valor_choque = vab_setor * (percentual_choque / 100.0)
                st.success(f"💵 **Investimento:** R$ {valor_choque:,.2f} Milhões")

                # Contexto econômico
                st.caption(f"Base: VAB {setor_selecionado} = R$ {vab_setor:,.1f} Mi")

            # Botão de simulação
            if st.button("🚀 **Executar Simulação**", type="primary", use_container_width=True):
                with st.spinner("🔄 Calculando impactos em 133 regiões..."):
                    st.session_state.resultados_simulacao = executar_simulacao_avancada(
                        df_economia, valor_choque, setor_selecionado
                    )
                st.success("✅ Simulação concluída!")
                st.rerun()

        # Exibição de resultados
        if st.session_state.resultados_simulacao is not None:
            st.markdown("---")
            st.subheader("📈 Resultados da Simulação")

            # Métricas principais
            total_impacto = st.session_state.resultados_simulacao['impacto_producao'].sum()
            total_empregos = st.session_state.resultados_simulacao['impacto_empregos'].sum()

            col1, col2 = st.columns(2)
            with col1:
                st.metric("💰 Impacto Total", f"R$ {total_impacto:,.1f} Mi")
            with col2:
                st.metric("👥 Empregos Gerados", f"{total_empregos:,.0f}")

            # Análise por setor
            impactos_por_setor = st.session_state.resultados_simulacao.groupby('setor')['impacto_producao'].sum()
            st.markdown("**📊 Impacto por Setor (Brasil):**")

            fig_setores = px.bar(
                x=impactos_por_setor.index,
                y=impactos_por_setor.values,
                labels={'x': '', 'y': 'Impacto (R$ Mi)'},
                color=impactos_por_setor.index,
                color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
            )
            fig_setores.update_layout(height=250, showlegend=False)
            st.plotly_chart(fig_setores, use_container_width=True)

            # Ranking de regiões
            criar_ranking_resultados(st.session_state.resultados_simulacao)

if __name__ == "__main__":
    main()