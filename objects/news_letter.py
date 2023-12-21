from datetime import datetime

from pydantic import BaseModel


class NewsLetter(BaseModel):
    EmailAddress: str
