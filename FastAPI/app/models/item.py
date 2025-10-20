from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ItemBase(BaseModel):
    title: str
    price: float
    description: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ItemUpdate(BaseModel):
    title: Optional[str] = None #Optional은 없어도 되지만 있다면 str을 받겠다는 뜻
    price: Optional[float] = None
    description: Optional[str] = None