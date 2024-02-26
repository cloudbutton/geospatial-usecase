import sys
sys.path.append('../')

import datetime as dt
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import rasterio
import lithops
import time
import shutil
import os
import gc
import datetime
import math
import collections
from rasterio.io import MemoryFile
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from IPython import display

import cloudbutton_geospatial.s2froms3 as s2froms3
from cloudbutton_geospatial.utils import notebook as notebook_utils
from cloudbutton_geospatial.io_utils.ndvi import get_ndvi_params, ndvi_calculation, ndvi_tile_sentinel, get_subset_raster, lonlat_to_utm, get_poly_within
from cloudbutton_geospatial.io_utils.plot import tiff_overview, plot_map

default_from = datetime.date(year=2019, month=9, day=17)
default_to = datetime.date(year=2020, month=9, day=16)

percentage = 15

start_date = default_from  # Start date to search images
end_date = default_to  # End date to search images
what = ['B04', 'B08']
cc = percentage

# Demonstration: Californa tile coords
cali_coords = [
    [38.510161585585045, -122.99194335937501],
    [36.071996052851325, -121.25610351562501],
    [36.96374622851412, -121.46484375000001],
    [37.575739257598414, -121.55273437500001],
    [39.15202827678992, -122.62939453125001],
    [39.703620879017976, -123.12377929687501],
    [36.74397383313428, -119.94873046875001],
   [38.472809653752314, -121.60766601562501]
]


scenes_f1 = []
scenes_f2 = []

# To use the demonstration tile coords, coment this line to use teh coords obtained from the map before
coords = cali_coords

for latency, longitude in coords:
    try:
        # Get scenes from intital date
        f1 = s2froms3.get_scene_list(lon=longitude, lat=latency, start_date=start_date, end_date=start_date,
        what=what, cloud_cover_le=cc)
        print(f1)

        # Get scenes from end date
        f2 = s2froms3.get_scene_list(lon=longitude, lat=latency, start_date=end_date, end_date=end_date,
        what=what, cloud_cover_le=cc)
        print(f2)

        # Not add duplicated scenes
        if len(scenes_f1) == 0 or f1 not in scenes_f1:
            scenes_f1.append(f1)
            scenes_f2.append(f2)

            print(f'Found scenes {start_date}:', f1)
            print(f'Found scenes {end_date}:', f2)
            print(f'Lon: {longitude}, Lat: {latency}')
            print(f'Cell: {f1[0][0].split("/")[2]} {f1[0][0].split("/")[3]} {f1[0][0].split("/")[4]}\n')
    
    except Exception:
        pass

if len(scenes_f1) == 0:
    raise Exception('No data found')

scenes_f1 = scenes_f1[:2]
scenes_f2 = scenes_f2[:2]

scene = scenes_f1[-1][-1]
scene_band = rasterio.open('s3://'+scene[0])
windows = list(scene_band.block_windows())

tile_band_keys = [tup[0] for tup in scenes_f1]
print(tile_band_keys)

fexec = lithops.FunctionExecutor()

def get_tile_meta(key, foo):
    with rasterio.open('s3://'+key) as src:
        x1, y1 = src.profile['transform'] * (0, 0)
        x2, y2 = src.profile['transform'] * (src.profile['width'], src.profile['height'])
    return key, (x1, y1), (x2, y2)

fs_meta = fexec.map(get_tile_meta, tile_band_keys)
tiles_meta = fexec.get_result(fs=fs_meta)
print(tiles_meta)

regions = [(tile_id, bound1, bound2,
            int(tile_id.split('/')[7].split('_')[1][:2]),
            True) for tile_id, bound1, bound2 in tiles_meta]

