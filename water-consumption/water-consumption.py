import sys
sys.path.append('../')

from collections import defaultdict
from cloudbutton_geospatial.io_utils.plot import plot_results
from cloudbutton_geospatial.utils.notebook import date_picker
from rasterio.windows import Window
from scipy.spatial import distance_matrix
from shapely.geometry import Point, MultiPoint, box
from pprint import pprint
import subprocess
import functools
import collections
import datetime
import os
import shutil
import psutil
import math
import numpy as np
import pandas as pd
import lithops
import requests
import rasterio
import json
import random
import boto3
import botocore
import re
import fiona
import os
import time
import sys
import tempfile
import pickle
import concurrent.futures
from IPython.display import Image
import matplotlib.pyplot as plt
from lithops.storage import Storage
from lithops.storage.utils import StorageNoSuchKeyError
from io import BytesIO


def get_stats(fexec, time, stage):
    stats = [f.stats for f in fexec.futures]

    worker_func_cpu_usage_values = [stat['worker_func_cpu_usage'] for stat in stats]
    worker_func_cpu_usage = np.mean(worker_func_cpu_usage_values)
    worker_func_cpu_usage_std = np.std(worker_func_cpu_usage_values)

    worker_func_sent_net_io = sum([stat['worker_func_sent_net_io'] for stat in stats])
    worker_func_recv_net_io = sum([stat['worker_func_recv_net_io'] for stat in stats])

    gbxms_price = 0.0000000167
    sum_total_time = sum([stat['worker_exec_time'] for stat in stats]) * 1000
    price = gbxms_price * sum_total_time * 2  # Price GB/ms * sum of times in ms * 2 GB

    stats_dict = {
        'CPU_avg_usage': worker_func_cpu_usage,
        'CPU_avg_usage_std': worker_func_cpu_usage_std,
        'CPU_avg_usage_values': worker_func_cpu_usage_values,
        'Net_io_total_sent': worker_func_sent_net_io,
        'Net_io_total_received': worker_func_recv_net_io,
        'Price (USD)': price,
        'Time (s)': time
    }

    # Print the statistics
    print(f'CPU usage values: {worker_func_cpu_usage_values}')
    print(f'CPU avg usage: {worker_func_cpu_usage}')
    print(f'CPU avg usage std: {worker_func_cpu_usage_std}')
    print(f'Net i/o sent: {worker_func_sent_net_io}')
    print(f'Net i/o received: {worker_func_recv_net_io}')
    print(f'Price: {price}')
    print(f'Time: {time}')
    return stats_dict


AREA_OF_INFLUENCE = 16000

DATA_BUCKET = 'geospatial-wc'
COMPUTE_BACKEND = 'aws_lambda'
STORAGE_BACKEND = 'aws_s3'
STORAGE_PREFIX = 's3://'
RUNTIME_MEMORY = 2048

DTM_PREFIX = 'DTMs/'
DTM_ASC_PREFIX = 'DTMs/asc/'
DTM_GEOTIFF_PREFIX = 'DTMs/geotiff/'

SPLITS = 3
r = -0.0056
zdet = 2000

date = datetime.date(2022, 5, 15)
DAY_OF_YEAR = 135 

storage = lithops.storage.Storage(backend=STORAGE_BACKEND)
fexec = lithops.FunctionExecutor(backend=COMPUTE_BACKEND, storage=STORAGE_BACKEND, runtime_memory=RUNTIME_MEMORY)

s_time = time.time()

siam_data_key = 'siam_data.csv'
try:
    siam_data_head = storage.head_object(bucket=DATA_BUCKET, key=siam_data_key)
    print(f'SIAM meteo data already in storage: {siam_data_head}')
except StorageNoSuchKeyError:
    print('Uploading SIAM meteo data to Object Storage...')
    with open(siam_data_key, 'rb') as f:
        storage.put_object(bucket=DATA_BUCKET, key=siam_data_key, body=f)

shapefile_key = 'shapefile_murcia.zip'
try:
    shapefile_head = storage.head_object(bucket=DATA_BUCKET, key=shapefile_key)
    print(f'Shapefile already in storage: {siam_data_head}')
except StorageNoSuchKeyError:
    print('Uploading shapefile to Object Storage...')
    with open(shapefile_key, 'rb') as f:
        storage.put_object(bucket=DATA_BUCKET, key=shapefile_key, body=f)

