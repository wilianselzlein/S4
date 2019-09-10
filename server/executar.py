# coding: latin-1
import avaliar as _avaliar
import config
from utils import utils
from aiohttp import web
import aiohttp_cors
import traceback
from server.postgres import Postgres
from elasticsearch import Elasticsearch
from datetime import datetime 
import json
from decimal import Decimal


log = utils.get_logger('Server')

prefix = f'/api/v1.0'


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


class APIException(Exception):
    pass


def get_key(name, data):
    if name in data:
        return data[name]
    else:
        raise APIException(f'Campo "{name}" não fornecido.')

async def wraps_exception(app, handler):
    async def middleware_handler(request):
        try:
            return await handler(request)
        except APIException as ae:
            log.info(f'API Exception: {str(ae)} ')
            return web.json_response({'msg': str(ae)}, status=400)
        except Exception as e:
            if e.status == 404:
                raise
            log.warning(f'Exception: {str(e)} ')
            log.warning(f'Traceback: {traceback.format_exc()} ')
            return web.json_response({'msg': 'Erro interno. Tente novamente ou entre em contato com nossa equipe.'},
                                     status=500)

    return middleware_handler


async def avaliacao(request):
    log.info('avaliacao')
    data = await request.json()
    log.info(f'Request data: {data}')

    atendimento = get_key('atendimento', data)
    item = get_key('item', data)
    # algoritmo = get_key('algoritmo', data)
    relacionado = get_key('relacionado', data)
    relacionadoitem = get_key('relacionadoitem', data)
    valor = get_key('valor', data)

    postgres = Postgres()
    postgres.avaliacao(postgres, atendimento, item, relacionado, relacionadoitem, valor)
    return web.json_response({'status': 'ok'})


async def avaliar(request):
    data = await request.json()
    log.info(f'Request data: {data}')

    atendimento = str(get_key('atendimento', data))
    item = str(get_key('item', data))

    _avaliar.executar(atendimento + '/' + item)
    relacionados, severidades, tempos, pessoas, texto = _avaliar.portal(atendimento + '/' + item)

    # should_queries = [qb(s).json() for s in should]

    # log.info('Generating DSL query')
    # dsl = {
    #     "from": 0,
    #     "_source": "cnj",
    #     "query": {
    #         "bool": {
    #             "must": must_queries,
    #             "must_no": must_not_queries,
    #             "should": should_queries
    #         }
    #     },
    #     "size": 10000
    # }
    dsl = {
            "relacionados": json.dumps(list(relacionados), cls=DecimalEncoder),
            "severidades": list(severidades),
            "tempos": list(tempos),
            "pessoas": list(pessoas), #json.dumps(
            "texto": texto
    }

    return web.json_response(dsl)

async def health(request):
    log.info('Health check')
    return web.json_response({'status': 'ok'})


async def start(request):
    return web.Response(text='S⁴ Sugestão de Solução de Salts na Sustentação')


async def index(request):
    log.info('index')
    postgres = Postgres()
    sugeridos = postgres.metricas(postgres, "count(relacionado)")
    avaliados = postgres.metricas(postgres, "count(distinct atendimento)")

    dsl = {
            "sugeridos": sugeridos,
            "avaliados": avaliados
    }

    return web.json_response(dsl)


async def buscas(request):
    log.info('buscas')

    es = Elasticsearch([config.elasticsearch])
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

    results = []
    # results['hits']['hits'][0]['_source']
    for ultima in ultimas['hits']['hits']:
        results.append(ultima['_source']['search'].replace("\"", ""))

    results = set(results)
    results = list(results)
    result = {"buscas": results}

    return web.json_response(results)


async def searchs(request):
    # url = "http://" + request.remote_addr + ":5601/app/kibana#/discover?_g=(refreshInterval:(pause:!t,value:0)," \
    #       "time:(from:now-5y,to:now))&_a=(columns:!(_source),index:'84c9b230-af0c-11e9-9a9a-eb64683ee0d2'," \
    #       "interval:auto,query:(language:kuery,query:'" + search + "'),sort:!(data,desc))"

    data = await request.json()
    log.info(f'Request data: {data}')
    search = get_key('search', data)

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

    results = {"search": cards}

    return web.json_response(results)


def executar():
    app = web.Application(logger=log, middlewares=[wraps_exception])

    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })

    app.add_routes([
        web.get('/index', index), 
        web.get('/buscas', buscas), 
        web.post('/searchs', searchs), 
        web.post('/health', health),
        web.post('/', start),
        web.post('/avaliacao', avaliacao), 
        web.post('/avaliar', avaliar)])

    for route in list(app.router.routes()):
        cors.add(route)
    web.run_app(app, host=config.server_host, port=config.server_port)
