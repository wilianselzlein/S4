from S4 import avaliar
from flask import Flask

app = Flask(__name__)

# if __name__ == "__main__":
#     app.run()

def executar():
    app.run()
    iniciar()


@app.route("/")
def iniciar():
    return "S4"


@app.route('/salt/<salt>/<item>')  # URL with a variable
def salt(salt, item):
    avaliar.executar(salt + '/' + item)
    return avaliar.portal(salt + '/' + item)


