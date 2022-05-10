"""
Este módulo se utiliza como ejemplo de uso de la clase AEMETClient
que es la que realmente se encarga de realizar la descarga de datos
meteorológicos de la AEMET.

Dado que se descargan datos de diferente rango de horas, en
el ejemplo se muestran los datos correspondientes a la
última hora.

AUTHOR: Juanjo

DATE: 07/02/2019

"""
import json

from aemet.aemet_client import AEMETClient

API_KEY = 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJqbG96YW5vQGFuc3dhcmUtdGVjaC5jb20iLCJqdGkiOiI5NzU5OTk1NC00ZGJjLTRkYzAtYjY2OS0wZTUzNGRlMzVlYjkiLCJpc3MiOiJBRU1FVCIsImlhdCI6MTU0OTU0NTUyOSwidXNlcklkIjoiOTc1OTk5NTQtNGRiYy00ZGMwLWI2NjktMGU1MzRkZTM1ZWI5Iiwicm9sZSI6IiJ9.jypGVc74zhzxV8V9ghLTT2XI75W2JWBrsha1B0gaOS0'
MURCIA_STATION = '7178I'


def todays_weather():
    aemet_client = AEMETClient(API_KEY)
    conv_observation = aemet_client.fetch_conventional_observation(MURCIA_STATION)
    last_observation = conv_observation[-1]
    # fecha de los datos
    print('Fecha: {}'.format(last_observation['fint']))
    # temperatura máxima día
    print('Temperatura máxima: {}'.format(last_observation['tamax']))
    # temperatura mínima día
    print('Temperatura mínima: {}'.format(last_observation['tamin']))
    # temperatura media
    print('Temperatura media: {}'.format(last_observation['ta']))
    # precipitación
    print('Precipitación: {}'.format(last_observation['prec']))
    # humedad
    print('Humedad: {}'.format(last_observation['hr']))
    # velocidad del viento
    print('Velocidad del viento: {}'.format(last_observation['vv']))
    return last_observation


if __name__ == '__main__':
    response = todays_weather()
    print(json.dumps(response))
