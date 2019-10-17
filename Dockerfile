FROM python:3.7-stretch

RUN apt-get update && apt-get install git

ARG DB2SAC_URI="172.23.1.2"
ENV DB2SAC_URI=$DB2SAC_URI

ARG CLI="pj"
ENV CLI=$CLI

WORKDIR /root
COPY ./ ./

RUN pip install -qr ./requirements.txt

RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('rslp'); nltk.download('punkt');"
