#!/usr/bin/env python3
"""
Test different compression algorithms for better GeoParquet optimization
"""

import geopandas as gpd
import os
import time

def test_compressions(input_file, compressions=['snappy', 'gzip', 'brotli', 'lz4']):
    """Test different compression algorithms"""
    
    print(f"📊 Testing different compression algorithms for: {input_file}")
    
    # Read the original shapefile
    gdf = gpd.read_file(input_file)
    original_size = os.path.getsize(input_file)
    
    results = []
    
    for compression in compressions:
        try:
            output_file = f"BR_RG_Imediatas_2024_{compression}.parquet"
            
            print(f"\n🔄 Testing {compression} compression...")
            start_time = time.time()
            
            # Write with different compression
            gdf.to_parquet(
                output_file,
                compression=compression,
                row_group_size=5000,  # Smaller row groups for better compression
                use_dictionary=True
            )
            
            end_time = time.time()
            output_size = os.path.getsize(output_file)
            compression_ratio = (1 - output_size / original_size) * 100
            
            result = {
                'algorithm': compression,
                'size_mb': output_size / (1024 * 1024),
                'compression_ratio': compression_ratio,
                'time_seconds': end_time - start_time,
                'file': output_file
            }
            results.append(result)
            
            print(f"✅ {compression}: {result['size_mb']:.2f} MB ({result['compression_ratio']:.1f}% reduction) in {result['time_seconds']:.2f}s")
            
        except Exception as e:
            print(f"❌ {compression} failed: {e}")
    
    # Find best compression
    if results:
        best = min(results, key=lambda x: x['size_mb'])
        print(f"\n🏆 Best compression: {best['algorithm']} - {best['size_mb']:.2f} MB ({best['compression_ratio']:.1f}% reduction)")
        
        # Clean up other files, keep the best one
        for result in results:
            if result['algorithm'] != best['algorithm']:
                try:
                    os.remove(result['file'])
                except:
                    pass
        
        # Rename best file to final name
        final_name = "BR_RG_Imediatas_2024_optimized.parquet"
        os.rename(best['file'], final_name)
        print(f"📁 Optimized file saved as: {final_name}")
        
        return final_name, best
    
    return None, None

if __name__ == "__main__":
    input_shapefile = "BR_RG_Imediatas_2024.shp"
    
    # Test different compression algorithms
    optimized_file, best_result = test_compressions(input_shapefile)
    
    if optimized_file:
        print(f"\n🎉 Optimization complete!")
        print(f"📁 Best compressed file: {optimized_file}")
        print(f"📊 Final size: {best_result['size_mb']:.2f} MB")
        print(f"🗜️  Total reduction: {best_result['compression_ratio']:.1f}%")
    else:
        print("❌ No successful compressions")
