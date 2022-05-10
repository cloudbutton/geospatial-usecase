"""
https://pypi.org/project/pyshp/

AUTHOR: Juanjo

DATE: 02/04/2019

"""

import os
import subprocess


class SelectParcelProcess:

    @staticmethod
    def run(parcels_dir, parcels_file, study_area):
        print('Selecting parcels from study area')
        study_area_dir, study_area_filename = os.path.split(study_area)
        parcels_file_name = os.path.join(parcels_dir, study_area_filename)

        # Cómo instalar GDAL en Windows http://www.sigdeletras.com/2016/instalacion-de-python-y-gdal-en-windows/
        val = subprocess.check_call(f'ogr2ogr -clipsrc {study_area} {parcels_file_name} {parcels_file}')
        print(f'ogr2ogr - Selecting parcels has finished {val}')
        return parcels_file_name
