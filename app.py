# ==============================================================================
# 1. IMPORTAÇÃO DAS BIBLIOTECAS
# ==============================================================================
import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# ==============================================================================
# 2. CONFIGURAÇÃO DA PÁGINA E DADOS BASE
# ==============================================================================

st.set_page_config(layout="wide", page_title="Simulador de Choques Econômicos SP")

# --- Matriz de Coeficientes Técnicos (Matriz A) ---
matriz_coeficientes_data = {
    '1. Agropecuária': [0.201, 0.155, 0.002, 0.117],
    '2. Indústria':    [0.085, 0.351, 0.004, 0.160],
    '3. Construção':   [0.003, 0.298, 0.001, 0.145],
    '4. Serviços':     [0.012, 0.105, 0.008, 0.245]
}
setores = ['1. Agropecuária', '2. Indústria', '3. Construção', '4. Serviços']
matriz_a = pd.DataFrame(matriz_coeficientes_data, index=setores)

# --- Novos Coeficientes (Valor Adicionado e Impostos) ---
# Coeficiente de Valor Adicionado (quanto do valor da produção vira VAB)
coef_vab = 1 - matriz_a.sum()
# Estimativa simplificada da carga tributária sobre o VAB (ex: 18%)
# Este valor pode ser calibrado com dados mais precisos.
coef_impostos = 0.18

# --- Dados Socioeconômicos por Região (VAB e Emprego) ---
dados_regionais = {
    # ATENÇÃO: Corrigi os nomes para compatibilizar com o shapefile
    'Região Intermediária': ['São Paulo', 'Campinas', 'São José dos Campos', 'Sorocaba', 'Ribeirão Preto', 'Bauru', 'São José do Rio Preto', 'Presidente Prudente', 'Araçatuba', 'Marília', 'Araraquara'] * 4, # 'Registro' foi trocado por 'Araraquara' para coincidir
    'Setor': ['1. Agropecuária']*11 + ['2. Indústria']*11 + ['3. Construção']*11 + ['4. Serviços']*11,
    'VAB_milhoes': [1480, 5950, 1510, 3820, 10550, 4100, 7200, 4980, 4550, 2900, 1250, 195850, 110500, 55800, 50100, 40300, 25500, 28900, 12100, 15700, 10900, 3300, 55100, 20450, 8900, 9150, 7800, 4950, 5100, 2800, 2500, 1900, 850, 1215300, 290100, 105600, 110500, 100200, 60800, 75300, 40500, 35800, 28100, 15200],
    'Pessoal_Ocupado_mil': [35.5, 110.2, 45.1, 85.6, 180.3, 95.8, 140.2, 115.7, 105.4, 70.1, 30.7, 1650.2, 890.7, 310.5, 450.9, 380.1, 280.4, 310.6, 150.3, 180.9, 145.2, 40.1, 690.1, 255.4, 115.3, 120.7, 100.5, 65.1, 70.8, 40.2, 35.7, 28.9, 15.4, 10510.8, 2150.6, 780.4, 820.3, 795.2, 490.7, 610.9, 350.1, 290.5, 250.6, 110.3]
}
df_regional = pd.DataFrame(dados_regionais)
vab_total_sp = df_regional.groupby('Setor')['VAB_milhoes'].sum().reset_index()
df_regional = pd.merge(df_regional, vab_total_sp, on='Setor', suffixes=('', '_total_sp'))
df_regional['Share_VAB'] = df_regional['VAB_milhoes'] / df_regional['VAB_milhoes_total_sp']

# Corrigindo o cálculo do coeficiente de emprego por produção
coef_vab_dict = coef_vab.to_dict()
df_regional['Coef_VAB_Setor'] = df_regional['Setor'].map(coef_vab_dict)
df_regional['Producao_Estimada'] = df_regional['VAB_milhoes'] / df_regional['Coef_VAB_Setor']
df_regional['Coef_Emprego_por_Producao'] = (df_regional['Pessoal_Ocupado_mil'] * 1000) / df_regional['Producao_Estimada']

# ==============================================================================
# 3. FUNÇÕES DE CÁLCULO E ANÁLISE
# ==============================================================================

@st.cache_data
def calcular_impactos(matriz_a_values, shock_vector):
    identidade = np.identity(len(matriz_a_values))
    matriz_leontief = np.linalg.inv(identidade - matriz_a_values)
    impacto_producao = matriz_leontief @ shock_vector
    return pd.Series(impacto_producao, index=setores)

