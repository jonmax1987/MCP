from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

app = FastAPI()

# מבנה הנתונים של רשומה
class Item(BaseModel):
    id: Optional[str] = None
    name: str
    status: Optional[str] = "active"

# מסד נתונים זמני בזיכרון
db = []

# יצירת רשומה חדשה
@app.post("/add")
def add_item(item: Item):
    item.id = str(uuid.uuid4())
    db.append(item)
    return {"message": "Item added", "item": item}

# עדכון רשומה לפי ID
@app.put("/update")
def update_item(updated_item: Item):
    for item in db:
        if item.id == updated_item.id:
            item.name = updated_item.name
            item.status = updated_item.status
            return {"message": "Item updated", "item": item}
    raise HTTPException(status_code=404, detail="Item not found")

# מחיקת רשומה לפי ID
@app.delete("/delete")
def delete_item(item_id: str):
    global db
    db = [item for item in db if item.id != item_id]
    return {"message": f"Item {item_id} deleted"}

# שליפת כל הרשומות
@app.get("/items", response_model=List[Item])
def get_items():
    return db

# שינוי סטטוס בלבד
@app.patch("/status")
def change_status(item_id: str, status: str):
    for item in db:
        if item.id == item_id:
            item.status = status
            return {"message": "Status updated", "item": item}
    raise HTTPException(status_code=404, detail="Item not found")
