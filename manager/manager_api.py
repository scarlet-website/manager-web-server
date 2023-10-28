import os

from db.db_consts import DBTable
from db.db_utils import DBUtils
from objects.book import Book
from utils.exceptions import UnknownInsertType


class ManagerAPI:
    _TOKEN = os.getenv(key="TOKEN")

    def __init__(self):
        self.db_utils = DBUtils()

    def check_authentication_token(self, authentication_token: str) -> bool:
        return authentication_token == self._TOKEN

    def insert_data(self, insert_type: str, data: dict, image_data=None):
        try:
            table_name = self.db_utils.get_table_name_by_insert_type(insert_type=insert_type)
            if image_data:
                data.update({"ImageData": image_data})
            return self.db_utils.insert_data(table_name=table_name, data=data)
        except UnknownInsertType as e:
            # FIXME - handle error
            pass

    def get_books(self, convert_books_do_dict: bool = False):
        books = self.db_utils.get_all_table_data(table_name=DBTable.BOOKS.value, data_object_type=Book)
        if convert_books_do_dict:
            books = [book.dict() for book in books]
        return books
