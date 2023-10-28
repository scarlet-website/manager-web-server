from pydantic import BaseModel


class Banner(BaseModel):
    CatalogNumber: str
    EncodedData: str
