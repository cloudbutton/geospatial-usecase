"""
Este módulo contiene métodos de utilidad para la descarga de
imágenes del satélite Sentinel-2.

Los distintos tiles del sistema de coordenadas MGRS en que
se divide España se pueden encontrar
en esta web https://www.asturnatura.com/sinflac/utm-mgrs.php

La documentación de la librería sentinelsat se puede consultar
en la siguiente dirección:
https://sentinelsat.readthedocs.io/en/stable/api.html

"""

import collections
import os
import os.path
import zipfile

import sentinelsat

SENT_USER = 'vmoreno'
SENT_PASS = '12345678'


BANDS_DIR = 'bands'
ZIP_EXTENSION = ".zip"
GRANULE_DIR = 'GRANULE'
IMAGE_DATA_DIR = 'IMG_DATA'
SAFE_EXTENSION = '.SAFE'
JP2_EXTENSION = '.jp2'


def download_products(tiles, start_date, end_date, output_folder, show_progressbars=True):
    """
    Descarga todos los productos del satélite Sentinel-2 para los tipos de producto S2MS2Ap y S2MSI1C

    :param tiles: Tiles para filtrar la descarga
    :param start_date: Fecha inicial en que se tomaron las imágenes
    :param end_date: Fecha final en que se tomaron las imágenes
    :param output_folder: Directorio en el que se almacenarán las imágenes
    :param show_progressbars: Indica si se muestran las barras de progreso durante la descarga
    """

    print('Downloading products')
    api = sentinelsat.SentinelAPI(user=SENT_USER,
                                  password=SENT_PASS,
                                  api_url='https://scihub.copernicus.eu/dhus',
                                  show_progressbars=show_progressbars)

    query_kwargs = {
        'platformname': 'Sentinel-2',
        'producttype': ('S2MS2Ap', 'S2MSI1C'),
        'cloudcoverpercentage': (0, 15),
        'date': (start_date, end_date)
    }

    products = collections.OrderedDict()
    for tile in tiles:
        kw = query_kwargs.copy()
        kw['tileid'] = tile
        pp = api.query(**kw)
        products.update(pp)

    api.download_all(products, output_folder)


# def extract_bands(sentinel_data_dir, sentinel_downloads_dir, sentinel_zip_filename, bands):
#     """
#     Recupera los ficheros correspondientes a las bandas *bands* contenidos en
#     el fichero zip (*sentinel_zip_filename*) descargado como producto del satélite Sentinel-2.
#     Las bandas las guarda en el directorio 'bands', en una carpeta con el nombre de producto.
#
#     :param sentinel_data_dir: Directorio de datos para los scripts de SENTINEL
#     :param sentinel_downloads_dir: Directorio en el que se encuentran los ficheros descargados
#     :param sentinel_zip_filename: Nombre del fichero del que extraer las bandas
#     :param bands: Nombre de las bandas a extraer
#     """
#
#     print('Extracting band ' + sentinel_zip_filename)
#     # Unzip the file product
#     sentinel_zip_file_path = os.path.abspath(os.path.join(sentinel_downloads_dir, sentinel_zip_filename))
#     zip_ref = zipfile.ZipFile(sentinel_zip_file_path)
#     zip_ref.extractall(sentinel_downloads_dir)
#     zip_ref.close()
#
#     # Create dir for product if doesn't exist
#     full_product_name = sentinel_zip_filename.split('.')[0]
#     bands_dir_path = os.path.join(sentinel_data_dir, BANDS_DIR, full_product_name)
#     try:
#         os.makedirs(bands_dir_path)
#     except OSError as e:
#         if e.errno != errno.EEXIST:
#             raise
#
#     # Extract the bands from product.SAFE dir to product bands dir
#     product_safe_dir = full_product_name + SAFE_EXTENSION
#     granule_dir_path = os.path.join(sentinel_downloads_dir, product_safe_dir, GRANULE_DIR)
#     granule_dirs = [d for d in os.listdir(granule_dir_path) if
#                     (os.path.isdir(os.path.join(granule_dir_path, d))) and (d != '.') and (d != '..')]
#     # There is only one folder
#     granule_dir = granule_dirs[0]
#     img_data_path = os.path.join(granule_dir_path, granule_dir, IMAGE_DATA_DIR)
#     band_files = [bf for bf in os.listdir(img_data_path)]
#     selected_bands = [band_file for band_file in band_files for band in bands if band_file.endswith(band + JP2_EXTENSION)]
#     for band in selected_bands:
#         band_path = os.path.join(img_data_path, band)
#         print(f'Copying band from {band_path} to {bands_dir_path}')
#         shutil.copy(band_path, bands_dir_path)
#
#
# def extract_bands_from_downloads(sentinel_data_dir, sentinel_downloads_dir, bands):
#     print('Extracting bands')
#     sentinel_file_names = [f for f in os.listdir(sentinel_downloads_dir) if
#                            (os.path.isfile(os.path.join(sentinel_downloads_dir, f))) and (f.endswith(ZIP_EXTENSION))]
#     for sentinel_zip_filename in sentinel_file_names:
#         extract_bands(sentinel_data_dir, sentinel_downloads_dir, sentinel_zip_filename, bands)


def unzip_bands_dirs(sentinel_downloads_dir):
    print('Unzipping bands')
    sentinel_file_names = [os.path.join(sentinel_downloads_dir, f) for f in os.listdir(sentinel_downloads_dir) if
                           (os.path.isfile(os.path.join(sentinel_downloads_dir, f))) and (f.endswith(ZIP_EXTENSION))]
    for sentinel_zip_filename in sentinel_file_names:
        print(f'Unzipping {sentinel_zip_filename}')
        zip_ref = zipfile.ZipFile(sentinel_zip_filename)
        zip_ref.extractall(sentinel_downloads_dir)
        zip_ref.close()


def download_bands(tiles, start_date, end_date, sentinel_downloads_dir):

    print('Downloading bands from Sentinel')
    download_products(tiles=tiles,
                      start_date=start_date,
                      end_date=end_date,
                      output_folder=sentinel_downloads_dir)
    unzip_bands_dirs(sentinel_downloads_dir)
    # extract_bands_from_downloads(sentinel_data_dir, sentinel_downloads_dir)
    print('Downloading bands from Sentinel finished')
