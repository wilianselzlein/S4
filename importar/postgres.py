import PostgresBase


class Postgres(PostgresBase.Base):
    @staticmethod
    def inserir(
        self, sac, item, texto, tratado, stemming, severidade, tempo, data, encerramento
    ):
        # tempo = str(tempo).replace(".", ",")
        sql = (
            "insert into sac (atendimento, item, original, texto, stemming, severidade, tempo, data, encerramento) "
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
            + str(tempo)
            + ", '"
            + str(data)
            + "', '"
            + str(encerramento)
            + "') "
            " ON CONFLICT (atendimento, item) DO NOTHING;"
        )

        try:
            self.cur.execute(sql)
            self.con.commit()
        except:
            print(sac)
            print(sql)

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
            + ") "
            "ON CONFLICT (atendimento, item, pessoa) DO NOTHING;"
        )

        self.cur.execute(sql)
        self.con.commit()

    def __init__(self):
        super().__init__()
