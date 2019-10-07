import gensim
from avaliar import modelo
import config
import os.path
import config

ARQUIVO = "doc2vec_" + config.cli + "_" + str(config.campo)


class Doc2Vec(modelo.Base):
    @staticmethod
    def avaliar(self, texto, atendimentos):
        model = gensim.models.doc2vec.Doc2Vec(
            vector_size=200, min_count=5, seed=1, max_vocab_size=20000, workers=1
        )  # , epochs=40
        if os.path.isfile(ARQUIVO):
            model = gensim.models.doc2vec.Doc2Vec.load(ARQUIVO)
        else:
            self.treinar(model, atendimentos)
        test_corpus = list(self.read_corpus(texto, tokens_only=True, updateList=False))

        inferred_vector = model.infer_vector(test_corpus[0])
        sims = model.docvecs.most_similar([inferred_vector], topn=config.quantidade)

        return sims

    def treinar(self, model, atendimentos):
        self.train_corpus = list(self.read_corpus(atendimentos))

        model.build_vocab(self.train_corpus)
        model.train(
            self.train_corpus, total_examples=model.corpus_count, epochs=model.epochs
        )
        # print('infer', model.infer_vector(['intimacao']))
        model.save(ARQUIVO)

    def read_corpus(self, atendimentos, tokens_only=False, updateList=True):
        # with smart_open.smart_open(fname, encoding="iso-8859-1") as f:
        # for i, line in enumerate(texto):
        i = 0
        for atendimento in atendimentos:
            # print('\r', '\t', i, len(atendimentos), end='')
            i += 1
            line = atendimento[config.campo]
            if tokens_only:
                yield gensim.utils.simple_preprocess(line)
            else:
                # For training data, add tags
                # yield gensim.models.doc2vec.TaggedDocument(gensim.utils.simple_preprocess(line), [i])
                yield gensim.models.doc2vec.TaggedDocument(
                    line.split(), [str(atendimento[0]) + "/" + str(atendimento[1])]
                )

    @property
    def arquivo(self):
        return ARQUIVO

    # def __init__(self):
    #     print('\t', ARQUIVO)
