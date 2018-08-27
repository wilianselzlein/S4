import argparse
import time

from S4 import config
from S4 import importar, avaliar, portal

parser = argparse.ArgumentParser()
parser.add_argument('--importar', help='Importar dados SAC DB2', action='store_true')
parser.add_argument('--salt', help='Salt para avaliar', default='', type=str)
parser.add_argument('--portal', help='Ativa portal', action='store_true')

if __name__ == '__main__':
    args_ = parser.parse_args()

    if args_.importar:
        importar.executar()

    if args_.salt is not '':
        avaliar.executar(args_.salt)

    if args_.portal:
        portal.executar()

    time.sleep(1)
