# Agentic AI Chatbot

A production-oriented agentic chatbot built incrementally.

- **Backend:** Python, FastAPI, LangGraph, LangChain, Google Gemini
- **Frontend:** Next.js (App Router), TypeScript, Tailwind CSS

> **Status: Step 1** — basic LangGraph chatbot backend + chat frontend.
> Tools, agents, RAG, memory, HITL, streaming, auth, and database come in later steps.

## Step 1 Architecture

```text
HTTP Request
    ↓
FastAPI Route  (app/api/routes/chat.py)
    ↓
Pydantic Schema  (app/schemas/chat.py)
    ↓
LangGraph  (app/graph/workflow.py)
    ↓
Chatbot Node  (app/graph/nodes.py)
    ↓
Gemini  (app/llm/model.py)
    ↓
LangGraph State  (app/graph/state.py)
    ↓
FastAPI Response
```

The graph is a single node:

```text
START → chatbot → END
```

The API route never calls Gemini directly — it always goes through LangGraph,
so tools, conditional routing, memory, and HITL can be added to the graph later
without touching the API layer.

## Folder Structure

```text
agentic-chatbot/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       └── chat.py          # POST /api/chat
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── config.py            # env-driven settings
│   │   ├── graph/
│   │   │   ├── __init__.py
│   │   │   ├── state.py             # ChatState (TypedDict)
│   │   │   ├── nodes.py             # chatbot_node
│   │   │   └── workflow.py          # build_graph + compiled graph
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   └── model.py             # Gemini model factory
│   │   └── schemas/
│   │       ├── __init__.py
│   │       └── chat.py              # ChatRequest / ChatResponse
│   ├── tests/
│   │   ├── conftest.py
│   │   └── test_graph.py
│   ├── .env                         # secrets (never committed)
│   ├── .env.example
│   └── requirements.txt
│
├── frontend/                        # Next.js chat UI (App Router + TypeScript)
│   ├── app/                         # layout.tsx, page.tsx, globals.css
│   ├── components/                  # ChatWindow, ChatInput, MessageBubble
│   ├── lib/api.ts                   # typed backend API client
│   ├── types/chat.ts                # shared chat types
│   └── .env.example                 # NEXT_PUBLIC_API_BASE_URL
│
├── .gitignore
├── README.md
└── docker-compose.yml               # filled in during the deployment step
```

## Installation

Requires Python 3.11+.

```bash
cd backend

# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

## Environment Variables

Copy the example and add your key:

```bash
cp .env.example .env
```

| Variable             | Required | Default             | Description                     |
| -------------------- | -------- | ------------------- | ------------------------------- |
| `GEMINI_API_KEY`     | yes      | —                   | Google AI Studio API key        |
| `GEMINI_MODEL_NAME`  | no       | `gemini-3.6-flash`  | Gemini model to use             |
| `GEMINI_TEMPERATURE` | no       | `0.7`               | Sampling temperature            |
| `DEBUG`              | no       | `false`             | Debug flag                      |
| `CORS_ORIGINS`       | no       | `http://localhost:3000` | Allowed browser origins (comma-separated) |

Get a key at <https://aistudio.google.com/apikey>. `.env` is git-ignored and must never be committed.

### Frontend environment variables

```bash
cd frontend
cp .env.example .env.local
```

| Variable                  | Default               | Description                    |
| ------------------------- | --------------------- | ------------------------------ |
| `NEXT_PUBLIC_API_BASE_URL`| `http://localhost:8000` | FastAPI backend base URL      |

## Run the Backend

From `backend/` (with the venv activated):

```bash
uvicorn app.main:app --reload --port 8000
```

- API docs: <http://localhost:8000/docs>
- Health check: <http://localhost:8000/health>

## Run the Frontend

In a second terminal, from `frontend/`:

```bash
npm install   # first time only
npm run dev
```

Open <http://localhost:3000> and chat. The UI calls `POST /api/chat` on the backend via `lib/api.ts`.

## Test the Workflow

Unit tests mock the LLM, so no API key or network is needed:

```bash
cd backend
python -m pytest tests/ -v
```

## Test the API

With the server running:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'
```

Example response:

```json
{
  "response": "Hello! How can I help you today?"
}
```

You can also use the interactive docs at <http://localhost:8000/docs>.
