from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import httpx
import json
from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import datetime
import uuid
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

# ========================
# 🔧 DB Configuration
# ========================
DATABASE_URL = "sqlite:///./mcp_history.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class CommandLog(Base):
    __tablename__ = "command_log"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    text = Column(Text, nullable=False)
    llm_result = Column(Text, nullable=False)
    api_result = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

# ========================
# 🌐 FastAPI Setup
# ========================
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_URL = "http://127.0.0.1:8000"
OPENROUTER_API_KEY = "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"

# ========================
# 📦 Models
# ========================
class CommandRequest(BaseModel):
    text: str

# ========================
# 📤 Utility
# ========================
def save_command_log(db: Session, text: str, llm_result: dict, api_result: dict):
    log = CommandLog(
        text=text,
        llm_result=json.dumps(llm_result, ensure_ascii=False),
        api_result=json.dumps(api_result, ensure_ascii=False),
    )
    db.add(log)
    db.commit()

# ========================
# 🤖 LLM Query
# ========================
async def query_llm(user_input: str) -> dict:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "mcp-agent/1.0"
    }

    body = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {
                "role": "system",
                "content": (
                    "אתה מתווך שמתרגם פקודות טקסטואליות לעברית לפעולות API בפורמט JSON תקני בלבד."
                    " תענה אך ורק JSON, בלי טקסט נוסף."
                    " אפשרויות פעולה: add, update, delete, retrieve."
                    " דוגמאות:\n"
                    " \"תוסיף פריט בשם גלידה\" ➜ {\"action\": \"add\", \"name\": \"גלידה\"}\n"
                    " \"מחק את הפריט עם מזהה 123\" ➜ {\"action\": \"delete\", \"id\": \"123\"}\n"
                    " \"תעדכן את הפריט עם מזהה 456 לשם חדש 'יוסי' וסטטוס 'פעיל'\" ➜ {\"action\": \"update\", \"id\": \"456\", \"name\": \"יוסי\", \"status\": \"active\"}\n"
                    " ניתן לציין שם במקום מזהה:\n"
                    " \"תעדכן את הפריט בשם 'שוקולד' לסטטוס לא פעיל\" ➜ {\"action\": \"update\", \"name\": \"שוקולד\", \"status\": \"inactive\"}\n"
                    " \"מחק את הפריט בשם קפה\" ➜ {\"action\": \"delete\", \"name\": \"קפה\"}\n"
                    " \"הצג את הפריט בשם תפוזים\" ➜ {\"action\": \"retrieve\", \"name\": \"תפוזים\"}\n"
                    " תמיד החזר JSON תקני בלבד."
                )
            },
            {"role": "user", "content": user_input}
        ]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=body)
            response.raise_for_status()
            reply = response.json()
            raw_text = reply["choices"][0]["message"]["content"]
            print("🧠 RAW LLM TEXT:\n", raw_text)
            return json.loads(raw_text)
        except Exception as err:
            raise HTTPException(status_code=500, detail=f"Failed LLM interaction: {err}")

# ========================
# 🔁 Action Dispatcher
# ========================
async def send_api_request(parsed: dict):
    async with httpx.AsyncClient() as client:
        try:
            # ID resolution by name if needed
            if parsed["action"] in ["delete", "update", "retrieve"]:
                id_missing = "id" not in parsed or not parsed["id"]
                if id_missing and "name" in parsed:
                    items = (await client.get(f"{API_URL}/items")).json()
                    match = next((item for item in items if item["name"] == parsed["name"]), None)
                    if not match:
                        return {"error": f"Item with name '{parsed['name']}' not found", "error_code": "name_not_found"}
                    parsed["id"] = match["id"]

            # Handle actions
            if parsed["action"] == "add":
                response = await client.post(f"{API_URL}/add", json={"name": parsed["name"]})

            elif parsed["action"] == "delete":
                response = await client.delete(f"{API_URL}/delete", params={"item_id": parsed["id"]})

            elif parsed["action"] == "update":
                response = await client.put(f"{API_URL}/update", json={
                    "id": parsed["id"],
                    "name": parsed.get("name", ""),
                    "status": parsed.get("status", "active")
                })

            elif parsed["action"] == "retrieve":
                items = (await client.get(f"{API_URL}/items")).json()
                match = next((item for item in items if item["id"] == parsed["id"]), None)
                return match if match else {"error": "Item not found", "error_code": "not_found"}

            else:
                return {"error": "Unsupported action", "error_code": "unsupported_action"}

            if response.status_code >= 400:
                return {"error": f"API error {response.status_code}", "details": response.text}
            return response.json()

        except Exception as e:
            print("❌ MCP Internal Error:", e)
            return {"error": str(e), "error_code": "internal_error"}

# ========================
# 📥 Endpoints
# ========================
@app.post("/command")
async def process_command(cmd: CommandRequest):
    parsed = await query_llm(cmd.text)
    result = await send_api_request(parsed)
    db = SessionLocal()
    save_command_log(db, cmd.text, parsed, result)
    db.close()
    return {"llm_result": parsed, "api_result": result}

@app.get("/history")
def get_history():
    db = SessionLocal()
    logs = db.query(CommandLog).order_by(CommandLog.timestamp.desc()).limit(20).all()
    db.close()
    return JSONResponse([
        {
            "id": log.id,
            "text": log.text,
            "llm_result": json.loads(log.llm_result),
            "api_result": json.loads(log.api_result),
            "timestamp": log.timestamp.isoformat()
        } for log in logs
    ])

@app.post("/resend/{command_id}")
async def resend_command(command_id: str):
    db = SessionLocal()
    log = db.query(CommandLog).filter(CommandLog.id == command_id).first()
    db.close()
    if not log:
        raise HTTPException(status_code=404, detail="Command not found")
    parsed = await query_llm(log.text)
    result = await send_api_request(parsed)
    db = SessionLocal()
    save_command_log(db, log.text, parsed, result)
    db.close()
    return {"original_id": command_id, "llm_result": parsed, "api_result": result, "resend": True}
