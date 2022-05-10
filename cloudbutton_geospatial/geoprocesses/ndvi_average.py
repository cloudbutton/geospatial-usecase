"""

AUTHOR: Juanjo

DATE: 15/04/2019

"""

import sys

import gdal
import numpy
import ogr
import osr


class NDVIAverageByParcel:

    @staticmethod
    def run(input_zone_polygon, input_value_raster):
        shp = ogr.Open(input_zone_polygon)
        lyr = shp.GetLayer()
        feat_list = range(lyr.GetFeatureCount())
        stat_dict = {}
        for FID in feat_list:
            feat = lyr.GetFeature(FID)
            mean_value = NDVIAverageByParcel.zonal_stats(feat, input_zone_polygon, input_value_raster)
            stat_dict[FID] = mean_value
        return stat_dict

    @staticmethod
    def zonal_stats(feat, input_zone_polygon, input_value_raster):
        try:
            # Open data
            raster = gdal.Open(input_value_raster)
            shp = ogr.Open(input_zone_polygon)
            lyr = shp.GetLayer()

            # Get raster georeference info
            transform = raster.GetGeoTransform()
            xOrigin = transform[0]
            yOrigin = transform[3]
            pixelWidth = transform[1]
            pixelHeight = transform[5]

            # Reproject vector geometry to same projection as raster
            # sourceSR = osr.SpatialReference()
            # sourceSR.ImportFromEPSG(4326)
            sourceSR = lyr.GetSpatialRef()
            targetSR = osr.SpatialReference()
            targetSR.ImportFromWkt(raster.GetProjectionRef())
            coordTrans = osr.CoordinateTransformation(sourceSR, targetSR)

            geom = feat.GetGeometryRef()
            geom.Transform(coordTrans)

            if geom.GetGeometryName() == 'MULTIPOLYGON':
                count = 0
                pointsX = []
                pointsY = []

                for polygon in geom:
                    geomInner = geom.GetGeometryRef(count)
                    ring = geomInner.GetGeometryRef(0)
                    numpoints = ring.GetPointCount()
                    for p in range(numpoints):
                        lon, lat, z = ring.GetPoint(p)
                        pointsX.append(lon)
                        pointsY.append(lat)
                    count += 1
            elif geom.GetGeometryName() == 'POLYGON':
                ring = geom.GetGeometryRef(0)
                numpoints = ring.GetPointCount()
                pointsX = []
                pointsY = []
                for p in range(numpoints):
                    lon, lat, z = ring.GetPoint(p)
                    pointsX.append(lon)
                    pointsY.append(lat)
            else:
                sys.exit('ERROR')

            xmin = min(pointsX)
            xmax = max(pointsX)
            ymin = min(pointsY)
            ymax = max(pointsY)

            # Specify offset and rows and columns to read
            xoff = int((xmin - xOrigin) / pixelWidth)
            yoff = int((yOrigin - ymax) / pixelWidth)
            xcount = int((xmax - xmin) / pixelWidth) + 1
            ycount = int((ymax - ymin) / pixelWidth) + 1

            # Create memory target raster
            target_ds = gdal.GetDriverByName('MEM').Create('', xcount, ycount, 1, gdal.GDT_Byte)
            target_ds.SetGeoTransform((
                xmin, pixelWidth, 0,
                ymax, 0, pixelHeight,
            ))
            # Create for target raster the same projection as for the value raster
            raster_srs = osr.SpatialReference()
            raster_srs.ImportFromWkt(raster.GetProjectionRef())
            target_ds.SetProjection(raster_srs.ExportToWkt())

            # Rasterize zone polygon to raster
            gdal.RasterizeLayer(target_ds, [1], lyr, burn_values=[1])
            # Read raster as arrays
            banddataraster = raster.GetRasterBand(1)
            dataraster = banddataraster.ReadAsArray(xoff, yoff, xcount, ycount).astype(numpy.float)
            bandmask = target_ds.GetRasterBand(1)
            datamask = bandmask.ReadAsArray(0, 0, xcount, ycount).astype(numpy.float)
            # Mask zone of raster

            zoneraster = numpy.ma.masked_array(dataraster, numpy.logical_not(datamask))
            # Calculate statistics of zonal raster
            return numpy.average(zoneraster), numpy.mean(zoneraster), numpy.median(zoneraster), numpy.std(
                zoneraster), numpy.var(zoneraster)
        except Exception:
            return 0, 0, 0, 0, 0
