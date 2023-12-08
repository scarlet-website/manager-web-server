from enum import Enum


class ContentConsts:
    FIXING_CHARACTERS = {" ": " "}
    LENGTH_OF_PRODUCT_ID = 7
    ORDER_IDS = [999991, 999992, 999993]
    REPLACE_INFO_PARSER_TO_TEXT = {
        '<br>': '\n',
        '<b>': '',
        '</b>': '',
        "'": "\""
    }
    REPLACE_INFO_PARSER_TO_HTML = {
        '\n': '<br>',
        "\"": "'"
    }


class InsertType(Enum):
    BOOK = 'book'
    BANNER = 'banner'
    NEWS_LETTER = 'news_letter'