dtm_asc_keys = storage.list_keys(bucket=DATA_BUCKET, prefix=DTM_ASC_PREFIX)
local_dtm_input = 'input_DTMs'
local_dtms = [os.path.join(local_dtm_input, dtm) for dtm in os.listdir(local_dtm_input) if dtm.endswith('.tif')]

def upload_file(file_path):
    key = os.path.join(DTM_ASC_PREFIX, os.path.basename(file_path))
    if key in dtm_asc_keys:
        print(f'Tile {key} already in storage')
        return key
    with open(file_path, 'rb') as f:
        print(f'Uploading {key}...')
        storage.put_object(bucket=DATA_BUCKET, key=key, body=f)
    return key

with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
    result = list(pool.map(upload_file, local_dtms))

def asc_to_geotiff(obj, storage):
    asc_file_name = os.path.basename(obj.key)
    tile_id, _ = os.path.splitext(asc_file_name)
    out_path = os.path.join(tempfile.gettempdir(), tile_id + '.tiff')
    out_key = os.path.join(DTM_GEOTIFF_PREFIX, tile_id + '.tiff')

    try:
        out_obj = storage.head_object(bucket=DATA_BUCKET, key=out_key)
    except StorageNoSuchKeyError:
        out_obj = None

    if out_obj:
        print(f'GeoTIFF {tile_id} already exists, skipping...')
        return out_key

    print(f'Converting {tile_id} to GeoTIFF...')
    with rasterio.open(obj.data_stream, 'r') as src:
        profile = src.profile
        # Cloud optimized GeoTiff parameters
        profile.update(driver='GTiff')
        profile.update(blockxsize=256)
        profile.update(blockysize=256)
        profile.update(tiled=True)
        profile.update(compress='deflate')
        profile.update(interleave='band')
        with rasterio.open(out_path, 'w', **profile) as dest:
            dest.write(src.read())

    with open(out_path, 'rb') as f:
        storage.put_object(bucket=DATA_BUCKET, key=out_key, body=f)

    return out_key

st1 = time.time()
fs_cog = fexec.map(asc_to_geotiff, os.path.join(STORAGE_PREFIX, DATA_BUCKET, DTM_ASC_PREFIX))
_, _ = fexec.wait(fs=fs_cog)
time_stage_1 = time.time() - st1
stats1 = get_stats(fexec, time_stage_1, '1')
print(f'Stage 1: {time_stage_1}')
dtm_geotiff_keys = storage.list_keys(bucket=DATA_BUCKET, prefix=DTM_GEOTIFF_PREFIX)
print(dtm_geotiff_keys)

def get_tile_meta(obj):
    storage = Storage()
    tile_id = os.path.splitext(os.path.basename(obj.key))[0]
    with rasterio.open(BytesIO(storage.get_cloudobject(obj)), 'r') as src:
        x1, y1 = src.profile['transform'] * (0, 0)
        x2, y2 = src.profile['transform'] * (src.profile['width'], src.profile['height'])
    return tile_id, (x1, y1), (x2, y2)

st2 = time.time()
fs_meta = fexec.map(get_tile_meta, os.path.join(STORAGE_PREFIX, DATA_BUCKET, DTM_GEOTIFF_PREFIX))
tiles_meta = fexec.get_result(fs=fs_meta)
time_stage_2 = time.time() - st2
print(f'Stage 2: {time_stage_2}')
stats2 = get_stats(fexec, time_stage_2, '2')
print(tiles_meta)

def data_chunker(obj, n_splits, block_x, block_y, storage):
    tile_key = os.path.basename(obj.key)
    tile_id, _ = os.path.splitext(tile_key)

    storage = Storage()

    with rasterio.open(BytesIO(storage.get_cloudobject(obj))) as src:
        transform = src.transform

        # Compute working window
        step_w = src.width / n_splits
        step_h = src.height / n_splits

        offset_h = round(step_h * block_x)
        offset_w = round(step_w * block_y)

        profile = src.profile

        width = math.ceil(step_w * (block_y + 1) - offset_w)
        height = math.ceil(step_h * (block_x + 1) - offset_h)

        profile.update(width=width)
        profile.update(height=height)

        window = Window(offset_w, offset_h, width, height)

        chunk_file = os.path.join(tempfile.gettempdir(), tile_id + str(block_x) + '_' + str(block_y) + '.tif')
        with rasterio.open(chunk_file, 'w', **profile) as dest:
            dest.write(src.read(window=window))

    with open(chunk_file, 'rb') as f:
        co = storage.put_cloudobject(body=f, bucket=DATA_BUCKET)

    return (tile_key, block_x, block_y, co)

