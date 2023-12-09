from typing import Optional

from pydantic import BaseModel

from objects.book import Book


class UpdateRequestData(BaseModel):
    token: Optional[str]
    insert_type: str
    data: Book
