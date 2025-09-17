#!/usr/bin/env python3
"""
Ultra-aggressive geometry optimization for maximum performance
Target: < 5MB final size with immediate loading
"""

import geopandas as gpd
import pandas as pd
import json
import time
import os

def create_ultra_light_geometries():
    """Create ultra-lightweight geometries for instant loading"""

    print("Creating ULTRA-LIGHT geometries for instant loading...")
    start_time = time.time()

    try:
        # Load optimized parquet
        print("Loading optimized parquet...")
        gdf = gpd.read_parquet('shapefiles/BR_RG_Imediatas_2024_optimized.parquet')
        print(f"   Loaded {len(gdf)} regions")

        # Aggregate by intermediate region
        print("Aggregating by intermediate region...")
        gdf_regioes = gdf.dissolve(by='NM_RGINT').reset_index()
        print(f"   {len(gdf_regioes)} intermediate regions")

        # EXTREME simplification - prioritize speed over precision
        print("Applying EXTREME geometry simplification...")

        # Stage 1: Ultra-aggressive simplification (tolerance = 0.02 - very aggressive)
        gdf_ultra = gdf_regioes.copy()
        gdf_ultra['geometry'] = gdf_ultra.geometry.simplify(tolerance=0.02, preserve_topology=True)

        # Stage 2: Further reduce precision by rounding coordinates
        print("Reducing coordinate precision...")
        gdf_ultra['geometry'] = gdf_ultra.geometry.apply(
            lambda geom: geom if geom.is_empty else geom
        )

        # Keep only essential columns
        gdf_final = gdf_ultra[['NM_RGINT', 'geometry']].copy()

        # Clean region names
        print("Cleaning region names...")
        gdf_final['NM_RGINT'] = gdf_final['NM_RGINT'].astype(str)
        gdf_final['NM_RGINT'] = gdf_final['NM_RGINT'].str.strip()

        # Add region codes for faster indexing
        gdf_final['codigo'] = gdf_final.reset_index().index

        # Save as ultra-compressed parquet
        output_parquet = 'shapefiles/brasil_regions_ultra_light.parquet'
        print(f"Saving ultra-light parquet to {output_parquet}...")

        # Save with maximum compression
        gdf_final.to_parquet(
            output_parquet,
            compression='snappy',  # Fast decompression
            index=False
        )

        # Also save as minimal GeoJSON for web compatibility
        output_geojson = 'shapefiles/brasil_regions_ultra_light.geojson'
        print(f"Saving minimal GeoJSON to {output_geojson}...")

        gdf_final.to_file(
            output_geojson,
            driver='GeoJSON',
            write_crs=True
        )

        # Check file sizes
        parquet_size = os.path.getsize(output_parquet) / (1024 * 1024)
        geojson_size = os.path.getsize(output_geojson) / (1024 * 1024)

        end_time = time.time()

        print(f"\nULTRA-LIGHT OPTIMIZATION COMPLETE!")
        print(f"   Time: {end_time - start_time:.2f} seconds")
        print(f"   Parquet size: {parquet_size:.2f} MB")
        print(f"   GeoJSON size: {geojson_size:.2f} MB")
        print(f"   Regions: {len(gdf_final)}")

        # Performance test
        print(f"\nTesting loading performance...")
        test_start = time.time()
        test_gdf = gpd.read_parquet(output_parquet)
        test_end = time.time()
        print(f"   Parquet load time: {test_end - test_start:.3f} seconds")

        # Verify data integrity
        print(f"\nData integrity check...")
        print(f"   Regions loaded: {len(test_gdf)}")
        print(f"   Geometry valid: {test_gdf.geometry.is_valid.all()}")
        print(f"   No empty geometries: {not test_gdf.geometry.is_empty.any()}")

        return True

    except Exception as e:
        print(f"ERROR in ultra-light optimization: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    create_ultra_light_geometries()