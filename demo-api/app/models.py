from pydantic import BaseModel, Field
from typing import List


class Item(BaseModel):
    id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., ge=0)


class ItemsResponse(BaseModel):
    items: List[Item]
