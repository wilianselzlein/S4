# coding: latin-1
import avaliar
import config
from utils import utils
from aiohttp import web
import aiohttp_cors
import traceback
from server.postgres import Postgres

log = utils.get_logger('Server')


prefix = f'/api/v1.0'


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

    atendimento = get_key('atendimento', data)
    item = get_key('item', data)
    
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
            "relacionados": [],
            "sever": [],
            "tempo": [],
            "pessoas": [],
            "texto": ""
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
        web.post('/health', health),
        web.post('/', start),
        web.get('/index', index), 
        web.post('/avaliacao', avaliacao), 
        web.post('/avaliar', avaliar)])

    for route in list(app.router.routes()):
        cors.add(route)
    web.run_app(app, host=config.server_host, port=config.server_port)
