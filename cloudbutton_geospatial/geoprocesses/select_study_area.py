"""

AUTHOR: Juanjo

DATE: 02/04/2019

"""

import ogr
import os


class SelectStudyAreaProcess:

    @staticmethod
    def run(map_sheet, filter_field, filter_value, dst_dir):
        print(f'Selecting {filter_value} from {filter_field}')

        normalized_field = filter_field.replace('-', '_')
        normalized_value = filter_value.replace('-', '_')

        # Check if the dst file exists
        study_area_file_name = f'{normalized_field}__{normalized_value}.shp'
        study_area_file = os.path.join(dst_dir, study_area_file_name)
        if os.path.exists(study_area_file):
            return study_area_file

        datasource = ogr.Open(map_sheet)
        input_layer = datasource.GetLayer()

        # Filter by our query
        query_str = "{} = '{}'".format(filter_field, filter_value)
        input_layer.SetAttributeFilter(query_str)

        # Copy Filtered Layer and Output File
        driver = ogr.GetDriverByName('ESRI Shapefile')
        out_ds = driver.CreateDataSource(study_area_file)
        out_layer = out_ds.CopyLayer(input_layer, str(filter_value))
        del input_layer, out_layer, out_ds
        return study_area_file
