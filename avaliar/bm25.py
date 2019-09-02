from avaliar.bm25class.parse import *
from avaliar.bm25class.query import QueryProcessor
import operator
import config
from avaliar import modelo

# import os.path

ARQUIVO = "bm25"


class Bm25(modelo.Base):

    @staticmethod
    def avaliar(self, texto, atendimentos):
        # qp = QueryParser(filename='E:\\OneDrive\\OneDrive - Softplan\\Python\\BM25-master\\text\\queries.txt')
        # qp.parse()
        # queries = qp.get_queries()
        queries = [texto[0][config.campo].split()]
        # print(queries)

        #cp = CorpusParser(filename='E:\\OneDrive\\OneDrive - Softplan\\Python\\BM25-master\\text\\corpus.txt')
        #cp.parse()
        #corpus = cp.get_corpus()

        #print (type(corpus)) #<class 'dict'>
        #print (type(corpus["1"])) #<class 'list'>
        #print("--------")

        corpus = {}
        for atendimento in atendimentos:
            codigo = str(atendimento[0]) + '/' + str(atendimento[1])
            #print(codigo)
            descricao = str(atendimento[config.campo]).split()
            #print(descricao)
            #print("--------")
            corpus[codigo] = descricao

        #corpus["1"] = ['sintese1', 'problema1', 'procurador1', 'reclama1', 'intimacoes1']
        #corpus["2-2"] = ['sempre2', 'insere2', 'movimentacoes2', 'intimacao2', 'notificacao2']
        #corpus["3/3"] = ['intimacoes3', 'referem3', 'processo3', 'incidente3']

        #print (type(corpus)) #<class 'dict'>
        #print (type(corpus["1"])) #<class 'list'>
        #print("--------")

        #print(corpus["1"])
        #print(corpus["2-2"])
        #print(corpus["3/3"])
        #print("--------")
        #for item in corpus:
        #    print(item)
        #    print("--------")
        #    print(corpus[item])
        #    print(corpus[item][0])
        #    if corpus[item][0] == "favor":
        #        break

        proc = QueryProcessor(queries, corpus)
        results = proc.run()
        qid = 0
        score = 0
        salt = 0
        item = 0

        for result in results:
            sorted_x = sorted(result.items(), key=operator.itemgetter(1))
            sorted_x.reverse()
            index = 0
            for i in sorted_x[:100]:
                tmp = (qid, i[0], index, i[1])
                score = i[1]
                salt = i[0].split('/')[0]
                #salt = 286478
                item = i[0].split('/')[1]

                # print ('{:>1}\tQ0\t{:>4}\t{:>2}\t{:>12}\tNH-BM25'.format(*tmp))
                index += 1
                break
            qid += 1

        #print(salt, '/', item, '-', score)
        return salt, item, score

    def treinar(self, model, atendimentos):
        model.save(ARQUIVO)

    @property
    def arquivo(self):
        return ARQUIVO

    # def __init__(self):
    #     print('\t', self.arquivo)
