from pydantic import BaseModel


class Book(BaseModel):
    CatalogNumber: int
    IsDigital: bool
    ImageURL: str
    Description: str
    Info: str
    UnitPrice: float
    NotRealUnitPrice: float
    inStock: bool
    isCase: bool
    ImageData = None
