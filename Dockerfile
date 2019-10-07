FROM python:3.7-stretch

RUN apt-get update && apt-get install git

WORKDIR /root
COPY ./ ./

RUN pip install -qr ./requirements.txt

RUN python -c "import nltk; nltk.download('stopwords'); nltk.download('rslp');"