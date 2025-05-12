# MCP - Management Control Panel

מערכת ניהול מתקדמת שמשלבת FastAPI ו-React TypeScript

## תיאור

מערכת MCP היא פלטפורמת ניהול מתקדמת שמספקת:
- API FastAPI
- ממשק משתמש מודרני ב-React TypeScript
- מסד נתונים SQLite
- ניהול היסטוריה של פעולות

## תקן טכנולוגי

- **Backend**: FastAPI
- **Frontend**: React TypeScript + Vite
- **Database**: SQLite
- **Dependencies**: fastapi, uvicorn, httpx

## התקנה

1. התקנת התלויות:
```bash
pip install -r requirements.txt
```

2. הפעלת השרת:
```bash
uvicorn main:app --reload
```

3. הפעלת הממשק:
```bash
cd mcp-ui
npm install
npm run dev
```

## מבנה הפרויקט

```
MCP/
├── mcp-ui/           # Frontend React TypeScript
├── main.py          # FastAPI Server
├── mcp_llm_server.py # LLM Server
├── requirements.txt  # Python Dependencies
└── .gitignore       # Git Ignore Rules
```

## שימוש

1. השרת זמין ב- http://localhost:8000
2. הממשק זמין ב- http://localhost:5173

## תרומות

תודה רבה על התרומה! אנא פתחו Issue או Pull Request עם הצעות לשיפור.

## רישיון

MIT License
