# S⁴ - Sugestão de Solução de Salts na Sustentação

Ferramenta que orienta o colaborador sobre os passos mais eficazes para a resolução dos atendimentos.​

## Tecnologias 

- Python3
- PostgreSQL
- Docker
- Kibana
- ElasticSearch
- Rabbit

## Inteligência Computacional
-  O  foi desenvolvida para realizar classificação do atendimentos a partir dos dados do processo e do texto extraído de outros atendimentos. 
    A classificação é feita através de modelos de machine learning

## Instalação
- https://docs.docker.com/install/linux/docker-ce/ubuntu/
- sudo docker-compose up --build
- https://tecadmin.net/install-rabbitmq-server-on-ubuntu/


## Utilização

O serviço será executado na porta **5000**

> http://localhost:5000/S4

> http://localhost:5000/S4/salt/232580/1

> http://127.0.0.1:8081/api/v1/doc/

### Montando o ambiente de desenvolvimento

Clonar o projeto no [repositório](https://github.com/wilianselzlein/S4.git) e entrar no mesmo.

```bash
git clone https://github.com/wilianselzlein/S4.git && cd $_
```

Você deve instalar o **pyenv** ou  **virtualenvwrapper**

Nesse [link](https://github.com/pyenv/pyenv-installer#installation--update--uninstallation) você pode encontrar dicas de como instalar o **pyenv**.

Nesse [link](https://virtualenvwrapper.readthedocs.io/en/latest/) você pode encontar dicas de como instalar o **virtualenvwrapper**

Após instalação e ativação de sua **env** execute o comando **make install** para instalar todas as dependencias do projeto.

```bash
sudo apt-get install python-psycopg2
sudo apt-get install libpq-dev
pip3 install psycopg2

sudo pip3 install --upgrade pip
sudo pip3 install -U PyYAML OU sudo pip3 install --ignore-installed PyYAML

sudo python3 -m nltk.downloader punkt
sudo python3 -m nltk.downloader stopwords
sudo python3 -m nltk.downloader words
sudo python3 -m spacy download pt

sysctl -w vm.max_map_count=262144

$ make install
```
A base de dados o própio app cria, bastando apenas ter um postgreSQL instalado.

Para execução:

```bash
export FLASK_DEBUG=1
ssh -R s4.serveo.net:80:localhost:5000 serveo.net
~/S4$  python3 __main__.py --portal
```

## Estilo de Código

Para garantir um estilo de código padronizado, usamos o formatador [black](https://github.com/python/black). Se o seu código não estiver formatado corretamente, a pipeline do Git CI não será finalizada, impedindo o **merge** das alterações.

Se você quiser formatar automaticamente seu código em cada commit, você pode usar [pré-commit](https://pre-commit.com/). Basta instalá-lo via **pip install pre-commit** executar pre-commit install na pasta raiz. Isso adicionará um gancho ao repositório, que reformata os arquivos em cada confirmação.

Se você quiser configurá-lo manualmente, instale via **pip install black**. Para reformatar arquivos, execute

```bash
black .
```
