# AI Persona of Syed Ayaan Ali

> An AI version of Ayaan that recruiters can **call** or **chat** with to learn about him and book an interview — fully RAG-grounded on his real resume and GitHub.

![Architecture](./architecture_diagram_1776111859458.png)

---

## Features

| Feature | Details |
|---------|---------|
| 💬 **Chat Interface** | Next.js UI, **Gemini 1.5 Flash**, RAG-grounded answers |
| 📞 **Voice Agent** | Vapi phone number, Deepgram STT, ElevenLabs TTS |
| 🧠 **RAG Pipeline** | resume.txt + GitHub repos → ChromaDB embeddings (**Gemini**) |
| 📅 **Calendar Booking** | Cal.com API — real slots, real bookings |
| 📊 **Eval Suite** | Automated hallucination, latency, and completion metrics |

---

## Quick Start (Local)

### 1. Prerequisites
- Node.js & Python 3.12
- Gemini API Key (`GOOGLE_API_KEY`)
- Cal.com & Vapi credentials

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and fill in GOOGLE_API_KEY, GITHUB_TOKEN, etc.
```

### 3. Launch Services

**Backend & RAG Ingestion:**
```bash
cd backend
pip install -r requirements.txt
# Run ingestion once to populate 63 vectors
PYTHONPATH=.. python3 ../rag/ingest.py
# Start API
uvicorn main:app --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev # Running at localhost:3000
```

---

## Voice Agent Setup

**Phone Number**: [+1 984 206 1807](tel:+19842061807)

The agent is live. To enable **calendar booking via voice** during local dev:
1. Run `ngrok http 8000`
2. Update `BACKEND_URL` in `.env` to the ngrok host
3. Sync Vapi: `cd voice && python setup_vapi.py`

---

## Evaluation

See [eval/eval_report.md](eval/eval_report.md) for the 1-page report covering:
- **Hallucination Rate**: 0%
- **Voice Response Latency**: 1.4s
- **Retrieval Quality**: grounded on 63 RAG vectors

---

## Tech Stack

- **LLM**: Google Gemini 1.5 Flash
- **Embeddings**: Gemini `gemini-embedding-001`
- **Vector DB**: ChromaDB
- **Backend**: Python FastAPI
- **Frontend**: Next.js 14 + Tailwind CSS
- **Voice**: Vapi
- **Calendar**: Cal.com
