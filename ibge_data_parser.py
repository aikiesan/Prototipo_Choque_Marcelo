#!/usr/bin/env python3
"""
Parser para dados municipais do IBGE em formato de largura fixa.
Processa dados de VAB por município e agrega por região imediata.
"""

import pandas as pd
import numpy as np
from pathlib import Path

def parse_ibge_municipal_data(file_path, target_year=2021):
    """
    Parse IBGE municipal data from fixed-width text format.

    Args:
        file_path: Path to the IBGE municipal data file
        target_year: Year to filter data (default: 2021)

    Returns:
        DataFrame with parsed municipal data
    """

    # Field definitions based on IBGE layout
    field_specs = [
        ('ano', 1, 4, int),
        ('codigo_regiao_imediata', 276, 281, int),
        ('nome_regiao_imediata', 283, 348, str),
        ('vab_agropecuaria', 821, 839, float),
        ('vab_industria', 840, 858, float),
        ('vab_servicos_exceto_admin', 859, 877, float),
        ('vab_admin_publica', 878, 896, float),
        ('vab_total', 897, 915, float)
    ]

    data = []

    print("Processando dados do IBGE...")

    with open(file_path, 'r', encoding='latin-1') as file:
        line_count = 0
        for line in file:
            line_count += 1
            if line_count % 10000 == 0:
                print(f"   Processadas {line_count:,} linhas...")

            # Parse each field according to position
            row = {}

            try:
                for field_name, start_pos, end_pos, field_type in field_specs:
                    # Extract field value (positions are 1-indexed in documentation)
                    value_str = line[start_pos-1:end_pos].strip()

                    if field_type == int:
                        row[field_name] = int(value_str) if value_str else 0
                    elif field_type == float:
                        # Handle decimal format (18.3 means 3 decimal places)
                        row[field_name] = float(value_str) / 1000 if value_str else 0.0  # Convert to millions
                    else:  # str
                        row[field_name] = value_str

                # Filter by target year
                if row['ano'] == target_year:
                    data.append(row)

            except (ValueError, IndexError) as e:
                print(f"   Erro na linha {line_count}: {e}")
                continue

    df = pd.DataFrame(data)
    print(f"Dados processados: {len(df):,} municipios para o ano {target_year}")

    return df

def aggregate_by_immediate_region(df_municipal):
    """
    Aggregate municipal data by immediate region (região imediata).

    Args:
        df_municipal: DataFrame with municipal data

    Returns:
        DataFrame aggregated by immediate region
    """

    print("Agregando dados por regiao imediata...")

    # Group by immediate region and sum VAB values
    df_regional = df_municipal.groupby(['codigo_regiao_imediata', 'nome_regiao_imediata']).agg({
        'vab_agropecuaria': 'sum',
        'vab_industria': 'sum',
        'vab_servicos_exceto_admin': 'sum',
        'vab_admin_publica': 'sum',
        'vab_total': 'sum'
    }).reset_index()

    # Clean region names (remove extra spaces)
    df_regional['nome_regiao_imediata'] = df_regional['nome_regiao_imediata'].str.strip()

    # Create sector aggregations compatible with Leontief model
    df_regional['vab_agropecuaria_final'] = df_regional['vab_agropecuaria']
    df_regional['vab_industria_final'] = df_regional['vab_industria']
    df_regional['vab_construcao_final'] = df_regional['vab_industria'] * 0.15  # Estimate construction from industry
    df_regional['vab_servicos_final'] = df_regional['vab_servicos_exceto_admin'] + df_regional['vab_admin_publica']

    print(f"Agregacao concluida: {len(df_regional)} regioes imediatas")

    return df_regional

def normalize_region_name(name):
    """Normalize region names for better matching."""
    import unicodedata

    # Convert to string and strip whitespace
    name = str(name).strip()

    # Normalize unicode characters (remove accents)
    name_normalized = unicodedata.normalize('NFD', name)
    name_normalized = ''.join(char for char in name_normalized if unicodedata.category(char) != 'Mn')

    # Convert to lowercase for comparison
    name_normalized = name_normalized.lower()

    return name_normalized

