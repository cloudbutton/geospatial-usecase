"""

AUTHOR: Juanjo

DATE: 02/04/2019

"""

import os
import subprocess


class AtmosphericCorrectionProcess:

    @staticmethod
    def run(products_dir):
        # Usar el software de corrección atmosférica Sen2Cor
        # Este crea los modelos con corrección L2A
        # TODO: Tendremos que probar con la versión para Linux
        if "SEN2COR_COM" not in os.environ:
            print(f'Variable SEN2COR_COM should be defined. It must contain path of L2A_Process command')
            return

        sentinel_products_dirs = [os.path.join(products_dir, d) for d in os.listdir(products_dir) if
                                  (os.path.isdir(os.path.join(products_dir, d))) and ('MSIL1C' in d)]

        for sentinel_product in sentinel_products_dirs:
            print(f'Doing the atmospheric correction for {sentinel_product}')
            val = subprocess.check_call(
                f'{os.environ["SEN2COR_COM"]} --resolution 10 {sentinel_product}', shell=True)
            print(f'Atmospheric correction finished {val}')
