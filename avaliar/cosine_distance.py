from nltk.corpus import brown, stopwords
from nltk.cluster.util import cosine_distance

from avaliar import modelo

# import os.path

ARQUIVO = "cosine_distance"


class CosineDistance(modelo.Base):

    @staticmethod
    def avaliar(self, texto, atendimentos):

        dic = {}
        r = 0
        for atendimento in atendimentos:
            codigo = str(atendimento[0]) + '/' + str(atendimento[1])
            descricao = str(atendimento[2])
            dic[codigo] = self.sentence_similarity(texto[0][2].split(), descricao.split())

        score = 0
        salt = 0
        item = 0

        for atendimento in sorted(dic, key=dic.get):
            score = dic[atendimento]
            salt = atendimento
            item = salt[7:8]
            salt = atendimento[0:6]
            break
            #print (dic[atendimento])

        return salt, item, score

    def sentence_similarity(self, sent1, sent2, stopwords=None):
        if stopwords is None:
            stopwords = []

        sent1 = [w.lower() for w in sent1]
        sent2 = [w.lower() for w in sent2]

        all_words = list(set(sent1 + sent2))

        vector1 = [0] * len(all_words)
        vector2 = [0] * len(all_words)

        # build the vector for the first sentence
        for w in sent1:
            if w in stopwords:
                continue
            vector1[all_words.index(w)] += 1

        # build the vector for the second sentence
        for w in sent2:
            if w in stopwords:
                continue
            vector2[all_words.index(w)] += 1

        return cosine_distance(vector1, vector2)

    def treinar(self, model, atendimentos):
        model.save(ARQUIVO)

    @property
    def arquivo(self):
        return ARQUIVO

    def __init__(self):
        print('\t', ARQUIVO)
