import os
import re
import json
from typing import Any
import requests
from duckduckgo_search import DDGS
from openai import OpenAI, BadRequestError
from bs4 import BeautifulSoup

from info_bot.logger import logger, search_results_logger
from info_bot.exceptions import GenreNotExists

_CLIENT = OpenAI(api_key = os.environ["OPENAI_API_KEY"])
class Tool:
    def __init__(self,name,keys):
        self.name = name
        self._keys = keys
        self.description = self.run.__doc__.format(tool_name = self.name)
        logger.info(f"tool initialized {self.name}")

    def parse(self, json_obj):
        logger.info(f'{self.name} received respnse {json_obj}')
        dct = json.loads(json_obj)
        return [dct[res] for res in self._keys]

    def run(self, json_object) -> list[Any]:
        return self.parse(json_object)
    def __repr__(self):
        return f'{self.__class__.__name__}(name = {self.name!r}, keys = {self._keys!r})'


class Search(Tool):
    def __init__(self, name):
        super().__init__(name, ["user_query","search_string"])
        self.ddgs = DDGS()
        
    def call_llm(self, system_prompt, user_query):
        try:
            completion = _CLIENT.chat.completions.create(
                model = "gpt-4o-mini",
                messages = [
                    {"role" : "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ]
            )
        except BadRequestError:
            result = []
        else:
            result = completion.choices[0].message.content
        return result

    def run(self, json_response):
        """
        name : {tool_name}
        description: this tool helps you access internet to help user with there query.
        paramaters: this search tools expects parameters in below format:

        JSON SCHEMA:
        '{{"user_query" : "actual user query", "search_string": "search string for the search engine"}}'


        """
        user_query, search_string = super().run(json_response)
        results = self.ddgs.text(search_string, max_results = 6)
        logger.info(f"Fetched search results from duckduck_go")
        search_results_logger.info(f"Results from search_results:\n{results = !r}")
        search_results = []
        for result in results:
            response = requests.get(result["href"])
            if not response:
                logger.error(f'Failed to get response from {result["href"]}')
                continue
            
            search_results += [{"title": result['title'], "url": result["href"], "body" : response.text.strip()}]

        search_results_logger.info(f"Results after reading page\n{search_results = !r}")
        logger.info('Passing search results to llm')
        brief_llm_understanding = []
        for search_result in search_results:
            result = self.call_llm("""Your a ai assistant your only job is to extract 6 most important points from below search  dictionary in a list""",f"Search result dicts: {search_result}")
            logger.debug(f'{result = }')
            search_results_logger.info(f"LLM's understanding of task\n{result = }")
            brief_llm_understanding += [result]
        
        final_result = self.call_llm(f"""You are a helpful assistant. Use only below search engine results to answer user query.\nYour response must be atleast be 5 lines.\n=== Search engine result===\n{brief_llm_understanding }\nRespond in below schema '{{"reply": "reply to user","sources": "list of urls sources of your reply"}}'\n""",user_query)
        logger.info(f"received response from llm: {final_result}")
        return final_result

class BookInformation(Tool):
    def __init__(self, tool_name):
        super().__init__(tool_name, ["genre"])

    def run(self,json_response):
        """
        name: {tool_name}
        description: this tool helps search book store for a book depending on genre or book name.
        paramaters: this tool expects parameters in below format:

        JSON SCHEMA
        '{{"genre": "genre of the book user is asking for."}}'
        """
        genre, =  super().run(json_response)
        logger.debug(f'{genre = }')
        try:
            url = self.form_url(genre)
        except GenreNotExists as e:
            return {"reply": "book in this genre does not exist"}
        return {"reply" : {book['title']: book for book in self.book_by_genre(url)}}
        
    
    def form_url(self, genre: str):
        # https://books.toscrape.com/catalogue/category/books/romance_8/index.html
        logger.debug(f'Will fetch books with genre exists: {genre!r}')
        base_url = 'https://books.toscrape.com'
        with open('agent/tools/data/book_store.json','r') as f:
            logger.debug("reading available genres from inventory")
            books_data = json.load(f)
            logger.debug(f'{books_data = }')
        try:
            genre_url = books_data['genre'][genre]
        except KeyError:
            logger.info(f"{genre} does not exists.")
            raise GenreNotExists(genre) from None
        url = f'{base_url}/{genre_url}'
        logger.debug(f"genre url = {url}")
        return url
    
    def book_by_genre(self, url:str):
        logger.debug(f'{url = }')
        response = requests.get(url)
        soup = BeautifulSoup(response.text,features="html.parser") 
        books_list = soup.select('article.product_pod')
        for book in books_list:
            book_url = 'https://books.toscrape.com/catalogue/'+book.h3.a.attrs['href'].split('/')[-2]+'/index.html'
            yield self.get_book_details(book_url)

        if (next_page:= soup.select('ul.pager > li.next')):
            url_parts = url.split('/')
            url = '/'.join(url_parts[:-1])+f'/{next_page[0].a.attrs["href"]}'
            logger.info(f'next page exists {url = }')
            yield from self.book_by_genre(url)
        
    

    def get_book_details(self, book_url):
        logger.debug(f'book url: {book_url}')
        response = requests.get(book_url)
        soup = BeautifulSoup(response.text,features = 'html.parser')
        book_title = soup.find('div', class_ = 'product_main').h1\
              .text
        table = soup.select('table > tr')
        upc = table[0].td.text
        price = table[2].td.text[2:]
        reviews = table[-1].text
        availability = re.search(r'\d+',table[-2].td.text).group(0)
        description = soup.select('div#product_description + p')[0].text
        return {
            'upc': upc, 'title': book_title, 'price': price,
            'reviews': reviews, 'stock': availability,
            'description': description 
        }
        
        
        


            


