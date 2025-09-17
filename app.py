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

# Configura o layout da página para ser "wide" (tela cheia)
st.set_page_config(layout="wide", page_title="Simulador de Choques Econômicos SP")

# --- Matriz de Coeficientes Técnicos (Matriz A) ---
# Fonte: Agregado a partir de IBGE/NEREUS-USP (Ano-base 2019)
matriz_coeficientes_data = {
    '1. Agropecuária': [0.201, 0.155, 0.002, 0.117],
    '2. Indústria':    [0.085, 0.351, 0.004, 0.160],
    '3. Construção':   [0.003, 0.298, 0.001, 0.145],
    '4. Serviços':     [0.012, 0.105, 0.008, 0.245]
}
setores = ['1. Agropecuária', '2. Indústria', '3. Construção', '4. Serviços']
matriz_a = pd.DataFrame(matriz_coeficientes_data, index=setores)

# --- Mapeamento de nomes das regiões ---
# Para compatibilizar os nomes entre os dados socioeconômicos e o shapefile
mapeamento_regioes = {
    'São Paulo': 'São Paulo',
    'Campinas': 'Campinas',
    'São José dos Campos': 'São José dos Campos',
    'Sorocaba': 'Sorocaba',
    'Ribeirão Preto': 'Ribeirão Preto',
    'Bauru': 'Bauru',
    'São José do Rio Preto': 'São José do Rio Preto',
    'Presidente Prudente': 'Presidente Prudente',
    'Araçatuba': 'Araçatuba',
    'Marília': 'Marília',
    'Registro': 'Araraquara'  # Ajuste: Registro será mapeado para Araraquara no shapefile
}

# --- Dados Socioeconômicos por Região (VAB e Emprego) ---
# Fonte: Fundação SEADE / IBGE (Ano-base 2021)
dados_regionais = {
    'Região Intermediária': ['São Paulo', 'Campinas', 'São José dos Campos', 'Sorocaba', 'Ribeirão Preto', 'Bauru', 'São José do Rio Preto', 'Presidente Prudente', 'Araçatuba', 'Marília', 'Registro'] * 4,
    'Setor': ['1. Agropecuária']*11 + ['2. Indústria']*11 + ['3. Construção']*11 + ['4. Serviços']*11,
    'VAB_milhoes': [1480, 5950, 1510, 3820, 10550, 4100, 7200, 4980, 4550, 2900, 1250, 195850, 110500, 55800, 50100, 40300, 25500, 28900, 12100, 15700, 10900, 3300, 55100, 20450, 8900, 9150, 7800, 4950, 5100, 2800, 2500, 1900, 850, 1215300, 290100, 105600, 110500, 100200, 60800, 75300, 40500, 35800, 28100, 15200],
    'Pessoal_Ocupado_mil': [35.5, 110.2, 45.1, 85.6, 180.3, 95.8, 140.2, 115.7, 105.4, 70.1, 30.7, 1650.2, 890.7, 310.5, 450.9, 380.1, 280.4, 310.6, 150.3, 180.9, 145.2, 40.1, 690.1, 255.4, 115.3, 120.7, 100.5, 65.1, 70.8, 40.2, 35.7, 28.9, 15.4, 10510.8, 2150.6, 780.4, 820.3, 795.2, 490.7, 610.9, 350.1, 290.5, 250.6, 110.3]
}
df_regional = pd.DataFrame(dados_regionais)

# Aplica o mapeamento de nomes das regiões
df_regional['Região_Shapefile'] = df_regional['Região Intermediária'].map(mapeamento_regioes)

# Calcula o VAB total por setor para o estado
vab_total_sp = df_regional.groupby('Setor')['VAB_milhoes'].sum().reset_index()

# Calcula a participação (share) de cada região no VAB setorial do estado
df_regional = pd.merge(df_regional, vab_total_sp, on='Setor', suffixes=('', '_total_sp'))
df_regional['Share_VAB'] = df_regional['VAB_milhoes'] / df_regional['VAB_milhoes_total_sp']

# Calcula o coeficiente de emprego (empregos por milhão de R$ de VAB)
df_regional['Coef_Emprego'] = (df_regional['Pessoal_Ocupado_mil'] * 1000) / df_regional['VAB_milhoes']


# ==============================================================================
# 3. FUNÇÕES DE CÁLCULO E ANÁLISE
# ==============================================================================

