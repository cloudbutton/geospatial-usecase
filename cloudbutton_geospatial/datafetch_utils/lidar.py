"""
Este módulo contiene métodos de utilidad para descargar imágenes
LIDAR de la web del CNIG.

AUTHOR: Juanjo

DATE: 11/02/2019

"""

import os

import requests
from bs4 import BeautifulSoup

LIDAR_IDS_DOC = 'lidar_ids_doc.txt'


def fetch_doc_list(state_cod, lidar_data_dir, whole_spain='N', lidar_ids_file=LIDAR_IDS_DOC):
    """
    Recupera el nombre y el identificador del enlace de descarga de todos los
    ficheros LIDAR de una provincia entera.

    :param state_cod: Código de provincia
    :param lidar_data_dir: Dir where to store the lidar files
    :param whole_spain: Indica si es para toda España
    :param lidar_ids_file: Nombre del fichero en el que almacenar los identificadores de los ficheros LIDAR

    """

    url = 'http://centrodedescargas.cnig.es/CentroDescargas/resultadosArchivos'
    next_page = 1
    doc_list = []
    while next_page:
        print('Leyendo documentos de la página {}'.format(next_page))
        data = {
            'numPagina': next_page,
            'codSerie': 'LIDA2',
            'series': 'LIDA2',
            'codProvAv': state_cod,
            'todaEsp': whole_spain,
            'tipoBusqueda': 'AV',
        }
        response = requests.post(url, data=data)
        if response.status_code != 200:
            print('>>>>> Error. No se pudo recuperar el listado de documentos')
            print(response.text)
            return
        data = response.text
        soup = BeautifulSoup(data, 'lxml')
        next_link = soup.find('a', {'title': 'Siguiente'})
        next_page = next_page + 1 if next_link else None
        file_list_div = soup.find('div', {'id': 'blqListaArchivos'})
        file_list_tb = file_list_div.find('table').find('tbody')
        trs = file_list_tb.find_all('tr')
        for tr in trs:
            ihidden = tr.find_all('input', {'type': 'hidden'})
            file_link_id = None
            for input in ihidden:
                if input['id'].startswith('secGeo_'):
                    file_link_id = input['value']
            file_name = tr.find('td', {'data-th': 'Nombre'}).text
            doc_list.append((file_name, file_link_id))
    print('Número de docs: {}'.format(len(doc_list)))

    # Save a file with all file links
    lidar_doc_file_path = os.path.join(lidar_data_dir, lidar_ids_file)
    with open(lidar_doc_file_path, 'w') as lidar_docs_file:
        for doc in doc_list:
            lidar_docs_file.write('{},{}\n'.format(doc[0], doc[1]))


def download_file(file_name, sec_desc_dir_la, lidar_data_dir):
    """
    Realiza la descarga de un fichero LIDAR a partir del id del enlace de descarga.

    NOTA: Esto se podría ejecutar en paralelo

    :param file_name: Nombre que se le dará al fichero a descargar
    :param sec_desc_dir_la: Id del enlace de descarga
    """

    print('{} - Leyendo fichero {}'.format(sec_desc_dir_la, file_name))
    url = 'http://centrodedescargas.cnig.es/CentroDescargas/descargaDir'
    data = {
        'codSerieMD': 'LIDA2',
        'codSerieSel': 'LIDA2',
        'secDescDirLA': sec_desc_dir_la
    }
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print(response.text)
    else:
        file_path = os.path.join(lidar_data_dir, file_name)
        with open(file_path, 'wb') as lidar_file:
            lidar_file.write(response.content)


def download_files(state, lidar_data_dir):
    """
    Este método comienza la descarga de cada uno de los ficheros LIDAR
    a partir del fichero que contiene los identificadores de los enlaces
    de descarga.

    """

    fetch_doc_list(state, lidar_data_dir)

    lidar_doc_file_path = os.path.join(lidar_data_dir, LIDAR_IDS_DOC)
    with open(lidar_doc_file_path, 'r') as f:
        for f_line in f:
            file_name, sec_desc_dir_la = f_line.rstrip().split(',')
            download_file(file_name, sec_desc_dir_la, lidar_data_dir)
