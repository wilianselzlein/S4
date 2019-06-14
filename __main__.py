import argparse
import time
import config
import importar, avaliar, portal
# import warnings

# warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
# warnings.filterwarnings("ignore", category=DeprecationWarning)

parser = argparse.ArgumentParser()
parser.add_argument('--importar', help='Importar dados SAC DB2 - ' + config.ultima_importacao, action='store_true')
parser.add_argument('--salt', help='Salt para avaliar no formato 000000/0', default='', type=str)
parser.add_argument('--portal', help='Ativa portal Ex: http://127.0.0.1:5000/salt/000000/0', action='store_true')

if __name__ == '__main__':
    args_ = parser.parse_args()

    if args_.importar:
        importar.executar()

    if args_.salt is not '':
        avaliar.executar(args_.salt)

    if args_.portal:
        portal.executar()

    time.sleep(1)
