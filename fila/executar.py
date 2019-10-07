import avaliar
import importar
import pika
import config
from utils import utils
from fila.postgres import Postgres

log = utils.get_logger("Service Queue")


def avaliar_queue(ch, method, properties, body):
    avaliar.executar(str(body, "utf-8"))


def importar_queue(ch, method, properties, body):
    atendimento = str(body, "utf-8").split("/")[0]
    item = str(body, "utf-8").split("/")[1]
    importar.atividades(atendimento, item)


def executar(fila):
    rabbit_conn = pika.BlockingConnection(pika.ConnectionParameters(config.rabbitmq))
    rabbit_public = rabbit_conn.channel()
    if fila == "I":
        add_atividades(rabbit_public)
        rabbit_public.queue_declare(queue=config.rabbitmq_import)
        rabbit_public.basic_consume(
            queue=config.rabbitmq_import,
            on_message_callback=importar_queue,
            auto_ack=True,
        )
    else:
        add_items(rabbit_public)
        rabbit_public.queue_declare(queue=config.rabbitmq_validate)
        rabbit_public.basic_consume(
            queue=config.rabbitmq_validate,
            on_message_callback=avaliar_queue,
            auto_ack=True,
        )

    rabbit_public.basic_qos(prefetch_count=1)
    rabbit_public.start_consuming()


def add_items(rabbit_public):
    postgres = Postgres()
    items = postgres.atendimentos(postgres)
    for row in items:
        es_id = str(row[0]) + "/" + str(row[1])
        rabbit_public.basic_publish(
            exchange="", routing_key=config.rabbitmq_validate, body=es_id
        )


def add_atividades(rabbit_public):
    postgres = Postgres()
    items = postgres.atividades(postgres)
    for row in items:
        es_id = str(row[0]) + "/" + str(row[1])
        rabbit_public.basic_publish(
            exchange="", routing_key=config.rabbitmq_import, body=es_id
        )
