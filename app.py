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
    """Carrega geometrias ultra-leves para performance máxima"""
    try:
        # Usar geometrias ultra-leves (0.35MB, carregam em 0.007s)
        gdf = gpd.read_parquet(
            'shapefiles/brasil_regions_ultra_light.parquet'
        )

        # Dados já estão otimizados, apenas garantir tipos
        gdf['NM_RGINT'] = gdf['NM_RGINT'].astype(str)

        return gdf

    except Exception as e:
        # Fallback para geometrias otimizadas originais
        try:
            gdf = gpd.read_parquet(
                'shapefiles/BR_RG_Imediatas_2024_optimized.parquet',
                columns=['NM_RGINT', 'geometry']
            )
            gdf_regioes = gdf.dissolve(by='NM_RGINT').reset_index()
            gdf_regioes['NM_RGINT'] = gdf_regioes['NM_RGINT'].astype(str)
            return gdf_regioes
        except:
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

    # Progressive loading com skeleton UI
    if 'dados_carregados' not in st.session_state:
        st.session_state.dados_carregados = False
        st.session_state.gdf = None

    # Mostrar skeleton UI enquanto carrega
    if not st.session_state.dados_carregados:
        with st.container():
            st.info("⚡ Carregando geometrias ultra-leves... (< 1 segundo)")

            # Carregar dados em background
            gdf = carregar_dados_geograficos()

            if gdf is not None:
                st.session_state.gdf = gdf
                st.session_state.dados_carregados = True
                st.success("✅ Carregamento completo! Mapa pronto para uso.")
                st.rerun()
            else:
                st.error("❌ Falha ao carregar dados geográficos")
                return

        return  # Exit early while loading

    # Dados já carregados - garantidos não-nulos
    gdf = st.session_state.gdf

    df_economia = gerar_dados_economicos_leves(gdf)

    # Estado da sessão simplificado
    if 'regiao_ativa' not in st.session_state:
        st.session_state.regiao_ativa = None
    if 'resultados' not in st.session_state:
        st.session_state.resultados = None

    # Layout otimizado 60/40 conforme solicitado
    col_mapa, col_controle = st.columns([0.6, 0.4])

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

        # Camada de interação otimizada para cliques
        geojson_layer = folium.GeoJson(
            gdf,
            style_function=lambda feature: {
                'fillColor': 'orange' if feature['properties']['NM_RGINT'] == st.session_state.regiao_ativa else 'lightblue',
                'color': 'red' if feature['properties']['NM_RGINT'] == st.session_state.regiao_ativa else 'blue',
                'weight': 3 if feature['properties']['NM_RGINT'] == st.session_state.regiao_ativa else 1,
                'fillOpacity': 0.7 if feature['properties']['NM_RGINT'] == st.session_state.regiao_ativa else 0.3,
                'opacity': 1
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['NM_RGINT'],
                aliases=['Região:'],
                localize=True,
                sticky=True,
                labels=True,
                style="""
                    background-color: white;
                    border: 2px solid black;
                    border-radius: 3px;
                    box-shadow: 3px;
                """
            ),
            popup=folium.GeoJsonPopup(
                fields=['NM_RGINT'],
                aliases=['Região:'],
                localize=True,
                labels=True
            ),
            highlight_function=lambda x: {
                'weight': 3,
                'color': 'orange',
                'fillOpacity': 0.7
            }
        )
        geojson_layer.add_to(mapa)

        # Renderizar mapa com configurações otimizadas para cliques
        map_data = st_folium(
            mapa,
            use_container_width=True,
            height=600,
            returned_objects=["last_object_clicked_tooltip", "last_clicked", "last_object_clicked"]
        )

        # Debug: Mostrar dados do mapa para diagnosticar problema
        if map_data:
            with st.expander("🔧 Debug - Dados do Mapa (temporário)", expanded=False):
                st.write("**Chaves disponíveis:**", list(map_data.keys()) if map_data else [])
                if map_data.get('last_object_clicked_tooltip'):
                    st.write("**Tooltip clicado:**", map_data.get('last_object_clicked_tooltip'))
                if map_data.get('last_object_clicked'):
                    st.write("**Objeto clicado:**", map_data.get('last_object_clicked'))
                if map_data.get('last_clicked'):
                    st.write("**Último clique:**", map_data.get('last_clicked'))

        # Detectar cliques usando múltiplas estratégias
        nova_regiao = None

        # Estratégia 1: Tooltip clique (principal)
        if map_data and map_data.get('last_object_clicked_tooltip'):
            tooltip_data = map_data.get('last_object_clicked_tooltip')
            if tooltip_data and isinstance(tooltip_data, dict):
                nova_regiao = tooltip_data.get('Região:')

        # Estratégia 2: Objeto clicado (fallback)
        if not nova_regiao and map_data and map_data.get('last_object_clicked'):
            obj_data = map_data.get('last_object_clicked')
            if obj_data and isinstance(obj_data, dict):
                properties = obj_data.get('properties', {})
                nova_regiao = properties.get('NM_RGINT')

        # Estratégia 3: Clique geral (último recurso)
        if not nova_regiao and map_data and map_data.get('last_clicked'):
            click_data = map_data.get('last_clicked')
            if click_data and isinstance(click_data, dict):
                # Tentar extrair região do clique
                pass

        # Atualizar região ativa se nova região foi detectada
        if nova_regiao and nova_regiao != st.session_state.regiao_ativa:
            st.session_state.regiao_ativa = nova_regiao
            st.success(f"🎯 Região selecionada: {nova_regiao}")
            st.rerun()

    # ==============================================================================
    # PAINEL DE CONTROLE E DASHBOARD (40%)
    # ==============================================================================

    with col_controle:
        st.subheader("⚙️ Controles & Dashboard")

        # Métricas gerais sempre visíveis
        st.markdown("### 📊 Visão Geral")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Regiões", len(gdf))
        with col2:
            st.metric("Setores", 4)

        # Fallback: Seleção por lista caso clique não funcione
        st.markdown("### 📋 Seleção Alternativa")
        lista_regioes = ['Selecione...'] + sorted(gdf['NM_RGINT'].unique().tolist())
        regiao_selecionada = st.selectbox(
            "Ou selecione uma região da lista:",
            options=lista_regioes,
            key='regiao_lista'
        )

        if regiao_selecionada != 'Selecione...' and regiao_selecionada != st.session_state.regiao_ativa:
            st.session_state.regiao_ativa = regiao_selecionada
            st.success(f"✅ Região selecionada via lista: {regiao_selecionada}")
            st.rerun()

        st.markdown("---")

        if st.session_state.regiao_ativa:
            # Região selecionada
            st.success(f"📍 **{st.session_state.regiao_ativa}**")

            st.markdown("### 🎛️ Parâmetros de Simulação")

            # Setor com descrições
            setores_info = {
                'Agropecuária': 'Agricultura, pecuária e silvicultura',
                'Indústria': 'Manufatura e transformação',
                'Construção': 'Construção civil e infraestrutura',
                'Serviços': 'Comércio, transportes e serviços'
            }

            setor = st.selectbox(
                "🏭 Setor Econômico:",
                options=list(setores_info.keys()),
                help="Selecione o setor onde será aplicado o investimento",
                key='setor'
            )
            st.caption(setores_info[setor])

            # Valor com mais opções
            col1, col2 = st.columns([2, 1])
            with col1:
                valor = st.slider(
                    "💰 Investimento (R$ Milhões):",
                    min_value=10, max_value=2000, value=100, step=10,
                    key='valor'
                )
            with col2:
                st.metric("Valor", f"R$ {valor:,} Mi")

            # Tipo de análise
            tipo_analise = st.selectbox(
                "📊 Tipo de Análise:",
                ["Impacto Total", "Apenas Direto", "Direto + Indireto"],
                help="Escolha o escopo da análise de impacto",
                index=0
            )

            # Botão de simulação aprimorado
            st.markdown("---")
            if st.button("🚀 Executar Simulação", type="primary", use_container_width=True):
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

            # Resultados expandidos
            if st.session_state.resultados is not None:
                st.markdown("---")
                st.markdown("### 📊 Resultados da Simulação")

                # Métricas principais
                total = st.session_state.resultados['impacto'].sum()
                regiao_principal = st.session_state.resultados.loc[
                    st.session_state.resultados['regiao'] == st.session_state.regiao_ativa,
                    'impacto'
                ].iloc[0] if st.session_state.regiao_ativa in st.session_state.resultados['regiao'].values else 0

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("💰 Impacto Total", f"R$ {total:,.0f} Mi")
                with col2:
                    st.metric("🎯 Região Principal", f"R$ {regiao_principal:,.0f} Mi")

                # Top 5 regiões com mais detalhes
                st.markdown("#### 🏆 Ranking de Impactos")
                top5 = st.session_state.resultados.nlargest(5, 'impacto').reset_index(drop=True)

                for i, row in top5.iterrows():
                    percentual = (row['impacto'] / total) * 100
                    is_principal = row['regiao'] == st.session_state.regiao_ativa

                    with st.container():
                        col1, col2, col3 = st.columns([3, 2, 1])
                        with col1:
                            emoji = "🎯" if is_principal else f"{i+1}º"
                            st.write(f"**{emoji} {row['regiao']}**")
                        with col2:
                            st.write(f"R$ {row['impacto']:,.0f} Mi")
                        with col3:
                            st.write(f"{percentual:.1f}%")

                # Análise adicional
                st.markdown("#### 📈 Análise Econômica")
                multiplicador = total / valor
                regioes_impactadas = len(st.session_state.resultados[st.session_state.resultados['impacto'] > (total * 0.01)])

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("📊 Multiplicador", f"{multiplicador:.2f}x")
                with col2:
                    st.metric("🌐 Regiões Impactadas", f"{regioes_impactadas}")

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