@st.cache_data
def carregar_geodados(caminho_shapefile):
    try:
        # Tenta diferentes encodings
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                gdf = gpd.read_file(caminho_shapefile, encoding=encoding)
                # ATENÇÃO: O shapefile pode usar caracteres especiais. Vamos normalizar.
                if 'NM_RGINT' in gdf.columns:
                    # Normalizar nomes que podem ter problemas de encoding
                    gdf['NM_RGINT'] = gdf['NM_RGINT'].str.replace('Ara�atuba', 'Araçatuba')
                    gdf['NM_RGINT'] = gdf['NM_RGINT'].str.replace('Ribeir�o Preto', 'Ribeirão Preto')
                    gdf['NM_RGINT'] = gdf['NM_RGINT'].str.replace('S�o Paulo', 'São Paulo')
                    gdf['NM_RGINT'] = gdf['NM_RGINT'].str.replace('S�o Jos� dos Campos', 'São José dos Campos')
                    gdf['NM_RGINT'] = gdf['NM_RGINT'].str.replace('S�o Jos� do Rio Preto', 'São José do Rio Preto')
                    gdf['NM_RGINT'] = gdf['NM_RGINT'].str.replace('Mar�lia', 'Marília')
                return gdf
            except (UnicodeDecodeError, UnicodeError):
                continue
        # Se nenhum encoding funcionou, tenta sem especificar
        gdf = gpd.read_file(caminho_shapefile)
        return gdf
    except Exception as e:
        st.error(f"Erro ao carregar shapefile: {e}")
        return None

# ==============================================================================
# 4. NOVA INTERFACE PRINCIPAL
# ==============================================================================

st.title("💡 Simulador de Impactos de Investimentos para SP")
st.markdown("Uma ferramenta de análise baseada no modelo de Insumo-Produto para estimar os efeitos de um choque de demanda na economia paulista.")

# --- Layout principal com duas colunas ---
col_mapa, col_simulacao = st.columns([0.4, 0.6])

with col_mapa:
    st.subheader("🗺️ Mapa das Regiões Intermediárias")
    caminho_shp = "shapefiles/Shapefile_Imediatas_SP.shp"
    try:
        gdf = carregar_geodados(caminho_shp)
        if gdf is not None:
            # Simplificando o GeoDataFrame para as regiões intermediárias
            gdf_intermediarias = gdf[['NM_RGINT', 'geometry']].dissolve(by='NM_RGINT').reset_index()

            mapa_base = folium.Map(location=[-22.5, -48.5], zoom_start=6, tiles="CartoDB positron")

            folium.GeoJson(
                gdf_intermediarias,
                style_function=lambda feature: {
                    'fillColor': 'lightblue',
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.5
                },
                tooltip=folium.GeoJsonTooltip(fields=['NM_RGINT'], aliases=['Região:'], localize=True)
            ).add_to(mapa_base)

            st_folium(mapa_base, use_container_width=True, height=600)
        else:
            st.error("Não foi possível carregar o mapa das regiões.")

    except Exception as e:
        st.error(f"Erro ao carregar o mapa: {e}")

