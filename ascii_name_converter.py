#!/usr/bin/env python3
"""
Convert region names to ASCII-safe versions for web deployment.
Fixes encoding issues that break visualization in deployed environments.
"""

import pandas as pd
import geopandas as gpd
import unicodedata
import re


def create_comprehensive_ascii_mapping():
    """
    Create comprehensive mapping from Portuguese characters to ASCII equivalents.
    """

    # Portuguese character mappings
    portuguese_ascii_map = {
        # Vowels with accents
        'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
        'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
        'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',

        # Uppercase versions
        'Á': 'A', 'À': 'A', 'Ã': 'A', 'Â': 'A', 'Ä': 'A',
        'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
        'Í': 'I', 'Ì': 'I', 'Î': 'I', 'Ï': 'I',
        'Ó': 'O', 'Ò': 'O', 'Õ': 'O', 'Ô': 'O', 'Ö': 'O',
        'Ú': 'U', 'Ù': 'U', 'Û': 'U', 'Ü': 'U',

        # Cedilla
        'ç': 'c', 'Ç': 'C',

        # Common encoding corruptions found in data
        'Ã¡': 'a', 'Ã©': 'e', 'Ã­': 'i', 'Ã³': 'o', 'Ãº': 'u',
        'Ã ': 'a', 'Ãª': 'e', 'Ã¢': 'a', 'Ã´': 'o', 'Ã§': 'c',
        'Ãµ': 'o', 'Ã±': 'n',

        # Other common corruptions
        '�': 'a',  # Common replacement character
        'Ã‡': 'C', 'Ã†': 'A',
    }

    return portuguese_ascii_map


def convert_to_ascii_safe(text):
    """
    Convert text to ASCII-safe version, handling Portuguese characters and encoding issues.

    Args:
        text: Input text with potential special characters

    Returns:
        ASCII-safe version of the text
    """

    if pd.isna(text):
        return ""

    text = str(text).strip()

    # Apply comprehensive character mapping
    ascii_map = create_comprehensive_ascii_mapping()

    for char, replacement in ascii_map.items():
        text = text.replace(char, replacement)

    # Use unicodedata to handle any remaining special characters
    text = unicodedata.normalize('NFD', text)
    text = ''.join(char for char in text if unicodedata.category(char) != 'Mn')

    # Remove any remaining non-ASCII characters
    text = ''.join(char if ord(char) < 128 else '' for char in text)

    # Clean up extra spaces
    text = ' '.join(text.split())

    return text


def create_ascii_region_mapping():
    """
    Create mapping from current region names to ASCII-safe versions.
    Uses shapefile as authoritative source for correct names.
    """

    print("Creating ASCII-safe region name mapping...")

    # Load shapefile (has correct UTF-8 encoding)
    gdf = gpd.read_parquet('shapefiles/regioes_imediatas_510_optimized.parquet')

    # Load official region codes
    df_official = pd.read_csv("regioes_oficiais_510_corrected.csv")

    mapping_data = []

    # Create mapping using shapefile names as source of truth
    for _, gdf_row in gdf.iterrows():
        original_name = str(gdf_row['NM_RGINT']).strip()
        ascii_name = convert_to_ascii_safe(original_name)

        # Find corresponding region code
        region_code = None
        for _, official_row in df_official.iterrows():
            if convert_to_ascii_safe(official_row['nome_regiao']) == ascii_name:
                region_code = official_row['codigo_regiao']
                break

        if not region_code:
            # If no exact match, use position-based mapping (they should be in same order)
            gdf_index = gdf.index.get_loc(gdf_row.name)
            if gdf_index < len(df_official):
                region_code = df_official.iloc[gdf_index]['codigo_regiao']

        mapping_data.append({
            'codigo_regiao': region_code if region_code else f"99{len(mapping_data):04d}",  # Fallback code
            'nome_original': original_name,
            'nome_ascii': ascii_name,
            'nome_correto_utf8': original_name  # Keep UTF-8 version for reference
        })

    df_mapping = pd.DataFrame(mapping_data)

    print(f"ASCII mapping created: {len(df_mapping)} regions")
    print("Sample conversions:")

    # Show examples of conversions
    for _, row in df_mapping.head(10).iterrows():
        if row['nome_original'] != row['nome_ascii']:
            print(f"  '{row['nome_original']}' -> '{row['nome_ascii']}'")

    return df_mapping


