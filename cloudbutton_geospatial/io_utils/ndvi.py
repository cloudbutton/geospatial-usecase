from shapely.geometry import Point, Polygon, MultiPolygon, shape, mapping
import numpy as np
import pyproj
import rasterio


def get_poly_within(multi_poly, raster_bounds):
    raster_poly = Polygon([
        (raster_bounds.left, raster_bounds.top),
        (raster_bounds.right, raster_bounds.top),
        (raster_bounds.right, raster_bounds.bottom),
        (raster_bounds.left, raster_bounds.bottom)
    ])
    return MultiPolygon([poly for poly in multi_poly if poly.within(raster_poly)])


def lonlat_to_utm(dataset_crs, lon, lat):
    """
    Transform lon and lat to utm coordinates
    """
    utm = pyproj.Proj(dataset_crs) # Pass CRS of image from rasterio
    lonlat = pyproj.Proj(init='epsg:4326')
    return pyproj.transform(lonlat, utm, lon, lat)


def get_subset_raster(tiff_url, east1, north1, east2, north2):
    with rasterio.open(tiff_url) as src:
        row1, col1 = src.index(min(east1, east2), max(north1, north2))
        row2, col2 = src.index(max(east1, east2), min(north1, north2))
        window = rasterio.windows.Window(col1, row1, col2-col1, row2-row1)
        return src.read(1, window=window)


def get_ndvi_params(band_04_url, band_08_url, area_mp):
    return [
        {
            'band_04': band_04_url,
            'band_08': band_08_url,
            'geometry': {'type': 'Polygon', 'coordinates': [coor for coor in mapping(mp)['coordinates'][0]]}
        }
        for mp in area_mp]


def ndvi_calculation(param):
    bounds = Polygon(param['geometry']['coordinates']).bounds
    band_04 = get_subset_raster(param['band_04'], bounds[0], bounds[1], bounds[2], bounds[3])
    band_08 = get_subset_raster(param['band_08'], bounds[0], bounds[1], bounds[2], bounds[3])
    nir = band_08.astype('float32')
    red = band_04.astype('float32')
    np.seterr(divide='ignore', invalid='ignore')
    ndvi = np.where(
        (nir + red) == 0.,
        0,
        (nir - red) / (nir + red))
    return red, nir, ndvi


def ndvi_tile_sentinel(band_04_url, band_08_url):
    with rasterio.open(band_04_url) as dataset:
        red = dataset.read(1).astype('float32')
    with rasterio.open(band_08_url) as dataset:
        nir = dataset.read(1).astype('float32')
    np.seterr(divide='ignore', invalid='ignore')
    ndvi = np.where(
        (nir + red) == 0.,
        0,
        (nir - red) / (nir + red))
    return red, nir, ndvi