# MCP UI - ממשק משתמש

ממשק משתמש מתקדם ל-Management Control Panel

## תיאור

ממשק משתמש מודרני המאפשר:
- ניהול פקודות
- תצוגת תוצאות
- היסטוריה של פעולות
- תצוגה ידידותית למשתמש

## תקן טכנולוגי

- **Framework**: React TypeScript
- **Build Tool**: Vite
- **UI Library**: Material-UI
- **State Management**: Local State
- **API Client**: Axios

## התקנה

1. התקנת התלויות:
```bash
npm install
```

2. הפעלת הממשק:
```bash
npm run dev
```

3. בניית הפרויקט:
```bash
npm run build
```

## מבנה הפרויקט

```
mcp-ui/
├── src/
│   ├── components/    # רכיבי UI
│   ├── App.tsx       # רכיב הראשי
│   └── index.tsx     # נקודה כניסה
├── public/           # קבצים_Static
└── package.json      # תלוויות
```

## שימוש

הממשק זמין ב- http://localhost:5173

## תכונות

- תצוגת פקודות
- ניהול היסטוריה
- תצוגת תוצאות
- אזהרות ושגיאות

## תרומות

תודה רבה על התרומה! אנא פתחו Issue או Pull Request עם הצעות לשיפור.

## רישיון

MIT License
