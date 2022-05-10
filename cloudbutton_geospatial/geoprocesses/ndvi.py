"""
Este script calcula el índice NDVI

AUTHOR: Juanjo

DATE: 06/02/2019

"""
import os

import numpy as np
import rasterio


class NDVIProcess:

    @staticmethod
    def run(b4_uri, b8_uri, dst_dir):
        band4 = rasterio.open(b4_uri)
        bands_dir, band_filename = os.path.split(b4_uri)
        dst_filename = band_filename.replace('_B04_', '_')
        band8 = rasterio.open(b8_uri)

        # Number of raster bands
#         print("Raster bands {}".format(band4.count))
#         print("Raster columns {}".format(band4.width))
#         print("Raster rows {}".format(band4.height))
#         print("Raster transform {}".format(band4.transform))
#         print("Type of raster byte {}".format(band4.dtypes[0]))
#         print("Raster system of reference {}".format(band4.crs))

        # Generate nir and red objects
        nir = band8.read(1).astype('float32')
        red = band4.read(1).astype('float32')

        np.seterr(divide='ignore', invalid='ignore')

        # Ndvi calculation, empty cells or nodata cells are reported as 0
        ndvi = np.where(
            (nir + red) == 0.,
            0,
            (nir - red) / (nir + red))

#         dst_file = os.path.join(dst_dir, dst_filename)
#         # Export ndvi image
#         ndvi_image = rasterio.open(
#             dst_file, 'w',
#             driver='Gtiff',
#             width=band4.width, height=band4.height,
#             count=1,
#             crs=band4.crs,
#             transform=band4.transform,
#             dtype='float32')
#         ndvi_image.write(ndvi, 1)
#        ndvi_image.close()
        return {'len': len(ndvi)} # dst_file
