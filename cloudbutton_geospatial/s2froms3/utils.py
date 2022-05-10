#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module contains some utils used mainly by the library itself.
"""

from typing import Union
import datetime as dt
from typing import Iterator, Tuple

import mgrs  # type: ignore


def _iter_dates(
    start_date: Union[dt.date, dt.datetime], end_date: Union[dt.date, dt.datetime]
) -> Iterator[Tuple[int, int]]:
    """Helper function to create a (year, month) iterator from start_date to
    end_date."""
    # REF: https://stackoverflow.com/a/5734564
    ym_start = 12 * start_date.year + start_date.month - 1
    ym_end = 12 * end_date.year + end_date.month - 1
    for ym in range(ym_start, ym_end + 1):
        y, m = divmod(ym, 12)
        yield y, m + 1


def point_in_tile(lon: Union[int, float], lat: Union[int, float]) -> str:
    """Function printing where is the (lon, lat) location within the tile.

    The idea of this function is to show you if the location is very close
    to a border/corner so you wonder if you would need other COGs in the
    surroundings."""
    m = mgrs.MGRS()
    _, _, x0, y0 = m.MGRSToUTM(m.toMGRS(lat, lon, MGRSPrecision=0))
    _, _, x10, y10 = m.MGRSToUTM(m.toMGRS(lat, lon, MGRSPrecision=1))
    x = (x10 - x0) / 10000
    y = 10 - (y10 - y0) / 10000
    res = "\n"
    for j in range(11):
        for i in range(11):
            if i == x and j == y:
                sign = "O "
            elif (i == 0 or i == 10) or (j == 0 or j == 10):
                sign = "+ "
            else:
                sign = "  "
            res += sign
        res += "\n"
    return res