def calculate_ndvi(scene, ij_window, storage):
    ij, window = ij_window
    band_4_s3_loc, band_8_s3_loc = scene
    band_path = band_4_s3_loc.split('/')
    ndvi_local = f'/tmp/{band_path[7]}_{ij}_NDVI.tif'
    jpg_local = f'/tmp/{band_path[7]}_{ij}_NDVI.jpg'

    # generate nir and red objects as arrays in float64 format
    band4 = rasterio.open('s3://'+band_4_s3_loc)  # red
    band8 = rasterio.open('s3://'+band_8_s3_loc)  # nir

    profile = band4.profile
    profile.update(dtype='float64')
    profile.update(width=window.width)
    profile.update(height=window.height)

    with rasterio.open(ndvi_local, 'w', **profile) as dst:
        red = band4.read(1, window=window).astype('float64')
        nir = band8.read(1, window=window).astype('float64')
        ndvi = (np.where((nir + red) == 0., 0, (nir - red) / (nir + red))).astype('float64')
        ndvi_mean = np.mean(ndvi, axis=0)
        dst.write(ndvi, 1)
        ndvi[0][0] = -1
        ndvi[0][1] = 1
        plt.imsave(jpg_local, ndvi, cmap="RdYlGn")

    with open(jpg_local, 'rb') as jpg_temp:
        co_jpg = storage.put_cloudobject(jpg_temp.read(), key=jpg_local.replace('/tmp/', ''))

    return ndvi_local, ndvi_mean, co_jpg


def compute_ndvi_diff(old_scene, new_scene, ij_window, storage):
    ij, window = ij_window
    band_path = new_scene[0].split('/')
    jpg_diff_local = f'/tmp/{band_path[7]}_{ij}_NDVI_DIFF.jpg'
    key = old_scene[0].split('/')[7].rsplit('_', 3)[0]

    ndvi_local_f1, ndvi_mean_f1, co_jpg_f1 = calculate_ndvi(old_scene, ij_window, storage)
    ndvi_local_f2, ndvi_mean_f2, co_jpg_f2 = calculate_ndvi(new_scene, ij_window, storage)

    ndvi_old = rasterio.open(ndvi_local_f1)
    ndvi_new = rasterio.open(ndvi_local_f2)

    profile = ndvi_old.profile
    profile.update(dtype='float64')
    profile.update(width=window.width)
    profile.update(height=window.height)

    no = ndvi_old.read(1).astype('float64')
    nn = ndvi_new.read(1).astype('float64')
    ndvi_cmp = ((nn - no) * (nn + no)).astype('float64')
    ndvi_cmp[0][0] = -1
    ndvi_cmp[0][1] = 1
    plt.imsave(jpg_diff_local, ndvi_cmp, cmap="RdYlGn")

    with open(jpg_diff_local, 'rb') as jpg_diff_file:
        co_jpg_diff = storage.put_cloudobject(jpg_diff_file, key=jpg_diff_local.replace('/tmp/', ''))

    return key, ij_window, co_jpg_f1, co_jpg_f2, co_jpg_diff

fexec = lithops.FunctionExecutor()

iterdata = []
for scene_f1, scene_f2 in zip(scenes_f1, scenes_f2):
    for wd in windows:
        iterdata.append((scene_f1[0], scene_f2[0], wd))

fs = fexec.map(compute_ndvi_diff, iterdata)
results = fexec.get_result(fs)

grouped_results = collections.defaultdict(list)

for res in results:
    key, ij_window, co_jpg_f1, co_jpg_f2, co_jpg_diff = res
    grouped_results[key].append((ij_window, co_jpg_f1, co_jpg_f2, co_jpg_diff))

print(grouped_results.keys())

fexec.plot(dst=fexec.executor_id)

import boto3

s3client = boto3.client('s3')
total_sz = 0

for scenes in [scenes_f1, scenes_f2]:
    for scene in scenes:
        for band_path in scene[0]:
            bucket, key = band_path.split('/', 1)
            meta = s3client.head_object(Bucket=bucket, Key=key)
            total_sz += int(meta['ResponseMetadata']['HTTPHeaders']['content-length'])

stats = [f.stats for f in fexec.futures]
mean_exec_time = np.mean([stat['worker_func_exec_time'] for stat in stats])
throughput = (total_sz / 1_000_000_000) / mean_exec_time

print(f'Procesed {round(total_sz / 1_000_000_000, 2)} GB in {round(mean_exec_time, 2)} s => {round(throughput, 2)} GB/s')

gbxms_price = 0.0000000167
sum_total_time = sum([stat['worker_exec_time'] for stat in stats]) * 1000
price = gbxms_price * sum_total_time * 1  # Price GB/ms * sum of times in ms * 1 GB
print(f'Experiment total price is {round(price, 3)} USD')
