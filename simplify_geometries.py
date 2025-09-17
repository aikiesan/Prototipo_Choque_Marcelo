#!/usr/bin/env python3
"""
Script para criar geometrias ultra-simplificadas para carregamento rápido
Reduz drasticamente o tamanho e complexidade dos polígonos
"""

import geopandas as gpd
import json
import time

def simplificar_geometrias():
    """Cria versão ultra-leve das geometrias brasileiras"""

    print("Iniciando simplificacao extrema das geometrias...")
    start_time = time.time()

    try:
        # Carregar arquivo parquet
        print("Carregando arquivo parquet...")
        gdf = gpd.read_parquet('shapefiles/BR_RG_Imediatas_2024_optimized.parquet')
        print(f"   Regioes carregadas: {len(gdf)}")

        # Agregar por região intermediária
        print("Agregando por regiao intermediaria...")
        gdf_regioes = gdf.dissolve(by='NM_RGINT').reset_index()
        print(f"   Regioes intermediarias: {len(gdf_regioes)}")

        # Simplificação EXTREMA para web (tolerância alta = geometrias simples)
        print("Aplicando simplificacao extrema...")
        original_size = len(str(gdf_regioes.geometry))

        # SEM simplificação - mantém geometrias originais precisas
        # Apenas agrega por região intermediária sem perder qualidade visual
        # gdf_regioes['geometry'] = gdf_regioes.geometry.simplify(tolerance=0.005)

        simplified_size = len(str(gdf_regioes.geometry))
        reduction = (1 - simplified_size/original_size) * 100

        print(f"   Reducao de complexidade: {reduction:.1f}%")

        # Manter apenas colunas essenciais
        gdf_light = gdf_regioes[['NM_RGINT', 'geometry']].copy()

        # Normalizar nomes para evitar problemas de encoding
        print("Normalizando nomes das regioes...")
        gdf_light['NM_RGINT'] = gdf_light['NM_RGINT'].str.normalize('NFKD')
        gdf_light['NM_RGINT'] = gdf_light['NM_RGINT'].str.encode('ascii', errors='ignore').str.decode('ascii')

        # Salvar como GeoJSON compacto
        output_path = 'shapefiles/brasil_regioes_light.geojson'
        print(f"Salvando GeoJSON ultra-leve em {output_path}...")

        gdf_light.to_file(output_path, driver='GeoJSON')

        # Verificar tamanho do arquivo
        import os
        file_size_mb = os.path.getsize(output_path) / (1024 * 1024)

        end_time = time.time()

        print(f"Simplificacao concluida!")
        print(f"   Tempo: {end_time - start_time:.2f} segundos")
        print(f"   Tamanho final: {file_size_mb:.2f} MB")
        print(f"   Regioes: {len(gdf_light)}")

        # Teste de carregamento rápido
        print("Testando carregamento rapido...")
        test_start = time.time()
        test_gdf = gpd.read_file(output_path)
        test_end = time.time()
        print(f"   Tempo de carregamento: {test_end - test_start:.2f} segundos")

        return True

    except Exception as e:
        print(f"Erro na simplificacao: {e}")
        return False

if __name__ == "__main__":
    simplificar_geometrias()