iterdata = [(os.path.join(STORAGE_PREFIX, DATA_BUCKET, tile), SPLITS, i, j)
            for i in range(SPLITS) for j in range(SPLITS) for tile in dtm_geotiff_keys]
print(f'Chunking {len(dtm_geotiff_keys)} tiles in {SPLITS * SPLITS} chunks each using {len(iterdata)} functions')
print(f"\nIterdata: {iterdata}\n")

st3 = time.time()
chunker_fs = fexec.map(data_chunker, iterdata)
chunks = fexec.get_result(fs=chunker_fs)
time_stage_3 = time.time() - st3
stats3 = get_stats(fexec, time_stage_3, '3')
print(f'Stage 3: {time_stage_3}')
print(chunks)

def compute_solar_irradiation(inputFile, outputFile, crs='32630'):
    # Define grass working set
    GRASS_GISDB = '/tmp/grassdata'
    #GRASS_GISDB = 'grassdata'
    GRASS_LOCATION = 'GEOPROCESSING'
    GRASS_MAPSET = 'PERMANENT'
    GRASS_ELEVATIONS_FILENAME = 'ELEVATIONS'

    os.environ['GRASSBIN'] = 'grass76'

    from grass_session import Session
    import grass.script as gscript
    import grass.script.setup as gsetup
    from grass.pygrass.modules.shortcuts import general
    from grass.pygrass.modules.shortcuts import raster
    
    os.environ.update(dict(GRASS_COMPRESS_NULLS='1'))

    # Clean previously processed data
    if os.path.isdir(GRASS_GISDB):
        shutil.rmtree(GRASS_GISDB)
    
    with Session(gisdb=GRASS_GISDB, location=GRASS_LOCATION, mapset=GRASS_MAPSET, create_opts='EPSG:32630') as ses:
        # Set project projection to match elevation raster projection
        general.proj(epsg=crs, flags='c') 
        # Load raster file into working directory
        raster.import_(input=inputFile, output=GRASS_ELEVATIONS_FILENAME, flags='o')    
        
        # Set project region to match raster region
        general.region(raster=GRASS_ELEVATIONS_FILENAME, flags='s')    
        # Calculate solar irradiation
        gscript.run_command('r.slope.aspect', elevation=GRASS_ELEVATIONS_FILENAME,
                            slope='slope', aspect='aspect')
        gscript.run_command('r.sun', elevation=GRASS_ELEVATIONS_FILENAME,
                            slope='slope', aspect='aspect', beam_rad='beam',
                            step=1, day=DAY_OF_YEAR)
        
        # Get extraterrestrial irradiation from history metadata
        regex = re.compile(r'\d+\.\d+')
        output = gscript.read_command("r.info", flags="h", map=["beam"])
        splits = str(output).split('\n')
        line = next(filter(lambda line: 'Extraterrestrial' in line, splits))
        extraterrestrial_irradiance = float(regex.search(line)[0])
        
        # Export generated results into a GeoTiff file
        if os.path.isfile(outputFile):
            os.remove(outputFile)

        raster.out_gdal(input='beam', output=outputFile)
        
        return extraterrestrial_irradiance

def filter_stations(bounds, stations):
    total_points = MultiPoint([Point(x, y) for x, y in stations[['X', 'Y']].to_numpy()])
    total_points_list = list(total_points.geoms)
    intersection = bounds.buffer(AREA_OF_INFLUENCE).intersection(total_points)
    filtered_stations = [point for point in total_points_list if intersection.contains(point)]

    return stations[[point in filtered_stations for point in total_points_list]]

def compute_basic_interpolation(shape, stations, field_value, offset = (0,0)):
    station_pixels = [[pixel[0], pixel[1]] for pixel in stations['pixel'].to_numpy()]

    # Get an array where each position represents pixel coordinates
    tile_pixels = np.indices(shape).transpose(1,2,0).reshape(shape[0]*shape[1], 2) + offset
    dist = distance_matrix(station_pixels, tile_pixels)
    weights = np.where(dist == 0, np.finfo('float32').max, 1.0 / dist )
    weights /=  weights.sum(axis=0)

    return np.dot(weights.T, stations[field_value].to_numpy()).reshape(shape).astype('float32')

