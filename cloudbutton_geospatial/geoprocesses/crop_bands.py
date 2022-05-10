"""

AUTHOR: Juanjo

DATE: 03/04/2019

"""

import operator
import os
import shutil

from osgeo import gdalnumeric, ogr
import numpy as np
from PIL import Image, ImageDraw

# This function will convert the rasterized clipper shapefile
# to a mask for use within GDAL.
from geoprocesses import utils


def image_to_array(i):
    """
    Converts a Python Imaging Library array to a
    gdalnumeric image.
    """
    a = gdalnumeric.fromstring(i.tobytes(), 'b')
    a.shape = i.im.size[1], i.im.size[0]
    return a


def array_to_image(a):
    """
    Converts a gdalnumeric array to a
    Python Imaging Library Image.
    """
    i = Image.fromstring('L', (a.shape[1], a.shape[0]), (a.astype('b')).tostring())
    return i


def world_to_pixel(geoMatrix, x, y):
    """
    Uses a gdal geomatrix (gdal.GetGeoTransform()) to calculate
    the pixel location of a geospatial coordinate
    """
    ulX = geoMatrix[0]
    ulY = geoMatrix[3]
    xDist = geoMatrix[1]
    yDist = geoMatrix[5]
    rtnX = geoMatrix[2]
    rtnY = geoMatrix[4]
    pixel = int((x - ulX) / xDist)
    line = int((ulY - y) / xDist)
    return (pixel, line)


#
#  EDIT: this is basically an overloaded
#  version of the gdal_array.OpenArray passing in xoff, yoff explicitly
#  so we can pass these params off to CopyDatasetInfo
#
def open_array(array, prototype_ds=None, xoff=0, yoff=0):
    #ds = gdal.Open( gdalnumeric.GetArrayFilename(array))
    from osgeo import gdal_array
    ds = gdal_array.OpenArray(array)

    if ds is not None and prototype_ds is not None:
        if type(prototype_ds).__name__ == 'str':
            prototype_ds = gdalnumeric.gdal.Open(prototype_ds)
        if prototype_ds is not None:
            gdalnumeric.CopyDatasetInfo( prototype_ds, ds, xoff=xoff, yoff=yoff )
    return ds


def histogram(a, bins=range(0,256)):
    """
    Histogram function for multi-dimensional array.
    a = array
    bins = range of numbers to match
    """
    fa = a.flat
    n = gdalnumeric.searchsorted(gdalnumeric.sort(fa), bins)
    n = gdalnumeric.concatenate([n, [len(fa)]])
    hist = n[1:] - n[:-1]
    return hist


def stretch(a):
    """
    Performs a histogram stretch on a gdalnumeric array image.
    """
    hist = histogram(a)
    im = array_to_image(a)
    lut = []
    for b in range(0, len(hist), 256):
        # step size
        step = np.reduce(operator.add, hist[b:b + 256]) / 255
        # create equalization lookup table
        n = 0
        for i in range(256):
            lut.append(n / step)
            n = n + hist[i + b]
    im = im.point(lut)
    return image_to_array(im)


