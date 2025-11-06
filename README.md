# Empathetic AI — Journaling Assistant

A local-first, privacy-minded journaling assistant that analyzes emotion from text, stores journal entries, and returns contextual, empathetic reflections (via Google Gemini).\
Back-end: **FastAPI** (emotion model inference, Chroma storage, Gemini integration).\
Front-end: **React + Vite + Tailwind** (empathetic journal UI, login, history).

---

## Quick status (what this repo includes)

- `app/` — FastAPI backend (routes: `/health`, `/analyze_emotion`, `/journal`, `/register`, `/login`)
- `app/utils/` — emotion model loader (`emotion_infer.py`), Chroma helpers, Gemini client, auth utils
- `frontend/` — React + Vite app with `EmpatheticJournal` component and simple Login/Register UI
- `.gitignore` — excludes venv, models, node\_modules, and secrets

> **Important:** Model files, virtualenvs, and `.env` are intentionally **excluded** from the repo.\
> Do **not** commit your API keys or model weights.

---

## Table of contents

- [Prerequisites](#prerequisites)
- [Quickstart — Run locally (recommended)](#quickstart)
  - Backend (FastAPI)
  - Frontend (React + Vite)
- [Environment variables](#environment-variables)
- [Model files](#model-files)
- [API endpoints (quick)](#api-endpoints-quick)
- [Testing the stack manually (curl examples)](#curl-examples)
- [Troubleshooting & tips](#troubleshooting--tips)
- [Development workflow & Git notes](#development-workflow--git-notes)
- [Next steps / roadmap](#next-steps--roadmap)
- [License & acknowledgements](#license--acknowledgements)

---

## Prerequisites

- Python 3.11+ strongly recommended (3.10 works but some Google libs warn about EOL).
- Node.js 18+ and npm/yarn.
- Git (for source control).
- (Optional) `git-lfs` if you decide to store model weights in the repo (generally not recommended).

---

## Quickstart

### Backend (FastAPI)

1. Create and activate a virtual environment:

**Windows (PowerShell)**

```powershell
python -m venv venv
.\venv\Scripts\Activate
```

**macOS / Linux**

```bash
python -m venv venv
source venv/bin/activate
```

2. Install backend dependencies:

```bash
pip install -r requirements.txt
```

3. Add environment variables (see section below).

4. Run the backend:

```bash
uvicorn app.main:app --reload --port 8000
```

Open: `http://127.0.0.1:8000/docs` to see FastAPI Swagger UI.

---

### Frontend (React + Vite)

1. From project root:

```bash
cd frontend
npm install
```

2. Create `.env` in `frontend/` (see section below), then start:

```bash
npm run dev
```

Open browser: `http://localhost:5173`

---

## Environment variables

Create a top-level `.env` (DO NOT commit this file):

```
# root/.env
GEMINI_API_KEY=your_google_gemini_api_key_here
EMOTION_MODEL_PATH=path/to/your/local/emotion_model  # optional if default location used
```

Create `frontend/.env`:

```
VITE_API_URL=http://127.0.0.1:8000
```

> Note: `main.py` loads `.env` on startup — make sure it exists before running the server.

---

## Model files

- **Do not** commit model files (`*.safetensors`, `*.pt`, etc.). Keep them locally in `app/models/emotion_model/` or store them in cloud storage and update `EMOTION_MODEL_PATH`.
- If you *must* version models, use **Git LFS**. Preferably: keep models outside the repository and only include instructions for obtaining them.

---

## API endpoints (quick)

- `GET /health` — health check
- `POST /analyze_emotion` — body `{ "text": "..." }` → returns `{ emotion, confidence, message }`
- `POST /register` — body `{ "username","password" }` → register user
- `POST /login` — body `{ "username","password" }` → returns `access_token`
- `POST /journal` — Auth required (Bearer token). Body `{ "user_id","text" }` or (if backend pulls user from JWT) `{ "text" }` → returns `{ reply, emotion, mood_swing }`

---

## Curl examples

Analyze emotion:

```bash
curl -X POST "http://127.0.0.1:8000/analyze_emotion" \
 -H "Content-Type: application/json" \
 -d '{"text":"I feel happy today"}'
```

Register & login:

```bash
curl -X POST "http://127.0.0.1:8000/register" -H "Content-Type: application/json" -d '{"username":"alice","password":"pass"}'
curl -X POST "http://127.0.0.1:8000/login" -H "Content-Type: application/json" -d '{"username":"alice","password":"pass"}'
# copy access_token from response
```

Submit a journal (authenticated):

```bash
curl -X POST "http://127.0.0.1:8000/journal" \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer <ACCESS_TOKEN>" \
 -d '{"user_id":"alice","text":"I felt stressed but better after a walk."}'
```

---

## Troubleshooting & tips

- **500 Internal Server Error** for `/analyze_emotion` — check backend logs; likely model load issues or predict\_emotion exceptions. Add `print()` debug lines or check the model path in `EMOTION_MODEL_PATH`.
- **Gemini no reply / errors** — ensure `GEMINI_API_KEY` is present and `load_dotenv()` is called before importing the Gemini client. Check available model names if you get `NotFound` errors.
- **CORS issues** — confirm `CorsMiddleware` is configured in `main.py` (`allow_origins=["*"]` for dev).
- **GitHub push failing due to large files** — ensure `.gitignore` excludes `venv`, `app/models`, and `frontend/node_modules`. Use `git rm --cached ...` to untrack files accidentally added.
- **Frontend can't find imports like ****@/...** — use relative imports or set up Vite aliases.

---

## Development workflow & Git notes

Recommended branch workflow:

- `main` — production-ready
- `feature/*` — for features (e.g., `feature/auth-ui`)
- Create PRs and merge to `main`.

Before pushing:

```bash
git status
git add -A
git commit -m "Meaningful message"
git push
```

If you accidentally committed secrets, rotate keys immediately. To remove secrets from history, use `git filter-repo` or re-create the repo (clean start).

---

## Next steps / roadmap (ideas)

- Emotion-aware context retrieval (only bring entries with similar labels)
- Per-user timeline view in the UI (history with filters)
- Optional model hosting (S3/GCS) and dynamic model loading
- Production deployment: FastAPI → Render/Heroku/Fly; Frontend → Vercel/Netlify. Use GitHub Actions for CI.

---

## License & acknowledgements

This project is provided as-is for learning and prototyping. Add a license file if you want to publish this repository (MIT is flexible and permissive).

Third-party tools and libraries used:

- FastAPI, Uvicorn
- Transformers / PyTorch
- Google Generative AI (Gemini) SDK
- Recharts, Framer Motion, Tailwind CSS for the frontend
- Chroma (for vector storage)

---

## Contact / Help

If you need setup help, debugging tips, or automated deployment scripts, open an issue in the repo or reach out via your preferred channel.

---

Happy building — this project already does the heart of what matters: listens, remembers, and responds with empathy. Keep iterating. 🌱

