from pydantic import BaseModel


class GetImageRequestData(BaseModel):
    insert_type: str
    item_id: str
