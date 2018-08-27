from S4.avaliar.cassandra import Cassandra
from S4.avaliar.doc2vec import Doc2Vec


def executar(salt):
    avaliar(salt)


def avaliar(salt):
    cassandra = Cassandra()
    atendimento = str(salt).split('/')[0]
    item = str(salt).split('/')[1]
    texto = cassandra.atendimento(cassandra, atendimento, item)
    row = texto[0]  # for row in texto:
    atendimentos = cassandra.atendimentos(cassandra)
    # copia = atendimentos

    doc2vec = Doc2Vec()
    relacionado, relacionadoitem, score = doc2vec.avaliar(doc2vec, texto, atendimentos)
    cassandra.relacionar(cassandra, atendimento, item, doc2vec.arquivo, relacionado, relacionadoitem, score)

    print(row.atendimento, '-', row.item)
    # print(row.texto)


def portal(salt):
    atendimento = str(salt).split('/')[0]
    item = str(salt).split('/')[1]

    s = 'SALT: <b>' + salt + '</b><br><br><b>Parecidas:</b><br>'
    cassandra = Cassandra()
    relacionados = cassandra.resultados(cassandra, atendimento, item)
    for relacionado in relacionados:
        # s += relacionado.algoritmo + '= ' + relacionado.relacionado + '/' + relacionado.relacionadoitem + ': ' + relacionado.score + '<br>'
        # s += 'sev ' + relacionado.severidade + ' ' + str(relacionado.horas) + ' horas <br>'
        s += str(relacionado.relacionado) + '/' + str(relacionado.relacionadoitem) + ' ' + str(relacionado.score) + '<br>'
        s += '<br><b>Pessoas:</b>' + '<br>'
        pessoas = cassandra.pessoas(cassandra, relacionado.relacionado, relacionado.relacionadoitem)
        for pessoa in pessoas:
            s += pessoa.pessoa + ' ' + str(pessoa.quant) + '<br>'

        s += '<br><b>Severidade:</b> 3 80%<br>'
        s += '<br><b>Tempo médio:</b> 8 horas<br>'
    return s
