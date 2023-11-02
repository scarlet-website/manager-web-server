from enum import Enum


class ContentConsts:
    FIXING_CHARACTERS = {" ": " "}
    LENGTH_OF_PRODUCT_ID = 7
    ORDER_IDS = [999991, 999992, 999993]


class InsertType(Enum):
    BOOK = 'book'
    BANNER = 'banner'
    NEWS_LETTER = 'news_letter'
