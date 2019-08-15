import avaliar
from flask import Flask, render_template, request, flash
from portal.postgres import Postgres
import urllib.parse
from elasticsearch import Elasticsearch
import config
from utils import Texto

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'you-will-never-guess-s4'

LIKE = True
DISLIKE = False

# if __name__ == "__main__":
#     app.run()

def executar():
    app.run(host="0.0.0.0")

def _host():
    return request.host_url

@app.route('/')
def home():
    # return "S4"
    return render_template('index.html', host=_host())

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
        return render_template('index.html', host=_host())
    else:
        avaliar.executar(salt + '/' + item)
        relacionados, severidades, tempos, pessoas, texto = avaliar.portal(salt + '/' + item)
        if len(relacionados) == 0:
            flash('Atendimento inválido ou ainda não importado.')
            return render_template('index.html', host=_host())
        else:
            return render_template('salt.html', host=_host(), salt=salt, item=item, relacionados=relacionados, severidades=severidades,
                               tempos=tempos, pessoas=pessoas, texto=texto, avaliacao=True)

@app.route('/kibana', methods=['GET'])
def kibana():
    if request.headers.get("Referer") is None:
        flash('Você deve avaliar o atendimento antes da consulta!')
        return render_template('index.html', host=_host()) 
    texto = Texto()
    search = request.args.get('search')
    # search = texto.kibana(texto, search)
    search = search.replace("+", "")
    # search = urllib.parse.quote_plus(search)
    search = '"' + search + '"'
    
    # url = "http://" + request.remote_addr + ":5601/app/kibana#/discover?_g=(refreshInterval:(pause:!t,value:0)," \
    #       "time:(from:now-5y,to:now))&_a=(columns:!(_source),index:'84c9b230-af0c-11e9-9a9a-eb64683ee0d2'," \
    #       "interval:auto,query:(language:kuery,query:'" + search + "'),sort:!(data,desc))"

    limit = config.elasticsearch_limit
    es = Elasticsearch([config.elasticsearch])
    results = es.search(index=config.elasticsearch_db, 
                        body={
                              "version": True,
                              "size": config.elasticsearch_limit,
                              "sort": [
                                {
                                  "data": {
                                    "order": "desc",
                                    "unmapped_type": "boolean"
                                  }
                                }
                              ],
                              # "aggs": {
                              #   "2": {
                              #     "date_histogram": {
                              #       "field": "data",
                              #       "interval": "30d",
                              #       "time_zone": "America/Sao_Paulo",
                              #       "min_doc_count": 1
                              #     }
                              #   }
                              # },
                              # "stored_fields": [
                              #   "*"
                              # ],
                              # "script_fields": {},
                              # "docvalue_fields": [
                              #   {
                              #     "field": "data",
                              #     "format": "date_time"
                              #   },
                              #   {
                              #     "field": "timestamp",
                              #     "format": "date_time"
                              #   }
                              # ],
                              "query": {
                                "bool": {
                                  "must": [
                                    {
                                      "query_string": {
                                        "query": search + '~4',
                                        "analyze_wildcard": True,
                                        "time_zone": "America/Sao_Paulo",
                                        "fields": ["original"]
                                      }
                                    }
                                    # {
                                    #   "range": {
                                    #     "data": {
                                    #       "format": "strict_date_optional_time",
                                    #       "gte": "2014-08-14T12:50:45.763Z",
                                    #       "lte": "2019-08-14T12:50:45.763Z"
                                    #     }
                                    #   }
                                    # }
                                  ],
                                  "filter": [],
                                  "should": [],
                                  "must_not": []
                                }
                              },
                              "highlight": {
                                "pre_tags": [
                                  "<kbd>"
                                ],
                                "post_tags": [
                                  "</kbd>"
                                ],
                                "fields": {
                                  "original": {}
                                },
                                "fragment_size": 2147483647
                              }
                            })

    cards = []
    # results['hits']['hits'][0]['_source']
    for result in results['hits']['hits']:
        card = {}
        card['atendimento'] = int(result['_source']['atendimento'])
        card['item'] = int(result['_source']['item'])
        if 'highlight' in result:
            card['original'] = result['highlight']['original'][0]
        else:
            card['original'] = result['_source']['original']

        cards.append(card)

    search = search.replace("\"", "")

    return render_template('kibana.html', host=_host(), search=search, cards=cards, limit=limit)

@app.route('/curtir', methods=['POST'])
def curtir():   
    avaliacao(request.form['salt'], request.form['item'], request.form['algoritmo'], request.form['relacionado'], request.form['relacionadoitem'], LIKE)
    return str(LIKE)