def radiation_interpolation(tile_key, block_x, block_y, chunk_cloudobject, storage):
    tile_id, _ = os.path.splitext(tile_key)
    print(tile_id)

    # Write tile chunk to file
    chunk_file = os.path.join(tempfile.gettempdir(), tile_id + str(block_x) + '_' + str(block_y) + '.tif')
    print(chunk_file)

    with open(chunk_file, 'wb') as f:
        body = storage.get_cloudobject(chunk_cloudobject)
        f.write(body)

    with rasterio.open(chunk_file, 'r') as chunk_src:
        profile = chunk_src.profile

    extr_chunk_file = os.path.join(tempfile.gettempdir(), tile_id + '_extr_' + str(block_x) + '_' + str(block_y) + '.tif')
    rad_chunk_file = os.path.join(tempfile.gettempdir(), tile_id + '_rad_' + str(block_x) + '_' + str(block_y) + '.tif')

    # Compute solar irradiation from inputFile, creates radiation raster at outputFile
    extraterrestrial_irradiation = compute_solar_irradiation(inputFile=chunk_file, outputFile=rad_chunk_file)

    # Create and store a raster with extraterrestrial irradiation
    with rasterio.open(extr_chunk_file, 'w', **profile) as dest:
        data = np.full((profile['height'], profile['width']), extraterrestrial_irradiation, dtype='float32')
        dest.write(data, 1)

    with open(extr_chunk_file, 'rb') as f:
        extr_co = storage.put_cloudobject(body=f, bucket=DATA_BUCKET)

    with open(rad_chunk_file, 'rb') as f:
        rad_co = storage.put_cloudobject(body=f, bucket=DATA_BUCKET)

    return [(tile_key, 'extr', block_x, block_y, extr_co), (tile_key, 'rad', block_x, block_y, rad_co)]

def map_interpolation(tile_key, block_x, block_y, chunk_cloudobject, data_field, storage):
    tile_id, _ = os.path.splitext(tile_key)

    # Get SIAM meteo data
    siam_stream = storage.get_object(DATA_BUCKET, siam_data_key, stream=True)
    siam_data = pd.read_csv(siam_stream)

    # print(siam_data)

    chunk = storage.get_cloudobject(chunk_cloudobject)

    with rasterio.open(BytesIO(chunk)) as chunk_src:
        transform = chunk_src.transform
        profile = chunk_src.profile

        bounding_rect = box(chunk_src.bounds.left, chunk_src.bounds.top, chunk_src.bounds.right, chunk_src.bounds.bottom)
        filtered = pd.DataFrame(filter_stations(bounding_rect, siam_data))
        #print(filtered)

        if filtered.shape[0] == 0:
            return [(tile_key, data_field, block_x, block_y, None)]

        filtered['pixel'] = filtered.apply(lambda station: rasterio.transform.rowcol(transform, station['X'], station['Y']), axis=1)

        # Interpolate variables from meteo station data, generate raster with result
        dest_chunk_file = os.path.join(tempfile.gettempdir(), tile_id + '_' + data_field + '_' + str(block_x) + '_' + str(block_y) + '.tif')

        with rasterio.open(dest_chunk_file, 'w', **profile) as chunk_dest:
            if data_field == 'temp':
                elevations = chunk_src.read(1)  # Get elevations content
                print(dest_chunk_file)
                interpolation = compute_basic_interpolation(elevations.shape, filtered, 'tdet', (0, 0))
                interpolation += r * (elevations - zdet)
                chunk_dest.write(np.where(elevations == chunk_src.nodata, np.nan, interpolation), 1)
            elif data_field == 'humi':
                interpolation = compute_basic_interpolation((profile['height'], profile['width']), filtered, 'hr', (0, 0))
                chunk_dest.write(interpolation, 1)
            elif data_field == 'wind':
                interpolation = compute_basic_interpolation((profile['height'], profile['width']), filtered, 'v', (0, 0))
                chunk_dest.write(interpolation, 1)
            else:
                raise Exception(f'Unknown data field "{data_field}"')

    # Upload results to storage as Cloudobject
    with open(dest_chunk_file, 'rb') as f:
        co = storage.put_cloudobject(body=f, bucket=DATA_BUCKET)

    return [(tile_key, data_field, block_x, block_y, co)]

