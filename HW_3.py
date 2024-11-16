import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from pprint import pprint
from pymongo import MongoClient
from pymongo.errors import *

ua = UserAgent()

url = 'https://books.toscrape.com/catalogue'
headers = {"User-Agent": ua.random}
page = 1

session = requests.Session()

all_books = []
counter = 0

while True:
    response = session.get(f"{url}/page-{page}.html", headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    books = soup.find_all('article', {'class':'product_pod'})
    if not books:
        break    

    for book in books:
        book_info = {}
        book_info['_id'] = counter
        try:
            name_info = book.find('h3').findChildren()[0]
            book_info['name'] = name_info.get('title', 'N/A')
            book_info['url'] = url + "/" + name_info.get('href', '')
        except AttributeError:
            book_info['name'] = 'N/A'
            book_info['url'] = 'N/A'

        price = book.find('p', {'class': 'price_color'})
        book_info['price'] = float(price.get_text().replace('Â', '').replace('£', '')) if price else 'N/A'
        
        availability = book.find('p', {'class': 'instock availability'})
        book_info['availability'] = availability.get_text(strip=True) if availability else 'N/A'
        counter += 1

        all_books.append(book_info)

    print(f'\rОбработана страница {page}', end='')
    page += 1

client = MongoClient('localhost',27017)
db = client['books']
info_books = db.info_books

info_books.delete_many({})

try:
    info_books.insert_many(all_books)
    print("\nДанные о книгах успешно сохранены в коллекцию MongoDB.")
except BulkWriteError as bwe:
    print(f"Произошла ошибка при вставке данных: {bwe.details}")


