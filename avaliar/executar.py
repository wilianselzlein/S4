# from S4.avaliar.cassandra import Cassandra
from avaliar.postgres import Postgres

# from avaliar.bagofwords import BagOfWords
from avaliar.doc2vec import Doc2Vec
from avaliar.cosine_distance import CosineDistance
from avaliar.bm25 import Bm25
from avaliar.lsa import Lsa

# import importar
import sys
from utils import utils
import pika
import config

log = utils.get_logger("Service loader")


def executar(salt):
    avaliar(salt)


def avaliar(salt):
    postgres = Postgres()
    atendimento = str(salt).split("/")[0]
    item = str(salt).split("/")[1]

    # importar.executar(atendimento, item)
    texto = postgres.atendimento(postgres, atendimento, item)

    if len(texto) == 0:
        return
    atendimentos = postgres.atendimentos(postgres, atendimento, item)
    log.critical(str(len(atendimentos)) + " atendimentos para avaliação")

    try:
        lsa = Lsa()
        relacionado, relacionadoitem, score = postgres.consultar(
            postgres, atendimento, item, lsa.arquivo
        )
        if relacionado == 0:
            sims = lsa.avaliar(lsa, texto, atendimentos)
            for sim in sims:
                relacionado = sim[0]
                relacionadoitem = sim[1]
                score = sim[2]
                if atendimento != relacionado or item != relacionadoitem:
                    postgres.relacionar(
                        postgres,
                        atendimento,
                        item,
                        lsa.arquivo,
                        relacionado,
                        relacionadoitem,
                        score,
                    )

        doc2vec = Doc2Vec()
        relacionado, relacionadoitem, score = postgres.consultar(
            postgres, atendimento, item, doc2vec.arquivo
        )
        if relacionado == 0:
            sims = doc2vec.avaliar(doc2vec, texto, atendimentos)
            for sim in sims:
                relacionado = sim[0].split("/")[0]
                relacionadoitem = sim[0].split("/")[1]
                score = sim[1]
                if atendimento != relacionado or item != relacionadoitem:
                    postgres.relacionar(
                        postgres,
                        atendimento,
                        item,
                        doc2vec.arquivo,
                        relacionado,
                        relacionadoitem,
                        score,
                    )

        cosinedistance = CosineDistance()
        relacionado, relacionadoitem, score = postgres.consultar(
            postgres, atendimento, item, cosinedistance.arquivo
        )
        if relacionado == 0:
            relacionado, relacionadoitem, score = cosinedistance.avaliar(
                cosinedistance, texto, atendimentos
            )
            postgres.relacionar(
                postgres,
                atendimento,
                item,
                cosinedistance.arquivo,
                relacionado,
                relacionadoitem,
                score,
            )

        bm25 = Bm25()
        relacionado, relacionadoitem, score = postgres.consultar(
            postgres, atendimento, item, bm25.arquivo
        )
        if relacionado == 0:
            relacionado, relacionadoitem, score = bm25.avaliar(
                bm25, texto, atendimentos
            )
            postgres.relacionar(
                postgres,
                atendimento,
                item,
                bm25.arquivo,
                relacionado,
                relacionadoitem,
                score,
            )

        # bagofwords = BagOfWords()
        # relacionado, relacionadoitem, score = postgres.consultar(postgres, atendimento, item, bagofwords.arquivo)
        # if relacionado == 0:
        #     relacionado, relacionadoitem, score = bagofwords.avaliar(bagofwords, texto, atendimentos)
        # postgres.relacionar(postgres, atendimento, item, bagofwords.arquivo, relacionado, relacionadoitem, score)

    except IOError as e:
        log.error(str(salt) + " " + "I/O error({0}): {1}".format(e.errno, e.strerror))
    except:
        log.error(str(salt) + " " + sys.exc_info()[0])


def portal(salt):
    atendimento = str(salt).split("/")[0]
    item = str(salt).split("/")[1]

    sever = {}
    tempo = {}
    pesso = {}

    postgres = Postgres()
    texto = postgres.atendimento(postgres, atendimento, item)
    if len(texto) == 0:
        return [], {}, {}, {}, texto

    texto = texto[0][4]
    relacionados = postgres.resultados(postgres, atendimento, item)
    for relacionado in relacionados:

        if str(relacionado[4]) in sever:
            sever[str(relacionado[4])] += 1
        else:
            sever[str(relacionado[4])] = 1

        if str(relacionado[5]) in tempo:
            tempo[str(relacionado[5])] += 1
        else:
            tempo[str(relacionado[5])] = 1

    pessoas = postgres.pessoas(postgres, relacionados)

    i = 0
    for pessoa in pessoas:
        pesso[i] = str(pessoa[1]) + " " + pessoa[0]
        i += 1

    return relacionados, sever.items(), tempo.items(), pesso.items(), texto


def fila():
    rabbit_conn = pika.BlockingConnection(pika.ConnectionParameters(config.rabbitmq))
    rabbit_public = rabbit_conn.channel()
    rabbit_public.queue_declare(queue=config.rabbitmq_validate)

    rabbit_public.basic_consume(
        queue=config.rabbitmq_validate, on_message_callback=callback, auto_ack=True
    )

    print(" [*] Waiting for messages. To exit press CTRL+C")
    rabbit_public.start_consuming()


def callback(ch, method, properties, body):
    executar(body)
