import ibm_db
from S4 import config
from S4.utils import Texto
from S4.importar.cassandra import Cassandra


def executar():
    atendimento()
    pessoas()


# if __name__ == '__main__':
#    executar()


def atendimento():
    conn = ibm_db.connect(config.dsn_database, config.dsn_uid, config.dsn_pwd)
    schema = ibm_db.exec_immediate(conn, "SET SCHEMA SAC")
    sql = """
    SELECT ia.NUATENDIMENTO, ia.NUITEM, ia.DEATENDIMENTO, pr.NUORDEM, 
    coalesce((SELECT sum(aa.QTHORASREAL) FROM sac.ESACATIVIDADE AA
        WHERE AA.CDPROJETO = IA.CDPROJETO
        AND AA.NUATENDIMENTO = IA.NUATENDIMENTO
        AND AA.NUITEM = IA.NUITEM),0) as QTHORASREAL 
      FROM sac.ESACREGISTROATEND ra
      JOIN sac.ESACITEMATEND ia
        ON ia.cdProjeto = ia.CDPROJETO
       AND ia.NUATENDIMENTO = ra.NUATENDIMENTO  
      JOIN sac.ESACLOCALSISTEMA ls 
        ON ia.CDPROJETO = ls.CDPROJETO
       AND ia.CDSISTEMA = ls.CDSISTEMA
       AND ia.CDLOCALSISTEMA = ls.CDLOCALSISTEMA
      JOIN sac.ESACPRIORIDADE pr
        ON pr.cdPrioridade = ia.cdPrioridade
     WHERE ra.cdProjeto = 3
       AND ia.CDPROJETO = 3
       AND ls.CDPROJETO = 3
       AND ra.CDORIGEMATEND = 10
       AND ra.CDSISTEMA IN (31,93)
    """
    sql += "AND VARCHAR_FORMAT (ra.DTREGISTRO,'YYYY-MM-DD') > '" + config.ultima_importacao + "'"
    # FETCH FIRST 5000 ROWS ONLY;

    texto = Texto()
    cassandra = Cassandra()

    stmt = ibm_db.exec_immediate(conn, sql)
    # result = ibm_db.fetch_assoc(stmt)

    row = ibm_db.fetch_assoc(stmt)
    while row:
        original = str(row['DEATENDIMENTO']).replace("\'", "").replace("\"", "")
        tratado = texto.tratar(texto, str(row['DEATENDIMENTO']))
        stemming = texto.tratar(texto, str(row['DEATENDIMENTO']), True)
        cassandra.inserir(cassandra, row['NUATENDIMENTO'], row['NUITEM'],
                          original, tratado, stemming,
                          row['NUORDEM'], row['QTHORASREAL'])
        row = ibm_db.fetch_assoc(stmt)


def pessoas():
    conn = ibm_db.connect(config.dsn_database, config.dsn_uid, config.dsn_pwd)
    schema = ibm_db.exec_immediate(conn, "SET SCHEMA SAC")
    sql = """
        SELECT ia.NUATENDIMENTO, ia.NUITEM, aa.CDUSUARIO, count(1) AS QUANT
          FROM sac.ESACREGISTROATEND ra
          JOIN sac.ESACITEMATEND ia
            ON ia.cdProjeto = ia.CDPROJETO
           AND ia.NUATENDIMENTO = ra.NUATENDIMENTO  
          JOIN sac.ESACLOCALSISTEMA ls 
            ON ia.CDPROJETO = ls.CDPROJETO
           AND ia.CDSISTEMA = ls.CDSISTEMA
           AND ia.CDLOCALSISTEMA = ls.CDLOCALSISTEMA
          JOIN sac.ESACPRIORIDADE pr
            ON pr.cdPrioridade = ia.cdPrioridade
          JOIN sac.ESACATIVIDADE AA
            ON AA.CDPROJETO = IA.CDPROJETO
           AND AA.NUATENDIMENTO = IA.NUATENDIMENTO
           AND AA.NUITEM = IA.NUITEM
         WHERE ra.cdProjeto = 3
           AND ia.CDPROJETO = 3
           AND ls.CDPROJETO = 3
           AND ra.CDORIGEMATEND = 10
           AND ra.CDSISTEMA IN (31,93)
           AND aa.CDUSUARIO NOT IN ('PORTALCLIENTE', 'AUTOMATIZACAO_PORTAL')
        """
    sql += "AND VARCHAR_FORMAT (ra.DTREGISTRO,'YYYY-MM-DD') > '" + config.ultima_importacao + "' " \
        "GROUP BY ia.NUATENDIMENTO, ia.NUITEM, aa.CDUSUARIO"

    # FETCH FIRST 5000 ROWS ONLY;

    texto = Texto()
    cassandra = Cassandra()

    stmt = ibm_db.exec_immediate(conn, sql)
    # result = ibm_db.fetch_assoc(stmt)

    row = ibm_db.fetch_assoc(stmt)
    while row:
        cassandra.pessoa(cassandra, row['NUATENDIMENTO'], row['NUITEM'], row['CDUSUARIO'], row['QUANT'])
        row = ibm_db.fetch_assoc(stmt)


