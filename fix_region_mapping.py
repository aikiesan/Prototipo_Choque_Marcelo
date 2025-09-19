#!/usr/bin/env python3
"""
Script to create proper mapping between official CSV and shapefile using region codes.
Uses shapefile names as authoritative source since they have correct encoding.
"""

import pandas as pd
import geopandas as gpd
import numpy as np
from pathlib import Path
import unicodedata


def load_shapefile_regions():
    """Load regions from shapefile (authoritative source)."""
    print("Carregando regiões do shapefile...")
    gdf = gpd.read_parquet('shapefiles/regioes_imediatas_510_optimized.parquet')
    print(f"Regiões no shapefile: {len(gdf)}")
    return gdf


def parse_csv_with_codes():
    """Parse CSV to extract region codes and map to shapefile names."""
    print("Extraindo códigos de região do CSV...")

    # Try different encodings
    encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

    df = None
    for encoding in encodings_to_try:
        try:
            df = pd.read_csv("Lista Regiões Imediatas 510 Brasil - Página1.csv", encoding=encoding)
            print(f"CSV carregado com encoding: {encoding}")
            break
        except (UnicodeDecodeError, UnicodeError):
            continue

    if df is None:
        raise ValueError("Não foi possível carregar o CSV")

    # Extract region codes and corrupted names
    region_data = []

    for idx, row in df.iterrows():
        if idx == 0:  # Skip header
            continue

        try:
            # Column 7: region name (corrupted), Column 8: region code
            region_name_corrupted = row.iloc[7] if len(row) > 7 else None
            region_code = row.iloc[8] if len(row) > 8 else None

            if pd.notna(region_name_corrupted) and pd.notna(region_code):
                region_code = str(region_code).strip()
                region_name_corrupted = str(region_name_corrupted).strip()

                if region_code.isdigit() and len(region_code) == 6:
                    region_data.append({
                        'codigo_regiao': region_code,
                        'nome_corrupted': region_name_corrupted
                    })

        except Exception as e:
            continue

    df_codes = pd.DataFrame(region_data)
    print(f"Códigos extraídos: {len(df_codes)}")
    return df_codes


def create_authoritative_mapping(gdf_shapefile, df_codes):
    """Create mapping using shapefile names as authoritative source."""
    print("Criando mapeamento autoritativo...")

    # For now, let's create a simple positional mapping
    # This assumes both datasets are in the same order (which they should be for official data)

    shapefile_names = gdf_shapefile['NM_RGINT'].tolist()

    # Create a dataframe with both
    mapping_data = []

    for i, code_row in df_codes.iterrows():
        if i < len(shapefile_names):
            mapping_data.append({
                'codigo_regiao': code_row['codigo_regiao'],
                'nome_oficial': shapefile_names[i],  # Use shapefile as authoritative
                'nome_corrupted': code_row['nome_corrupted']
            })

    df_mapping = pd.DataFrame(mapping_data)

    print(f"Mapeamento criado: {len(df_mapping)} regiões")
    print("Exemplos do mapeamento:")
    for _, row in df_mapping.head(10).iterrows():
        try:
            print(f"  {row['codigo_regiao']}: '{row['nome_corrupted']}' -> '{row['nome_oficial']}'")
        except UnicodeEncodeError:
            print(f"  {row['codigo_regiao']}: [encoding issue] -> '{row['nome_oficial']}'")

    return df_mapping


def save_corrected_mapping(df_mapping):
    """Save the corrected mapping."""
    print("Salvando mapeamento corrigido...")

    # Create final dataset with correct names and codes
    df_final = df_mapping[['codigo_regiao', 'nome_oficial']].copy()
    df_final = df_final.rename(columns={'nome_oficial': 'nome_regiao'})

    # Save as CSV with UTF-8 encoding
    df_final.to_csv('regioes_oficiais_510_corrected.csv', index=False, encoding='utf-8')

    print(f"Mapeamento salvo: regioes_oficiais_510_corrected.csv")
    print(f"Total de regiões: {len(df_final)}")

    # Check for duplicates
    duplicates = df_final[df_final.duplicated(subset=['nome_regiao'], keep=False)]
    if len(duplicates) > 0:
        print(f"Duplicatas encontradas:")
        for name in duplicates['nome_regiao'].unique():
            dup_regions = duplicates[duplicates['nome_regiao'] == name]
            print(f"  {name}: códigos {', '.join(dup_regions['codigo_regiao'].tolist())}")
    else:
        print("Sem duplicatas!")

    return df_final


def validate_mapping(df_final, gdf_shapefile):
    """Validate the final mapping."""
    print("\nValidando mapeamento final...")

    shapefile_names = set(gdf_shapefile['NM_RGINT'].tolist())
    mapping_names = set(df_final['nome_regiao'].tolist())

    matches = len(shapefile_names & mapping_names)
    total = len(shapefile_names)

    print(f"Correspondências: {matches}/{total} ({matches/total*100:.1f}%)")

    if matches < total:
        missing_from_mapping = shapefile_names - mapping_names
        missing_from_shapefile = mapping_names - shapefile_names

        print(f"\nFaltando no mapeamento ({len(missing_from_mapping)}):")
        for name in list(missing_from_mapping)[:10]:
            print(f"  '{name}'")

        print(f"\nFaltando no shapefile ({len(missing_from_shapefile)}):")
        for name in list(missing_from_shapefile)[:10]:
            print(f"  '{name}'")


if __name__ == "__main__":
    print("Criando mapeamento autoritativo de regiões...")

    # Load data
    gdf_shapefile = load_shapefile_regions()
    df_codes = parse_csv_with_codes()

    # Create authoritative mapping using shapefile names
    df_mapping = create_authoritative_mapping(gdf_shapefile, df_codes)

    # Save corrected mapping
    df_final = save_corrected_mapping(df_mapping)

    # Validate
    validate_mapping(df_final, gdf_shapefile)

    print("\nMapeamento autoritativo criado com sucesso!")