import os
import logging

cli = "pj"

ultima_importacao = '2017-01-01'
data_avaliacao = '2017-01-01'
quantidade = 3

cassandra_host = '127.0.0.1'
cassandra_KEYSPACE = 'keyspaceS4'

elasticsearch = 'http://localhost:9200'
elasticsearch_db = 's4' + cli
elasticsearch_search = 's4_search' + cli
elasticsearch_limit = 100

rabbitmq = 'localhost'
rabbitmq_import = 's4_import' + cli
rabbitmq_validate = 's4_validate' + cli
rabbitmq_limit = 100000

postgres_host = os.environ.get("POSTGRE_URI", '127.0.0.1')
postgres_db = 's4' + cli
postgres_dbpostgres = 'postgres'
postgres_user = 'postgres'
postgres_pass = 'root'
postgres_port = 5432

dsn_driver = "IBM DB2 ODBC DRIVER"
dsn_database = "SAC"            # e.g. "BLUDB"
dsn_hostname = os.environ.get("DB2SAC_URI", "172.23.1.2")  #""172.23.2.120" # e.g.: "awh-yp-small03.services.dal.bluemix.net"
dsn_port = "50100"                # e.g. "50000"
dsn_protocol = "TCPIP"            # i.e. "TCPIP"
dsn_uid = "UNJ_BI_PROCURADORIAS"        # e.g. "dash104434"
dsn_pwd = "3z@kthAzb"       # e.g. "7dBZ3jWt9xN6$o0JiX!m"
db2jcc = "/home/ivo/Downloads/jdbc_sqlj/db2_db2driver_for_jdbc_sqlj/db2jcc.jar"

dsn = (
    "DRIVER={{IBM DB2 ODBC DRIVER}};"
    "DATABASE={0};"
    "HOSTNAME={1};"
    "PORT={2};"
    "PROTOCOL=TCPIP;"
    "UID={3};"
    "PWD={4};").format(dsn_database, dsn_hostname, dsn_port, dsn_uid, dsn_pwd)

DEBUG_LEVEL = logging.DEBUG