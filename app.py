# ==============================================================================
# SIMULADOR DE IMPACTOS ECONÔMICOS NACIONAL - MAP FIRST
# Análise de 133 Regiões Intermediárias do Brasil
# ==============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import random

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ==============================================================================

st.set_page_config(
    layout="wide",
    page_title="🗺️ Simulador Nacional de Impactos Econômicos",
    page_icon="🗺️"
)

# ==============================================================================
# DADOS BASE E CONFIGURAÇÕES
# ==============================================================================

# Matriz de Coeficientes Técnicos (mantida do modelo de SP, será expandida futuramente)
matriz_coeficientes_data = {
    '1. Agropecuária': [0.201, 0.155, 0.002, 0.117],
    '2. Indústria':    [0.085, 0.351, 0.004, 0.160],
    '3. Construção':   [0.003, 0.298, 0.001, 0.145],
    '4. Serviços':     [0.012, 0.105, 0.008, 0.245]
}
setores = ['1. Agropecuária', '2. Indústria', '3. Construção', '4. Serviços']
matriz_a = pd.DataFrame(matriz_coeficientes_data, index=setores)

# Coeficientes econômicos
coef_vab = 1 - matriz_a.sum()
coef_impostos = 0.18

# Configurações de camadas do mapa
LAYER_CONFIGS = {
    'Mapa Base': {
        'color': 'lightblue',
        'description': 'Visualização padrão das regiões'
    },
    'Impacto na Produção': {
        'color': 'YlOrRd',
        'description': 'Intensidade do impacto na produção por região'
    },
    'Geração de Empregos': {
        'color': 'Blues',
        'description': 'Quantidade de empregos gerados por região'
    },
    'Crescimento do PIB': {
        'color': 'Greens',
        'description': 'Impacto no PIB (VAB) por região'
    },
    'Arrecadação de Impostos': {
        'color': 'Purples',
        'description': 'Arrecadação de impostos estimada por região'
    }
}

# ==============================================================================
# FUNÇÕES DE DADOS
# ==============================================================================

@st.cache_data
def carregar_shapefile_nacional():
    """Carrega o shapefile das 133 regiões intermediárias do Brasil"""
    try:
        gdf = gpd.read_parquet('shapefiles/BR_RG_Imediatas_2024_optimized.parquet')
        # Agregar por região intermediária
        gdf_grouped = gdf.dissolve(by='NM_RGINT').reset_index()
        # Normalizar nomes (encoding issues)
        gdf_grouped['NM_RGINT'] = gdf_grouped['NM_RGINT'].str.replace('�', 'ã').str.replace('�', 'á').str.replace('�', 'ç').str.replace('�', 'é').str.replace('�', 'í').str.replace('�', 'ó').str.replace('�', 'ú')
        return gdf_grouped
    except Exception as e:
        st.error(f"Erro ao carregar shapefile: {e}")
        return None

@st.cache_data
def gerar_dados_mockados_brasil():
    """Gera dados mockados para as 133 regiões intermediárias"""
    gdf = carregar_shapefile_nacional()
    if gdf is None:
        return pd.DataFrame()

    regioes = gdf['NM_RGINT'].unique()

    # Gerar dados sintéticos baseados em padrões realistas
    dados_sinteticos = []

    for regiao in regioes:
        for setor in setores:
            # Gerar VAB baseado em distribuições realistas
            if setor == '1. Agropecuária':
                vab_base = random.uniform(1000, 15000)  # Menor em geral
            elif setor == '2. Indústria':
                vab_base = random.uniform(5000, 200000)  # Muito variável
            elif setor == '3. Construção':
                vab_base = random.uniform(2000, 60000)  # Médio
            else:  # Serviços
                vab_base = random.uniform(10000, 1500000)  # Maior setor

            # Gerar emprego correlacionado com VAB
            emprego_base = vab_base * random.uniform(8, 25) / 1000  # Relação VAB/emprego

            dados_sinteticos.append({
                'Região Intermediária': regiao,
                'Setor': setor,
                'VAB_milhoes': vab_base,
                'Pessoal_Ocupado_mil': emprego_base
            })

    df_brasil = pd.DataFrame(dados_sinteticos)

    # Calcular shares e coeficientes
    vab_total_sp = df_brasil.groupby('Setor')['VAB_milhoes'].sum().reset_index()
    df_brasil = pd.merge(df_brasil, vab_total_sp, on='Setor', suffixes=('', '_total_br'))
    df_brasil['Share_VAB'] = df_brasil['VAB_milhoes'] / df_brasil['VAB_milhoes_total_br']

    # Coeficientes de emprego por produção
    coef_vab_dict = coef_vab.to_dict()
    df_brasil['Coef_VAB_Setor'] = df_brasil['Setor'].map(coef_vab_dict)
    df_brasil['Producao_Estimada'] = df_brasil['VAB_milhoes'] / df_brasil['Coef_VAB_Setor']
    df_brasil['Coef_Emprego_por_Producao'] = (df_brasil['Pessoal_Ocupado_mil'] * 1000) / df_brasil['Producao_Estimada']

    return df_brasil

