__author__ = 'av.nikitin'

from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from natasha import (
    Segmenter,
    NewsEmbedding,
    NewsSyntaxParser,
    Doc
)

segmenter = Segmenter()
emb = NewsEmbedding()
syntax_parser = NewsSyntaxParser(emb)


class SyntaxTree:
    """

    """
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36"
    }

    @staticmethod
    def validate_url(url) -> bool:
        """
        Валидация url
        :param url: Целевой url
        :return: True, если у целевого url была определена scheme и netloc
        """

        result = urlparse(url)
        return all([result.scheme, result.netloc])

    def get(self, url: str, **request_kwargs):
        """
        :param url:
        :return:
        """

        if not url.startswith('http'):
            url = 'https://' + url

        if not self.validate_url(url):
            return {'error': 'not a valid url'}

        request_kwargs.setdefault('headers', self.HEADERS)
        request_kwargs.setdefault('allow_redirects', True)
        request_kwargs.setdefault('verify', False)

        response = requests.get(url, **request_kwargs)
        response.raise_for_status()

        result = self.parse_tree(response.text)

        return result

    @staticmethod
    def parse_syntax(sentence: str):
        """
        Получить синтаксическое дерево предложения
        :param sentence:
        :return:
        """
        result = []

        doc = Doc(sentence)
        doc.segment(segmenter)
        doc.parse_syntax(syntax_parser)

        if doc.syntax:
            for sentence in doc.syntax.tokens:
                if sentence.rel == 'nsubj':
                    result.append(sentence.text)

        return ' '.join(result)

    def parse_tree(self, html):
        """
        :param html:
        :return:
        """
        result = {'keywords': ''}

        soup = BeautifulSoup(html, features='html.parser')
        keywords = soup.find("meta", attrs={'name': 'keywords'}) or soup.find("meta", attrs={'name': 'Keywords'})

        # Мы нашли keyword
        if keywords:
            result.update({'keywords': keywords['content']})

        # Если нет - забриаем description
        else:
            description = soup.find("meta", attrs={'name': 'description'}) or \
                          soup.find("meta", attrs={'name': 'Description'})
            if description:
                # Пытаемся разобрать
                result.update({'keywords': self.parse_syntax(description['content'])})

        return result


SyntaxTree().get('https://www.sandra.lact.ru/')
