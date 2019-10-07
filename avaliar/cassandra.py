import config
from cassandra.cluster import Cluster


class Cassandra(object):
    @staticmethod
    def atendimento(self, sac, item):
        sql = "  select atendimento, item, texto "
        sql += " from sac "
        sql += " where atendimento = " + str(sac)
        sql += " and item = " + str(item) + ";"

        return self.session.execute(sql)

    @staticmethod
    def atendimentos(self):
        sql = "  select atendimento, item, texto "
        sql += " from sac ;"

        return self.session.execute(sql)

    @staticmethod
    def relacionar(
        self, atendimento, item, algoritmo, relacionado, relacionadoitem, score
    ):
        sql = " insert into resultados "
        sql += " (atendimento, item, algoritmo, relacionado, relacionadoitem, score) "
        sql += (
            " values ("
            + str(atendimento)
            + ", "
            + str(item)
            + ", '"
            + algoritmo
            + "', "
        )
        sql += (
            str(relacionado) + ", " + str(relacionadoitem) + ", " + str(score) + " ) "
        )
        sql += " IF NOT EXISTS;"

        self.session.execute(sql)

    @staticmethod
    def resultados(self, sac, item):
        """
        sql = "  select r.algoritmo, r.relacionado, r.relacionadoitem, r.score, s.severidade, s.tempo "
        sql += " from resultados r"
        sql += " join sac s"
        sql += " on r.relacionado = s.atendimento and r.relacionadoitem = s.item"
        """

        sql = "  select algoritmo, relacionado, relacionadoitem, score "
        sql += " from resultados"
        sql += " where atendimento = " + str(sac)
        sql += " and item = " + str(item) + ";"

        return self.session.execute(sql)

    @staticmethod
    def pessoas(self, sac, item):
        """
        sql = "  select pessoa, sum(quant) as quant "
        sql += " from pessoas "
        sql += " where atendimento = " + str(sac)
        sql += " and item = " + str(item)
        sql += " group by pessoa"
        sql += " order by quant desc;"
        """
        sql = "  select pessoa, quant "
        sql += " from pessoas "
        sql += " where atendimento = " + str(sac)
        sql += " and item = " + str(item)

        return self.session.execute(sql)

    def __init__(self):
        cluster = Cluster([config.cassandra_host])
        self.session = cluster.connect()
        self.session.set_keyspace(config.cassandra_KEYSPACE)
