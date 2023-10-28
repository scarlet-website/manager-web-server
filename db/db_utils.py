import sqlite3

from db.db_consts import DBTable, CommandsFormats
from objects.book import Book
from utils.consts import InsertType
from utils.exceptions import UnknownInsertType


class DBUtils:
    __DATABASE_NAME = 'scarlet.db'
    TABLE_NAME_BY_INSET_TYPE = {
        InsertType.BOOK.value: DBTable.BOOKS.value,
        InsertType.BANNER.value: DBTable.BANNERS.value,
        InsertType.NEWS_LETTER.value: DBTable.NEWS_LETTERS.value
    }

    def __init__(self):
        try:
            self._db = sqlite3.connect(self.__DATABASE_NAME)
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

    def is_table_exists(self, table_name: str) -> bool:
        query = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        self._cursor.execute(query)
        result = self._cursor.fetchone()
        if result:
            return True
        else:
            return False

    def create_table(self, table_name: str):
        self._cursor.execute(f"CREATE TABLE {table_name}{CommandsFormats.CREATE_TABLE_FORMAT[table_name]}")
        self._db.commit()

    def insert_data(self, table_name: str, data: dict):
        if not self.is_table_exists(table_name=table_name):
            self.create_table(table_name=table_name)

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        values = tuple(data.values())

        try:
            self._cursor.execute(query, values)
            self._db.commit()
            print("Data inserted successfully.")
            return data
        except sqlite3.Error as e:
            print(f"Error inserting data: {e}")
            raise e

    def get_all_table_data(self, table_name: str, data_object_type):
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
                obj = data_object_type.model_validate(data_dict)
                data.append(obj)
            return data
        except sqlite3.Error as e:
            print(f"Error retrieving data: {e}")


if __name__ == '__main__':
    db = DBUtils()
    # db.create_table(table_name="books")
    # catalog_number = random.randint(1000, 2000)
    # print(f"catalog_number: {catalog_number}")
    # example_book = Book(
    #     CatalogNumber=catalog_number,
    #     IsDigital=False,
    #     ImageURL="https://www.aaa",
    #     Description="asd ASDASD",
    #     Info="2d12d",
    #     UnitPrice="5.55555",
    #     NotRealUnitPrice=234.2342,
    #     inStock=True,
    #     isCase=True
    # )
    # db.insert_data(table_name="books", data=example_book.model_dump())
    books = db.get_all_table_data(table_name="books", data_object_type=Book)
    print(len(books))
    print(books[1].model_dump())
    print(db.is_table_exists("books"))
    print(db.is_table_exists("edges"))
