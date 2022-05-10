"""
Utilities to download Sentinel-2 COGS from S3

Original package: https://github.com/kikocorreoso/s2froms3
GNU Affero General Public License v3.0
"""

import json
import os
import datetime as dt
from typing import Union, Iterable, List, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from itertools import cycle
from time import sleep
import boto3

import mgrs  # type: ignore
import s3fs  # type: ignore

from .utils import _iter_dates
from .products import Properties

CPU_COUNT = os.cpu_count()


def get_scene_list(
    lon: float,
    lat: float,
    start_date: Union[dt.date, dt.datetime],
    end_date: Union[dt.date, dt.datetime],
    what: Union[str, Iterable[str]],
    cloud_cover_le: float = 50,
    use_ssl: bool = True,
    also: Optional[List[str]] = None
) -> List[str]:
    """
    Returns the scene list of a given location

    Parameters
    ----------
    lon: float
        Float value defining the longitude of interest.
    lat: float
        Float value defining the latitude of interest.
    start_date: datetime.date or datetime.datetime
        Date to start looking for images to download.
    end_date: datetime.date or datetime.datetime
        Date to end looking for images to download.
    what: str or array_like
        Here you have to define what you want to download as a string or as an
        array_like of strings. Valid values are:
            'TCI', 'B01', 'B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08',
            'B8A', 'B09', 'B11', 'B12', 'AOT', 'WVP', 'SCL'
    cloud_cover_le: float
        FLoat indicating the maximum cloud cover allowed. If the value is 10
        it indicates the allowed cloud cover on the image must be lower or
        equal to 10%. Default value is 50 (%).
    also: list or None
        A list detailing if you want to download other COG files in the
        borders. Valid values are 'N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'.
        See below where 'X' is the original target.
          +-----+-----+-----+
          |NW   |  N  |   NE|
          |     |     |     |
          |     |     |     |
          +-----+-----+-----+
          |     |     |     |
          |W    |  X  |    E|
          |     |     |     |
          +-----+-----+-----+
          |     |     |     |
          |     |     |     |
          |SW   |  S  |   SE|
          +-----+-----+-----+
    """
    _also = {
        "N": {"x": 0, "y": 150_000},
        "NE": {"x": 150_000, "y": 150_000},
        "E": {"x": 150_000, "y": 0},
        "SE": {"x": 150_000, "y": -150_000},
        "S": {"x": 0, "y": -150_000},
        "SW": {"x": -150_000, "y": -150_000},
        "W": {"x": -150_000, "y": 0},
        "NW": {"x": -150_000, "y": 150_000},
    }
    if start_date > end_date:
        raise ValueError("`start_date` has to be lower or equal than `end_date`")
    if isinstance(what, str):
        what = [what]
    for w in what:
        if w.upper() not in [item.value for item in Properties]:
            raise ValueError(f"{w} is not a valid product")

    fs = s3fs.S3FileSystem(anon=True, use_ssl=use_ssl)

    start_date = dt.date(start_date.year, start_date.month, start_date.day)
    end_date = dt.date(end_date.year, end_date.month, end_date.day)

    rpaths = []

    path: Union[str, Path]
    m = mgrs.MGRS()

    # Get the remote and local paths for the original target
    coord = m.toMGRS(lat, lon, MGRSPrecision=0)
    number, a, b = coord[:-3], coord[-3:-2], coord[-2:]

    def check_tile(_c):
        name = _c.split("/")[-1]
        info = _c + "/" + name + ".json"
        with fs.open(info, "r") as f:
            info = json.load(f)
        date_str = name.split("_")[2]
        cc = info["properties"]["eo:cloud_cover"]
        date = dt.datetime.strptime(date_str, "%Y%m%d").date()
        if cloud_cover_le >= cc and start_date <= date <= end_date:
            package = []
            for w in what:
                package.append(str(_c + f"/{w}.tif"))
            rpaths.append(tuple(package))

    def check_package(path):
        _contents = fs.ls(path)
        with ThreadPoolExecutor() as exe:
            for _c in _contents:
                exe.submit(check_tile, _c)

    with ThreadPoolExecutor() as ex:
        for yy, mm in _iter_dates(start_date, end_date):
            path = f"sentinel-cogs/sentinel-s2-l2a-cogs/{number}/{a}/{b}/{yy}/{mm}"
            ex.submit(check_package, path)

    # Get the remote and local paths for the adjacent COGS to the target,
    # if required
    # TODO (josep) make it threaded as before
    if also is None:
        also = []
    for al in also:
        al = al.upper()
        if al not in list(_also.keys()):
            raise ValueError(f'"{al}" is not a valid value for `also` keyword')
        z, hem, x, y = m.MGRSToUTM(coord)
        x += _also[al]["x"]
        y += _also[al]["y"]
        _coord = m.UTMToMGRS(z, hem, x, y, MGRSPrecision=0)
        number, a, b = _coord[:-3], _coord[-3:-2], _coord[-2:]
        for yy, mm in _iter_dates(start_date, end_date):
            path = "sentinel-cogs/sentinel-s2-l2a-cogs/" f"{number}/{a}/{b}/{yy}/{mm}"
            _contents = fs.ls(path)
            for _c in _contents:
                name = _c.split("/")[-1]
                info = _c + "/" + name + ".json"
                with fs.open(info, "r") as f:
                    info = json.load(f)
                date_str = name.split("_")[2]
                cc = info["properties"]["eo:cloud_cover"]
                date = dt.datetime.strptime(date_str, "%Y%m%d").date()
                if cloud_cover_le >= cc and start_date <= date <= end_date:
                    package = []
                    for w in what:
                        package.append(str(_c + f"/{w}.tif"))
                    rpaths.append(tuple(package))

    if not rpaths:
        raise Exception('No data found')

    return rpaths


def download_S2(
    scenes: List[str],
    folder: Union[str, Path] = Path.home(),
    workers: int = CPU_COUNT,
) -> List[str]:
    """Download Sentinel 2 COG (Cloud Optimized GeoTiff) images from Amazon S3.

    The dataset on AWS contains all of the scenes in the original Sentinel-2
    Public Dataset and will grow as that does. L2A data are available from
    April 2017 over wider Europe region and globally since December  2018. Read
    more at the url https://registry.opendata.aws/sentinel-2-l2a-cogs/

    Parameters
    ----------
    packages: list
        List of tuples that contains what to download
    folder: str or Path
        Where to download the data. The folder must exist. Default value is
        the home directory of the user.
    workers: int
        Number of parallel downloads using threading. Default value is 4.

    Returns
    -------
    list
        A list with the paths of the downloaded files.
    """
    rpaths = []
    lpaths = []

    for s in scenes:
        for what in s:
            rpaths.append(what)
            path = what.rsplit('/', 2)
            lpath = f'{folder}/{path[1]}_{path[2]}'
            lpaths.append(lpath)

    s3 = boto3.client('s3')

    def get_file(rpath: Union[str, Path], lpath: Union[str, Path]) -> None:
        bucket, obj = rpath.split('/', 1)
        s3.download_file(bucket, obj, lpath)

    executor = ThreadPoolExecutor(max_workers=workers)
    ex = [executor.submit(get_file, rp, lp) for rp, lp in zip(rpaths, lpaths)]
    cy = cycle(r"-\|/")
    while not all([exx.done() for exx in ex]):
        print("Downloading data " + next(cy), end="\r")
        sleep(0.1)

    return sorted(lpaths)
