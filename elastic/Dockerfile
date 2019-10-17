FROM ubuntu:18.04


RUN apt-get update && apt-get install -y wget

RUN useradd -ms /bin/bash elastic

USER elastic
WORKDIR /home/elastic

RUN wget -q https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.4.0-linux-x86_64.tar.gz

RUN tar -zxvf elasticsearch-7.4.0-linux-x86_64.tar.gz

EXPOSE 9200:9200

EXPOSE 9300:9200

ENTRYPOINT elasticsearch-7.4.0/bin/elasticsearch

