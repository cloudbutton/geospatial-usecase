#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""This module contains Enums for the Sentinel-2 bands and some derived 
products.
"""

from enum import Enum, unique
from typing import Dict, Any


@unique
class Properties(Enum):
    TCI = "TCI"
    B01 = "B01"
    B02 = "B02"
    B03 = "B03"
    B04 = "B04"
    B05 = "B05"
    B06 = "B06"
    B07 = "B07"
    B08 = "B08"
    B8A = "B8A"
    B09 = "B09"
    B11 = "B11"
    B12 = "B12"
    AOT = "AOT"
    WVP = "WVP"
    SCL = "SCL"

    def describe(self) -> Dict[str, Any]:
        properties = {
            "TCI": {
                "resolution": 10,
                "title": "True color image",
                "center wavelength": None,
            },
            "B01": {
                "resolution": 60,
                "title": "Band 1 (coastal)",
                "center wavelength": 0.4439,
            },
            "B02": {
                "resolution": 10,
                "title": "Band 2 (blue)",
                "center wavelength": 0.4966,
            },
            "B03": {
                "resolution": 10,
                "title": "Band 3 (green)",
                "center wavelength": 0.56,
            },
            "B04": {
                "resolution": 10,
                "title": "Band 4 (red)",
                "center wavelength": 0.6645,
            },
            "B05": {
                "resolution": 20,
                "title": "Band 5",
                "center wavelength": 0.7039,
            },
            "B06": {
                "resolution": 20,
                "title": "Band 6",
                "center wavelength": 0.7402,
            },
            "B07": {
                "resolution": 20,
                "title": "Band 7",
                "center wavelength": 0.7825,
            },
            "B08": {
                "resolution": 10,
                "title": "Band 8 (nir)",
                "center wavelength": 0.8351,
            },
            "B8A": {
                "resolution": 20,
                "title": "Band 8A",
                "center wavelength": 0.8648,
            },
            "B09": {
                "resolution": 60,
                "title": "Band 9",
                "center wavelength": 0.945,
            },
            "B11": {
                "resolution": 20,
                "title": "Band 11 (swir16)",
                "center wavelength": 1.6137,
            },
            "B12": {
                "resolution": 20,
                "title": "Band 12 (swir22)",
                "center wavelength": 2.22024,
            },
            "AOT": {
                "resolution": 60,
                "title": "Aerosol Optical Thickness (AOT)",
                "center wavelength": None,
            },
            "WVP": {
                "resolution": 10,
                "title": "Water Vapour (WVP)",
                "center wavelength": None,
            },
            "SCL": {
                "resolution": 20,
                "title": "Scene Classification Map (SCL)",
                "center wavelength": None,
            },
        }
        return properties[self.name]