@st.cache_data
def calcular_impactos(matriz_a_values, shock_vector):
    """Calcula impactos usando Matriz de Leontief"""
    identidade = np.identity(len(matriz_a_values))
    matriz_leontief = np.linalg.inv(identidade - matriz_a_values)
    impacto_producao = matriz_leontief @ shock_vector
    return pd.Series(impacto_producao, index=setores)

# ==============================================================================
# FUNÇÕES DE INTERFACE
# ==============================================================================

def criar_mapa_interativo(gdf, dados_simulacao=None, layer_selecionada='Mapa Base', regiao_selecionada=None, mostrar_fluxos=False):
    """Cria o mapa interativo principal com camadas"""

    # Mapa base centralizado no Brasil
    mapa = folium.Map(
        location=[-15.0, -55.0],  # Centro do Brasil
        zoom_start=4,
        tiles="CartoDB positron"
    )

    # Determinar estilo baseado na camada selecionada
    if layer_selecionada == 'Mapa Base' or dados_simulacao is None:
        # Mapa base simples
        folium.GeoJson(
            gdf,
            style_function=lambda feature: {
                'fillColor': 'lightblue' if feature['properties']['NM_RGINT'] != regiao_selecionada else 'orange',
                'color': 'black',
                'weight': 2 if feature['properties']['NM_RGINT'] == regiao_selecionada else 0.5,
                'fillOpacity': 0.7 if feature['properties']['NM_RGINT'] == regiao_selecionada else 0.3
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['NM_RGINT'],
                aliases=['Região:'],
                localize=True
            ),
            popup=folium.GeoJsonPopup(
                fields=['NM_RGINT'],
                aliases=['Região:']
            )
        ).add_to(mapa)

    else:
        # Mapa com dados de simulação
        gdf_com_dados = gdf.merge(dados_simulacao, left_on='NM_RGINT', right_on='Região Intermediária', how='left')
        gdf_com_dados = gdf_com_dados.fillna(0)

        # Definir coluna de dados baseada na camada
        if layer_selecionada == 'Impacto na Produção':
            data_column = 'Impacto_Producao'
            legend_name = 'Impacto na Produção (R$ Mi)'
        elif layer_selecionada == 'Geração de Empregos':
            data_column = 'Impacto_Empregos'
            legend_name = 'Empregos Gerados'
        elif layer_selecionada == 'Crescimento do PIB':
            data_column = 'Impacto_VAB'
            legend_name = 'Impacto no PIB (R$ Mi)'
        elif layer_selecionada == 'Arrecadação de Impostos':
            data_column = 'Impacto_Impostos'
            legend_name = 'Arrecadação de Impostos (R$ Mi)'
        else:
            data_column = 'Impacto_Producao'
            legend_name = 'Impacto na Produção (R$ Mi)'

        # Criar mapa coroplético
        folium.Choropleth(
            geo_data=gdf_com_dados,
            data=gdf_com_dados,
            columns=['NM_RGINT', data_column],
            key_on='feature.properties.NM_RGINT',
            fill_color=LAYER_CONFIGS[layer_selecionada]['color'],
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name=legend_name,
            nan_fill_color='lightgray'
        ).add_to(mapa)

        # Adicionar tooltips informativos
        folium.GeoJson(
            gdf_com_dados,
            style_function=lambda feature: {
                'fillOpacity': 0,
                'color': 'transparent'
            },
            tooltip=folium.GeoJsonTooltip(
                fields=['NM_RGINT', data_column],
                aliases=['Região:', f'{legend_name}:'],
                localize=True
            )
        ).add_to(mapa)

        # Adicionar fluxos econômicos se solicitado
        if mostrar_fluxos and regiao_selecionada:
            adicionar_fluxos_economicos(mapa, gdf, dados_simulacao, regiao_selecionada, data_column)

    return mapa

