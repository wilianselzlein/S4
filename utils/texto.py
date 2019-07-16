import re
import string
import nltk

from unicodedata import normalize

FRASES = ['data/hora',
          'servidor app',
          'versão da aplicação',
          'nome do usuário',
          'login do usuário',
          'data e hora da ocorrência',
          'descrição da salt',
          'nome e telefone do analistalocal informado pelo cliente',
          'anexo após o envio do portal',
          'local informado pelo cliente',
          'bom dia',
          'boa tarde',
          'boa noite',
          'senhores',
          'doutores',
          'doutor',
          'jpeg',
          'jpg',
          'png',
          'zip',
          'rar',
          'pdf',
          'informamos',
          'prezados',
          'prezado',

          ]

class Texto(object):

    @staticmethod
    def tratar(self, s, stemming=False):
        s = self.minusculo(s)
        s = self.RemoveURL(s)
        s = self.RemoveEmail(s)
        s = self.RemoverFrasesPadrao(s)
        s = self.RemoverUsuarios(s)
        s = self.RemoverNomes(s)
        s = self.RemoverNumeros(s)
        s = self.Pontuacao(s)
        s = self.RemoveAcentos(s)
        s = self.RemoveStopWords(s)
        s = self.normalize_text(s)
        s = self.clear_text(s)
        if stemming:
            s = self.Stemming(s)
        return s

    def clear_text(self, text):
        text = text.lower()

        text = self.re_tree_dots.sub('...', text)
        text = re.sub('\.\.\.', '', text)
        text = self.re_remove_brackets.sub('', text)
        text = self.re_changehyphen.sub('-', text)
        text = self.re_remove_html.sub(' ', text)
        text = self.re_transform_numbers.sub('0', text)
        text = self.re_transform_url.sub('url', text)
        # text = self.re_transform_emails.sub('email', text)
        text = self.re_quotes_1.sub(r'\1"', text)
        text = self.re_quotes_2.sub(r'"\1', text)
        text = self.re_quotes_3.sub('"', text)
        text = re.sub('"', '', text)
        text = re.sub('\*', '', text)
        text = self.re_dots.sub('.', text)
        text = self.re_punctuation.sub(r'\1', text)
        text = self.re_hiphen.sub(' - ', text)
        text = self.re_punkts.sub(r'\1 \2 \3', text)
        text = self.re_punkts_b.sub(r'\1 \2 \3', text)
        text = self.re_punkts_c.sub(r'\1 \2', text)
        text = self.re_doublequotes_1.sub('\"', text)
        text = self.re_doublequotes_2.sub('\'', text)
        text = self.re_trim.sub(' ', text)
        text = re.sub(r'[x]+', 'x', text)
        text = re.sub(r'[\-]+', '-', text)
        text = re.sub(r'[\*]+', '*', text)

        text = re.sub(r'[-./?$@!,":;()=\']', ' ', text)
        text = normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
        self.pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        text = self.pattern.sub('', text)

        return text.strip()

    def RemoveStopWords(self, instancia):
        instancia = instancia.lower()
        stopwords = set(nltk.corpus.stopwords.words('portuguese'))
        for letter in range(97, 123):
            stopwords.add(chr(letter))
        palavras = [i for i in instancia.split() if not i in stopwords]
        stopwords = set(nltk.corpus.stopwords.words('english'))
        palavras = " ".join(palavras)
        palavras = [i for i in palavras.split() if not i in stopwords]
        return (" ".join(palavras))

    def normalize_text(self, text):
        return normalize('NFKD', text).encode('ASCII', 'ignore').decode(
          'ASCII').lower()

    def clean_text(self, text):
        if not isinstance(text, str):
            return

        remove = ['\n', '\t', '\r', '\xa0', ':']

        for item in remove:
            text = text.replace(item, '')
        return text.strip()

    def RemoverFrasesPadrao(self, s):
        for frase in FRASES:
            s = s.replace(frase.lower(), '')
        return s

    def RemoverUsuarios(self, s):
        with open('CDUSUARIO.txt') as f:
            for cdusuario in f:
                s = s.replace(cdusuario.lower(), '__cdusuario__')
        return s

    def RemoverNomes(self, s):
        with open('NMPESSOA.txt') as f:
            for nmpessoa in f:
                s = s.replace(nmpessoa.lower(), '__nome__')
        return s

    def minusculo(self, s):
        return s.lower()

    def Stemming(self, instancia):
        stemmer = nltk.stem.RSLPStemmer()
        palavras=[]
        for w in instancia.split():
            palavras.append(stemmer.stem(w))
        return (" ".join(palavras))

    def Pontuacao(self, s):
        return re.sub(r'[\\_\+\*-./?!,":;()=#\<\>\'|]',' ',s)

    def RemoverNumeros(self, s):
        # return re.sub(r'[0123456789]',' ',s)
        return re.sub(r'[\d]+[\d\,\.\-\(\) \/:ºª\%]*', ' __num__ ', s)

    def RemoveAcentos(self, s):
        return normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII')

    def RemoveURL(self, s):
        # Código-Fonte utilizado para remoção de hashtags e URLs do corpus
        # Remove as hashtags do corpus pattern = re.compile(r'\#\w+') raw = pattern.sub('', raw)
        # Remove as URLs do corpus
        # pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        # return pattern.sub('', s)
        return re.sub(r'(https?:\/\/(?:www\d?\.|(?!www\d?))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\d?\.'
                      r'[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\d?\.|(?!www\d?))[a-zA-Z0-9]'
                      r'+\.[^\s]{2,}|www\d?\.[a-zA-Z0-9]+\.[^\s]{2,})', ' __url__ ', s)

    def RemoveEmail(self, s):
        return re.sub(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', ' __email__ ', s)

    def __init__(self):
        punctuations = re.escape('!"#%\'()*+,./:;<=>?@[\\]^_`{|}~_')
        #stop_words = [unidecode(x) for x in get_stop_words('pt')]
        # REGEX
        self.pattern = re.compile(r'^\s+|\s+$')
        self.re_remove_brackets = re.compile(r'\[.*?\]')
        self.re_remove_html = re.compile(r'<(\/|\\)?.+?>', re.UNICODE)
        self.re_transform_numbers = re.compile(r'\d', re.UNICODE)
        # self.re_transform_emails = re.compile(r'[^\s]+@[^\s]+', re.UNICODE)
        self.re_transform_url = re.compile(r'(http|https)://[^\s]+', re.UNICODE)
        #
        self.re_quotes_1 = re.compile(r"(?u)(^|\W)[‘’′`']", re.UNICODE)
        self.re_quotes_2 = re.compile(r"(?u)[‘’`′'](\W|$)", re.UNICODE)
        self.re_quotes_3 = re.compile(r'(?u)[‘’`′“”]', re.UNICODE)
        self.re_dots = re.compile(r'(?<!\.)\.\.(?!\.)', re.UNICODE)
        self.re_punctuation = re.compile(r'([,";:]){2},', re.UNICODE)
        self.re_hiphen = re.compile(r' -(?=[^\W\d_])', re.UNICODE)
        self.re_tree_dots = re.compile(u'…', re.UNICODE)
        #
        self.re_punkts = re.compile(r'(\w+)([%s])([ %s])' %
                               (punctuations, punctuations), re.UNICODE)
        self.re_punkts_b = re.compile(r'([ %s])([%s])(\w+)' %
                                 (punctuations, punctuations), re.UNICODE)
        self.re_punkts_c = re.compile(r'(\w+)([%s])$' % (punctuations), re.UNICODE)
        self.re_changehyphen = re.compile(u'–')
        self.re_doublequotes_1 = re.compile(r'(\"\")')
        self.re_doublequotes_2 = re.compile(r'(\'\')')
        self.re_trim = re.compile(r' +', re.UNICODE)

        self.remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
