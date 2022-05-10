"""
Este script calcula la temperatura determinada

AUTHOR: Juanjo

DATE: 06/02/2019

"""


class DetTemperatureProcess:

    @staticmethod
    def run(stations_info, temperatures, rate=-0.0056, det_alt=2000):
        det_temperature = {}
        for station in stations_info:
            if station in temperatures:
                det_temperature[station] = temperatures[station] + rate*(det_alt - stations_info[station]['alt'])
        return det_temperature
