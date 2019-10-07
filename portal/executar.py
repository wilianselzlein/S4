from flask import Flask, render_template, request, flash
import config
import requests
from requests.exceptions import HTTPError
import json

app = Flask(__name__, static_url_path="/static")
app.config["SECRET_KEY"] = "you-will-never-guess-s4"

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


def request_server(method, payload={}):
    url = config.server_url + "/" + method
    try:
        if payload == {}:
            response = requests.get(url)
        else:
            response = requests.post(url, data=json.dumps(payload))
    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Python 3.6
    except Exception as err:
        print(f"Other error occurred: {err}")  # Python 3.6

    # print('response.status_code', response.status_code)
    # print('response.text', response.text)
    response = json.loads(response.text)
    # print('response', response)
    return response


@app.route("/")
def home():
    response = request_server("index")
    sugeridos = response["sugeridos"]
    avaliados = response["avaliados"]

    return render_template(
        "index.html", host=_host(), cli=_cli(), avaliados=avaliados, sugeridos=sugeridos
    )


@app.route("/salt/<salt>/<item>")
def salt(salt, item):
    return avaliar_render(salt, item)


@app.route("/redirect", methods=["GET"])
def redirect():
    salt = request.args.get("salt")
    item = request.args.get("item")
    return avaliar_render(salt, item)


@app.route("/like/<salt>/<item>/<relacionado>/<relacionadoitem>")
def like(salt, item, relacionado, relacionadoitem):
    avaliacao(salt, item, relacionado, relacionadoitem, LIKE)
    # return redirect(url_for('salt', salt=salt, item=item))
    return avaliar_render(salt, item)


@app.route("/dislike/<salt>/<item>/<relacionado>/<relacionadoitem>")
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

    response = request_server("avaliacao", payload)


def avaliar_render(salt, item):
    if int(salt) == 0 or int(item) == 0:
        flash("Atendimento inválido.")
        return home()
    else:
        # avaliar.executar(salt + '/' + item)
        # relacionados, severidades, tempos, pessoas, texto = avaliar.portal(salt + '/' + item)
        payload = {}
        payload["atendimento"] = salt
        payload["item"] = item

        response = request_server("avaliar", payload)

        relacionados = json.loads(response["relacionados"])
        severidades = response["severidades"]
        tempos = response["tempos"]
        pessoas = response["pessoas"]
        texto = response["texto"]

        if len(relacionados) == 0:
            flash("Atendimento inválido ou ainda não importado.")
            return home()
        else:
            return render_template(
                "salt.html",
                host=_host(),
                cli=_cli(),
                salt=salt,
                item=item,
                relacionados=relacionados,
                severidades=severidades,
                tempos=tempos,
                pessoas=pessoas,
                texto=texto,
                avaliacao=True,
            )


@app.route("/kibana", methods=["GET"])
def kibana():
    if request.headers.get("Referer") is None:
        flash("Você deve avaliar o atendimento antes da consulta!")
        return home()

    # texto = Texto()
    search = request.args.get("search")
    # search = texto.kibana(texto, search)
    search = search.replace("+", " ")
    # search = urllib.parse.quote_plus(search)
    search = '"' + search + '"'
    payload = {}
    payload["search"] = search

    cards = request_server("searchs", payload)

    search = search.replace('"', "")
    buscas = request_server("buscas")

    limit = config.elasticsearch_limit
    return render_template(
        "kibana.html",
        host=_host(),
        cli=_cli(),
        search=search,
        cards=cards["search"],
        limit=limit,
        buscas=buscas,
    )


@app.route("/curtir", methods=["POST"])
def curtir():
    avaliacao(
        request.form["salt"],
        request.form["item"],
        request.form["relacionado"],
        request.form["relacionadoitem"],
        LIKE,
    )
    return str(LIKE)
