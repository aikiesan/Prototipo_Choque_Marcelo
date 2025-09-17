# 📊 Protótipo: Simulador de Impactos Econômicos para São Paulo

Uma aplicação web interativa desenvolvida em Streamlit para simular o impacto econômico de investimentos em setores específicos das regiões de São Paulo, utilizando a metodologia de Insumo-Produto de Leontief.

## 🎯 Funcionalidades

- **Simulação de Choques Econômicos**: Calcule o impacto de um investimento em qualquer setor e região
- **Visualização Geográfica**: Mapa interativo mostrando os impactos regionais
- **Cálculos Automáticos**: Impactos diretos, indiretos e induzidos na produção e emprego
- **Interface Intuitiva**: Parâmetros configuráveis via sidebar

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

O simulador utiliza o **Modelo de Insumo-Produto de Leontief** para calcular:

1. **Impactos Diretos**: Efeito inicial do investimento no setor escolhido
2. **Impactos Indiretos**: Efeitos em cadeia nos setores fornecedores
3. **Impactos Induzidos**: Efeitos multiplicadores na economia

A regionalização dos impactos é feita através da participação de cada região no VAB setorial do estado.

## 🗺️ Visualizações

- **Mapa Coroplético**: Intensidade do impacto por região
- **Tabelas Interativas**: Resultados detalhados por região e setor
- **Métricas Resumidas**: Totais de produção e emprego gerados

## 🤝 Contribuições

Contribuições são bem-vindas! Por favor, abra uma issue ou envie um pull request.

## 📧 Contato

Para dúvidas ou sugestões sobre o projeto, entre em contato através do GitHub.

---
*Desenvolvido com ❤️ usando Streamlit e dados oficiais do Brasil*