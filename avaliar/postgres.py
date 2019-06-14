import PostgresBase
import config


class Postgres(PostgresBase.Base):

    @staticmethod
    def atendimento(self, sac, item):
        sql = "  select atendimento, item, texto "
        sql += " from sac "
        sql += " where atendimento = " + str(sac)
        sql += " and item = " + str(item) + ";"
        self.cur.execute(sql)
        return self.cur.fetchall()

    @staticmethod
    def atendimentos(self, sac, item):
        sql = "  select s.atendimento, s.item, s.texto "
        sql += " from sac s"
        sql += " where s.atendimento||'-'||s.item <> '" + str(sac) + "-" + str(item) + "'"
        sql += " and s.atendimento||'-'||s.item not in ("
        sql += "  select r.relacionado||'-'||r.relacionadoitem "
        sql += "  from resultados r"
        sql += "  where r.atendimento = " + str(sac)
        sql += "  and r.item = " + str(item)
        sql += f" and r.util = {False})"
        #print(sql)
        data = config.data_avaliacao
        if data != '':
            sql += " and s.data > '" + data + "'"
            print("Avaliados a partir de", data)

        self.cur.execute(sql)
        return self.cur.fetchall()

    @staticmethod
    def relacionar(self, atendimento, item, algoritmo, relacionado, relacionadoitem, score):
        sql = " insert into resultados "
        sql += " (atendimento, item, algoritmo, relacionado, relacionadoitem, score) "
        sql += " values (" + str(atendimento) + ", " + str(item) + ", '" + algoritmo + "', "
        sql += str(relacionado) + ", " + str(relacionadoitem) + ", " + str(score) + " ) "
        sql += " ON CONFLICT (atendimento, item, algoritmo, relacionado, relacionadoitem) DO NOTHING; "
        print(str(relacionado)+'/'+str(relacionadoitem),score)
        self.cur.execute(sql)
        self.con.commit()

    @staticmethod
    def resultados(self, sac, item):
        sql = "  select r.algoritmo, r.relacionado, r.relacionadoitem, r.score, s.severidade, s.tempo "
        sql += " from resultados r"
        sql += " join sac s"
        sql += " on r.relacionado = s.atendimento and r.relacionadoitem = s.item"
        sql += " where r.atendimento = " + str(sac)
        sql += " and r.item = " + str(item)
        sql += f" and (r.util <> {False} or r.util is null) "
        sql += " order by r.algoritmo;"
        self.cur.execute(sql)
        return self.cur.fetchall()

    @staticmethod
    def pessoas(self, relacionados):
        sql = "  select pessoa, sum(quant) as quant "
        sql += " from pessoas "
        sql += " where atendimento||'-'||item in ("
        first = True
        for relacionado in relacionados:
            if not first:
                sql += ","
            first = False
            sql += str(relacionado[1]) + "||'-'||" + str(relacionado[2])
        sql += " )"
        sql += " group by pessoa"
        sql += " order by quant desc;"

        self.cur.execute(sql)
        return self.cur.fetchall()

    @staticmethod
    def consultar(self, atendimento, item, algoritmo):
        sql = "  select r.relacionado, r.relacionadoitem, r.score "
        sql += " from resultados r"
        sql += " join sac s"
        sql += " on r.relacionado = s.atendimento and r.relacionadoitem = s.item"
        sql += " where r.atendimento = " + str(atendimento)
        sql += " and r.item = " + str(item)
        sql += " and r.algoritmo = '" + str(algoritmo) + "'"
        sql += f" and (r.util <> {False} or r.util is null)"
        sql += " order by r.algoritmo;"
        #print(sql)
        self.cur.execute(sql)

        relacionado = 0
        relacionadoitem = 0
        score = 0

        registros = self.cur.fetchall()
        for registro in registros:
            relacionado = registro[0]
            relacionadoitem = registro[1]
            score = registro[2]

        return relacionado, relacionadoitem, score

    def __init__(self):
        super().__init__()
