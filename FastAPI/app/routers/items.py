from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
from models.item import ItemCreate, ItemResponse, ItemUpdate

router = APIRouter(prefix="/items", tags=["items"])

fake_items_db = []
item_id_counter = 1

@router.get("/", response_model=List[ItemResponse])
async def get_items():
    return fake_items_db

@router.post("/", response_model=ItemResponse) #post는 원래 없던 것
async def create_items(item: ItemCreate):
    global item_id_counter

    new_item = {
        "id": item_id_counter,
        "title": item.title,
        "description": item.description,
        "price": item.price,
        "created_at": datetime.now()
    }

    fake_items_db.append(new_item)
    item_id_counter += 1

    return new_item

@router.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    for item in fake_items_db:
        if item["id"] == item_id:
            return item
        
    raise HTTPException(status_code=404, detail="Item not found")

@router.put("/{item_id}", response_model=ItemResponse) #put은 원래 있던 것
async def update_item(item_id: int, item_update: ItemUpdate):
    for i, item in enumerate(fake_items_db):
        if item["id"] == item_id:
            update_data = item_update.dict(exclude_unset=True)
            fake_items_db[i].update(update_data)

            return fake_items_db[i]
        
    raise HTTPException(status_code=404, detail="update_item 실패")

@router.delete("/{item_id}")
async def delete_item(item_id: int):
    for i, item in enumerate(fake_items_db):
        if item["id"] == item_id:
            delete_item = fake_items_db.pop(i)

            return {
                "message": f"item {delete_item["title"]}가 성공적으로 삭제됐습니다."
            }
        
    raise HTTPException(status_code=404, detail="Item not found")