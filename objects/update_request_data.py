from pydantic import BaseModel

from objects.book import Book


class UpdateRequestData(BaseModel):
    token: str
    insert_type: str
    data: Book
