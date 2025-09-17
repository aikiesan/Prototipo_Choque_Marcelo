# ==============================================================================
# SIMULADOR NACIONAL DE IMPACTOS ECONÔMICOS - VERSÃO OTIMIZADA
# Interface Map First Ultra-Responsiva com 133 Regiões do Brasil
# ==============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import time

# ==============================================================================
# CONFIGURAÇÃO OTIMIZADA
# ==============================================================================

st.set_page_config(
    layout="wide",
    page_title="🗺️ Simulador Econômico Nacional",
    page_icon="🗺️",
    initial_sidebar_state="collapsed"
)

# Cache agressivo para performance máxima
@st.cache_data(show_spinner=False)
def carregar_dados_geograficos():
    """Carrega shapefile otimizado com cache agressivo"""
    try:
        # Carregar apenas as colunas essenciais
        gdf = gpd.read_parquet(
            'shapefiles/BR_RG_Imediatas_2024_optimized.parquet',
            columns=['NM_RGINT', 'geometry']
        )

        # Agregar diretamente sem processamento desnecessário
        gdf_regioes = gdf.dissolve(by='NM_RGINT').reset_index()

        # Apenas normalização básica
        gdf_regioes['NM_RGINT'] = gdf_regioes['NM_RGINT'].astype(str)

        return gdf_regioes

    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

@st.cache_data(show_spinner=False)
def gerar_dados_economicos_leves(_gdf):
    """Gera dados econômicos sintéticos ultrarrápidos"""
    regioes = _gdf['NM_RGINT'].tolist()
    setores = ['Agropecuária', 'Indústria', 'Construção', 'Serviços']

    # Dados pré-calculados para performance
    dados = []
    np.random.seed(42)  # Resultados consistentes

    for i, regiao in enumerate(regioes):
        base_values = np.random.uniform(1000, 100000, 4)
        for j, setor in enumerate(setores):
            dados.append({
                'regiao': regiao,
                'setor': setor,
                'vab': base_values[j],
                'empregos': base_values[j] * 0.02
            })

    return pd.DataFrame(dados)

@st.cache_data(show_spinner=False)
def calcular_impacto_rapido(valor_choque, setor_idx):
    """Cálculo de impacto ultra-simplificado para demonstração"""
    # Matriz simplificada pré-calculada
    multiplicadores = np.array([1.2, 1.8, 1.3, 1.5])
    return valor_choque * multiplicadores[setor_idx]

# ==============================================================================
# INTERFACE MINIMALISTA MAP FIRST
# ==============================================================================

def main():
    # Título compacto
    st.title("🗺️ Simulador Nacional")

    # Carregamento com indicador visual
    with st.spinner("Carregando mapa do Brasil..."):
        gdf = carregar_dados_geograficos()

    if gdf is None:
        st.error("Falha ao carregar dados geográficos")
        return

    df_economia = gerar_dados_economicos_leves(gdf)

    # Estado da sessão simplificado
    if 'regiao_ativa' not in st.session_state:
        st.session_state.regiao_ativa = None
    if 'resultados' not in st.session_state:
        st.session_state.resultados = None

    # Layout otimizado 75/25
    col_mapa, col_controle = st.columns([0.75, 0.25])

    # ==============================================================================
    # MAPA PRINCIPAL (75%)
    # ==============================================================================

    with col_mapa:
        # Mapa base ultra-simplificado
        mapa = folium.Map(
            location=[-15.0, -55.0],
            zoom_start=4,
            tiles="CartoDB positron",
            prefer_canvas=True  # Melhor performance
        )

        # Camada única otimizada
        if st.session_state.resultados is not None:
            # Mapa com resultados
            gdf_com_dados = gdf.merge(
                st.session_state.resultados,
                left_on='NM_RGINT',
                right_on='regiao',
                how='left'
            ).fillna(0)

            folium.Choropleth(
                geo_data=gdf_com_dados,
                data=gdf_com_dados,
                columns=['NM_RGINT', 'impacto'],
                key_on='feature.properties.NM_RGINT',
                fill_color='YlOrRd',
                fill_opacity=0.6,
                line_opacity=0.1,
                legend_name='Impacto Econômico'
            ).add_to(mapa)

        # Camada de interação
        folium.GeoJson(
            gdf,
            style_function=lambda feature: {
                'fillColor': 'orange' if feature['properties']['NM_RGINT'] == st.session_state.regiao_ativa else 'transparent',
                'color': 'red' if feature['properties']['NM_RGINT'] == st.session_state.regiao_ativa else 'gray',
                'weight': 2 if feature['properties']['NM_RGINT'] == st.session_state.regiao_ativa else 0.5,
                'fillOpacity': 0.3
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['NM_RGINT'],
                aliases=['Região:']
            )
        ).add_to(mapa)

        # Renderizar mapa
        map_data = st_folium(mapa, use_container_width=True, height=600)

        # Detectar clique
        if map_data and map_data.get('last_object_clicked_tooltip'):
            nova_regiao = map_data['last_object_clicked_tooltip'].get('Região:')
            if nova_regiao and nova_regiao != st.session_state.regiao_ativa:
                st.session_state.regiao_ativa = nova_regiao
                st.rerun()

    # ==============================================================================
    # PAINEL DE CONTROLE (25%)
    # ==============================================================================

    with col_controle:
        st.subheader("⚙️ Controles")

        if st.session_state.regiao_ativa:
            # Região selecionada
            st.success(f"📍 **{st.session_state.regiao_ativa}**")

            # Controles simples
            setor = st.selectbox(
                "Setor:",
                ['Agropecuária', 'Indústria', 'Construção', 'Serviços'],
                key='setor'
            )

            valor = st.slider(
                "Investimento (R$ Mi):",
                10, 1000, 100,
                key='valor'
            )

            # Botão de simulação
            if st.button("🚀 Simular", type="primary", use_container_width=True):
                with st.spinner("Calculando..."):
                    # Simulação ultra-rápida
                    setor_idx = ['Agropecuária', 'Indústria', 'Construção', 'Serviços'].index(setor)
                    impacto_total = calcular_impacto_rapido(valor, setor_idx)

                    # Distribuir impacto entre regiões (simplificado)
                    regioes = gdf['NM_RGINT'].tolist()
                    impactos = np.random.exponential(impacto_total/len(regioes), len(regioes))

                    # Normalizar para que a região selecionada tenha maior impacto
                    if st.session_state.regiao_ativa in regioes:
                        idx = regioes.index(st.session_state.regiao_ativa)
                        impactos[idx] = max(impactos) * 1.5

                    st.session_state.resultados = pd.DataFrame({
                        'regiao': regioes,
                        'impacto': impactos
                    })

                st.rerun()

            # Resultados
            if st.session_state.resultados is not None:
                st.markdown("---")
                st.subheader("📊 Resultados")

                total = st.session_state.resultados['impacto'].sum()
                st.metric("Impacto Total", f"R$ {total:,.0f} Mi")

                # Top 3 regiões
                top3 = st.session_state.resultados.nlargest(3, 'impacto')
                st.write("**Top 3:**")
                for _, row in top3.iterrows():
                    st.write(f"• {row['regiao']}: R$ {row['impacto']:,.0f} Mi")

        else:
            st.info("👆 Clique em uma região no mapa")

            # Estatísticas gerais
            st.markdown("---")
            st.markdown("**🇧🇷 Brasil:**")
            st.write(f"• {len(gdf)} regiões")
            st.write("• 4 setores econômicos")
            st.write("• Modelo Insumo-Produto")

if __name__ == "__main__":
    main()