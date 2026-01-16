# NeuroLog — Empathetic AI Companion

> **A privacy-first, multi-agent journaling assistant that listens, remembers, and responds with empathy.**

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Status](https://img.shields.io/badge/status-active-success.svg) ![Stack](https://img.shields.io/badge/stack-FastAPI%20%7C%20React%20%7C%20Gemini-orange)

---

## 📖 Overview
NeuroLog is an advanced mental wellness prototype designed to provide a safe, private space for emotional reflection. Unlike standard chatbots, it uses **long-term memory**, **psychological models** (CBT-based pattern recognition), and **encrypted storage** to build genuine rapport without compromising user privacy.

The system features a **Multi-Agent Companion Room** where users can interact with distinct, non-judgmental personas (Listener, Planner, Reflector), orchestrated in parallel to provide diverse perspectives on their thoughts.

---

## 🌟 Key Features & Technical Depth

### �️ Privacy & Trust (Phase 1)
We treat user thoughts as sensitive medical data.
- **Client-Side Embeddings**: 
  - Using `@xenova/transformers` (all-MiniLM-L6-v2), vector embeddings are generated **in the browser**. 
  - *Benefit*: The backend receives pre-computed vectors, reducing the need to process raw text on the server for indexing.
- **Encryption at Rest**: 
  - All journal entries are encrypted using **AES-GCM (Fernet)** and stored in **SQLite** (structured) and **ChromaDB** (vectors).
  - *Benefit*: Even if the database file is exfiltrated, the content is mathematically unreadable without the key.
- **Privacy Dashboard** (In Progress): 
  - A transparency hub where users can see exactly what memories are stored and perform **granular deletion** or a **full wipe**.
- **Client-Only Mode**:
  - A toggle to keep specific entries strictly local or encrypted without any AI functioning.

### 🎭 Multi-Agent Companion Room (Phase 2 & 2.5)
A unified interface (`AgentRoom.jsx`) where users communicate with multiple AI personas simultaneously.
- **Orchestrator Service**: 
  - A backend service (`orchestrator.py`) that manages the chat flow.
  - **Parallel Execution**: Uses `asyncio.gather` to query multiple Gemini instances concurrently, ensuring sub-2s latency.
  - **Memory Scoping**: Each agent has strict access boundaries defined in JSON.
    - *The Listener* sees your emotional history.
    - *The Planner* only sees the current session (to remain objective).
- **Room Memory Policy**: 
  - **User Messages**: Stored (Encrypted).
  - **Agent Replies**: **Ephemeral**. They are never stored to prevent database pollution and AI feedback loops.

### � Structured Journaling (New in Sprint 1)
- **Hierarchical Organization**:
  - **Books** (e.g., "Personal", "Work") -> **Chapters** (e.g., "January 2026") -> **Entries**.
  - **SQLAlchemy ORM**: Robust relational data storage replacing the previous flat-file system.
- **Premium UI/UX**:
  - **Dark Mode**: Fully implemented system-wide dark theme (Sprint 2.5).
  - **Sidebar Navigation**: Efficiently switch between journals and chapters.
  - **Rich Editor**: Autosaves content and manages entry history.

### 🧠 Core Intelligence (Phase 0/0.5)
- **Mood Volatility Detection**: 
  - Calculates the cosine distance between the current entry's vector and the moving average of the last 5 entries.
  - *Trigger*: If volatility score > 0.3, the system tags the entry as a "Mood Swing".
- **Cognitive Distortion Analysis**: 
  - Analyzes text for common CBT distortions (e.g., "Catastrophizing", "All-or-Nothing Thinking") and prompts the reflection agent to gently challenge them.
- **Memory Decay Algorithm**: 
  - Retrieval isn't just semantic. It weights memories by: `Relevance * (1 / (TimeDays + 1)) * EmotionalIntensity`.
- **Safety Circuit Breaker**: 
  - **Pre-Computation Check**: Regex patterns scan for self-harm/crisis keywords on the *raw input*.
  - *Action*: Immediate block. No AI inference. Returns a hardcoded crisis resource message (988).

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.10+**
- **Node.js 18+**
- **Google Gemini API Key** ([Get one here](https://aistudio.google.com/))

### 1. Backend Setup (FastAPI)
```bash
# Clone the repository
git clone https://github.com/your-username/neurolog.git
cd neurolog

# Create Virtual Environment
python -m venv venv
.\venv\Scripts\activate   # Windows PowerShell
# source venv/bin/activate # Mac/Linux

# Install Python Dependencies
pip install -r requirements.txt

# Configure Environment
# We need a secure key for encryption. Run this one-liner to generate one:
python -c "from cryptography.fernet import Fernet; print(f'ENCRYPTION_KEY={Fernet.generate_key().decode()}')" > .env
# Add your Gemini Key
echo "GEMINI_API_KEY=your_actual_key_here" >> .env
# Add Database URL
echo "DATABASE_URL=sqlite:///./journal.db" >> .env

# Run the Server
python -m uvicorn app.main:app --reload --port 8000
```
*The backend documentation will be available at http://127.0.0.1:8000/docs*

### 2. Frontend Setup (React + Vite)
```bash
cd frontend

# Install Node Dependencies
npm install

# Configure API Connection
echo "VITE_API_URL=http://localhost:8000" > .env

# Start Development Server
npm run dev
```
*Access the app at http://localhost:5173*

---

## 🛠️ Architecture Overview

| Component | Technology | Responsibility |
|-----------|------------|----------------|
| **Frontend** | React, Tailwind, Framer Motion | User Interface, Client-Side Vectors (`embeddings.js`) |
| **Backend API** | FastAPI, Uvicorn | REST Endpoints, Auth (`OAuth2`), Orchestration |
| **Logic Layer** | Python (`orchestrator.py`) | Safety Checks, Agent parellelization, Memory filtering |
| **Data Layer** | **SQLAlchemy** (New) | Relational Data (Books, Chapters, Entries) |
| **Vector Store** | ChromaDB (Local) | Vector Search, Encrypted Document Store |
| **AI Model** | Google Gemini Flash | Text Generation, Empathetic Reflection |
| **Security** | Cryptography (Fernet) | AES-GCM Encrypted Storage |

---

## 📂 Project Structure
```
NeuroLog/
├── app/
│   ├── main.py              # Application Entry Point
│   ├── orchestrator.py      # Multi-Agent Logic Manager
│   ├── database.py          # SQLAlchemy Database Setup 🆕
│   ├── models/              
│   │   └── sql.py           # SQL Data Models (Book, Chapter, Entry) 🆕
│   ├── routers/
│   │   ├── journal.py       # Journaling Endpoints 🆕
│   │   └── companion.py     # Room Endpoints 🆕
│   └── utils/
│       ├── security.py      # Encryption Logic
│       └── safety.py        # Crisis Detection Regex
├── agent_configs/
│   └── default_personas.json # Agent definitions (Prompts, Access Scopes)
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── AgentRoom.jsx       # Multi-Agent UI
    │   │   ├── BookSelector.jsx    # Journal Navigation 🆕
    │   │   ├── Editor.jsx          # Rich Text Editor 🆕
    │   │   └── PrivacyDashboard.jsx
    │   └── utils/
    │       └── journal.js       # Frontend API Client 🆕
```

---

## 🔒 Comprehensive Security Policy
1.  **Zero-Knowledge-ish**: While the server holds the key in this MVP (`.env`), the database file itself is unintelligible on disk.
2.  **Access Control**: Agents are sandboxed. The "Planner" agent physically cannot access your emotional history logs.
3.  **Ephemeral Responses**: The AI's words in the Companion Room disappear after the session. We do not train on your data or store AI generation to keep the long-term memory pure (User-only).
4.  **Right to Vanish**: The `DELETE /memories` endpoint physically removes the vector and metadata from ChromaDB.

---

## 🤝 Contributing
We welcome contributions, especially in:
- **New Personas**: Create JSON profiles in `agent_configs/`.
- **UI Themes**: Accessible themes for users with visual sensitivities.
- **Local LLM Support**: Adapting `manifest` to support Ollama/LlamaCPP.

1. Fork the repo.
2. Create feature branch (`git checkout -b feature/amazing-feature`).
3. Commit changes (`git commit -m 'Add amazing feature'`).
4. Push to branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

---

## 📜 License
MIT License. Built with ❤️ for mental wellness.
