"""
Este módulo contiene métodos de utilidad para la consulta
de información meteorológica del Sistema de Información
Agrario de Murcia (SIAM)

AUTOR: Juanjo

FECHA DE CREACIÓN: 11/02/2019

"""

import os
import urllib.parse

import requests
from bs4 import BeautifulSoup

RESULTS_DIR = 'results'
SIAM_RESULTS_DIR = 'siam'


def download_weather_info(siam_data_dir):
    """
    Descarga un fichero CSV con la información meteorológica
    correspondiente con el informe: "INFORME AGROMETEOROLÓGICO
    DE UN DÍA". Los datos del informe se corresponden con los
    del día anterior al momento de la ejecución de este script.
    """

    print('Reading weather from SIAM')
    url = 'http://siam.imida.es'

    response = requests.get(url)
    if response.status_code != 200:
        print('>>>>>>>>>>> Error: ' + response.text)
        return
    soup = BeautifulSoup(response.text, 'lxml')
    report_link = soup.find('a', text='INFORME AGROMETEOROLÓGICO DE UN DÍA')
    report_page_link = urllib.parse.urljoin(url, '/apex/' + report_link['href'])

    print(f'Fetching {report_page_link}')
    response = requests.get(report_page_link)
    if response.status_code != 200:
        print('>>>>>>>>>>> Error: ' + response.text)
        return
    soup = BeautifulSoup(response.text, 'lxml')
    date_str = soup.find('input', {'id': 'P47_FECHA'})['value']
    date_str = date_str.replace('/', '_')
    csv_report_link = report_page_link + ':CSV::::'
    print(f'Downloading file {csv_report_link} from {date_str}')
    response = requests.get(csv_report_link)
    if response.status_code != 200:
        print('>>>>>>>>>>> Error: ' + response.text)
        return
    else:
        print('Saving file')
        file_path = os.path.join(siam_data_dir, 'siam_' + date_str + '.csv')
        with open(file_path, 'wb') as siam_csv_file:
            siam_csv_file.write(response.content)
    print('>>> Finish')


def temperature_by_station(filename):
    def clean_row(row):
        return row.replace('"', '')

    temperatures = {}
    with open(filename, 'r', encoding='windows-1252') as csv_file:
        next(csv_file)  # Saltamos la línea del encabezado del CSV
        for row in csv_file:
            values = clean_row(row).split(';')
            temperatures[values[0]] = float(values[3].replace(',', '.'))
    return temperatures
