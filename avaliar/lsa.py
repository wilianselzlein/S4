# import sklearn
from sklearn.decomposition import TruncatedSVD
# from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import Normalizer
# from sklearn import metrics
# from sklearn.cluster import KMeans, MiniBatchKMeans
from nltk.corpus import stopwords
import numpy as np
import pandas as pd
# from scipy.spatial.distance import cosine
from sklearn.metrics.pairwise import cosine_similarity

from avaliar import modelo

# import os.path

ARQUIVO = "lsa"


class Lsa(modelo.Base):

    @staticmethod
    def avaliar(self, texto, atendimentos):

        example = []
        salts = []
        for atendimento in atendimentos:
            example.append(atendimento[2])
            salts.append(str(atendimento[0]) + '/' + str(atendimento[1]))

        vectorizer = CountVectorizer(min_df=5, ngram_range=(1, 3), stop_words=stopwords.words("portuguese"))

        dtm = vectorizer.fit_transform(example)

        lsa = TruncatedSVD(150, algorithm='arpack')

        dtm = dtm.asfptype()
        dtm_model = lsa.fit(dtm)
        dtm_lsa = dtm_model.transform(dtm)

        dtm_lsa = Normalizer(copy=False).fit_transform(dtm_lsa)

        example2 = [texto[0][2]]

        dtm = vectorizer.transform(example2)

        dtm_lsa_exemplo = dtm_model.transform(dtm)

        dtm_lsa_exemplo = Normalizer(copy=False).fit_transform(dtm_lsa_exemplo)

        similarity = np.asarray(np.asmatrix(dtm_lsa) * np.asmatrix(dtm_lsa_exemplo).T)

        # similarity = cosine_similarity(np.asmatrix(dtm_lsa), np.asmatrix(dtm_lsa_exemplo))

        res = pd.DataFrame(similarity, index=salts, columns=example2).sort_values(example2, ascending=False).head(1)

        salt = res.index.tolist()[0].split('/')[0]

        item = res.index.tolist()[0].split('/')[1]

        score = res.values.tolist()[0][0]

        return salt, item, score

    def treinar(self, model, atendimentos):
        model.save(ARQUIVO)

    @property
    def arquivo(self):
        return ARQUIVO

    def __init__(self):
        print('\t', self.arquivo)
