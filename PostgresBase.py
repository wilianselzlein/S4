import config
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from peewee import PostgresqlDatabase, SmallIntegerField
from peewee import Model, CharField, BooleanField, ForeignKeyField, IntegerField, CompositeKey, DateTimeField

db = PostgresqlDatabase(config.postgres_db, user=config.postgres_user, password=config.postgres_pass,
                        host=config.postgres_host, port=config.postgres_port)


class BaseModel(Model):

    class Meta:
        database = db


class Pessoas(BaseModel):
    atendimento = IntegerField()
    item = SmallIntegerField()
    pessoa = CharField(max_length=25)
    quant = SmallIntegerField()

    class Meta:
        primary_key = CompositeKey('atendimento', 'item', 'pessoa')


TABLES = [Pessoas]


class Base(object):

    @staticmethod
    def create_database(self):
        sql = "select EXISTS(SELECT FROM pg_database WHERE datname = '%s')"
        self.cur.execute(sql % config.postgres_db)
        registros = self.cur.fetchall()
        exist_db = False
        for registro in registros:
            exist_db = registro[0]

        if not exist_db:
            sql = "CREATE DATABASE %s WITH ENCODING='UTF8' CONNECTION LIMIT=-1;"
            self.cur.execute(sql % config.postgres_db)
            self.con.commit()


    @staticmethod
    def create_tables(self):

        db.create_tables(TABLES)

        sql = " CREATE TABLE IF NOT EXISTS public.sac ("\
              " atendimento integer," \
              " item smallint," \
              " original text," \
              " stemming text," \
              " texto text," \
              " severidade smallint," \
              " tempo smallint," \
              " data date," \
              " CONSTRAINT pk_sac PRIMARY KEY(atendimento, item)" \
               ");"
        self.cur.execute(sql)
        # print(sql)
        self.con.commit()



        # sql = " CREATE TABLE IF NOT EXISTS public.pessoas ("\
        #       " atendimento integer," \
        #       " item smallint," \
        #       " pessoa varchar(25)," \
        #       " quant smallint," \
        #       " CONSTRAINT pk_pessoas PRIMARY KEY(atendimento, item, pessoa)" \
        #        ");"
        # self.cur.execute(sql)
        # self.con.commit()

        sql = " CREATE TABLE IF NOT EXISTS public.fontes ("\
              " atendimento integer," \
              " item smallint," \
              " changeset integer," \
              " fontes text," \
              " CONSTRAINT pk_fontes PRIMARY KEY(atendimento, item, changeset)" \
               ");"
        self.cur.execute(sql)
        self.con.commit()

        sql = " CREATE TABLE IF NOT EXISTS public.resultados ("\
              " atendimento integer," \
              " item smallint," \
              " relacionado integer," \
              " relacionadoitem smallint," \
              " algoritmo varchar(25)," \
              " util boolean, " \
              " score double precision, " \
              " CONSTRAINT pk_resultados PRIMARY KEY(atendimento, item, algoritmo, relacionado, relacionadoitem)" \
               ");"
        self.cur.execute(sql)
        self.con.commit()


    def __init__(self):
        self.con = psycopg2.connect(host=config.postgres_host, database=config.postgres_dbpostgres,
                                    user=config.postgres_user, password=config.postgres_pass)

        self.con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        self.cur = self.con.cursor()

        self.create_database(self)

        self.con = psycopg2.connect(host=config.postgres_host, database=config.postgres_db,
                                    user=config.postgres_user, password=config.postgres_pass)

        self.con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        self.cur = self.con.cursor()

        self.create_tables(self)

