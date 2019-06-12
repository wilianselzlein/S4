from S4 import config
import psycopg2

class base(object):


    def __init__(self):
        self.con = psycopg2.connect(host=config.postgres_host, database=config.postgres_db,
                                    user=config.postgres_user, password=config.postgres_pass)
        self.cur = self.con.cursor()