def adicionar_fluxos_economicos(mapa, gdf, dados_simulacao, regiao_origem, data_column):
    """Adiciona visualização de fluxos econômicos ao mapa"""
    try:
        # Obter coordenadas da região de origem
        regiao_origem_geom = gdf[gdf['NM_RGINT'] == regiao_origem].geometry.iloc[0]
        origem_coords = [regiao_origem_geom.centroid.y, regiao_origem_geom.centroid.x]

        # Obter top 5 regiões mais impactadas (excluindo a origem)
        top_regioes = dados_simulacao[
            (dados_simulacao['Região Intermediária'] != regiao_origem) &
            (dados_simulacao[data_column] > 0)
        ].nlargest(5, data_column)

        max_impacto = top_regioes[data_column].max() if not top_regioes.empty else 1

        # Adicionar linha para cada região impactada
        for _, row in top_regioes.iterrows():
            try:
                destino_geom = gdf[gdf['NM_RGINT'] == row['Região Intermediária']].geometry.iloc[0]
                destino_coords = [destino_geom.centroid.y, destino_geom.centroid.x]

                # Calcular espessura da linha proporcional ao impacto
                weight = max(1, (row[data_column] / max_impacto) * 8)

                folium.PolyLine(
                    locations=[origem_coords, destino_coords],
                    color='red',
                    weight=weight,
                    opacity=0.7,
                    tooltip=f"Fluxo para {row['Região Intermediária']}: {row[data_column]:,.1f}"
                ).add_to(mapa)

            except (IndexError, KeyError):
                continue

        # Adicionar marcador na região de origem
        folium.Marker(
            location=origem_coords,
            popup=f"Origem do Choque: {regiao_origem}",
            icon=folium.Icon(color='red', icon='star')
        ).add_to(mapa)

    except Exception as e:
        # Se houver erro, não interrompe o mapa
        pass

def mostrar_dashboard_regiao(regiao, df_dados):
    """Mostra dashboard contextual da região selecionada"""
    if not regiao:
        st.info("👆 Clique em uma região no mapa para ver detalhes")
        return

    dados_regiao = df_dados[df_dados['Região Intermediária'] == regiao]

    if dados_regiao.empty:
        st.warning(f"Dados não encontrados para {regiao}")
        return

    st.subheader(f"📊 {regiao}")

    # Métricas principais da região
    total_vab = dados_regiao['VAB_milhoes'].sum()
    total_empregos = dados_regiao['Pessoal_Ocupado_mil'].sum()

    col1, col2 = st.columns(2)
    col1.metric("VAB Total", f"R$ {total_vab:,.0f} M")
    col2.metric("Empregos", f"{total_empregos:,.0f} mil")

    # Composição setorial
    st.write("**Composição Setorial:**")
    chart_data = dados_regiao.set_index('Setor')['VAB_milhoes']
    st.bar_chart(chart_data)

# ==============================================================================
# INTERFACE PRINCIPAL - MAP FIRST
# ==============================================================================

# Cabeçalho
st.title("🗺️ Simulador Nacional de Impactos Econômicos")
st.markdown("**Análise espacial de choques econômicos nas 133 regiões intermediárias do Brasil**")

# Carregar dados
gdf = carregar_shapefile_nacional()
df_brasil = gerar_dados_mockados_brasil()

if gdf is None or df_brasil.empty:
    st.error("Erro ao carregar dados. Verifique os arquivos de dados.")
    st.stop()

# Inicializar estado da sessão
if 'selected_region' not in st.session_state:
    st.session_state.selected_region = None
if 'simulation_results' not in st.session_state:
    st.session_state.simulation_results = None

# Layout principal: 70% mapa, 30% painel de controle
col_mapa, col_painel = st.columns([0.7, 0.3])

# ==============================================================================
# COLUNA DO MAPA (70%)
# ==============================================================================

with col_mapa:
    st.subheader("🗺️ Mapa Interativo do Brasil")

    # Controles de camada
    layer_selecionada = st.selectbox(
        "📊 Camada de Visualização:",
        list(LAYER_CONFIGS.keys()),
        help="Selecione diferentes camadas para visualizar no mapa"
    )

    # Controle de fluxos econômicos
    mostrar_fluxos = st.checkbox(
        "🔗 Mostrar Fluxos Econômicos",
        value=False,
        help="Exibe linhas conectando a região de origem às 5 mais impactadas",
        disabled=(st.session_state.simulation_results is None)
    )

    st.caption(LAYER_CONFIGS[layer_selecionada]['description'])

    # Criar e exibir mapa
    mapa = criar_mapa_interativo(
        gdf,
        st.session_state.simulation_results,
        layer_selecionada,
        st.session_state.selected_region,
        mostrar_fluxos
    )

    map_data = st_folium(mapa, use_container_width=True, height=700)

    # Detectar clique no mapa
    if map_data and map_data.get('last_object_clicked_tooltip'):
        clicked_region = map_data['last_object_clicked_tooltip'].get('Região:')
        if clicked_region and clicked_region != st.session_state.selected_region:
            st.session_state.selected_region = clicked_region
            st.rerun()

