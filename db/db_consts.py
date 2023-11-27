from enum import Enum


class CommandsFormats:
    CREATE_TABLE_FORMAT = {
        'books':
            f'''
            (CatalogNumber INTEGER KEY, IsDigital INTEGER, ImageURL TEXT, Description TEXT, Info TEXT, UnitPrice REAL,
            NotRealUnitPrice REAL, inStock INTEGER, isCase INTEGER, ImageData BLOB)
            ''',
        'banners':
            f'''
            
            ''',
        'news_letters':
            f'''
            
            '''
    }


class DBTable(Enum):
    BOOKS = 'books'
    BANNERS = 'banners'
    NEWS_LETTERS = 'news_letters'


class ProductIDKeys(Enum):
    BOOKS = 'CatalogNumber'
