"""

AUTHOR: Juanjo

DATE: 14/03/2019

"""

import os

import subprocess


def jp2_to_gtiff(jp2_filepath, gtif_filepath, otype='Float32'):
    # Cómo instalar GDAL en Windows http://www.sigdeletras.com/2016/instalacion-de-python-y-gdal-en-windows/

    print('Invoca a gdal_translate')
    val = subprocess.check_call(f'gdal_translate -ot "{otype}" -of "Gtiff" {jp2_filepath} {gtif_filepath}', shell=True)
    print(f'gdal_translate ha finalizado con valor {val}')


def select_b4_b8_bands(product_dir):
    # 1. Find the bands to work with
    granule_dir = os.path.join(product_dir, 'GRANULE')
    granule_dirs = [d for d in os.listdir(granule_dir) if
                    (os.path.isdir(os.path.join(granule_dir, d))) and (d != '.') and (d != '..')]
    img_data_dir = os.path.join(granule_dir, granule_dirs[0] + '/IMG_DATA/R10m')
    band_files = [bf for bf in os.listdir(img_data_dir)]
    b4 = None
    b8 = None
    for band_file in band_files:
        if '_B04_' in band_file:
            b4 = os.path.join(img_data_dir, band_file)
        if '_B08_' in band_file:
            b8 = os.path.join(img_data_dir, band_file)
    return b4, b8


def get_gdal_calc_path():
    try:
        import gdal_calc
    except ImportError:
        return None
    return os.path.abspath(gdal_calc.__file__)


def ndvi_filter_calc(ndvi_file_path, calc_expr, dst_dir, out_filename, nodata='0', typeof='Byte'):
    gdal_calc_path = get_gdal_calc_path()

    output_file_path = os.path.join(dst_dir, out_filename)

    # Generate string of process.
    gdal_calc_process = f'python {gdal_calc_path} -A {ndvi_file_path} --outfile={output_file_path} --calc={calc_expr} --NoDataValue={nodata} --type={typeof}'

    subprocess.check_call(gdal_calc_process, shell=True)