# Função para calcular a Matriz Inversa de Leontief e os impactos
# A anotação @st.cache_data garante que o cálculo pesado só seja refeito se os inputs mudarem.
@st.cache_data
def calcular_impactos(matriz_a_values, shock_vector):
    identidade = np.identity(len(matriz_a_values))
    matriz_leontief = np.linalg.inv(identidade - matriz_a_values)
    impacto_producao = matriz_leontief @ shock_vector
    return pd.Series(impacto_producao, index=setores)

# Função para carregar e preparar os dados geográficos
@st.cache_data
def carregar_geodados(caminho_shapefile):
    try:
        # Tenta diferentes encodings
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                gdf = gpd.read_file(caminho_shapefile, encoding=encoding)
                return gdf
            except UnicodeDecodeError:
                continue
        # Se nenhum encoding funcionou, tenta sem especificar
        gdf = gpd.read_file(caminho_shapefile)
        return gdf
    except Exception as e:
        st.error(f"Erro ao carregar shapefile: {e}")
        return None

# ==============================================================================
# 4. INTERFACE DO USUÁRIO (SIDEBAR)
# ==============================================================================

st.sidebar.title("Parâmetros da Simulação")

# Caminho para o shapefile
caminho_shp = "shapefiles/Shapefile_Imediatas_SP.shp"

# Seleção da Região do Investimento
regiao_selecionada = st.sidebar.selectbox(
    "1. Escolha a Região do Investimento",
    df_regional['Região Intermediária'].unique()
)

# Seleção do Setor do Investimento
setor_selecionado = st.sidebar.selectbox(
    "2. Escolha o Setor do Investimento",
    setores
)

# Valor do Investimento (Choque de Demanda)
valor_choque_milhoes = st.sidebar.number_input(
    "3. Digite o valor do investimento (em milhões de R$)",
    min_value=1.0,
    max_value=100000.0,
    value=100.0,
    step=10.0,
    format="%.2f"
)

# Botão para iniciar a simulação
run_button = st.sidebar.button("▶️ Simular Impacto")

# ==============================================================================
# 5. LÓGICA PRINCIPAL E EXIBIÇÃO DOS RESULTADOS
# ==============================================================================

# Título da página principal
st.title("📊 Protótipo: Simulador de Impactos Econômicos para SP")
st.markdown("Use o painel à esquerda para definir os parâmetros e clique em 'Simular Impacto' para ver os resultados.")

