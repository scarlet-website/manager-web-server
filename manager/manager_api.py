import base64
import json
import os

import requests

from db.db_consts import DBTable
from db.db_utils import DBUtils
from objects.book import Book
from utils.consts import InsertType, ContentConsts
from utils.content_utils import ContentUtils
from utils.exceptions import UnknownInsertType


class ManagerAPI:
    _AUTH_TOKEN = os.getenv(key="AUTH_TOKEN")

    def __init__(self):
        self.db_utils = DBUtils()
        self.content_utils = ContentUtils()

    def check_authentication_token(self, authentication_token: str) -> bool:
        return authentication_token == self._AUTH_TOKEN

    def insert_data(self, insert_type: str, data: dict, image_data=None, parse: bool = False):
        try:
            table_name = self.db_utils.get_table_name_by_insert_type(insert_type=insert_type)

            if image_data:
                data.update({"ImageData": image_data})

            # TODO - Move to utils or other class instead of doing this in manager api
            if parse and table_name == DBTable.BOOKS.value:
                data['Info'] = ContentUtils.info_html_parser(data['Info'])

            return self.db_utils.insert_data(table_name=table_name, data=data)
        except UnknownInsertType as e:
            # FIXME - handle error
            pass
        except Exception as e:
            # FIXME - handle error
            pass

    def update_data(self, insert_type: str, data: dict, image_data=None):
        try:
            table_name = self.db_utils.get_table_name_by_insert_type(insert_type=insert_type)
            if image_data:
                data.update({"ImageData": image_data})
            return self.db_utils.update_data(table_name=table_name, data=data)
        except UnknownInsertType as e:
            # FIXME - handle error
            pass
        except Exception as e:
            # FIXME - handle error
            pass

    def delete_data(self, insert_type: str, data: dict):
        try:
            table_name = self.db_utils.get_table_name_by_insert_type(insert_type=insert_type)
            product_id_key = self.db_utils.get_product_id_key_by_insert_type(insert_type=insert_type)
            filter_data = {product_id_key: data[product_id_key]}
            return self.db_utils.delete_data_by_filter(table_name=table_name, filter_data=filter_data)
        except UnknownInsertType as e:
            # FIXME - handle error
            pass

    def get_books(self, no_images: bool = None):
        books = self.db_utils.get_all_table_data(table_name=DBTable.BOOKS.value, data_object_type=Book)

        # Take only wanted books (not orders items)
        wanted_books = []

        # No books
        if books is None:
            return []

        # for book in books:
        #     # if book.Cat/alogNumber not in ContentConsts.ORDER_IDS:
        #     wanted_books.append(book)

        # Convert books to dict
        # if wanted_books:
        #     wanted_books = [book.dict() for book in books]

        for book in books:
            dict_book = book.dict()
            if no_images:
                dict_book['ImageData'] = None
            wanted_books.append(dict_book)

        # Fixing html info
        for book in wanted_books:
            book['Info'] = self.content_utils.info_text_parser(html_info=book['Info'])

        # Converting bytes data of image to base64 encoding
        for book in wanted_books:
            if 'ImageData' in book.keys() and book['ImageData']:
                book['ImageData'] = "data:image/jpeg;base64," + base64.b64encode(book['ImageData']).decode('utf-8')

        # Soring books by catalog number
        wanted_books = sorted(wanted_books, key=lambda x: x['CatalogNumber'])

        return wanted_books

    def reset_books_from_github(self):
        self.db_utils.delete_all_table(table_name=DBTable.BOOKS.value)
        self.db_utils.create_table(table_name=DBTable.BOOKS.value)
        self.db_utils.get_table_columns(table_name=DBTable.BOOKS.value)
        res = requests.get("https://github.com/scarlet-website/api-data/blob/main/books.json")
        data = json.loads(res.text)
        books = json.loads(''.join(data['payload']['blob']['rawLines']).strip())['books']

        for index, book in enumerate(books):
            if book['ImageURL']:
                try:
                    response = requests.get(book['ImageURL'], timeout=15)
                    if response.status_code == 200:
                        book['ImageData'] = response.content
                except Exception as e:
                    print(f"Error getting image of `{book['ImageURL']}`, except: {str(e)}")

            self.insert_data(insert_type=InsertType.BOOK.value, data=book)
            print(f"{index + 1}/{len(books)}) Inserted book, book id: {book['CatalogNumber']}")