st4 = time.time()
fs_rad = fexec.map(radiation_interpolation, chunks)
res_rad = fexec.get_result(fs=fs_rad)
time_stage_4 = time.time() - st4
stats4 = get_stats(fexec, time_stage_4, '4')
print(f'Stage 4: {time_stage_4}')
st5 = time.time()
fs_temp = fexec.map(map_interpolation, chunks, extra_args=('temp', ), runtime_memory=2048)
res_temp = fexec.get_result(fs=fs_temp)
time_stage_5 = time.time() - st5
stats5 = get_stats(fexec, time_stage_5, '5')
print(f'Stage 5: {time_stage_5}')

st6 = time.time()
fs_humi = fexec.map(map_interpolation, chunks, extra_args=('humi', ), runtime_memory=2048)
res_humi = fexec.get_result(fs=fs_humi)
time_stage_6 = time.time() - st6
stats6 = get_stats(fexec, time_stage_6, '6')
print(f'Stage 6: {time_stage_6}')

st7 = time.time()
fs_wind = fexec.map(map_interpolation, chunks, extra_args=('wind', ), runtime_memory=2048)
res_wind = fexec.get_result(fs=fs_wind)
time_stage_7 = time.time() - st7
stats7 = get_stats(fexec, time_stage_7, '7')
print(f'Stage 7: {time_stage_7}')

res_flatten = []
for l in [res_rad, res_temp, res_humi, res_wind]:
    for elem in l:
        for sub_elem in elem:
           res_flatten.append(sub_elem)

#print(res_flatten)

grouped_chunks = collections.defaultdict(list)

for chunk_result in res_flatten:
    tile_key, data_field, block_x, block_y, co = chunk_result
    grouped_chunks[(tile_key, data_field)].append((block_x, block_y, co))
#print(grouped_chunks)

def merge_blocks(tile_data, chunks, storage):
    from rasterio.windows import Window

    tile_key, data_field = tile_data

    cobjs = [tup[2] for tup in chunks]
    if None in cobjs:
        return None

    # Get width and height from original tile
    source_tile_key = os.path.join(DTM_GEOTIFF_PREFIX, tile_key)
    with rasterio.open(BytesIO(storage.get_object(bucket=DATA_BUCKET, key=source_tile_key))) as source_tile:
        height = source_tile.profile['height']
        width = source_tile.profile['width']

    # Open first object to obtain profile metadata
    with rasterio.open(BytesIO(storage.get_cloudobject(chunks[0][2]))) as chunk_src:
        profile = chunk_src.profile
        profile.update(width=width)
        profile.update(height=height)

    # Iterate each object and print its block into the destination file
    merged_file = os.path.join(tempfile.gettempdir(), data_field + '_' + tile_key)
    with rasterio.open(merged_file, 'w', **profile) as dest:
        for chunk in chunks:
            j, i, co = chunk
            with rasterio.open(BytesIO(storage.get_cloudobject(co))) as src:
                step_w = math.floor(width / SPLITS)
                step_h = math.floor(height / SPLITS)
                curr_window = Window(round(step_w * i), round(step_h * j), src.width, src.height)
                content = src.read(1)
                dest.write(content, 1, window=curr_window)

    output_key = os.path.join(DTM_PREFIX, data_field, tile_key)
    with open(merged_file, 'rb') as out_file:
        storage.put_object(bucket=DATA_BUCKET, key=output_key, body=out_file)

    return output_key

iterdata = []
for (tile_id, data_field), chunks in grouped_chunks.items():
    iterdata.append(((tile_id, data_field), chunks))

st8 = time.time()
fs_merged = fexec.map(merge_blocks, iterdata, runtime_memory=2048)
tiles_merged = fexec.get_result(fs=fs_merged)
time_stage_8 = time.time() - st8
stats8 = get_stats(fexec, time_stage_8, '8')
print(f'Stage 8: {time_stage_8}')

tile_keys_merged = set([os.path.basename(t) for t in tiles_merged])
print(tile_keys_merged)


# Computation of potential evaporation
def compute_crop_evapotranspiration(temperatures,
                                    humidities,
                                    wind_speeds,
                                    external_radiations,
                                    global_radiations,
                                    KCs):
    gamma = 0.665*101.3/1000
    eSat = 0.6108 * np.exp((17.27*temperatures)/(temperatures+237.3))
    delta = 4098 * eSat / np.power((temperatures + 237.3),2)
    eA = np.where(humidities < 0, 0, eSat * humidities / 100)     # Avoid sqrt of a negative number
    T4 = 4.903 * np.power((273.3 + temperatures),4)/1000000000
    rSrS0 = global_radiations/(external_radiations * 0.75)
    rN = 0.8* global_radiations-T4*(0.34-0.14*np.sqrt(eA))*((1.35*rSrS0)-0.35)
    den = delta + gamma *(1 + 0.34* wind_speeds)
    tRad = 0.408 * delta * rN / den
    tAdv = gamma * (900/(temperatures+273))*wind_speeds * (eSat - eA)/den
    return ((tRad + tAdv) * 7 * KCs).astype('float32')

