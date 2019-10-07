import PostgresBase


class Postgres(PostgresBase.Base):
    @staticmethod
    def avaliacao(self, atendimento, item, relacionado, relacionadoitem, valor):
        sql = f" update resultados set util = {valor}"
        sql += " where atendimento = " + str(atendimento)
        sql += " and item = " + str(item)
        # sql += " and algoritmo = '" + algoritmo + "'"
        sql += " and relacionado = " + str(relacionado)
        sql += " and relacionadoitem = " + str(relacionadoitem)

        # print(str(atendimento)+'/'+str(item),algoritmo, valor)
        self.cur.execute(sql)
        self.con.commit()

    @staticmethod
    def metricas(self, campo):
        sql = "  select " + str(campo)
        sql += " from resultados;"
        self.cur.execute(sql)

        conta = 0
        registros = self.cur.fetchall()
        for registro in registros:
            conta = registro[0]

        return conta

    def __init__(self):
        super().__init__()
