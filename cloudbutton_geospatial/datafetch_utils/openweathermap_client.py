"""
Este módulo se utiliza como ejemplo de uso de la clase OpenWeatherMapClient
que es la que realmente se encarga de realizar la descarga de datos
meteorológicos del API de Open Weather Map.

AUTHOR: Juanjo

DATE: 07/02/2019

"""

from owm.openweathermap_client import OpenWeatherMapClient

API_KEY = '77d76b5088577c44866d05c63a0a80d1'


def fetch_weather(city_id):
    owm_murcia = OpenWeatherMapClient(API_KEY, city_id)
    current_weather = owm_murcia.fetch_current_weather()
    weather = dict()
    weather['temperature'] = current_weather.get_temperature()
    weather['rain'] = current_weather.get_rain()
    weather['wind_speed'] = current_weather.get_wind_speed()
    return weather


if __name__ == '__main__':
    weather = fetch_weather('6355234')
    print('Temperatura actual {}'.format(weather['temperature']))
    print('Lluvia actual {}'.format(weather['rain']))
    print('Velocidad del viento actual {}'.format(weather['wind_speed']))
