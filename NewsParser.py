from datetime import datetime

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class NewsParser:
    def __init__(self, start_page=1, last_page=2550):
        self.start_page = start_page
        self.last_page = last_page
        self.news_id = 0
        self.base_link = 'https://www.segodnya.ua/ua/allnews/'
        self.ua = UserAgent()
        self.data = {}
        self.news_lang = 'UA'

    def start(self):
        for current_page in range(self.start_page, self.last_page + 1):
            # link to the current page
            current_url = self.base_link + f'p{current_page}.html'
            response = self.make_request(current_url)

            content = BeautifulSoup(response.text, 'html.parser')

            # get list of news on current page
            list_of_news = content.find('div', {'class': 'st__news-list'})
            list_of_news = list_of_news.find_all('li')
            self.progress(list_of_news)

        print(self.finish())

    def progress(self, list_of_news):
        for news in list_of_news:
            if news.find('a') is not None:
                # get url for each news
                news_url = news.find('a').attrs['href']

                # get news page content
                news_info = self.make_request(news_url)
                response = BeautifulSoup(news_info.text, 'html.parser')

                # parsing news
                news_details = {}

                # title
                title = self.__get_title(response)

                # text
                text = self.__get_text(response)

                # author
                author = self.__get_author(response)

                # lang
                lang = self.news_lang

                # link
                link = news_url

                # source
                source = None

                # views
                views = None

                # likes
                likes = None

                # shares
                shares = None

                # date_published
                date_published = self.__get_pub_date(response)

                # date_parsed
                date_parsed = datetime.now().timestamp()

                # topic
                topic = None

                # tags
                tags = None

                news_details['title'] = title
                news_details['text'] = text
                news_details['author'] = author
                news_details['lang'] = lang
                news_details['link'] = link
                news_details['source'] = source
                news_details['views'] = views
                news_details['likes'] = likes
                news_details['shares'] = shares
                news_details['date_published'] = date_published
                news_details['date_parsed'] = date_parsed
                news_details['topic'] = topic
                news_details['tags'] = tags

                self.news_id += 1

                self.data[f'{self.news_id}'] = news_details

    def publish(self, news_id):
        print(self.data[f'{news_id}'])

    def finish(self):
        return 'Parsing is over!\nUse method publish() to look collected news.'

    def make_request(self, url):
        headers = {'User-Agent': self.ua.random}
        response = requests.get(url, headers)

        return response

    def __get_title(self, response):
        title = response.find('h1', {'class': 'article__header_title'})
        if title is not None:
            title = title.text.strip()

        # parsing from lifestyle section
        else:
            title = response.find('h1', {'class': 'article__title'})
            if title is not None:
                title = title.text.strip()

            # parsing title from sport.segodnya.ua
            else:
                title = response.find('div', {'class': 'content-title'})
                if title is not None:
                    title = title.text.strip()
                else:
                    title = response.find('h1', {'class': 'main-title'}).text.strip()
        return title

    def __get_text(self, response):
        text = ''
        rough_text = response.find('div', {'class': 'article__body'})
        if rough_text is not None:
            rough_text = rough_text.find_all('p', attrs={'class': ''})

        if rough_text is not None:
            for item in rough_text:
                text += item.text
        else:
            rough_text = response.find('div', {'class': 'col-lg-8 col-md-12'})
            if rough_text is not None:
                rough_text = rough_text.find_all('p', attrs={'class': ''})

                for item in rough_text:
                    text += item.text
            else:
                rough_text = response.find('article', {'class': 'article__content'})
                rough_text = rough_text.find_all('p', attrs={'class': ''})

                for item in rough_text:
                    text += item.text
        return text

    def __get_author(self, response):
        author = response.find('p', {'class': 'authors'})
        if author is None:
            author = response.find('div', {'class': 'article__author'})
            if author is not None:
                author = author.find('span').text.strip()
            else:
                author = response.find('div', {'class': 'article-content__author_name'})
                if author is not None:
                    author = author.text.strip()
        else:
            author = author.text.strip()

        if author is None:
            author = 'SEGODNYA.UA'

        return author

    def __get_pub_date(self, response):
        pub_date = response.find('p', {'class': 'time'})

        if pub_date is None:
            pub_date = response.find('time', {'class': 'article__time'})

        if pub_date is None:
            pub_date = response.find('div', {'class': 'article-content__date'})

        pub_date = pub_date.text
        return pub_date


if __name__ == '__main__':
    parser = NewsParser()
    parser.start()
