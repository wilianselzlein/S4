from S4 import PostgresBase


class Postgres(PostgresBase.base):


    @staticmethod
    def avaliacao(self, atendimento, item, algoritmo, relacionado, relacionadoitem, valor):
        sql = f" update resultados set util = {valor}"
        sql += " where atendimento = " + str(atendimento)
        sql += " and item = " + str(item)
        sql += " and algoritmo = '" + algoritmo + "'"
        sql += " and relacionado = " + str(relacionado)
        sql += " and relacionadoitem = " + str(relacionadoitem)

        print(str(atendimento)+'/'+str(item),algoritmo, valor)
        self.cur.execute(sql)
        self.con.commit()


    def __init__(self):
        super().__init__()
