import avaliar
from flask import Flask, render_template, redirect, request, flash
from portal.postgres import Postgres

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
