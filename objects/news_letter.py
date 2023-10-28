from datetime import datetime

from pydantic import BaseModel


class NewsLetter(BaseModel):
    email_address: str
    name: str
    register_timestamp: datetime
