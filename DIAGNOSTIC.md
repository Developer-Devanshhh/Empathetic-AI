# NeuroLog Diagnostic Checklist

Run this to diagnose issues:

## 1. Check Backend is Running
```bash
curl http://localhost:8000/health
```
Expected: `{"status":"ok","mode":"SQL-primary"}`

## 2. Check Environment Variables
The app needs `GEMINI_API_KEY` for agents to work.

Create a `.env` file in `Empathetic-AI/` with:
```
GEMINI_API_KEY=your_actual_api_key_here
```

## 3. Test Auth
```bash
# Register
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'

# Login
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'
```

Expected: You should get a token back

## 4. Test Journal Save (with token from step 3)
```bash
# Create a book
curl -X POST http://localhost:8000/api/books \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"title":"Test Book"}'
```

## 5. Check Browser Console
1. Open browser dev tools (F12)
2. Go to Console tab
3. Look for errors when:
   - Creating a chapter
   - Typing in the editor
   - Sending a message to agents

## Common Issues & Fixes

### Issue: Journals not saving
- **Cause**: Auth token not being sent
- **Fix**: Check browser localStorage has a "token" key
- **Debug**: Look for 401 errors in Network tab

### Issue: Only 2/3 agents working
- **Cause**: Missing GEMINI_API_KEY or orchestrator error
- **Fix**: Add API key to .env file and restart backend
- **Debug**: Check backend terminal for errors

### Issue: Dark mode not applying
- **Cause**: CSS classes not loaded
- **Fix**: Hard refresh browser (Ctrl+Shift+R)

### Issue: UI not updating
- **Cause**: State management bug
- **Fix**: Refresh browser after each backend restart
