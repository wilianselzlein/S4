import config

# from cassandra.cluster import Cluster
# from cassandra.query import SimpleStatement
# from cassandra import ConsistencyLevel


class Cassandra(object):
    @staticmethod
    def inserir(self, sac, item, texto, tratado, stemming, severidade, tempo):
        tempo = str(tempo).replace(".", "")
        sql = (
            "insert into sac (atendimento, item, original, texto, stemming, severidade, tempo) "
            "values ("
            + str(sac)
            + ", "
            + str(item)
            + ", '"
            + texto
            + "', '"
            + tratado
            + "', '"
            + stemming
            + "', "
            + str(severidade)
            + ", "
            + tempo
            + ") IF NOT EXISTS;"
        )

        self.session.execute(sql)
        # self.session.execute(self.prepared.bind((sac, item, texto)))
        # self.session.execute(self.query, dict("atendimento"=sac, "item"=item, "texto"=str(texto)))

    @staticmethod
    def pessoa(self, sac, item, usuario, quant):
        quant = str(quant).replace(".", "")
        sql = (
            "insert into pessoas (atendimento, item, pessoa, quant) "
            "values ("
            + str(sac)
            + ", "
            + str(item)
            + ", '"
            + usuario
            + "', "
            + quant
            + ") IF NOT EXISTS;"
        )

        self.session.execute(sql)

    def __init__(self):
        cluster = Cluster([config.cassandra_host])
        self.session = cluster.connect()
        self.session.set_keyspace(config.cassandra_KEYSPACE)

        # self.session.execute("TRUNCATE sac")


#        self.query = SimpleStatement("""
#            INSERT INTO sac (atendimento, item, texto)
#            VALUES (%(key)s, %(a)s, %(b)s)
#            """, consistency_level=ConsistencyLevel.ONE)

#        self.prepared = self.session.prepare("""
#            INSERT INTO sac (atendimento, item, texto)
#            VALUES (?, ?, ?)
#            """)
#            IF NOT EXISTS;
