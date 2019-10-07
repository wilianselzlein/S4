from avaliar import modelo
import nltk
import numpy as np
from sklearn.feature_extraction.text import TfidfTransformer
import config

ARQUIVO = "BagOfWords"


class BagOfWords(modelo.Base):
    @staticmethod
    def avaliar(self, texto, atendimentos):

        listaResumo = self.montaresumo(atendimentos)

        # print("Total de documentos na colecao:")
        # print(len(listaResumo))
        # print("Primeiras linhas:")
        # for linha in listaResumo[0:9]:
        #   print(linha)

        # print("Algumas linha aleatorias:")
        # from random import randint
        # for i in range(1, 10):
        #    print(listaResumo[randint(0, len(listaResumo))])

        # print("Montando vocabulario...")
        vocab = self.montaDictVocabulario(listaResumo)
        # print("Total de palavras do Vocabulario da TEC:")
        # print(len(vocab))

        # print("Montando vetores...")
        vetores, vetorVocab = self.montaVetores(listaResumo, vocab)

        print("Vetor de vocabulario:")
        print(vetorVocab.shape)
        print("Vetor de documentos:")
        print(len(vetores))

        todasaspalavras = str(texto)
        listatodasaspalavras = todasaspalavras.split()
        print("Total de palavras:")
        print(len(listatodasaspalavras))

        todasaspalavrasResumo = str(listaResumo)
        listatodasaspalavrasResumo = todasaspalavrasResumo.split()
        # print("Total de palavras das linhas com descricao completa (Colecao de documentos):")
        # print(len(listatodasaspalavrasResumo))

        # print("Media de palavras por linha (Colecao de documentos):")
        # print(len(listatodasaspalavrasResumo) / len(listaResumo))

        print("Numero de documentos da colecao:")
        print(len(vetores))

        print("Estatisticas das ocorrencias das palavras no vocabulario:")
        print(
            "Media {}, minimo {}, maximo {}".format(
                vetorVocab.mean(), vetorVocab.min(), vetorVocab.max()
            )
        )
        print(type(vetores))
        print(type(vetores.values()))
        print(vetores["315731/1"])
        transformer = TfidfTransformer()

        matrizVetores = np.asarray(list(vetores.values()), dtype=np.int16)
        tfidf = transformer.fit_transform(matrizVetores)
        matriz_tfidf = tfidf.toarray()

        # print(matrizVetores[1:10])

        # print(matriz_tfidf[1:10])

        # print(texto[0][2])
        salt = 0
        item = 0
        score = 0

        if len(texto) > 0:
            matrizPontos, explica = self.pontuaVetores_tfidf(
                texto[0][config.campo], vocab, vetores, vetorVocab
            )
            # print(explica)
            ind = 1
            if ind > matrizPontos.shape[1]:
                ind = matrizPontos.shape[1]
                # print("1 mais:")

            for codigo in matrizPontos[0, :ind]:
                for linha in listaResumo:
                    codigo2 = linha[:10]
                    if codigo2 == codigo:
                        score = matrizPontos[1, :ind][0]
                        # print(score)
                        salt = linha[:6]
                        item = linha[7:8]
                        # print(linha)

        # print(score)
        return salt, item, score

    def treinar(self, model, atendimentos):

        model.save(ARQUIVO)

    def montaresumo(self, atendimentos):
        listaresumo = []
        for atendimento in atendimentos:
            codigo = str(atendimento[0]) + "/" + str(atendimento[1])
            descricao = str(atendimento[config.campo])
            listaresumo.append(" ".join([codigo, " ", descricao]))

        return listaresumo

    def montaDictVocabulario(self, lista):
        # Percorre todos os subitens COM descricao completa.
        stopwords = nltk.corpus.stopwords.words("portuguese")
        vocab = {}
        # Cria vocabulario atraves desta descricao completa
        index = 0
        for linha in lista:
            codigo = linha[:8]
            descricao = linha[10:]
            listadepalavras = descricao.split()
            for palavra in listadepalavras:
                if (len(palavra) > 3) and (stopwords.count(palavra) == 0):
                    if palavra not in vocab:
                        vocab[palavra] = index
                        index += 1
        return vocab

    # Percorre todos os subitens COM descricao completa.
    # Cria um dict de vetores para cada item.
    # Cria um vetor do vocabulario primeiro
    def montaVetores(self, plista, pvocab):
        vetorVocab = np.zeros(len(pvocab), dtype=np.int16)
        vetores = {}
        for linha in plista:
            codigo = linha[:10]
            descricao = linha[11:]
            listadepalavras = descricao.split()
            tecvector = np.zeros(len(pvocab), dtype=np.int16)
            for palavra in listadepalavras:
                if palavra in pvocab:
                    index = pvocab[palavra]
                    tecvector[index] += 1
                    vetorVocab[index] += 1

            vetores[codigo] = tecvector
        return vetores, vetorVocab

    def pontuaVetores(self, ptexto, pvocab, pvetores, vetorVocab, ponderado=False):
        # Por eficiencia, selecionar somente as colunas com palavras que ocorrem na busca
        # Portanto, primeiro converter a lista vetores de uma Matriz de dimensoes
        # numerodes x tamanhodoVocabulario
        # Depois criar uma matriz somando os valores das colunas do vocabulario da consulta
        matrizVetores = np.asarray(list(pvetores.values()), dtype=np.int16)
        matrizCodigos = np.asarray(list(pvetores.keys()))
        matrizSoma = np.zeros(len(pvetores))
        listadepalavras = ptexto.split()
        explicacao = ""
        for palavra in listadepalavras:
            if palavra in pvocab:
                index = pvocab[palavra]
                vetor = matrizVetores[:, index]
                explicacao = explicacao + palavra + " " + str(vetorVocab[index]) + " "
                matrizSoma = np.add(matrizSoma, vetor)
        indicesnaozero = np.nonzero(matrizSoma)
        matrizTemp = np.vstack(
            (matrizCodigos[indicesnaozero], matrizSoma[indicesnaozero])
        )
        indices = matrizTemp[1, :].argsort()
        indices = indices[::-1]
        matrizCodigoePontuacao = matrizTemp[:, indices]
        return matrizCodigoePontuacao, explicacao

    def pontuaVetores_tfidf(
        self, ptexto, pvocab, pvetores, vetorVocab, ponderado=False
    ):
        # Por eficiencia, selecionar somente as colunas com palavras que ocorrem na busca
        # Portanto, primeiro converter a lista vetores de uma Matriz de dimensoes
        # numero x tamanhodoVocabulario
        # Depois criar uma matriz somando os valores das colunas do vocabulario da consulta
        matrizVetores = np.asarray(list(pvetores.values()), dtype=np.int16)

        transformer = TfidfTransformer()
        tfidf = transformer.fit_transform(matrizVetores)
        matriz_tfidf = tfidf.toarray()
        matrizCodigos = np.asarray(list(pvetores.keys()))
        matrizSoma = np.zeros(len(pvetores))
        listadepalavras = ptexto.split()
        explicacao = ""
        for palavra in listadepalavras:
            if palavra in pvocab:
                index = pvocab[palavra]
                vetor = matriz_tfidf[:, index]
                explicacao = explicacao + palavra + " " + str(vetorVocab[index]) + " "
                matrizSoma = np.add(matrizSoma, vetor)
        indicesnaozero = np.nonzero(matrizSoma)
        matrizTemp = np.vstack(
            (matrizCodigos[indicesnaozero], matrizSoma[indicesnaozero])
        )
        indices = matrizTemp[1, :].argsort()
        indices = indices[::-1]
        matrizCodigoePontuacao = matrizTemp[:, indices]
        return matrizCodigoePontuacao, explicacao

    @property
    def arquivo(self):
        return ARQUIVO

    # def __init__(self):
    #     print('\t', ARQUIVO)
