# import ibm_db
import ibm_db_dbi as db
import config
from utils import Texto
# from importar.cassandra import Cassandra
from importar.postgres import Postgres
import dateutil.parser
import nltk
# from nltk import word_tokenize
from nltk.util import ngrams
from collections import Counter
import pickle
import os
from utils import utils


log = utils.get_logger('Importer')

def executar(salt=None, item=None):
    atendimento(salt, item)
    pessoas(salt, item)


# if __name__ == '__main__':
#    executar()


def atendimento(salt=None, item=None):
    # conn = ibm_db.connect(config.dsn_database, config.dsn_uid, config.dsn_pwd)
    conn = db.connect("DATABASE=" + config.dsn_database + ";HOSTNAME=" + config.dsn_hostname + ";PORT=" + config.dsn_port +
                      ";UID=" + config.dsn_uid + ";PWD=" + config.dsn_pwd + ";",
                      "/home/ivo/Downloads/jdbc_sqlj/db2_db2driver_for_jdbc_sqlj/db2jcc.jar", "")

    #schema = ibm_db.exec_immediate(conn, "SET SCHEMA SAC")
    sql = """
    SELECT ia.NUATENDIMENTO, ia.NUITEM, ia.DEATENDIMENTO, pr.NUORDEM, ra.DTREGISTRO, 
    coalesce((SELECT sum(aa.QTHORASREAL) FROM sac.ESACATIVIDADE AA
        WHERE AA.CDPROJETO = IA.CDPROJETO
        AND AA.NUATENDIMENTO = IA.NUATENDIMENTO
        AND AA.NUITEM = IA.NUITEM),0) as QTHORASREAL 
      FROM sac.ESACREGISTROATEND ra
      JOIN sac.ESACITEMATEND ia
        ON ia.cdProjeto = ia.CDPROJETO
       AND ia.NUATENDIMENTO = ra.NUATENDIMENTO  
      JOIN sac.ESACPRIORIDADE pr
        ON pr.cdPrioridade = ia.cdPrioridade
     WHERE ra.cdProjeto = 3
       AND ia.CDPROJETO = 3
       AND ra.CDSISTEMA IN (31,93)
    """
    if salt is not None and item is not None:
        sql += " AND ia.NUATENDIMENTO = " + str(salt) + " AND ia.NUITEM = " + str(item)
    else:
        sql += " AND VARCHAR_FORMAT (ra.DTREGISTRO,'YYYY-MM-DD') > '" + config.ultima_importacao + "'"
    sql += " AND VARCHAR_FORMAT (ra.DTREGISTRO,'YYYY-MM-DD') > '" + config.ultima_importacao + "'"
    sql += " ORDER BY ra.DTREGISTRO"

    texto = Texto()
    postgres = Postgres()

    rows = conn.cursor()
    rows.execute(sql)
    # stmt = ibm_db.exec_immediate(conn, sql)
    # row = ibm_db.fetch_assoc(stmt)

    texto_salt = ''
    rows = list(rows)
    for row in rows: # enumerate com print /r end
        texto_salt += ' ' + texto.tratar(texto, str(row[2]))

    if salt is None and item is None:
        grams_pickle = open('grams.pickle', 'wb')

        token = nltk.word_tokenize(texto_salt)
        trigrams = ngrams(token, 3)
        trigrams = Counter(trigrams)
        trimost = trigrams.most_common(500)

        dic = []
        for key, value in trimost:
            palavra = ''
            for n in range(len(key)):
                palavra += key[n] + ' '
            palavra = palavra.strip()
            gram = palavra.replace(' ', '_')
            dic.append(palavra)
            texto_salt = texto_salt.replace(palavra, gram)

        token = nltk.word_tokenize(texto_salt)
        bigrams = ngrams(token, 2)
        bigrams = Counter(bigrams)
        bimost = bigrams.most_common(500)

        for key, value in bimost:
            palavra = ''
            for n in range(len(key)):
                palavra += key[n] + ' '
            palavra = palavra.strip()
            dic.append(palavra.strip())

        pickle.dump(dic, grams_pickle, protocol=pickle.HIGHEST_PROTOCOL)

    registro = ''
    i = 0
    total = 0
    for row in rows:
        print("\t" + str(total) + "/" + str(len(rows)), end="\r")
        total += 1

        # NUATENDIMENTO  NUITEM  DEATENDIMENTO   NUORDEM     DTREGISTRO  QTHORASREAL
        # 0              1       2               3           4           5

        linha = str(row[4]) # 'DTREGISTRO'
        linha = dateutil.parser.parse(linha).date()

        if registro != linha:
            registro = linha
            if salt is None:
                log.debug(str(registro) + ' ' + str(i))
            i = 0

        i += 1
        original = str(row[2]).replace("\'", "").replace("\"", "")
        tratado = texto.tratar(texto, str(row[2]))

        if os.path.isfile('grams.pickle'):
            grams_pickle = open('grams.pickle', 'rb')
            grams = pickle.load(grams_pickle)
            for palavras in grams:
                tratado = tratado.replace(palavras, palavras.replace(' ', '_'))

        stemming = texto.tratar(texto, str(row[2]), True)
        postgres.inserir(postgres, row[0], row[1],
                          original, tratado, stemming,
                          row[3], row[5], row[4])

        # row = ibm_db.fetch_assoc(stmt)
    log.info('Registros importados:' + str(total))


def pessoas(salt=None, item=None):
    # conn = ibm_db.connect(config.dsn_database, config.dsn_uid, config.dsn_pwd)
    conn = db.connect("DATABASE=" + config.dsn_database + ";HOSTNAME=" + config.dsn_hostname + ";PORT=" + config.dsn_port +
                      ";UID=" + config.dsn_uid + ";PWD=" + config.dsn_pwd + ";",
                      "/home/ivo/Downloads/jdbc_sqlj/db2_db2driver_for_jdbc_sqlj/db2jcc.jar", "")

    # schema = ibm_db.exec_immediate(conn, "SET SCHEMA SAC")
    sql = """
        SELECT ia.NUATENDIMENTO, ia.NUITEM, aa.CDUSUARIO, count(1) AS QUANT
          FROM sac.ESACREGISTROATEND ra
          JOIN sac.ESACITEMATEND ia
            ON ia.cdProjeto = ia.CDPROJETO
           AND ia.NUATENDIMENTO = ra.NUATENDIMENTO  
          JOIN sac.ESACPRIORIDADE pr
            ON pr.cdPrioridade = ia.cdPrioridade
          JOIN sac.ESACATIVIDADE AA
            ON AA.CDPROJETO = IA.CDPROJETO
           AND AA.NUATENDIMENTO = IA.NUATENDIMENTO
           AND AA.NUITEM = IA.NUITEM
         WHERE ra.cdProjeto = 3
           AND ia.CDPROJETO = 3
           AND ra.CDSISTEMA IN (31,93)
           AND aa.CDUSUARIO NOT IN ('PORTALCLIENTE', 'AUTOMATIZACAO_PORTAL')
        """
    if salt is not None and item is not None:
        sql += " AND ia.NUATENDIMENTO = " + str(salt) + " AND ia.NUITEM = " + str(item)
    sql += " AND VARCHAR_FORMAT (ra.DTREGISTRO,'YYYY-MM-DD') > '" + config.ultima_importacao + "' " \
        "GROUP BY ia.NUATENDIMENTO, ia.NUITEM, aa.CDUSUARIO"

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