vineyard = ['VI', 'VO', 'VF', 'FV', 'CV' ]
olive_grove = ['OV', 'VO', 'OF', 'FL', 'OC']
fruit = ['FY', 'VF', 'OF', 'FF', 'CF']
nuts = ['FS', 'FV', 'FL', 'FF', 'CS' ]
citrus = ['CI', 'CV', 'OC', 'CF', 'CS' ]

def get_kc(feature):
    # TODO: Get more precise values of Kc
    print(feature['properties'].keys())
    # sigpac_use = feature['properties']['uso_sigpac']
    sigpac_use = 'FF'
    if sigpac_use in vineyard:
        # Grapes for wine - 0.3, 0.7, 0.45
        return 0.7
    if sigpac_use in olive_grove:
        # Olive grove - ini: 0.65, med: 0.7, end: 0.7
        return 0.7
    if sigpac_use in fruit:
        # Apples, Cherries, Pears - 0.45, 0.95, 0.7
        return 0.95
    if sigpac_use in nuts:
        # Almonds - 0.4, 0.9, 0.65
        return 0.9
    if sigpac_use in citrus:
        # Citrus, without ground coverage - 0.7, 0.65, 0.7
        return 0.65

    return None

def get_geometry_window(src, geom_bounds):
    left, bottom, right, top = geom_bounds
    src_left, src_bottom, src_right, src_top = src.bounds
    window = src.window(max(left,src_left), max(bottom,src_bottom), min(right,src_right), min(top,src_top))
    window_floored = window.round_offsets(op='floor', pixel_precision=3)
    w = math.ceil(window.width + window.col_off - window_floored.col_off)
    h = math.ceil(window.height + window.row_off - window_floored.row_off)
    return Window(window_floored.col_off, window_floored.row_off, w, h)

def compute_evapotranspiration_by_shape(tem, hum, win, rad, extrad, dst):

    import fiona
    from shapely.geometry import shape, box
    from rasterio import features

    non_arable_land = ['AG', 'CA', 'ED', 'FO', 'IM', 'PA', 'PR', 'ZU', 'ZV']

    #with fiona.open('zip://home/docker/shape.zip') as shape_src:
    with fiona.open('zip:///tmp/shape.zip') as shape_src:
        for feature in shape_src.filter(bbox=tem.bounds):
            KC = get_kc(feature)
            if KC is not None:
                geom = shape(feature['geometry'])
                window = get_geometry_window(tem, geom.bounds)
                win_transform = rasterio.windows.transform(window, tem.transform)
                # Convert shape to raster matrix
                image = features.rasterize([geom],
                                           out_shape=(window.height, window.width),
                                           transform = win_transform,
                                           fill = 0,
                                           default_value = 1).astype('bool')
                # Get values to compute evapotranspiration
                temperatures = tem.read(1, window=window)
                humidities = hum.read(1, window=window)
                wind_speeds = win.read(1, window=window)
                # Convert from W to MJ (0.0036)
                global_radiations = rad.read(1, window=window) * 0.0036
                external_radiations = extrad.read(1, window=window) * 0.0036
                KCs = np.full(temperatures.shape, KC)
                # TODO: compute external radiation
                #external_radiations = np.full(temperatures.shape, 14)
                # TODO: compute global radiation
                # global_radiations = np.full(temperatures.shape, 10)
                etc = compute_crop_evapotranspiration(
                        temperatures,
                        humidities,
                        wind_speeds,
                        external_radiations,
                        global_radiations,
                        KCs
                )
                etc[temperatures == tem.nodata] = dst.nodata
                etc[np.logical_not(image)] = dst.nodata
                dst.write(etc + dst.read(1, window=window), 1, window=window)

