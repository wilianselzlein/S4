import gensim
from S4.avaliar import modelo

# import os.path

ARQUIVO = "doc2vec"


class Doc2Vec(modelo.Base):

    @staticmethod
    def avaliar(self, texto, atendimentos):

        model = gensim.models.doc2vec.Doc2Vec(vector_size=50, min_count=2, epochs=40)
        # if os.path.isfile(ARQUIVO):
        #    self.treinar(model, atendimentos)
        # model.load(ARQUIVO)
        self.treinar(model, atendimentos)

        # test_corpus = list(self.read_corpus(texto, tokens_only=True))

        ranks = []
        for doc_id in range(len(self.train_corpus)):
            inferred_vector = model.infer_vector(self.train_corpus[doc_id].words)
            sims = model.docvecs.most_similar([inferred_vector], topn=len(model.docvecs))
            rank = [docid for docid, sim in sims].index(doc_id)
            ranks.append(rank)

        # print(collections.Counter(ranks))
        # print(sims[0]) #mais similar (24, 0.9981840252876282)
        # print(' '.join(self.train_corpus[sims[0][0]].words))

        similar = sims[0][0]
        score = sims[0][1]
        salt = self.numeros[similar][0]
        item = self.numeros[similar][1]
        # print(salt, '/', item)
        return salt, item, score

    def treinar(self, model, atendimentos):
        self.train_corpus = list(self.read_corpus(atendimentos))

        model.build_vocab(self.train_corpus)
        # print(model.train(self.train_corpus, total_examples=model.corpus_count, epochs=model.epochs))
        # print(model.infer_vector(['intimacao']))
        model.save(ARQUIVO)

    def read_corpus(self, atendimentos, tokens_only=False):
        # with smart_open.smart_open(fname, encoding="iso-8859-1") as f:
        # for i, line in enumerate(texto):
        i = 0
        self.numeros = []
        for atendimento in atendimentos:
            i += 1
            self.numeros.append([atendimento[0], atendimento[1]])
            line = atendimento[2]
            if tokens_only:
                yield gensim.utils.simple_preprocess(line)
            else:
                # For training data, add tags
                yield gensim.models.doc2vec.TaggedDocument(gensim.utils.simple_preprocess(line), [i])

    @property
    def arquivo(self):
        return ARQUIVO

    def __init__(self):
        print(ARQUIVO)
