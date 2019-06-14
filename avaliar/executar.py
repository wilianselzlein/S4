# from S4.avaliar.cassandra import Cassandra
from avaliar.postgres import Postgres
from avaliar.bagofwords import BagOfWords
from avaliar.doc2vec import Doc2Vec
from avaliar.cosine_distance import CosineDistance
from avaliar.bm25 import Bm25
import importar
import datetime
import sys

def executar(salt):
    avaliar(salt)


def avaliar(salt):
    postgres = Postgres()
    atendimento = str(salt).split('/')[0]
    item = str(salt).split('/')[1]
    importar.executar(atendimento, item)
    texto = postgres.atendimento(postgres, atendimento, item)

    atendimentos = postgres.atendimentos(postgres, atendimento, item)
    print(len(atendimentos), "atendimentos para avaliação")
    # copia = atendimentos

    datahora()

    try:
        doc2vec = Doc2Vec()
        relacionado, relacionadoitem, score = postgres.consultar(postgres, atendimento, item, doc2vec.arquivo)
        if relacionado == 0:
            relacionado, relacionadoitem, score = doc2vec.avaliar(doc2vec, texto, atendimentos)
        postgres.relacionar(postgres, atendimento, item, doc2vec.arquivo, relacionado, relacionadoitem, score)

        cosinedistance = CosineDistance()
        relacionado, relacionadoitem, score = postgres.consultar(postgres, atendimento, item, cosinedistance.arquivo)
        if relacionado == 0:
            relacionado, relacionadoitem, score = cosinedistance.avaliar(cosinedistance, texto, atendimentos)
        postgres.relacionar(postgres, atendimento, item, cosinedistance.arquivo, relacionado, relacionadoitem, score)

        bm25 = Bm25()
        relacionado, relacionadoitem, score = postgres.consultar(postgres, atendimento, item, bm25.arquivo)
        if relacionado == 0:
            relacionado, relacionadoitem, score = bm25.avaliar(bm25, texto, atendimentos)
        postgres.relacionar(postgres, atendimento, item, bm25.arquivo, relacionado, relacionadoitem, score)
        datahora()

        bagofwords = BagOfWords()
        relacionado, relacionadoitem, score = postgres.consultar(postgres, atendimento, item, bagofwords.arquivo)
        if relacionado == 0:
            relacionado, relacionadoitem, score = bagofwords.avaliar(bagofwords, texto, atendimentos)
        postgres.relacionar(postgres, atendimento, item, bagofwords.arquivo, relacionado, relacionadoitem, score)

    except IOError as e:
         print("I/O error({0}): {1}".format(e.errno, e.strerror))
    except:
        print("Erro:", sys.exc_info()[0])
        # raise


def datahora():
    now = datetime.datetime.now()
    print(now)


def portal(salt):
    atendimento = str(salt).split('/')[0]
    item = str(salt).split('/')[1]

    sever = {}
    tempo = {}
    pesso = {}

    postgres = Postgres()
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

    return relacionados, sever.items(), tempo.items(), pesso.items()

