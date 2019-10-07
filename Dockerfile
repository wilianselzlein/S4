FROM python:3.7-stretch

RUN apt-get update && apt-get install git

ARG POSTGRE_URI="127.0.0.1"
ENV POSTGRE_URI=$POSTGRE_URI

ARG DB2SAC_URI="172.23.1.2"
ENV DB2SAC_URI=$DB2SAC_URI

WORKDIR /root
COPY ./ ./

RUN pip install -r ./requirements.txt

RUN python3 -c "import nltk; nltk.download('stopwords'); nltk.download('rslp');"

CMD python3 ./__main__.py --server && python3 ./__main__.py --portal

EXPOSE 5000
EXPOSE 8081
