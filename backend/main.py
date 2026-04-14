"""
AI Persona — FastAPI Backend (Google Gemini 2.0 Flash)
"""
import os
import sys
import json
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv

# Add rag/ and backend/ to path so we can import local modules
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "rag"))
sys.path.insert(0, str(ROOT / "backend"))

load_dotenv(dotenv_path=ROOT / ".env")

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
client = genai.Client(api_key=GOOGLE_API_KEY)
MODEL_NAME = "gemini-flash-latest"

# Try to import real retriever; fall back to stub
try:
    from retriever import retrieve as _retrieve
    def retrieve(query: str, n_results: int = 5):
        return _retrieve(query, n_results=n_results)
except Exception as e:
    print(f"Retriever import error: {e}")
    def retrieve(query: str, n_results: int = 5):
        return []

try:
    from cal_client import get_available_slots, book_interview
except Exception as e:
    print(f"Cal client import error: {e}")
    async def get_available_slots(days_ahead: int = 7):
        return []
    async def book_interview(name: str, email: str, start_time: str):
        return {"status": "mock", "name": name, "email": email, "start_time": start_time}

app = FastAPI(title="AI Persona — Syed Ayaan Ali", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Persona system prompt ─────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are the AI persona of Syed Ayaan Ali — a Computer Science student and developer.

PERSONAL DETAILS (always accurate, use these directly):
- Full name: Syed Ayaan Ali
- Email: aliaayan6786@gmail.com
- Phone: 9430029400
- GitHub: https://github.com/SyedAyaanAli6786
- Education:
    • Scaler School of Technology, Bangalore — B.S. + M.S. in Computer Science (Jul 2023 – present)
    • BITS (Birla Institute of Technology and Science) — B.S. in Computer Science (Jul 2023 – present)
- Languages: SQL, Python, Java, JavaScript
- Frontend: React.js, HTML, CSS, Next.js, TypeScript, Tailwind CSS
- Backend: Node.js, Express.js, FastAPI, REST APIs
- Databases: PostgreSQL, MySQL
- ML/AI: NLP, Scikit-learn, Deep Learning, Time Series Analysis, Data Analysis
- Tools: Git, Prisma ORM, Linux, Docker

KEY PROJECTS:
1. Trello-style Task Management System (Next.js, TypeScript, Node.js, Prisma, PostgreSQL) — https://trello-clone-ar1i.vercel.app
2. Kindle Review Sentiment Analysis (Python, NLP, Scikit-learn)
3. Crypto Currency Data Fetcher (Python, CoinGecko API)
4. Expense Tracker (HTML, CSS, JS) — https://expense-tracker-wine-phi.vercel.app
5. AI Notes App (TypeScript, Next.js) — https://ai-notes-xi-jet.vercel.app
6. ChatBot (Python) — https://chat-bot-three-teal.vercel.app

RULES:
1. Use the CONTEXT below for additional project details and repo specifics.
2. For personal details and projects above, answer directly without needing context.
3. If asked something not in context or personal details, say: "I don't have that information handy — feel free to reach out at aliaayan6786@gmail.com"
4. Be warm, friendly, and conversational — like Ayaan himself is answering.
5. When a recruiter shows interest in hiring, proactively offer to schedule an interview.
6. Keep responses concise and focused. Use bullet points for lists.
7. Always speak in first person as Ayaan ("I built...", "my experience is...", "I'm currently studying...").

CONTEXT:
{context}"""

# ── Models ────────────────────────────────────────────────────────────────────
class Message(BaseModel):
    role: str  # "user" | "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: List[Message] = []

class BookRequest(BaseModel):
    name: str
    email: str
    start_time: str


# ── /chat ─────────────────────────────────────────────────────────────────────
@app.post("/chat")
async def chat(req: ChatRequest):
    # 1. Retrieve relevant chunks
    chunks = retrieve(req.message, n_results=5)
    context = "\n\n---\n\n".join(
        f"[Source: {c['source']}]\n{c['text']}" for c in chunks
    ) if chunks else "No additional context available."

    # 2. Build the full system prompt with context injected
    full_system = SYSTEM_PROMPT.format(context=context)

    # 3. Build contents list for Gemini
    # The new SDK uses a contents list of objects with parts
    contents = []
    # Add history
    for m in req.history[-12:]:
        # Map assistant -> model for Gemini
        role = "user" if m.role == "user" else "model"
        contents.append({"role": role, "parts": [{"text": m.content}]})
    
    # Add current message
    contents.append({"role": "user", "parts": [{"text": req.message}]})

    # 4. Call Gemini 2.0 Flash
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            config={
                "system_instruction": full_system,
                "temperature": 0.5,
            },
            contents=contents
        )
        reply = response.text
    except Exception as e:
        print(f"Gemini API error: {e}")
        raise HTTPException(status_code=502, detail=f"Gemini API error: {str(e)}")

    return {
        "reply": reply,
        "sources": [{"source": c["source"], "distance": c.get("distance", 0)} for c in chunks],
    }


# ── /slots ────────────────────────────────────────────────────────────────────
@app.get("/slots")
async def slots(days_ahead: int = 7):
    try:
        available = await get_available_slots(days_ahead=days_ahead)
        return {"slots": available}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


# ── /book ─────────────────────────────────────────────────────────────────────
@app.post("/book")
async def book(req: BookRequest):
    try:
        booking = await book_interview(
            name=req.name,
            email=req.email,
            start_time=req.start_time,
        )
        return {"booking": booking}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


# ── /vapi/webhook ─────────────────────────────────────────────────────────────
@app.post("/vapi/webhook")
async def vapi_webhook(request: Request):
    body = await request.json()
    message = body.get("message", {})
    msg_type = message.get("type")

    if msg_type == "tool-calls":
        tool_calls = message.get("toolCalls", [])
        results = []
        for tc in tool_calls:
            fn_name = tc.get("function", {}).get("name")
            fn_args_raw = tc.get("function", {}).get("arguments", "{}")
            try:
                fn_args = json.loads(fn_args_raw) if isinstance(fn_args_raw, str) else fn_args_raw
            except json.JSONDecodeError:
                fn_args = {}

            if fn_name == "get_slots":
                days = fn_args.get("days_ahead", 7)
                try:
                    slots_data = await get_available_slots(days_ahead=days)
                    result = {"slots": slots_data[:5]}
                except Exception as e:
                    result = {"error": str(e)}
            elif fn_name == "book_meeting":
                try:
                    booking = await book_interview(
                        name=fn_args.get("name", "Recruiter"),
                        email=fn_args.get("email", ""),
                        start_time=fn_args.get("start_time", ""),
                    )
                    result = {"booking": booking}
                except Exception as e:
                    result = {"error": str(e)}
            else:
                result = {"error": f"Unknown tool: {fn_name}"}

            results.append({"toolCallId": tc.get("id"), "result": json.dumps(result)})

        return JSONResponse({"results": results})

    return JSONResponse({"status": "ok"})


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL_NAME}
