from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import re

app = FastAPI()

API_URL = "http://127.0.0.1:8000"

class CommandRequest(BaseModel):
    text: str

@app.post("/command")
async def process_command(cmd: CommandRequest):
    text = cmd.text.lower()

    if match := re.match(r"add item named (.+)", text):
        name = match.group(1)
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{API_URL}/add", json={"name": name})
            return {"action": "add", "response": response.json()}

    elif match := re.match(r"delete item with id (.+)", text):
        item_id = match.group(1)
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{API_URL}/delete", params={"item_id": item_id})
            return {"action": "delete", "response": response.json()}

    elif match := re.match(r"update item (.+) to name (.+)", text):
        item_id = match.group(1)
        new_name = match.group(2)
        async with httpx.AsyncClient() as client:
            response = await client.put(f"{API_URL}/update", json={"id": item_id, "name": new_name})
            return {"action": "update", "response": response.json()}

    else:
        raise HTTPException(status_code=400, detail="Unrecognized command format")
