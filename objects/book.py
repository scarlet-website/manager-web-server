from typing import Any, Optional

from pydantic import BaseModel


class Book(BaseModel):
    CatalogNumber: int
    IsDigital: bool = False
    ImageURL: str = ""
    Description: str = ""
    Info: str
    UnitPrice: float
    NotRealUnitPrice: Optional[float]
    inStock: bool
    isCase: bool = False
    ImageData: Any = None