# ==============================================================================
# PAINEL DE CONTROLE (30%)
# ==============================================================================

with col_painel:
    st.subheader("⚙️ Painel de Controle")

    # Dashboard da região selecionada
    mostrar_dashboard_regiao(st.session_state.selected_region, df_brasil)

    if st.session_state.selected_region:
        st.markdown("---")
        st.subheader("🎯 Simulação de Choque")

        # Controles de simulação
        setor_selecionado = st.selectbox(
            "Setor do Investimento:",
            setores,
            key='setor_select'
        )

        percentual_choque = st.slider(
            "Aumento na Demanda (% do VAB):",
            min_value=0.1,
            max_value=50.0,
            value=10.0,
            step=0.1,
            format="%.1f%%"
        )

        # Calcular valor do choque
        vab_base = df_brasil[
            (df_brasil['Região Intermediária'] == st.session_state.selected_region) &
            (df_brasil['Setor'] == setor_selecionado)
        ]['VAB_milhoes'].iloc[0]

        valor_choque_milhoes = vab_base * (percentual_choque / 100.0)

        st.info(f"💰 Choque: **R$ {valor_choque_milhoes:,.1f} milhões**")

        # Botão de simulação
        if st.button("🚀 Executar Simulação", type="primary", use_container_width=True):

            # Calcular impactos
            shock_vector = pd.Series(0.0, index=setores)
            shock_vector[setor_selecionado] = valor_choque_milhoes
            impacto_total_producao = calcular_impactos(matriz_a.values, shock_vector)

            # Processar resultados
            df_resultados = df_brasil.copy()
            df_resultados['Impacto_Producao_Setorial'] = df_resultados['Setor'].map(impacto_total_producao)
            df_resultados['Impacto_Producao_Regional'] = df_resultados['Impacto_Producao_Setorial'] * df_resultados['Share_VAB']
            df_resultados['Impacto_VAB_Regional'] = df_resultados['Impacto_Producao_Regional'] * df_resultados['Coef_VAB_Setor']
            df_resultados['Impacto_Impostos_Regional'] = df_resultados['Impacto_VAB_Regional'] * coef_impostos
            df_resultados['Impacto_Empregos_Gerados'] = df_resultados['Impacto_Producao_Regional'] * df_resultados['Coef_Emprego_por_Producao']

            # Agregar por região
            st.session_state.simulation_results = df_resultados.groupby('Região Intermediária').agg(
                Impacto_Producao=('Impacto_Producao_Regional', 'sum'),
                Impacto_VAB=('Impacto_VAB_Regional', 'sum'),
                Impacto_Impostos=('Impacto_Impostos_Regional', 'sum'),
                Impacto_Empregos=('Impacto_Empregos_Gerados', 'sum')
            ).reset_index()

            st.success("✅ Simulação concluída! Veja os resultados no mapa.")
            st.rerun()

    # Resultados da simulação
    if st.session_state.simulation_results is not None:
        st.markdown("---")
        st.subheader("📈 Resultados Nacionais")

        total_prod = st.session_state.simulation_results['Impacto_Producao'].sum()
        total_empregos = int(st.session_state.simulation_results['Impacto_Empregos'].sum())
        multiplicador = total_prod / valor_choque_milhoes if valor_choque_milhoes > 0 else 0

        st.metric("Impacto Total na Produção", f"R$ {total_prod:,.1f} M")
        st.metric("Empregos Gerados", f"{total_empregos:,}")
        st.metric("Multiplicador", f"{multiplicador:.2f}x")

        # Top 5 regiões mais impactadas
        st.write("**Top 5 Regiões Impactadas:**")
        top_5 = st.session_state.simulation_results.nlargest(5, 'Impacto_Producao')[['Região Intermediária', 'Impacto_Producao']]
        for idx, row in top_5.iterrows():
            st.write(f"• {row['Região Intermediária']}: R$ {row['Impacto_Producao']:,.1f} M")

    else:
        st.markdown("---")
        st.info("💡 Selecione uma região no mapa e execute uma simulação para ver os resultados.")

# ==============================================================================
# RODAPÉ INFORMATIVO
# ==============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
<small>
🔬 <strong>Modelo:</strong> Insumo-Produto de Leontief |
📊 <strong>Dados:</strong> 133 Regiões Intermediárias IBGE |
🗺️ <strong>Interface:</strong> Map First Design
</small>
</div>
""", unsafe_allow_html=True)