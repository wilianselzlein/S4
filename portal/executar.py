import avaliar
from flask import Flask, render_template, redirect, url_for
from portal.postgres import Postgres

#app = Flask(__name__, static_url_path='/static')
app = Flask(__name__, static_url_path='/static')

LIKE = True
DISLIKE = False

# if __name__ == "__main__":
#     app.run()

def executar():
    app.run(host="0.0.0.0")
    #app.run(debug=True) #erro

@app.route('/')
def home():
    # return "S4"
    # return render_template('E:\\OneDrive\\OneDrive - Softplan\\Python\\S4\\S4\\templates\\index.html');
    return render_template('index.html')

@app.route('/salt/<salt>/<item>')
def salt(salt, item):
    avaliar.executar(salt + '/' + item)
    relacionados, severidades, tempos, pessoas = avaliar.portal(salt + '/' + item)

    return render_template('salt.html', salt=salt, item=item, relacionados=relacionados, severidades=severidades,
                           tempos=tempos, pessoas=pessoas)

@app.route('/like/<salt>/<item>/<algoritmo>/<relacionado>/<relacionadoitem>')
def like(salt, item, algoritmo, relacionado, relacionadoitem):
    avaliacao(salt, item, algoritmo, relacionado, relacionadoitem, LIKE)
    return redirect(url_for('salt', salt=salt, item=item))

@app.route('/dislike/<salt>/<item>/<algoritmo>/<relacionado>/<relacionadoitem>')
def dislike(salt, item, algoritmo, relacionado, relacionadoitem):
    avaliacao(salt, item, algoritmo, relacionado, relacionadoitem, DISLIKE)
    return redirect(url_for('salt', salt=salt, item=item))

def avaliacao(salt, item, algoritmo, relacionado, relacionadoitem, valor):
    postgres = Postgres()
    postgres.avaliacao(postgres, salt, item, algoritmo, relacionado, relacionadoitem, valor)