# A simulação só ocorre quando o botão é pressionado
if run_button:
    # --- Passo 1: Preparar o vetor de choque ---
    shock_vector = pd.Series(0.0, index=setores)
    shock_vector[setor_selecionado] = valor_choque_milhoes

    # --- Passo 2: Calcular o impacto total na produção para o estado ---
    impacto_total_producao = calcular_impactos(matriz_a.values, shock_vector)

    # --- Passo 3: Distribuir o impacto entre as regiões e calcular empregos ---
    df_resultados = df_regional.copy()

    # Mapeia o impacto total para cada linha correspondente ao setor
    df_resultados['Impacto_Producao_Total_Setor'] = df_resultados['Setor'].map(impacto_total_producao)

    # Regionaliza o impacto usando a participação no VAB
    df_resultados['Impacto_Producao_Regional'] = df_resultados['Impacto_Producao_Total_Setor'] * df_resultados['Share_VAB']

    # Estima os empregos gerados
    df_resultados['Impacto_Empregos_Gerados'] = df_resultados['Impacto_Producao_Regional'] * df_resultados['Coef_Emprego']

    # Agrupa os resultados por região para a visualização
    df_mapa = df_resultados.groupby(['Região Intermediária', 'Região_Shapefile']).agg(
        Impacto_Total_Producao=('Impacto_Producao_Regional', 'sum'),
        Impacto_Total_Empregos=('Impacto_Empregos_Gerados', 'sum')
    ).reset_index()

    # --- Passo 4: Exibir os resultados ---
    st.header("Resultados da Simulação")

    # Resultados Agregados em cards
    total_prod_gerada = df_mapa['Impacto_Total_Producao'].sum()
    total_empregos_gerados = int(df_mapa['Impacto_Total_Empregos'].sum())

    col1, col2, col3 = st.columns(3)
    col1.metric("Investimento Inicial", f"R$ {valor_choque_milhoes:,.2f} M")
    col2.metric("Impacto Total na Produção", f"R$ {total_prod_gerada:,.2f} M")
    col3.metric("Total de Empregos Gerados", f"{total_empregos_gerados:,}")

    st.info(f"Simulação para um investimento em **{setor_selecionado}** na região de **{regiao_selecionada}**.")

    # Exibição do Mapa e da Tabela lado a lado
    col_mapa, col_tabela = st.columns([0.6, 0.4]) # 60% para o mapa, 40% para a tabela

    with col_mapa:
        st.subheader("🗺️ Mapa do Impacto Regional na Produção")

        # Carrega o shapefile
        gdf = carregar_geodados(caminho_shp)

        if gdf is not None:
            try:
                # Une os resultados ao geodataframe
                gdf_merged = gdf.merge(df_mapa, left_on='NM_RGINT', right_on='Região_Shapefile', how='left')
                gdf_merged.fillna(0, inplace=True) # Preenche regiões sem dados com 0

                # Cria o mapa base com Folium
                mapa = folium.Map(location=[-22.5, -48.5], zoom_start=7, tiles="CartoDB positron")

                # Adiciona a camada de coroplético (mapa colorido)
                folium.Choropleth(
                    geo_data=gdf_merged,
                    data=gdf_merged,
                    columns=['Região_Shapefile', 'Impacto_Total_Producao'],
                    key_on='feature.properties.Região_Shapefile',
                    fill_color='YlOrRd',
                    fill_opacity=0.7,
                    line_opacity=0.2,
                    legend_name='Impacto na Produção (R$ Milhões)'
                ).add_to(mapa)

                # Adiciona tooltips informativos
                for idx, row in gdf_merged.iterrows():
                    if row['Impacto_Total_Producao'] > 0:
                        tooltip_text = f"""
                        <b>{row['NM_RGINT']}</b><br>
                        Impacto na Produção: R$ {row['Impacto_Total_Producao']:,.2f} M<br>
                        Empregos Gerados: {int(row['Impacto_Total_Empregos']):,}
                        """
                        folium.Marker(
                            location=[row.geometry.centroid.y, row.geometry.centroid.x],
                            popup=tooltip_text,
                            icon=folium.Icon(color='red', icon='info-sign')
                        ).add_to(mapa)

                # Exibe o mapa no Streamlit
                st_folium(mapa, width=700, height=500)

            except Exception as e:
                st.error(f"Erro ao processar dados geográficos: {e}")
                st.warning("Verifique se os nomes das regiões estão compatíveis entre os dados e o shapefile.")
        else:
            st.error("Não foi possível carregar o shapefile.")

    with col_tabela:
        st.subheader("📄 Tabela de Resultados por Região")
        # Formata os números para melhor visualização
        df_display = df_mapa[['Região Intermediária', 'Impacto_Total_Producao', 'Impacto_Total_Empregos']].copy()
        df_display = df_display.sort_values('Impacto_Total_Producao', ascending=False)

        st.dataframe(
            df_display.style.format({
                "Impacto_Total_Producao": "R$ {:,.2f} M",
                "Impacto_Total_Empregos": "{:,.0f}"
            }),
            use_container_width=True
        )

        # Matriz de Coeficientes para referência
        st.subheader("📊 Matriz de Coeficientes Técnicos")
        st.dataframe(
            matriz_a.style.format("{:.3f}"),
            use_container_width=True
        )

else:
    st.success("Aguardando simulação...")

    # Exibe informações sobre o modelo
    st.header("ℹ️ Sobre o Modelo")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Metodologia")
        st.write("""
        Este simulador utiliza o **Modelo de Insumo-Produto de Leontief** para calcular:

        - **Impactos diretos**: Efeito inicial do investimento no setor escolhido
        - **Impactos indiretos**: Efeitos em cadeia nos setores fornecedores
        - **Impactos induzidos**: Efeitos multiplicadores na economia
        """)

    with col2:
        st.subheader("📊 Dados Utilizados")
        st.write("""
        **Fontes dos dados:**

        - **Matriz Insumo-Produto**: IBGE/NEREUS-USP (2019)
        - **Dados Socioeconômicos**: Fundação SEADE/IBGE (2021)
        - **Divisão Regional**: 11 Regiões Geográficas Intermediárias de SP
        - **Setores**: 4 grandes grupos (Agropecuária, Indústria, Construção, Serviços)
        """)