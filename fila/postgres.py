import PostgresBase
import config


class Postgres(PostgresBase.Base):

    @staticmethod
    def atendimentos(self):
        sql = "  select distinct s.atendimento, s.item "
        sql += " from sac s"
        sql += " where s.atendimento||'-'||s.item not in ("
        sql += "  select r.relacionado||'-'||r.relacionadoitem "
        sql += "  from resultados r)"
        sql += " order by s.atendimento desc LIMIT " + str(config.rabbitmq_limit) + ";"

        #log.info("Adicionando a fila. Limite: " + str(config.rabbitmq_limit))

        self.cur.execute(sql)
        return self.cur.fetchall()


    @staticmethod
    def atividades(self):
        sql = "  select distinct s.atendimento, s.item, s.data "
        sql += " from sac s"
        sql += " order by s.data desc LIMIT " + str(config.rabbitmq_limit) + ";"

        self.cur.execute(sql)
        return self.cur.fetchall()


    def __init__(self):
        super().__init__()
