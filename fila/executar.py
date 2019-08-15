import avaliar
import importar
import pika
import config
from utils import utils

log = utils.get_logger('Service Queue')


def avaliar_queue(ch, method, properties, body):
    avaliar.executar(str(body, "utf-8"))


def importar_queue(ch, method, properties, body):
    log.info(str(body) + " queue rabbit")


def executar(fila):
    rabbit_conn = pika.BlockingConnection(pika.ConnectionParameters(config.rabbitmq))
    rabbit_public = rabbit_conn.channel()
    if fila == 'I':
        rabbit_public.queue_declare(queue=config.rabbitmq_import)
        rabbit_public.basic_consume(queue=config.rabbitmq_import, on_message_callback=importar_queue, auto_ack=True)
    else:
        rabbit_public.queue_declare(queue=config.rabbitmq_validate)
        rabbit_public.basic_consume(queue=config.rabbitmq_validate, on_message_callback=avaliar_queue, auto_ack=True)

    rabbit_public.basic_qos(prefetch_count=1)
    rabbit_public.start_consuming()

