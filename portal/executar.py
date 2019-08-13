import avaliar
from flask import Flask, render_template, request, flash
from portal.postgres import Postgres
import urllib.parse
from elasticsearch import Elasticsearch
import config
from utils import Texto

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'you-will-never-guess'

LIKE = True
DISLIKE = False

# if __name__ == "__main__":
#     app.run()

def executar():
    app.run(host="0.0.0.0")

@app.route('/')
def home():
    # return "S4"
    return render_template('index.html')

@app.route('/salt/<salt>/<item>')
def salt(salt, item):
    return avaliar_render(salt, item)

@app.route('/redirect', methods=['GET'])
def redirect():
    salt = request.args.get('salt')
    item = request.args.get('item')
    return avaliar_render(salt, item)

@app.route('/like/<salt>/<item>/<algoritmo>/<relacionado>/<relacionadoitem>')
def like(salt, item, algoritmo, relacionado, relacionadoitem):
    avaliacao(salt, item, algoritmo, relacionado, relacionadoitem, LIKE)
    # return redirect(url_for('salt', salt=salt, item=item))
    return avaliar_render(salt, item)

@app.route('/dislike/<salt>/<item>/<algoritmo>/<relacionado>/<relacionadoitem>')
def dislike(salt, item, algoritmo, relacionado, relacionadoitem):
    avaliacao(salt, item, algoritmo, relacionado, relacionadoitem, DISLIKE)
    #return redirect(url_for('salt', salt=salt, item=item))
    return avaliar_render(salt, item)

def avaliacao(salt, item, algoritmo, relacionado, relacionadoitem, valor):
    postgres = Postgres()
    postgres.avaliacao(postgres, salt, item, algoritmo, relacionado, relacionadoitem, valor)

def avaliar_render(salt, item):
    if int(salt) == 0 or int(item) == 0:
        flash('Atendimento inválido.')
        return render_template('index.html')
    else:
        avaliar.executar(salt + '/' + item)
        relacionados, severidades, tempos, pessoas, texto = avaliar.portal(salt + '/' + item)
        if len(relacionados) == 0:
            flash('Atendimento inválido ou ainda não importado.')
            return render_template('index.html')
        else:
            return render_template('salt.html', salt=salt, item=item, relacionados=relacionados, severidades=severidades,
                               tempos=tempos, pessoas=pessoas, texto=texto, avaliacao=True)

@app.route('/kibana', methods=['GET'])
def kibana():
    texto = Texto()
    search = request.args.get('search')
    search = texto.kibana(texto, search)
    search = urllib.parse.quote_plus(search)
    
    # url = "http://" + request.remote_addr + ":5601/app/kibana#/discover?_g=(refreshInterval:(pause:!t,value:0)," \
    #       "time:(from:now-5y,to:now))&_a=(columns:!(_source),index:'84c9b230-af0c-11e9-9a9a-eb64683ee0d2'," \
    #       "interval:auto,query:(language:kuery,query:'" + search + "'),sort:!(data,desc))"

    limit = config.elasticsearch_limit
    es = Elasticsearch([config.elasticsearch])
    results = es.search(index=config.elasticsearch_db, body={"size": limit, "sort": [{"data": {"order": "desc"}}], "_source" : ["atendimento", "item", "data", "original"], "query": {"bool": {"filter": [{"multi_match": {"type": "phrase", "query": search, "lenient": "true"}}]}}})

    cards = []
    # results['hits']['hits'][0]['_source']
    for result in results['hits']['hits']:
        cards.append({'atendimento': int(result['_source']['atendimento']),
                      'item': int(result['_source']['item']),
                      'original': result['_source']['original']})

    return render_template('kibana.html', search=search, cards=cards, limit=limit)

@app.route('/curtir', methods=['POST'])
def curtir():   
    avaliacao(request.form['salt'], request.form['item'], request.form['algoritmo'], request.form['relacionado'], request.form['relacionadoitem'], LIKE)
    return str(LIKE)