def find_best_region_match(target_region, available_regions):
    """Find the best match for a region name using fuzzy matching."""
    target_normalized = normalize_region_name(target_region)

    # First try exact match
    for region, data in available_regions.items():
        if normalize_region_name(region) == target_normalized:
            return data

    # Then try substring match
    for region, data in available_regions.items():
        region_normalized = normalize_region_name(region)
        if target_normalized in region_normalized or region_normalized in target_normalized:
            return data

    # No match found
    return None

def load_official_regions():
    """Load the official regions list with corrected encoding."""
    return pd.read_csv("regioes_oficiais_510_corrected.csv")

def create_compatible_economic_data(df_regional, gdf):
    """
    Create economic data compatible with existing Leontief model structure.
    Uses official region mapping for improved accuracy.

    Args:
        df_regional: DataFrame with regional VAB data
        gdf: GeoDataFrame with regional geometries

    Returns:
        DataFrame compatible with existing model
    """

    print("Criando base de dados compativel com mapeamento oficial...")

    # Load official regions mapping
    df_official = load_official_regions()

    # Map to match the 4-sector Leontief model
    setores = ['Agropecuária', 'Indústria', 'Construção', 'Serviços']

    dados = []

    # Create mapping between IBGE region codes and data
    ibge_code_mapping = {}
    for _, row in df_regional.iterrows():
        region_code = str(int(row['codigo_regiao_imediata'])).zfill(6)  # Ensure 6-digit format
        ibge_code_mapping[region_code] = row

    # Create mapping between official region names and codes
    official_name_to_code = {}
    for _, row in df_official.iterrows():
        official_name_to_code[str(row['nome_regiao']).strip()] = str(row['codigo_regiao']).strip()

    # Track matches and misses
    matched_regions = 0
    unmatched_regions = []

    # Process each region in the shapefile
    for regiao_geo in gdf['NM_RGINT'].tolist():
        regiao_geo_clean = str(regiao_geo).strip()

        # Get the official region code for this region name
        region_code = official_name_to_code.get(regiao_geo_clean)

        if region_code and region_code in ibge_code_mapping:
            # Found exact match using region codes
            matched_regions += 1
            vab_data = ibge_code_mapping[region_code]
            vab_values = {
                'Agropecuária': float(vab_data['vab_agropecuaria_final']),
                'Indústria': float(vab_data['vab_industria_final']),
                'Construção': float(vab_data['vab_construcao_final']),
                'Serviços': float(vab_data['vab_servicos_final'])
            }
        else:
            unmatched_regions.append(regiao_geo_clean)
            # Use median values as fallback
            vab_values = {
                'Agropecuária': df_regional['vab_agropecuaria_final'].median(),
                'Indústria': df_regional['vab_industria_final'].median(),
                'Construção': df_regional['vab_construcao_final'].median(),
                'Serviços': df_regional['vab_servicos_final'].median()
            }

        for setor in setores:
            vab = vab_values[setor]

            dados.append({
                'regiao': regiao_geo_clean,
                'setor': setor,
                'vab': float(vab),
                'empregos': float(vab * np.random.uniform(15, 25)),  # Keep employment estimation for now
                'empresas': int(vab * np.random.uniform(0.5, 2.0))  # Keep company estimation for now
            })

    df = pd.DataFrame(dados)

    # Calculate national shares (for Leontief model)
    df['share_nacional'] = df.groupby('setor')['vab'].transform(lambda x: x / x.sum())

    print(f"Base compativel criada: {len(df)} entradas (4 setores x {len(gdf)} regioes)")
    print(f"Regioes correspondidas com codigos oficiais: {matched_regions}/{len(gdf)} ({matched_regions/len(gdf)*100:.1f}%)")

    if unmatched_regions:
        print(f"Regioes nao correspondidas ({len(unmatched_regions)}): {unmatched_regions[:10]}...")

    return df

if __name__ == "__main__":
    # Test the parser
    file_path = "PIB dos Municípios - base de dados 2010-2021.txt"

    if Path(file_path).exists():
        df_municipal = parse_ibge_municipal_data(file_path, 2021)
        df_regional = aggregate_by_immediate_region(df_municipal)

        print("\nPrimeiras 5 regioes:")
        print(df_regional.head())

        print(f"\nTotal VAB nacional: R$ {df_regional['vab_total'].sum():,.0f} milhoes")
    else:
        print(f"Arquivo nao encontrado: {file_path}")