import ibm_db
from S4 import config
from S4.utils import Texto
# from S4.importar.cassandra import Cassandra
from S4.importar.postgres import Postgres
import dateutil.parser

def executar(salt=None, item=None):
    atendimento(salt, item)
    pessoas(salt, item)


# if __name__ == '__main__':
#    executar()


def atendimento(salt=None, item=None):
    conn = ibm_db.connect(config.dsn_database, config.dsn_uid, config.dsn_pwd)
    schema = ibm_db.exec_immediate(conn, "SET SCHEMA SAC")
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
    sql += " ORDER BY ra.DTREGISTRO"

    texto = Texto()
    postgres = Postgres()

    stmt = ibm_db.exec_immediate(conn, sql)
    # result = ibm_db.fetch_assoc(stmt)

    row = ibm_db.fetch_assoc(stmt)
    registro = ''
    i = 0
    total = 0
    while row:
        total += 1
        linha = str(row['DTREGISTRO'])
        linha = dateutil.parser.parse(linha).date()

        if registro != linha:
            registro = linha
            if salt is None:
                print(registro, ' ', i) #errado
            i = 0

        i += 1
        original = str(row['DEATENDIMENTO']).replace("\'", "").replace("\"", "")
        tratado = texto.tratar(texto, str(row['DEATENDIMENTO']))
        stemming = texto.tratar(texto, str(row['DEATENDIMENTO']), True)
        postgres.inserir(postgres, row['NUATENDIMENTO'], row['NUITEM'],
                          original, tratado, stemming,
                          row['NUORDEM'], row['QTHORASREAL'], row['DTREGISTRO'])
        row = ibm_db.fetch_assoc(stmt)
    print('Registros importados:', total)


def pessoas(salt=None, item=None):
    conn = ibm_db.connect(config.dsn_database, config.dsn_uid, config.dsn_pwd)
    schema = ibm_db.exec_immediate(conn, "SET SCHEMA SAC")
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

    texto = Texto()
    postgres = Postgres()

    stmt = ibm_db.exec_immediate(conn, sql)
    # result = ibm_db.fetch_assoc(stmt)

    row = ibm_db.fetch_assoc(stmt)
    while row:
        postgres.pessoa(postgres, row['NUATENDIMENTO'], row['NUITEM'], row['CDUSUARIO'], row['QUANT'])
        row = ibm_db.fetch_assoc(stmt)