class CropBandsProcess:

    @staticmethod
    def run(bands, map_mask, dst_dir):
        cropped_bands = []
        for band in bands:
            # http://pcjericks.github.io/py-gdalogr-cookbook/raster_layers.html#clip-a-geotiff-with-shapefile
            # http://karthur.org/2015/clipping-rasters-in-python.html
            # https://gis.stackexchange.com/questions/228602/clip-raster-by-mask-without-change-values
            # http://karthur.org/2015/clipping-rasters-in-python.html

            # Copiamos el fichero correspondiente a la banda en el directorio destino para las bandas
            band_dir, band_filename = os.path.split(band)
            shutil.copy(band, dst_dir)

            # raster_path es nuestra banda origen
            raster_path = os.path.join(dst_dir, band_filename)
            if band_filename.endswith('.jp2'):
                raster_gtiff = raster_path.replace('.jp2', '.tiff')
                utils.jp2_to_gtiff(raster_path, raster_gtiff)
                raster_path = raster_gtiff

            # Load the source data as a gdalnumeric array
            rast = gdalnumeric.LoadFile(raster_path)

            # Also load as a gdal image to get geotransform
            # (world file) info
            srcImage = gdalnumeric.gdal.Open(raster_path)
            gt = srcImage.GetGeoTransform()
            srcImage = None

            # Create an OGR layer from a boundary shapefile
            shapef = ogr.Open(map_mask)
            lyr = shapef.GetLayer(os.path.split(os.path.splitext(map_mask)[0])[1])
            poly = lyr.GetNextFeature()

            # Convert the layer extent to image pixel coordinates
            minX, maxX, minY, maxY = lyr.GetExtent()
            ulX, ulY = world_to_pixel(gt, minX, maxY)
            lrX, lrY = world_to_pixel(gt, maxX, minY)

            # Calculate the pixel size of the new image
            pxWidth = int(lrX - ulX)
            pxHeight = int(lrY - ulY)

            # If the clipping features extend out-of-bounds and ABOVE the raster...
            if gt[3] < maxY:
                # In such a case... ulY ends up being negative--can't have that!
                iY = ulY
                ulY = 0

            try:
                # Multi-band image?
                clip = rast[:, ulY:lrY, ulX:lrX]
            except IndexError:
                # Nope: Must be single-band
                clip = rast[ulY:lrY, ulX:lrX]

            # create pixel offset to pass to new image Projection info
            xoffset = ulX
            yoffset = ulY

            # Create a new geomatrix for the image
            gt2 = list(gt)
            gt2[0] = minX
            gt2[3] = maxY

            # Map points to pixels for drawing the boundary on a blank 8-bit,
            # black and white, mask image.
            points = []
            pixels = []
            geom = poly.GetGeometryRef()
            pts = geom.GetGeometryRef(0)
            for p in range(pts.GetPointCount()):
                points.append((pts.GetX(p), pts.GetY(p)))
            for p in points:
                pixels.append(world_to_pixel(gt2, p[0], p[1]))

            raster_poly = Image.new("L", (pxWidth, pxHeight), 1)
            rasterize = ImageDraw.Draw(raster_poly)
            rasterize.polygon(pixels, 0)

            # If the clipping features extend out-of-bounds and ABOVE the raster...
            if gt[3] < maxY:
                # The clip features were "pushed down" to match the bounds of the
                #   raster; this step "pulls" them back up
                premask = image_to_array(raster_poly)
                # We slice out the piece of our clip features that are "off the map"
                mask = np.ndarray((premask.shape[-2] - abs(iY), premask.shape[-1]), premask.dtype)
                mask[:] = premask[abs(iY):, :]
                mask.resize(premask.shape)  # Then fill in from the bottom

                # Most importantly, push the clipped piece down
                gt2[3] = maxY - (maxY - gt[3])
            else:
                mask = image_to_array(raster_poly)

            # Clip the image using the mask
            try:
                clip = gdalnumeric.choose(mask, (clip, 0))
                clip = clip.astype(gdalnumeric.numpy.float32)
            # If the clipping features extend out-of-bounds and BELOW the raster...
            except ValueError:
                # We have to cut the clipping features to the raster!
                rshp = list(mask.shape)
                if mask.shape[-2] != clip.shape[-2]:
                    rshp[0] = clip.shape[-2]

                if mask.shape[-1] != clip.shape[-1]:
                    rshp[1] = clip.shape[-1]

                mask.resize(*rshp, refcheck=False)

                clip = gdalnumeric.choose(mask, (clip, 0))
                clip = clip.astype(gdalnumeric.numpy.float32)

            # Save new tiff
            raster_name, raster_ext = os.path.splitext(band_filename)
            mask_dir, mask_file = os.path.split(map_mask)
            mask_name, mask_ext = os.path.splitext(mask_file)
            cropped_band = os.path.join(dst_dir, raster_name + '-' + mask_name + '.tiff')
            gtiff_driver = gdalnumeric.gdal.GetDriverByName('GTiff')
            if gtiff_driver is None:
                raise ValueError("Can't find GeoTiff Driver")
            a = open_array(clip, prototype_ds=raster_path, xoff=xoffset, yoff=yoffset)
            gtiff_driver.CreateCopy(cropped_band, a)

            gdalnumeric.gdal.ErrorReset()

            cropped_bands.append(cropped_band)

            # Eliminamos los ficheros de las bandas auxiliares que copiamos en el directorio de destino
            os.remove(raster_path)
            raster_path = raster_path.replace('.tiff', '.jp2')
            if os.path.exists(raster_path):
                os.remove(raster_path)
        return cropped_bands
