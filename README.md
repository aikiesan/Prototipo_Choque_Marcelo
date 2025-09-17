# 📊 Protótipo: Simulador de Impactos Econômicos para São Paulo

Uma aplicação web interativa desenvolvida em Streamlit para simular o impacto econômico de investimentos em setores específicos das regiões de São Paulo, utilizando a metodologia de Insumo-Produto de Leontief.

## 🎯 Funcionalidades

### 🧮 **Modelo Econômico Completo**
- **Impactos na Produção**: Efeitos diretos, indiretos e induzidos (metodologia Leontief)
- **PIB (VAB) por Região**: Cálculo do Valor Agregado Bruto gerado
- **Arrecadação de Impostos**: Estimativa da receita tributária (18% sobre VAB)
- **Geração de Empregos**: Aproximação de postos de trabalho criados

### 🗺️ **Interface Avançada**
- **Mapa Interativo**: Visualização geográfica com múltiplas simulações sobrepostas
- **Sidebar Colapsável**: Maximize o espaço do mapa quando necessário
- **Simulação Personalizada**: Configure região, setor e valor de investimento
- **Múltiplas Simulações**: Compare até 6 simulações simultaneamente com cores diferenciadas

### 📊 **Análise e Export**
- **Dashboard de Comparação**: Métricas lado a lado de diferentes simulações
- **Relatórios Completos**: Export CSV com todos os indicadores econômicos
- **Validação Técnica**: Aba dedicada aos parâmetros e matriz do modelo

## 📊 Dados Utilizados

- **Matriz Insumo-Produto**: IBGE/NEREUS-USP (2019) - 4 setores agregados
- **Dados Socioeconômicos**: Fundação SEADE/IBGE (2021)
- **Cobertura Geográfica**: 11 Regiões Geográficas Intermediárias de São Paulo
- **Setores**: Agropecuária, Indústria, Construção e Serviços

## 🚀 Como Executar

### Pré-requisitos
- Python 3.7+
- Bibliotecas: `streamlit`, `pandas`, `numpy`, `geopandas`, `folium`, `streamlit-folium`

### Instalação
```bash
# Clone o repositório
git clone https://github.com/aikiesan/Prototipo_Choque_Marcelo.git

# Entre no diretório
cd Prototipo_Choque_Marcelo

# Instale as dependências
pip install streamlit pandas numpy geopandas folium streamlit-folium

# Execute a aplicação
streamlit run app.py
```

## 🔧 Estrutura do Projeto

```
Prototipo_Choque_Marcelo/
│
├── app.py                 # Aplicação principal do Streamlit
├── shapefiles/            # Dados geográficos das regiões de SP
│   ├── Shapefile_Imediatas_SP.shp
│   └── ...
├── .gitignore            # Exclusões do Git
└── README.md             # Documentação do projeto
```

## 📈 Metodologia

O simulador utiliza o **Modelo de Insumo-Produto de Leontief** com os seguintes cálculos:

### 🎯 **Impactos Econômicos**
1. **Produção Total**: L × Y (onde L = matriz de Leontief, Y = vetor de choque)
2. **PIB (VAB)**: Produção × Coeficientes de VAB por setor
3. **Impostos**: VAB × Carga tributária (18%)
4. **Empregos**: Produção × Coeficiente de emprego (aproximação)

### 📍 **Regionalização Gravitacional**
- **Impacto Direto**: 100% do investimento inicial impacta a região de origem
- **Efeito Cascata**: Distribuído por proximidade geográfica × tamanho econômico
- **Modelo de Distância**: Baseado em centroides geográficos das regiões
- **Cobertura**: 133 Regiões Intermediárias do Brasil (IBGE, 2017)
- **Setores**: Agropecuária, Indústria, Construção, Serviços

### 🔢 **Coeficientes Técnicos (Estimativas Conservadoras)**
- **VAB/Produção por Setor**: Agropecuária (69.9%), Indústria (29.1%), Construção (98.5%), Serviços (57.3%)
- **Empregos por R$ Milhão**: Agropecuária (12.5), Indústria (8.1), Construção (17.6), Serviços (14.8)
- **Carga Tributária**: 18% sobre o VAB gerado  
- **Decaimento Espacial**: Exponencial com fator de atrito 1.0 (distribuição realista)
- **Binning de Classes**: Escala logarítmica para visualização clara
- **Base de Dados**: Tabela de Recursos e Usos (TRU) - IBGE 2017

## 🗺️ Visualizações

- **Mapa Interativo**: Choropleth com múltiplas simulações e cores diferenciadas
- **Dashboard de Métricas**: Produção, PIB (VAB), Impostos e Empregos
- **Ranking de Regiões**: Top 10 regiões mais impactadas
- **Comparação de Cenários**: Análise lado a lado de múltiplas simulações
- **Validação Técnica**: Matriz de Leontief e multiplicadores setoriais

## 🤝 Contribuições

Contribuições são bem-vindas! Por favor, abra uma issue ou envie um pull request.

## 📧 Contato

Para dúvidas ou sugestões sobre o projeto, entre em contato através do GitHub.

---
*Desenvolvido com ❤️ usando Streamlit e dados oficiais do Brasil*