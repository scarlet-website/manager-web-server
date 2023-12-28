import json
import sqlite3
from typing import List

from db.db_consts import DBTable, CommandsFormats, ProductIDKeys
from objects.news_letter import NewsLetter
from utils.consts import InsertType
from utils.exceptions import UnknownInsertType


class DBUtils:
    __DATABASE_NAME = 'scarlet.db'
    TABLE_NAME_BY_INSET_TYPE = {
        InsertType.BOOK.value: DBTable.BOOKS.value,
        InsertType.BANNER.value: DBTable.BANNERS.value,
        InsertType.NEWS_LETTER.value: DBTable.NEWS_LETTERS.value
    }

    PRODUCT_ID_KEY_BY_INSET_TYPE = {
        InsertType.BOOK.value: ProductIDKeys.BOOKS.value,
        InsertType.BANNER.value: ProductIDKeys.BANNERS.value
    }

    def __init__(self):
        try:
            self._db = sqlite3.connect(self.__DATABASE_NAME, check_same_thread=False)
            self._cursor = self._db.cursor()
            self.initialized = True
        except Exception as e:
            print(f"Exception while trying to connect DB, {str(e)}")
            self.initialized = False

    def close(self):
        self._db.close()

    def get_table_name_by_insert_type(self, insert_type: str) -> str:
        try:
            return self.TABLE_NAME_BY_INSET_TYPE[insert_type]
        except KeyError:
            raise UnknownInsertType(msg=f"Unknown insert type: `{insert_type}`")

    def get_product_id_key_by_insert_type(self, insert_type: str) -> str:
        try:
            return self.PRODUCT_ID_KEY_BY_INSET_TYPE[insert_type]
        except KeyError:
            raise UnknownInsertType(msg=f"Unknown insert type: `{insert_type}`")

    def is_table_exists(self, table_name: str) -> bool:
        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        self._cursor.execute(query)
        result = self._cursor.fetchone()
        if result:
            return True
        else:
            return False

    def create_table(self, table_name: str):
        if not self.is_table_exists(table_name=table_name):
            self._cursor.execute(f"CREATE TABLE {table_name}{CommandsFormats.CREATE_TABLE_FORMAT[table_name]}")
            self._db.commit()

    def get_table_columns(self, table_name: str) -> List[str]:
        self._cursor.execute(f"PRAGMA table_info({table_name})")
        columns_names = []
        columns = self._cursor.fetchall()
        for column in columns:
            column_name = column[1]
            columns_names.append(column_name)
            print(column_name)
        return columns_names

    def delete_data_by_filter(self, table_name: str, filter_data: dict) -> bool:
        where_conditions = []
        for column, value in filter_data.items():
            condition = f"{column} = ?"
            where_conditions.append(condition)

        if not where_conditions:
            print("No filter conditions specified. No rows deleted.")
            return False

        where_clause = " AND ".join(where_conditions)
        query = f"DELETE FROM {table_name} WHERE {where_clause}"

        try:
            self._cursor.execute(query, tuple(filter_data.values()))
            self._db.commit()
            print(f"{self._cursor.rowcount} row(s) deleted.")
            return True
        except sqlite3.Error as e:
            print(f"Error deleting rows: {e}")
            return False

    def insert_data(self, table_name: str, data: dict):
        print("Start db_utils insert_data")
        if not self.is_table_exists(table_name=table_name):
            self.create_table(table_name=table_name)

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        values = tuple(data.values())

        try:
            self._cursor.execute(query, values)
            self._db.commit()
            print(f"Data inserted successfully, data: {data}")
            return data
        except sqlite3.Error as e:
            print(f"Error inserting data: {e}")
            raise e

    def get_all_table_data(self, table_name: str, data_object_type):
        print(f"data_object_type: {data_object_type.__name__}")
        print(f"Initialized: {self.initialized}")
        object_keys = list(data_object_type.__annotations__.keys())
        query = f"SELECT * FROM {table_name}"
        try:
            self._cursor.execute(query)
            rows = self._cursor.fetchall()
            data = []
            for row in rows:
                data_dict = dict()
                for key, value in zip(object_keys, row):
                    data_dict[key] = value
                data.append(data_dict)

            data_objects = []
            for index, data_dict_entry in enumerate(data):
                obj = data_object_type.model_validate(data_dict_entry)
                data_objects.append(obj)

            return data_objects
        except sqlite3.Error as e:
            print(f"(get_all_table_data) Error retrieving data: {e}")
            raise e
        except Exception as e:
            print(f"Error while trying to get_all_table_data, except: {str(e)}")
            raise e

    def delete_all_table(self, table_name: str):
        if self.is_table_exists(table_name=table_name):
            self._cursor.execute(f"DELETE FROM {table_name}")
            self._db.commit()

    def export_table_to_json(self, table_name, json_file_path):
        query = f"SELECT * FROM {table_name}"

        try:
            self._cursor.execute(query)
            rows = self._cursor.fetchall()

            columns = [description[0] for description in self._cursor.description]

            data = []
            for row in rows:
                row_dict = dict(zip(columns, row))
                data.append(row_dict)

            with open(json_file_path, 'w') as json_file:
                json.dump(data, json_file, indent=2)

            print(f"Data from '{table_name}' exported to '{json_file_path}' successfully.")
        except sqlite3.Error as e:
            print(f"Error exporting data: {e}")

    @staticmethod
    def _base_model_object_valid_by_data_filter(data_filter: dict, base_model_object) -> bool:
        """
        Given a base model pydantic object and a data_filter
        if each key value exists also in the object - return true, else - falses
        :param data_filter:
        :param base_model_object:
        :return:
        """
        try:
            for key, value in data_filter.items():
                if base_model_object.model_dump()[key] != value:
                    return False
            return True
        except (KeyError, ValueError):
            return False
        except Exception as e:
            print(f"Cannot check if base model object is valid by data filter, except: {str(e)}")
            return False

    def exists(self, table_name, data_filter: dict) -> bool:
        data = self.get_all_table_data(table_name=table_name, data_object_type=NewsLetter)
        for data_obj in data:
            if self._base_model_object_valid_by_data_filter(data_filter=data_filter, base_model_object=data_obj):
                return True
        return False
