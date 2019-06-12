from S4 import PostgresBase

class Postgres(PostgresBase.base):

    @staticmethod
    def inserir(self, sac, item, texto, tratado, stemming, severidade, tempo, data):
        # tempo = str(tempo).replace(".", ",")
        sql = "insert into sac (atendimento, item, original, texto, stemming, severidade, tempo, data) " \
              "values (" + str(sac) + ", " + str(item) + ", '" + texto + "', '" + tratado + "', '" \
              + stemming + "', " + str(severidade) + ", " + tempo + ", '" + str(data) + "') " \
              " ON CONFLICT (atendimento, item) DO NOTHING;"

        self.cur.execute(sql)
        self.con.commit()

    @staticmethod
    def pessoa(self, sac, item, usuario, quant):
        quant = str(quant).replace(".", "")
        sql = "insert into pessoas (atendimento, item, pessoa, quant) " \
              "values (" + str(sac) + ", " + str(item) + ", '" + usuario + "', " + quant + ") " \
              "ON CONFLICT (atendimento, item, pessoa) DO NOTHING;"

        self.cur.execute(sql)
        self.con.commit()

    def __init__(self):
        super().__init__()