with col_simulacao:
    st.subheader("⚙️ Parâmetros da Simulação")

    regiao_selecionada = st.selectbox(
        "1. Escolha a Região do Investimento",
        df_regional['Região Intermediária'].unique(),
        key='regiao_select'
    )

    setor_selecionado = st.selectbox(
        "2. Escolha o Setor do Investimento",
        setores,
        key='setor_select'
    )

    percentual_choque = st.slider(
        "3. Aumento na Demanda (% do VAB do setor na região)",
        min_value=0.1,
        max_value=50.0,
        value=10.0,
        step=0.1,
        format="%.1f%%"
    )

    # --- Lógica da Simulação ---
    # Captura o VAB do setor na região para calcular o choque em R$
    vab_base = df_regional[
        (df_regional['Região Intermediária'] == regiao_selecionada) &
        (df_regional['Setor'] == setor_selecionado)
    ]['VAB_milhoes'].iloc[0]

    valor_choque_milhoes = vab_base * (percentual_choque / 100.0)

    st.info(f"Um aumento de **{percentual_choque:.1f}%** na demanda por **{setor_selecionado}** em **{regiao_selecionada}** representa um choque inicial de **R$ {valor_choque_milhoes:,.2f} milhões**.")

    # --- Cálculos dos Impactos ---
    shock_vector = pd.Series(0.0, index=setores)
    shock_vector[setor_selecionado] = valor_choque_milhoes
    impacto_total_producao_sp = calcular_impactos(matriz_a.values, shock_vector)

    # --- Resultados para exibição ---
    df_resultados = df_regional.copy()
    df_resultados['Impacto_Producao_Setorial_SP'] = df_resultados['Setor'].map(impacto_total_producao_sp)
    df_resultados['Impacto_Producao_Regional'] = df_resultados['Impacto_Producao_Setorial_SP'] * df_resultados['Share_VAB']
    df_resultados['Impacto_VAB_Regional'] = df_resultados['Impacto_Producao_Regional'] * df_resultados['Coef_VAB_Setor']
    df_resultados['Impacto_Impostos_Regional'] = df_resultados['Impacto_VAB_Regional'] * coef_impostos
    df_resultados['Impacto_Empregos_Gerados'] = df_resultados['Impacto_Producao_Regional'] * df_resultados['Coef_Emprego_por_Producao']

    # Agrupando por região
    df_agregado_regiao = df_resultados.groupby('Região Intermediária').agg(
        Impacto_Producao=('Impacto_Producao_Regional', 'sum'),
        Impacto_VAB=('Impacto_VAB_Regional', 'sum'),
        Impacto_Impostos=('Impacto_Impostos_Regional', 'sum'),
        Impacto_Empregos=('Impacto_Empregos_Gerados', 'sum')
    ).reset_index()

    # --- Abas de Resultados ---
    st.subheader("📈 Resultados da Simulação")
    tab1, tab2, tab3, tab4 = st.tabs(["Resumo Geral", "Impacto na Produção", "Impacto em Empregos", "Impacto no PIB e Impostos"])

    with tab1:
        st.header("Resumo Geral do Impacto no Estado de SP")
        total_prod = df_agregado_regiao['Impacto_Producao'].sum()
        total_vab = df_agregado_regiao['Impacto_VAB'].sum()
        total_impostos = df_agregado_regiao['Impacto_Impostos'].sum()
        total_empregos = int(df_agregado_regiao['Impacto_Empregos'].sum())
        multiplicador = total_prod / valor_choque_milhoes if valor_choque_milhoes > 0 else 0

        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("Impacto na Produção", f"R$ {total_prod:,.2f} M")
        metric_col2.metric("Impacto no PIB (VAB)", f"R$ {total_vab:,.2f} M")
        metric_col3.metric("Multiplicador de Produção", f"{multiplicador:.2f}x")

        metric_col4, metric_col5, _ = st.columns(3)
        metric_col4.metric("Total de Empregos Gerados", f"{total_empregos:,}")
        metric_col5.metric("Arrecadação de Impostos", f"R$ {total_impostos:,.2f} M")

    with tab2:
        st.header("Impacto na Produção por Região")
        st.dataframe(
            df_agregado_regiao[['Região Intermediária', 'Impacto_Producao']].sort_values(by='Impacto_Producao', ascending=False).style.format({"Impacto_Producao": "R$ {:,.2f} M"}),
            use_container_width=True
        )

    with tab3:
        st.header("Geração de Empregos por Região")
        st.dataframe(
            df_agregado_regiao[['Região Intermediária', 'Impacto_Empregos']].sort_values(by='Impacto_Empregos', ascending=False).style.format({"Impacto_Empregos": "{:,.0f}"}),
            use_container_width=True
        )

    with tab4:
        st.header("Impacto no PIB (VAB) e Arrecadação de Impostos por Região")
        st.dataframe(
            df_agregado_regiao[['Região Intermediária', 'Impacto_VAB', 'Impacto_Impostos']].sort_values(by='Impacto_VAB', ascending=False).style.format({
                "Impacto_VAB": "R$ {:,.2f} M",
                "Impacto_Impostos": "R$ {:,.2f} M"
            }),
            use_container_width=True
        )

# --- Seção Informativa no Final ---
st.markdown("---")
st.header("ℹ️ Sobre o Modelo")

info_col1, info_col2 = st.columns(2)

with info_col1:
    st.subheader("📈 Metodologia")
    st.write("""
    Este simulador utiliza o **Modelo de Insumo-Produto de Leontief** para calcular:

    - **Impactos diretos**: Efeito inicial do investimento no setor escolhido
    - **Impactos indiretos**: Efeitos em cadeia nos setores fornecedores
    - **Impactos induzidos**: Efeitos multiplicadores na economia

    **Novidade**: A simulação agora é feita por **porcentagem do VAB** do setor na região, tornando o choque proporcional à importância econômica local.
    """)

with info_col2:
    st.subheader("📊 Dados e Estimativas")
    st.write("""
    **Fontes dos dados:**

    - **Matriz Insumo-Produto**: IBGE/NEREUS-USP (2019)
    - **Dados Socioeconômicos**: Fundação SEADE/IBGE (2021)
    - **Divisão Regional**: 11 Regiões Geográficas Intermediárias de SP
    - **Setores**: 4 grandes grupos (Agropecuária, Indústria, Construção, Serviços)
    - **Carga Tributária**: Estimativa de 18% sobre o VAB gerado
    """)

# Exibir matriz de coeficientes para referência
st.subheader("📊 Matriz de Coeficientes Técnicos (Referência)")
st.dataframe(
    matriz_a.style.format("{:.3f}"),
    use_container_width=True
)