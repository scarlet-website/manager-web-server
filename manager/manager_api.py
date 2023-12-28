import json
import os
from datetime import datetime
from typing import List

import requests

from db.db_consts import DBTable, ProductIDKeys
from db.db_utils import DBUtils
from objects.banner import Banner
from objects.book import Book
from objects.news_letter import NewsLetter
from utils.consts import InsertType
from utils.content_utils import ContentUtils
from utils.exceptions import UnknownInsertType


class ManagerAPI:
    _AUTH_TOKEN = os.getenv(key="AUTH_TOKEN")

    def __init__(self):
        self.db_utils = DBUtils()
        self.content_utils = ContentUtils()

    def set_db_utils_connection_if_needed(self):
        if self.db_utils.initialized:
            self.db_utils = DBUtils()

    def check_authentication_token(self, authentication_token: str) -> bool:
        return authentication_token == self._AUTH_TOKEN

    def get_product_id_key_by_insert_type(self, insert_type: str):
        return self.db_utils.get_product_id_key_by_insert_type(insert_type=insert_type)

    def extract_item_id(self, data: dict, insert_type: str) -> str:
        item_id = data[self.db_utils.get_product_id_key_by_insert_type(insert_type=insert_type)]
        return item_id

    def insert_data(self, insert_type: str, data: dict, image_data=None, parse: bool = False):
        try:
            print(f"Data to insert: `{data}`")
            table_name = self.db_utils.get_table_name_by_insert_type(insert_type=insert_type)

            if image_data:
                item_id = self.extract_item_id(data=data, insert_type=insert_type)
                file_name = self.content_utils.get_image_file_name(insert_type=insert_type, item_id=item_id)
                data.update({"ImageURL": file_name})
                self.content_utils.add_image(image_data=image_data, file_name=file_name)

            # TODO - Move to utils or other class instead of doing this in manager api
            if parse and table_name == DBTable.BOOKS.value:
                data['Info'] = self.content_utils.info_html_parser(data['Info'])

            return self.db_utils.insert_data(table_name=table_name, data=data)
        except UnknownInsertType as e:
            desc = f"Error: Unknown insert type `{insert_type}`, except: {str(e)}"
            print(desc)
            raise UnknownInsertType(desc)
        except Exception as e:
            print(f"Error inserting data")
            raise e

    def update_data(self, insert_type: str, data: dict, image_data=None):
        try:
            table_name = self.db_utils.get_table_name_by_insert_type(insert_type=insert_type)
            if image_data:
                data.update({"ImageData": image_data})

            filter_data = {ProductIDKeys.BOOKS.value: data[ProductIDKeys.BOOKS.value]}
            self.db_utils.delete_data_by_filter(table_name=table_name, filter_data=filter_data)
            return self.insert_data(insert_type=insert_type, data=data, image_data=image_data)
            # return self.db_utils.update_data(table_name=table_name, data=data)
        except UnknownInsertType as e:
            desc = f"Error: Unknown insert type `{insert_type}`, except: {str(e)}"
            print(desc)
            raise UnknownInsertType(desc)
        except Exception as e:
            print(f"Error updating data")
            raise e

    def delete_data(self, insert_type: str, data: dict):
        try:
            # Delete image
            item_id = self.extract_item_id(data=data, insert_type=insert_type)
            file_name = self.content_utils.get_image_file_name(insert_type=insert_type, item_id=item_id)
            self.content_utils.delete_image_if_exists(image_file_name=file_name)

            # Delete from db
            table_name = self.db_utils.get_table_name_by_insert_type(insert_type=insert_type)
            product_id_key = self.db_utils.get_product_id_key_by_insert_type(insert_type=insert_type)
            filter_data = {product_id_key: data[product_id_key]}
            return self.db_utils.delete_data_by_filter(table_name=table_name, filter_data=filter_data)
        except UnknownInsertType as e:
            # FIXME - handle error
            pass

    def get_books(self, parse_info: bool = None):
        self.set_db_utils_connection_if_needed()
        books = self.db_utils.get_all_table_data(table_name=DBTable.BOOKS.value, data_object_type=Book)

        # No books
        if books is None:
            return []

        # Convert to dict
        wanted_books = [book.dict() for book in books]

        # Fixing html info
        for book in wanted_books:
            if parse_info:
                book['Info'] = self.content_utils.info_html_parser(text_info=book['Info'])

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
            image_data = None
            if book['ImageURL']:
                try:
                    response = requests.get(book['ImageURL'], timeout=15)
                    if response.status_code == 200:
                        image_data = response.content
                        # book['ImageData'] = response.content
                except Exception as e:
                    print(f"Error getting image of `{book['ImageURL']}`, except: {str(e)}")

            self.insert_data(insert_type=InsertType.BOOK.value, data=book, image_data=image_data)
            print(f"{index + 1}/{len(books)}) Inserted book, book id: {book['CatalogNumber']}")

    def add_email_to_newsletter(self, email: str):
        self.set_db_utils_connection_if_needed()
        self.content_utils.check_valid_email_address(email=email)
        newsletter_object = NewsLetter(EmailAddress=email)
        email_exists = self.db_utils.exists(table_name=DBTable.NEWS_LETTERS.value, data_filter={"EmailAddress": email})
        if email_exists:
            print(f"Email `{email}` already exists")
        else:
            self.db_utils.insert_data(table_name=DBTable.NEWS_LETTERS.value, data=newsletter_object.model_dump())
            print(f"Inserted new newsletter email: `{email}`")

    def get_newsletters_emails(self):
        emails_objects: List[NewsLetter] = self.db_utils.get_all_table_data(
            table_name=DBTable.NEWS_LETTERS.value, data_object_type=NewsLetter
        )

        if not emails_objects:
            return []

        emails: List[str] = [email.EmailAddress for email in emails_objects]
        return emails

    def get_banners(self):
        self.set_db_utils_connection_if_needed()
        banners = self.db_utils.get_all_table_data(table_name=DBTable.BANNERS.value, data_object_type=Banner)

        # No banners
        if banners is None:
            return []

        # Convert to dict
        wanted_banners = [banner.dict() for banner in banners]

        # Soring banners by catalog number
        wanted_banners = sorted(wanted_banners, key=lambda x: x['banner_id'])

        return wanted_banners
