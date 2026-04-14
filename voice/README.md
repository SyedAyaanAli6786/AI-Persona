# Voice Agent — Vapi Setup

## Prerequisites
1. A [Vapi](https://vapi.ai) account with a provisioned phone number
2. Your `.env` file with `VAPI_API_KEY` and `VAPI_PHONE_NUMBER_ID`
3. Backend running publicly (use ngrok for local dev: `ngrok http 8000`)

## Setup

```bash
cd voice
pip install requests python-dotenv
python setup_vapi.py
```

This will:
- Create (or update) the "Ayaan AI Persona" assistant on Vapi
- Attach it to your phone number
- Save the assistant config to `assistant_config.json`
- Print the `VAPI_ASSISTANT_ID` to add to your `.env`

## Architecture

```
Caller → Vapi (STT: Deepgram, TTS: ElevenLabs)
              ↓
         GPT-4o-mini (with tools)
              ↓
     /vapi/webhook (FastAPI)
              ↓
     get_slots / book_meeting (Cal.com)
```

## Local Testing with ngrok

```bash
# Terminal 1: start backend
cd backend && uvicorn main:app --reload

# Terminal 2: expose publicly
ngrok http 8000

# Copy the ngrok URL, update NEXT_PUBLIC_API_URL in .env, re-run setup_vapi.py
```

## Phone Number

After running `setup_vapi.py`, your Vapi dashboard will show the phone number.
The assistant handles:
- Introduction on call answer
- Natural conversation about Ayaan's background
- Booking via calendar tools
- Graceful interruptions
