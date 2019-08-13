# import ibm_db
import ibm_db_dbi as db
import config
from utils import Texto
from importar.postgres import Postgres
import dateutil.parser
import nltk
from nltk.util import ngrams
from collections import Counter
import pickle
import os
from utils import utils
import json
from importar import sql_sac
from elasticsearch import Elasticsearch
import pika

MOST_COMMON = 500

log = utils.get_logger('Importer')
file_grams_pickle = 'grams.pickle'


def executar(salt=None, item=None):
    atendimento(salt, item)
    pessoas(salt, item)


# if __name__ == '__main__':
#    executar()


def atendimento(salt=None, item=None):
    conn = connect_db2_linux()

    # schema = ibm_db.exec_immediate(conn, "SET SCHEMA SAC")
    sql = sql_sac.atendimentos
    sql = sql_fiters(item, salt, sql)
    sql += sql_sac.atendimentos_order

    texto = Texto()
    postgres = Postgres()
    es = Elasticsearch([config.elasticsearch])

    rabbit_conn = pika.BlockingConnection(pika.ConnectionParameters(config.rabbitmq))
    rabbit_public = rabbit_conn.channel()
    rabbit_public.queue_declare(queue=config.rabbitmq_import)
    rabbit_public.queue_declare(queue=config.rabbitmq_validate)

    nomes = {}
    users = {}

    rows = conn.cursor()
    rows.execute(sql)
    # stmt = ibm_db.exec_immediate(conn, sql)
    # row = ibm_db.fetch_assoc(stmt)

    texto_salt = ''
    rows = list(rows)

    for index, row in enumerate(rows):
        if len(rows) > 10:
            print(str(index) + "/" + str(len(rows)), end="\r")
        texto_salt += ' ' + texto.tratar(texto, str(row[2]), remove=True)

    texto_salt += texto.RemoverNomes(texto_salt, nomes)
    texto_salt += texto.RemoverUsuarios(texto_salt, users)

    log.info('Total palavras: ' + str(len(texto_salt.split(' '))))

    save_words(texto_salt, "palavras_todas.txt")

    if salt is None and item is None:
        grams_pickle = open(file_grams_pickle, 'wb')

        dic = []

        texto_salt = counter_grams(3, dic, texto_salt)
        texto_salt = counter_grams(2, dic, texto_salt)

        save_words(texto_salt, "palavras_grams.txt")
        pickle.dump(dic, grams_pickle, protocol=pickle.HIGHEST_PROTOCOL)

    registro = ''
    i = 0
    total = 0

    for row in rows:
        if len(rows) > 10:
            print("\t" + str(total) + "/" + str(len(rows)), end="\r")
        total += 1

        # NUATENDIMENTO  NUITEM  DEATENDIMENTO   NUORDEM     DTREGISTRO  QTHORASREAL
        # 0              1       2               3           4           5

        linha = str(row[4])
        linha = dateutil.parser.parse(linha).date()

        if registro != linha:
            registro = linha
            if salt is None:
                log.debug(str(registro) + ' ' + str(i))
            i = 0

        i += 1
        original = str(row[2]).replace("\'", "").replace("\"", "")
        tratado = texto.tratar(texto, str(row[2]), remove=True, users=users, nomes=nomes)
        tratado = replace_grams_pickle(tratado)

        stemming = texto.tratar(texto, str(row[2]), stemming=True)

        doc = {
            'atendimento': row[0],
            'item': row[1],
            'original': original,
            'texto': tratado,
            'data': row[4],
            'timestamp': row[4] #datetime.now(),
        }
        es_id = str(row[0]) + '/' + str(row[1])
        es.index(index=config.elasticsearch_db, id=es_id, body=doc)

        rabbit_public.basic_publish(exchange='', routing_key=config.rabbitmq_import, body=es_id)
        rabbit_public.basic_publish(exchange='', routing_key=config.rabbitmq_validate, body=es_id)

        postgres.inserir(postgres, row[0], row[1],
                          original, tratado, stemming,
                          row[3], row[5], row[4], texto.RemoveQuotes(row[6]))

    print(json.dumps(dict(sorted(nomes.items(), key=lambda x: x[1], reverse=True)), indent=4))
    print(json.dumps(dict(sorted(users.items(), key=lambda x: x[1], reverse=True)), indent=4))

    # row = ibm_db.fetch_assoc(stmt)
    es.indices.refresh(index=config.elasticsearch_db)
    rabbit_conn.close()

    log.info('Registros importados:' + str(total))


def connect_db2_linux():
    # conn = ibm_db.connect(config.dsn_database, config.dsn_uid, config.dsn_pwd)
    conn = db.connect(
        "DATABASE=" + config.dsn_database + ";HOSTNAME=" + config.dsn_hostname + ";PORT=" + config.dsn_port +
        ";UID=" + config.dsn_uid + ";PWD=" + config.dsn_pwd + ";", config.db2jcc, "")

    return conn


def sql_fiters(item, salt, sql):
    if salt is not None and item is not None:
        sql += sql_sac.atendimentos_filtro.format(str(salt), str(item))
    else:
        sql += sql_sac.atendimentos_data.format(config.ultima_importacao)
    return sql


def counter_grams(ngram, dic, texto_salt):
    token = nltk.word_tokenize(texto_salt)
    grams = ngrams(token, ngram)
    grams = Counter(grams)
    most = grams.most_common(MOST_COMMON)
    for key, value in most:
        palavra = ''
        for n in range(len(key)):
            palavra += key[n] + ' '
        palavra = palavra.strip()
        gram = palavra.replace(' ', '_')
        dic.append(palavra)
        texto_salt = texto_salt.replace(palavra, gram)
    return texto_salt


def replace_grams_pickle(text):
    if os.path.isfile(file_grams_pickle):
        grams_pickle = open(file_grams_pickle, 'rb')
        grams = pickle.load(grams_pickle)
        for gram in grams:
            text = text.replace(gram, gram.replace(' ', '_'))
    return text


def save_words(words, file_name):
    text_file = open('txt/' + file_name, "w")
    text_file.write(words)
    text_file.close()


def pessoas(salt=None, item=None):
    conn = connect_db2_linux()
    # schema = ibm_db.exec_immediate(conn, "SET SCHEMA SAC")
    sql = sql_sac.pessoas
    sql = sql_fiters(item, salt, sql)
    sql += sql_sac.pessoas_group

    # texto = Texto()
    postgres = Postgres()

    # stmt = ibm_db.exec_immediate(conn, sql)
    # result = ibm_db.fetch_assoc(stmt)
    rows = conn.cursor()
    rows.execute(sql)

    # row = ibm_db.fetch_assoc(stmt)
    for row in rows:
        postgres.pessoa(postgres, row[0], row[1], row[2], row[3])
        # postgres.pessoa(postgres, row['NUATENDIMENTO'], row['NUITEM'], row['CDUSUARIO'], row['QUANT'])
        # row = ibm_db.fetch_assoc(stmt)


