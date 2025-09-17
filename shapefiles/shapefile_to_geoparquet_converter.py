#!/usr/bin/env python3
"""
Shapefile to GeoParquet Converter
Converts large shapefiles to optimized GeoParquet format for better performance and storage efficiency.
"""

import geopandas as gpd
import pyarrow as pa
import pyarrow.parquet as pq
import os
import time
from pathlib import Path


def convert_shapefile_to_geoparquet(
    shapefile_path: str,
    output_path: str = None,
    compression: str = "snappy",
    row_group_size: int = 10000,
    use_dictionary: bool = True,
    optimize_strings: bool = True
):
    """
    Convert a shapefile to GeoParquet format with optimization settings.
    
    Args:
        shapefile_path (str): Path to the input shapefile
        output_path (str): Path for the output GeoParquet file (optional)
        compression (str): Compression algorithm ('snappy', 'gzip', 'brotli', 'lz4')
        row_group_size (int): Number of rows per row group for optimization
        use_dictionary (bool): Use dictionary encoding for string columns
        optimize_strings (bool): Optimize string columns for better compression
    
    Returns:
        tuple: (output_file_path, conversion_stats)
    """
    
    print(f"🔄 Starting conversion of: {shapefile_path}")
    start_time = time.time()
    
    # Validate input file
    if not os.path.exists(shapefile_path):
        raise FileNotFoundError(f"Shapefile not found: {shapefile_path}")
    
    # Generate output path if not provided
    if output_path is None:
        base_name = Path(shapefile_path).stem
        output_path = f"{base_name}.parquet"
    
    # Get original file size
    original_size = os.path.getsize(shapefile_path)
    
    try:
        # Read shapefile with optimizations
        print("📖 Reading shapefile...")
        gdf = gpd.read_file(shapefile_path)
        
        print(f"✅ Successfully loaded {len(gdf)} features")
        print(f"📊 Columns: {list(gdf.columns)}")
        print(f"🗺️  CRS: {gdf.crs}")
        print(f"📏 Bounds: {gdf.total_bounds}")
        
        # Optimize data types for better compression
        if optimize_strings:
            print("🔧 Optimizing data types...")
            for col in gdf.columns:
                if col != gdf.geometry.name and gdf[col].dtype == 'object':
                    # Convert to category if it has repeated values
                    unique_ratio = len(gdf[col].unique()) / len(gdf[col])
                    if unique_ratio < 0.5:  # Less than 50% unique values
                        gdf[col] = gdf[col].astype('category')
                        print(f"  📋 Converted {col} to category (uniqueness: {unique_ratio:.2%})")
        
        # Configure Parquet writing options
        parquet_options = {
            'compression': compression,
            'row_group_size': row_group_size,
            'use_dictionary': use_dictionary,
        }
        
        print(f"💾 Writing GeoParquet with {compression} compression...")
        print(f"⚙️  Row group size: {row_group_size}")
        
        # Write to GeoParquet
        gdf.to_parquet(
            output_path,
            compression=compression,
            row_group_size=row_group_size,
            use_dictionary=use_dictionary
        )
        
        # Get conversion statistics
        end_time = time.time()
        conversion_time = end_time - start_time
        output_size = os.path.getsize(output_path)
        compression_ratio = (1 - output_size / original_size) * 100
        
        stats = {
            'original_size_mb': original_size / (1024 * 1024),
            'output_size_mb': output_size / (1024 * 1024),
            'compression_ratio_percent': compression_ratio,
            'conversion_time_seconds': conversion_time,
            'features_count': len(gdf),
            'columns_count': len(gdf.columns),
            'crs': str(gdf.crs),
            'compression_algorithm': compression
        }
        
        print("\n✅ Conversion completed successfully!")
        print(f"📁 Output file: {output_path}")
        print(f"📊 Original size: {stats['original_size_mb']:.2f} MB")
        print(f"📊 Compressed size: {stats['output_size_mb']:.2f} MB")
        print(f"🗜️  Compression ratio: {stats['compression_ratio_percent']:.1f}%")
        print(f"⏱️  Conversion time: {stats['conversion_time_seconds']:.2f} seconds")
        
        return output_path, stats
        
    except Exception as e:
        print(f"❌ Error during conversion: {str(e)}")
        raise


def validate_geoparquet(parquet_path: str):
    """
    Validate the converted GeoParquet file by reading it back and checking basic properties.
    
    Args:
        parquet_path (str): Path to the GeoParquet file
    
    Returns:
        bool: True if validation successful
    """
    try:
        print(f"\n🔍 Validating GeoParquet file: {parquet_path}")
        
        # Read the file back
        gdf_test = gpd.read_parquet(parquet_path)
        
        print(f"✅ Successfully read {len(gdf_test)} features")
        print(f"📊 Columns: {list(gdf_test.columns)}")
        print(f"🗺️  CRS: {gdf_test.crs}")
        
        # Check if geometry is valid
        if gdf_test.geometry.name in gdf_test.columns:
            valid_geoms = gdf_test.geometry.is_valid.sum()
            print(f"✅ Valid geometries: {valid_geoms}/{len(gdf_test)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Configuration
    INPUT_SHAPEFILE = "BR_RG_Imediatas_2024.shp"
    OUTPUT_GEOPARQUET = "BR_RG_Imediatas_2024.parquet"
    
    # Compression options: 'snappy' (fast), 'gzip' (balanced), 'brotli' (best compression)
    COMPRESSION = "snappy"  # Good balance of speed and compression
    ROW_GROUP_SIZE = 10000  # Optimize for typical GIS workflows
    
    try:
        # Convert shapefile to GeoParquet
        output_file, conversion_stats = convert_shapefile_to_geoparquet(
            shapefile_path=INPUT_SHAPEFILE,
            output_path=OUTPUT_GEOPARQUET,
            compression=COMPRESSION,
            row_group_size=ROW_GROUP_SIZE,
            use_dictionary=True,
            optimize_strings=True
        )
        
        # Validate the conversion
        if validate_geoparquet(output_file):
            print("\n🎉 Conversion and validation completed successfully!")
            print(f"📁 Your optimized GeoParquet file is ready: {output_file}")
            
            # Print performance benefits
            print(f"\n📈 Performance Benefits:")
            print(f"   • File size reduced by {conversion_stats['compression_ratio_percent']:.1f}%")
            print(f"   • Faster loading with columnar storage")
            print(f"   • Better compression with {COMPRESSION} algorithm")
            print(f"   • Optimized for analytical workloads")
            
        else:
            print("\n⚠️  Conversion completed but validation failed. Please check the output file.")
            
    except Exception as e:
        print(f"\n💥 Conversion failed: {str(e)}")
        exit(1)