def compute_global_evapotranspiration(tem, hum, win, rad, extrad, dst):
    for ji, window in tem.block_windows(1):
        bounds = rasterio.windows.bounds(window, tem.transform)
        temperatures = tem.read(1, window=window)
        humidities = hum.read(1, window=window)
        wind_speeds = win.read(1, window=window)
         # Convert from W to MJ (0.0036)
        global_radiations = rad.read(1, window=window) * 0.0036
        external_radiations = extrad.read(1, window=window) * 0.0036
        # TODO: compute external radiation
        #external_radiations = np.full(temperatures.shape, 14)
        # TODO: compute global radiation
        # global_radiations = np.full(temperatures.shape, 10)
        # TODO: compute KCs
        KCs = np.full(temperatures.shape, 1)
        etc = compute_crop_evapotranspiration(
                temperatures,
                humidities,
                wind_speeds,
                external_radiations,
                global_radiations,
                KCs
        )
        dst.write(np.where(temperatures == tem.nodata, dst.nodata, etc), 1, window=window)

def combine_calculations(tile_key, storage):
    from functools import partial
      
    # Download shapefile
    shapefile = storage.get_object(bucket=DATA_BUCKET, key='shapefile_murcia.zip', stream=True)
    #with open('/home/docker/shape.zip', 'wb') as shapf:
    with open('/tmp/shape.zip', 'wb') as shapf:
        for chunk in iter(partial(shapefile.read, 200 * 1024 * 1024), ''):
            if not chunk:
                break
            shapf.write(chunk)
    try:
        temp = storage.get_object(bucket=DATA_BUCKET, key=os.path.join(DTM_PREFIX, 'temp', tile_key))
        humi = storage.get_object(bucket=DATA_BUCKET, key=os.path.join(DTM_PREFIX, 'humi', tile_key))
        rad = storage.get_object(bucket=DATA_BUCKET, key=os.path.join(DTM_PREFIX, 'rad', tile_key))
        extrad = storage.get_object(bucket=DATA_BUCKET, key=os.path.join(DTM_PREFIX, 'extr', tile_key))
        wind = storage.get_object(bucket=DATA_BUCKET, key=os.path.join(DTM_PREFIX, 'wind', tile_key))
    except StorageNoSuchKeyError:
        print("Storage error")
        return None
    
    output_file = os.path.join(tempfile.gettempdir(), 'eva' + '_' + tile_key)
    with rasterio.open(BytesIO(temp)) as temp_raster:
        with rasterio.open(BytesIO(humi)) as humi_raster:
            with rasterio.open(BytesIO(rad)) as rad_raster:
                with rasterio.open(BytesIO(extrad)) as extrad_raster:
                    with rasterio.open(BytesIO(wind)) as wind_raster:
                        profile = temp_raster.profile
                        profile.update(nodata=0)
                        with rasterio.open(output_file, 'w+', **profile) as dst:
#                             compute_global_evapotranspiration(temp_raster, humi_raster, wind_raster,
#                                                               rad_raster, extrad_raster, dst)
                            compute_evapotranspiration_by_shape(temp_raster, humi_raster, wind_raster,
                                                                rad_raster, extrad_raster, dst)
    
    output_key = os.path.join(DTM_PREFIX, 'eva', tile_key)
    with open(output_file, 'rb') as output_f:
        storage.put_object(bucket=DATA_BUCKET, key=output_key, body=output_f)
    return output_key

st9 = time.time()
fs_eva = fexec.map(combine_calculations, tile_keys_merged)
res_eva = fexec.get_result(fs=fs_eva)
time_stage_9 = time.time() - st9
stats9 = get_stats(fexec, time_stage_9, '9')
print(f'Stage 9: {time_stage_9}')
print(res_eva)

print(f'Files: {len(dtm_asc_keys)}')
input_sz = 0
for input_key in dtm_asc_keys:
    meta = storage.head_object(bucket=DATA_BUCKET, key=input_key)
    input_sz += int(meta['content-length'])
print(f'Input size: {round(input_sz / 1_000_000_000, 2)} GB')
elapsed = time.time() - s_time
print(f'Total time: {elapsed} s')

stats_list = [stats1, stats2, stats3, stats4, stats5, stats6, stats7, stats8, stats9]
total_price = sum(stat['Price (USD)'] for stat in stats_list)
print(f'Total price: {total_price} USD')

with open(f'stats_wc-aws-x1.pickle', 'wb') as pickle_file:
    pickle.dump([stats_list, elapsed, total_price], pickle_file)

fexec.plot(dst=fexec.executor_id)
fexec.clean(clean_cloudobjects=True)
