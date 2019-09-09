import avaliar
from flask import Flask, render_template, request, flash
import urllib.parse
from elasticsearch import Elasticsearch
import config
from utils import Texto
from datetime import datetime
import aiohttp
import requests
from requests.exceptions import HTTPError
import json

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'you-will-never-guess-s4'

LIKE = True
DISLIKE = False


# if __name__ == "__main__":
#     app.run()

def executar():
    app.run(host=config.server_host)


def _host():
    return request.host_url


def _cli():
    return config.cli.upper()


def request_server(method, payload = {}):
    url = config.server_url + "/" + method
    try:
        if payload == {}:
            response = requests.get(url)
        else:
            response = requests.post(url, data=json.dumps(payload))
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6

    # print('response.status_code', response.status_code)
    # print('response.text', response.text)
    response = json.loads(response.text)
    # print('response', response)
    return response


@app.route('/')
def home():
    response = request_server('index')
    sugeridos = response['sugeridos']
    avaliados = response['avaliados']

    return render_template('index.html', host=_host(), avaliados=avaliados, sugeridos=sugeridos)


@app.route('/salt/<salt>/<item>')
def salt(salt, item):
    return avaliar_render(salt, item)


@app.route('/redirect', methods=['GET'])
def redirect():
    salt = request.args.get('salt')
    item = request.args.get('item')
    return avaliar_render(salt, item)


@app.route('/like/<salt>/<item>/<relacionado>/<relacionadoitem>')
def like(salt, item, relacionado, relacionadoitem):
    avaliacao(salt, item, relacionado, relacionadoitem, LIKE)
    # return redirect(url_for('salt', salt=salt, item=item))
    return avaliar_render(salt, item)


@app.route('/dislike/<salt>/<item>/<relacionado>/<relacionadoitem>')
def dislike(salt, item, relacionado, relacionadoitem):
    avaliacao(salt, item, relacionado, relacionadoitem, DISLIKE)
    # return redirect(url_for('salt', salt=salt, item=item))
    return avaliar_render(salt, item)


def avaliacao(atendimento, item, relacionado, relacionadoitem, valor):
    payload = {}
    payload["atendimento"] = atendimento
    payload["item"] = item
    payload["relacionado"] = relacionado
    payload["relacionadoitem"] = relacionadoitem
    payload["valor"] = valor    
    
    response = request_server('avaliacao', payload)


def avaliar_render(salt, item):
    if int(salt) == 0 or int(item) == 0:
        flash('Atendimento inválido.')
        return render_template('index.html', host=_host(), cli=_cli())
    else:
        avaliar.executar(salt + '/' + item)
        relacionados, severidades, tempos, pessoas, texto = avaliar.portal(salt + '/' + item)
        if len(relacionados) == 0:
            flash('Atendimento inválido ou ainda não importado.')
            return render_template('index.html', host=_host(), cli=_cli())
        else:
            return render_template('salt.html', host=_host(), cli=_cli(), salt=salt, item=item,
                                   relacionados=relacionados, severidades=severidades,
                                   tempos=tempos, pessoas=pessoas, texto=texto, avaliacao=True)


@app.route('/kibana', methods=['GET'])
def kibana():
    if request.headers.get("Referer") is None:
        flash('Você deve avaliar o atendimento antes da consulta!')
        return render_template('index.html', host=_host(), cli=_cli())
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
    doc = {
        'search': search,
        'timestamp': datetime.now()
    }
    es.index(index=config.elasticsearch_search, body=doc)
    es.indices.refresh(index=config.elasticsearch_search)

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
        try:
            card['item'] = int(result['_source']['item'])
            card['label'] = str(int(result['_source']['atendimento'])) + '/' + str(int(card['item']))
        except:
            card['item'] = int(result['_source']['item'].split('/')[0])
            card['label'] = str(int(result['_source']['atendimento'])) + '/' + str(result['_source']['item'])

        if 'highlight' in result:
            card['original'] = result['highlight']['original'][0]
        else:
            card['original'] = result['_source']['original']

        cards.append(card)

    search = search.replace("\"", "")

    ultimas = []
    ultimas = es.search(index=config.elasticsearch_search,
                        body={
                            "size": 100,
                            "sort": [
                                {
                                    "timestamp": {
                                        "order": "desc",
                                        "unmapped_type": "boolean"
                                    }
                                }
                            ],
                            "query": {
                                "match_all": {
                                }
                            }
                        }
                        )

    buscas = []
    # results['hits']['hits'][0]['_source']
    for ultima in ultimas['hits']['hits']:
        buscas.append(ultima['_source']['search'].replace("\"", ""))

    buscas = set(buscas)
    return render_template('kibana.html', host=_host(), cli=_cli(), search=search, cards=cards, limit=limit,
                           buscas=buscas)


@app.route('/curtir', methods=['POST'])
def curtir():
    avaliacao(request.form['salt'], request.form['item'], request.form['relacionado'], request.form['relacionadoitem'], LIKE)
    return str(LIKE)
