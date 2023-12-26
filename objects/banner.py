from pydantic import BaseModel


class Banner(BaseModel):
    banner_id: int
    ImageURL: str = ""
