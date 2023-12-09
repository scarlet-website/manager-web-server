from pydantic import BaseModel, validator


class DeleteRequestData(BaseModel):
    token: str
    insert_type: str
    item_id: str

    @validator("item_id", pre=True)
    def set_item_id(cls, value):
        print("ITEM ID VALIDATOR")
        return str(value)
