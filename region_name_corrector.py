#!/usr/bin/env python3
"""
Script para corrigir nomes de regiões usando a lista oficial do IBGE.
Resolve problemas de encoding e duplicatas usando códigos oficiais.
"""

import pandas as pd
import geopandas as gpd
import numpy as np
from pathlib import Path
import unicodedata


def parse_official_regions_csv(csv_path):
    """
    Parse the official CSV list of 510 immediate regions with proper encoding.

    Args:
        csv_path: Path to the official CSV file

    Returns:
        DataFrame with official region names and codes
    """

    print("Carregando lista oficial de regioes...")

    # Try different encodings to handle the CSV properly
    encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

    df = None
    for encoding in encodings_to_try:
        try:
            df = pd.read_csv(csv_path, encoding=encoding)
            print(f"Arquivo carregado com encoding: {encoding}")
            break
        except (UnicodeDecodeError, UnicodeError):
            continue

    if df is None:
        raise ValueError(f"Nao foi possivel carregar o arquivo com nenhum encoding testado")

    print(f"Colunas encontradas: {list(df.columns)}")
    print(f"Primeiras linhas:")
    print(df.head())

    # The structure appears to be:
    # Column 7 (index 7): Region name
    # Column 8 (index 8): Region code
    # Let's identify the correct columns

    region_data = []

    for idx, row in df.iterrows():
        # Skip header row
        if idx == 0:
            continue

        try:
            # Based on CSV structure analysis:
            # Column 7 (index 7): Immediate region name
            # Column 8 (index 8): Immediate region code (6 digits)

            region_name = row.iloc[7] if len(row) > 7 else None
            region_code = row.iloc[8] if len(row) > 8 else None

            # Validate that we have both name and code
            if pd.notna(region_name) and pd.notna(region_code):
                region_name = str(region_name).strip()
                region_code = str(region_code).strip()

                # Validate that code is 6 digits
                if region_code.isdigit() and len(region_code) == 6:
                    # Clean and normalize the region name
                    region_name_clean = clean_region_name(region_name)

                    region_data.append({
                        'codigo_regiao': region_code,
                        'nome_oficial': region_name_clean,
                        'nome_original': region_name
                    })

        except Exception as e:
            print(f"Erro ao processar linha {idx}: {e}")
            continue

    df_regions = pd.DataFrame(region_data)

    print(f"\nRegioes processadas: {len(df_regions)}")
    print(f"Primeiras regioes:")
    print(df_regions.head(10))

    # Check for duplicates
    duplicates = df_regions[df_regions.duplicated(subset=['nome_oficial'], keep=False)]
    if len(duplicates) > 0:
        print(f"\nRegioes duplicadas encontradas:")
        for name in duplicates['nome_oficial'].unique():
            dup_regions = duplicates[duplicates['nome_oficial'] == name]
            print(f"  {name}: codigos {', '.join(dup_regions['codigo_regiao'].tolist())}")

    return df_regions


def clean_region_name(name):
    """
    Clean and normalize region names, fixing encoding issues.

    Args:
        name: Raw region name

    Returns:
        Cleaned region name
    """

    if pd.isna(name):
        return ""

    name = str(name).strip()

    # Fix common encoding issues
    encoding_fixes = {
        'Ã§': 'ç',
        'Ã©': 'é',
        'Ã¡': 'á',
        'Ã ': 'à',
        'Ã³': 'ó',
        'Ãµ': 'õ',
        'Ãª': 'ê',
        'Ã¢': 'â',
        'Ã­': 'í',
        'Ãº': 'ú',
        'Ã¼': 'ü',
        'Ã±': 'ñ',
        '�': 'é',  # Common corruption
        'Ã�': 'í',
        'Ã´': 'ô',
        'ÃŒ': 'í',
        'Ã': 'é',  # Single character corruption
    }

    for wrong, correct in encoding_fixes.items():
        name = name.replace(wrong, correct)

    # Remove extra spaces
    name = ' '.join(name.split())

    return name


def create_region_mapping_table(df_official, gdf_current, df_ibge):
    """
    Create a comprehensive mapping table between different region name sources.

    Args:
        df_official: Official regions from CSV
        gdf_current: Current shapefile regions
        df_ibge: IBGE regions

    Returns:
        DataFrame with mapping between all sources
    """

    print("Criando tabela de mapeamento...")

    mapping_data = []

    # Start with official regions as the base
    for _, official_row in df_official.iterrows():
        official_name = official_row['nome_oficial']
        official_code = official_row['codigo_regiao']

        # Find best match in current shapefile
        shapefile_match = find_best_match(official_name, gdf_current['NM_RGINT'].tolist())

        # Find best match in IBGE data
        ibge_match = find_best_match(official_name, df_ibge['nome_regiao_imediata'].tolist() if 'nome_regiao_imediata' in df_ibge.columns else [])

        mapping_data.append({
            'codigo_oficial': official_code,
            'nome_oficial': official_name,
            'nome_shapefile': shapefile_match,
            'nome_ibge': ibge_match,
            'shapefile_found': shapefile_match is not None,
            'ibge_found': ibge_match is not None
        })

    df_mapping = pd.DataFrame(mapping_data)

    print(f"Mapeamento criado:")
    print(f"  Total regioes oficiais: {len(df_mapping)}")
    print(f"  Correspondidas no shapefile: {df_mapping['shapefile_found'].sum()}")
    print(f"  Correspondidas no IBGE: {df_mapping['ibge_found'].sum()}")

    return df_mapping


def find_best_match(target_name, available_names):
    """
    Find the best match for a target name in a list of available names.

    Args:
        target_name: Name to find
        available_names: List of available names

    Returns:
        Best matching name or None
    """

    target_norm = normalize_name_for_matching(target_name)

    # Try exact match first
    for name in available_names:
        if normalize_name_for_matching(name) == target_norm:
            return name

    # Try substring match
    for name in available_names:
        name_norm = normalize_name_for_matching(name)
        if target_norm in name_norm or name_norm in target_norm:
            return name

    return None


def normalize_name_for_matching(name):
    """
    Normalize a name for fuzzy matching.

    Args:
        name: Name to normalize

    Returns:
        Normalized name
    """

    if pd.isna(name):
        return ""

    name = str(name).strip().lower()

    # Remove accents
    name = unicodedata.normalize('NFD', name)
    name = ''.join(char for char in name if unicodedata.category(char) != 'Mn')

    # Remove common prepositions and articles
    words_to_remove = ['de', 'da', 'do', 'das', 'dos', 'e']
    words = name.split()
    words = [w for w in words if w not in words_to_remove]

    return ' '.join(words)


if __name__ == "__main__":
    # Test the functions
    csv_path = "Lista Regiões Imediatas 510 Brasil - Página1.csv"

    if Path(csv_path).exists():
        print("Testando parsing do CSV oficial...")
        df_official = parse_official_regions_csv(csv_path)

        # Save the official regions for reference
        df_official.to_csv("regioes_oficiais_510.csv", index=False, encoding='utf-8')
        print(f"Lista oficial salva em: regioes_oficiais_510.csv")

    else:
        print(f"Arquivo nao encontrado: {csv_path}")