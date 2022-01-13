from bs4 import BeautifulSoup as bs
import requests
from queue import Queue, Empty
import concurrent.futures
from urllib.parse import urljoin, urlparse
import time
from Docs import Docs
import os

document_dict = {}
decline_list = ['filter', '?', 'jpg', 'png', 'tags', 'category']
black_list = ['[document]', 'noscript', 'header', 'html', 'meta', 'head', 'input', 'script']


class Crawler:


    def __init__(self, start_url, pages_to_crawl, flag, threads):

        self.docs_urls = []
        self.counter = 0
        self.url_dict = {}
        self.starting_url = start_url
        self.pages_to_crawl = pages_to_crawl
        self.starting_url = start_url

        # Scheme: 0 index "http or https"
        # Netloc: 1 index "in.gr" in our example
        self.root_url = '{}://{}'.format(urlparse(self.starting_url).scheme, urlparse(self.starting_url).netloc)
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=threads)
        self.scraped_pages = set([])
        self.to_crawl = Queue()
        self.to_crawl.put(self.starting_url)
        self.run()


    def parse_links(self, html):
        soup = bs(html, 'html.parser')
        links = soup.find_all('a', href=True)
        for link in links:
            url = link['href']
            # url can return category links like '/category/life/pet-stories/' without the starting_url
            # that's why we format it to 'starting_url/category/life/pet-stories/'
            if url.startswith('/') or url.startswith(self.root_url):
                url = urljoin(self.root_url, url)
                if url not in self.scraped_pages:
                    self.to_crawl.put(url)
        return

    def post_callback(self, url):
        result = url.result()
        try:
            if result.status_code == 200:
                ''' Here we add all the functionality.
                    We have successfully parse the url and we can access the links and text'''
                self.parse_links(result.text)
                self.parse_info(result.text, result.url)
        except AttributeError:
            print("Bad response")
        return

    def scrape_page(self, url):
        try:
            request = requests.get(url)
            return request
        except requests.RequestException:
            print("None")
            return None

    def parse_info(self, html, url):
        soup = bs(html, "html.parser")
        text = "{} ".format(self.counter)
        self.url_dict[self.counter] = url

        for para in soup.find_all('p'):
            text += "{} ".format(para.get_text())
        text = ' '.join(text.split())
        self.docs_urls.append(Docs(self.counter, url, text))
        text += '\n'
        self.counter += 1

        # with open("documents.txt", "a", encoding="utf-8") as f:
        #     f.write(text)
        #     f.close()



    @staticmethod
    def check_decline_characters(url):
        for i in decline_list:
            if i in url:
                return False
        return True

    def run(self):

        i = 0
        while i < self.pages_to_crawl:
            try:
                target_url = self.to_crawl.get()
                if (target_url not in self.scraped_pages) and self.check_decline_characters(target_url):
                    i += 1
                    print("Scraping URL: {} {}".format(i, target_url))
                    self.scraped_pages.add(target_url)
                    job = self.thread_pool.submit(self.scrape_page, target_url)
                    # The returning attribute from the above line goes below
                    # as attribute to the callback function
                    job.add_done_callback(self.post_callback)
                    time.sleep(0.1)

            except Empty:
                print("Links are over")
                return
            except Exception as e:
                print(e)
                continue

    def lets_continue_crawling(self, starting_url, pages_to_crawl, flag, threads):
        # Scheme: 0 index "http or https"
        # Netloc: 1 index "in.gr" in our example

        if flag == 0:
            # os.remove('documents.txt')
            self.docs_urls = []
        self.starting_url = starting_url
        self.pages_to_crawl = pages_to_crawl
        self.root_url = '{}://{}'.format(urlparse(self.starting_url).scheme, urlparse(self.starting_url).netloc)
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=threads)
        self.scraped_pages = set([])
        self.to_crawl = Queue()
        self.to_crawl.put(starting_url)
        self.run()