def create_ascii_region_files():
    """
    Create ASCII-safe region files for deployment.
    """

    print("Creating ASCII-safe region files...")

    # Create the mapping
    df_mapping = create_ascii_region_mapping()

    # Create ASCII-only CSV for deployment
    df_ascii = df_mapping[['codigo_regiao', 'nome_ascii']].copy()
    df_ascii = df_ascii.rename(columns={'nome_ascii': 'nome_regiao'})

    # Save ASCII version
    df_ascii.to_csv('regioes_oficiais_510_ascii.csv', index=False, encoding='utf-8')
    print(f"ASCII regions saved: regioes_oficiais_510_ascii.csv")

    # Save comprehensive mapping for reference
    df_mapping.to_csv('mapeamento_nomes_completo.csv', index=False, encoding='utf-8')
    print(f"Complete mapping saved: mapeamento_nomes_completo.csv")

    # Check for any problematic characters in ASCII version
    problematic_regions = []
    for _, row in df_ascii.iterrows():
        name = row['nome_regiao']
        if any(ord(char) > 127 for char in name):
            problematic_regions.append(name)

    if problematic_regions:
        print(f"WARNING: {len(problematic_regions)} regions still have non-ASCII characters:")
        for name in problematic_regions[:5]:
            print(f"  '{name}'")
    else:
        print("✅ All region names are ASCII-safe!")

    return df_ascii, df_mapping


def update_shapefile_with_ascii_names():
    """
    Create an ASCII version of the shapefile for deployment.
    """

    print("Creating ASCII-safe shapefile...")

    # Load original shapefile
    gdf = gpd.read_parquet('shapefiles/regioes_imediatas_510_optimized.parquet')

    # Load ASCII mapping
    df_mapping = pd.read_csv('mapeamento_nomes_completo.csv')

    # Create mapping dictionary
    name_mapping = {}
    for _, row in df_mapping.iterrows():
        name_mapping[row['nome_original']] = row['nome_ascii']

    # Apply ASCII names to shapefile
    gdf_ascii = gdf.copy()
    gdf_ascii['NM_RGINT_ORIGINAL'] = gdf_ascii['NM_RGINT']  # Keep original for reference
    gdf_ascii['NM_RGINT'] = gdf_ascii['NM_RGINT'].map(name_mapping).fillna(gdf_ascii['NM_RGINT'])

    # Save ASCII shapefile
    gdf_ascii.to_parquet('shapefiles/regioes_imediatas_510_ascii.parquet')
    print(f"ASCII shapefile saved: shapefiles/regioes_imediatas_510_ascii.parquet")

    # Verify conversion
    changes = (gdf_ascii['NM_RGINT'] != gdf_ascii['NM_RGINT_ORIGINAL']).sum()
    print(f"Region names converted: {changes}/{len(gdf_ascii)}")

    return gdf_ascii


if __name__ == "__main__":
    print("Converting region names to ASCII-safe format...")

    # Create ASCII region files
    df_ascii, df_mapping = create_ascii_region_files()

    # Create ASCII shapefile
    gdf_ascii = update_shapefile_with_ascii_names()

    print("\n✅ ASCII conversion completed!")
    print(f"Files created:")
    print(f"  - regioes_oficiais_510_ascii.csv ({len(df_ascii)} regions)")
    print(f"  - mapeamento_nomes_completo.csv (conversion reference)")
    print(f"  - shapefiles/regioes_imediatas_510_ascii.parquet ({len(gdf_ascii)} regions)")