#!/usr/bin/env python3
"""
Vapi Voice Assistant Setup Script
Run once to create/update the Ayaan AI Persona assistant on Vapi.
Usage: python setup_vapi.py
"""
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv("../.env")

VAPI_API_KEY          = os.environ["VAPI_API_KEY"]
VAPI_PHONE_NUMBER_ID  = os.environ.get("VAPI_PHONE_NUMBER_ID", "")
BACKEND_URL           = os.environ.get("NEXT_PUBLIC_API_URL", "http://localhost:8000")

API_BASE = "https://api.vapi.ai"

HEADERS = {
    "Authorization": f"Bearer {VAPI_API_KEY}",
    "Content-Type": "application/json",
}

SYSTEM_PROMPT = """You are the AI persona of Syed Ayaan Ali — a skilled AI/ML engineer and full-stack developer.

RULES:
1. Only answer using information retrieved via your tools (context provided by get_context tool if available) or stated facts.
2. If you don't know, say: "I don't have that information available."
3. Never fabricate projects or experiences.
4. Be warm, natural, and conversational.
5. Handle interruptions gracefully — don't crash or repeat yourself.
6. When the recruiter shows interest in scheduling, proactively offer to book using get_slots and book_meeting tools.

BOOKING FLOW:
1. Ask for recruiter's name and email.
2. Call get_slots to fetch available times.
3. Propose top 3 slots.
4. When confirmed, call book_meeting.
5. Confirm with meeting details.
"""

ASSISTANT_CONFIG = {
    "name": "Ayaan AI Persona",
    "firstMessage": "Hi! I'm Ayaan's AI assistant. I can answer questions about his background, projects, and skills — and help schedule an interview if you're interested.",
    "model": {
        "provider": "openai",
        "model": "gpt-4o",
        "temperature": 0.4,
        "systemPrompt": SYSTEM_PROMPT,
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "get_slots",
                    "description": "Fetch available interview slots from Ayaan's calendar.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "days_ahead": {"type": "integer", "description": "Check availability (default 7).", "default": 7}
                        },
                        "required": [],
                    },
                },
                "server": {"url": f"{BACKEND_URL}/vapi/webhook"},
            },
            {
                "type": "function",
                "function": {
                    "name": "book_meeting",
                    "description": "Book an interview meeting on Ayaan's calendar.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name":       {"type": "string", "description": "Name"},
                            "email":      {"type": "string", "description": "Email"},
                            "start_time": {"type": "string", "description": "ISO time"},
                        },
                        "required": ["name", "email", "start_time"],
                    },
                },
                "server": {"url": f"{BACKEND_URL}/vapi/webhook"},
            },
        ],
    },
}


def create_or_update_assistant() -> dict:
    # Check if assistant already exists via ID from env or by name
    assistant_id = os.environ.get("VAPI_ASSISTANT_ID")
    
    if assistant_id:
        print(f"[vapi] Updating assistant from VAPI_ASSISTANT_ID: {assistant_id}")
        r = requests.patch(f"{API_BASE}/assistant/{assistant_id}", json=ASSISTANT_CONFIG, headers=HEADERS)
    else:
        # Fallback to name-based lookup
        resp = requests.get(f"{API_BASE}/assistant", headers=HEADERS)
        resp.raise_for_status()
        assistants = resp.json() if isinstance(resp.json(), list) else resp.json().get("data", [])
        existing = next((a for a in assistants if a.get("name") == "Ayaan AI Persona"), None)

        if existing:
            assistant_id = existing["id"]
            print(f"[vapi] Updating existing assistant by name: {assistant_id}")
            r = requests.patch(f"{API_BASE}/assistant/{assistant_id}", json=ASSISTANT_CONFIG, headers=HEADERS)
        else:
            print("[vapi] Creating new assistant...")
            r = requests.post(f"{API_BASE}/assistant", json=ASSISTANT_CONFIG, headers=HEADERS)

    if r.status_code >= 400:
        print(f"[vapi] Error response: {r.text}")
    r.raise_for_status()
    assistant = r.json()
    print(f"[vapi] ✅ Assistant ID: {assistant['id']}")
    return assistant


def attach_phone_number(assistant_id: str):
    if not VAPI_PHONE_NUMBER_ID:
        print("[vapi] VAPI_PHONE_NUMBER_ID not set — skipping phone attachment.")
        return

    payload = {"assistantId": assistant_id}
    r = requests.patch(f"{API_BASE}/phone-number/{VAPI_PHONE_NUMBER_ID}", json=payload, headers=HEADERS)
    r.raise_for_status()
    phone = r.json()
    print(f"[vapi] ✅ Phone number attached: {phone.get('number', VAPI_PHONE_NUMBER_ID)}")


if __name__ == "__main__":
    print("=== Vapi Assistant Setup ===")
    assistant = create_or_update_assistant()

    # Save config for reference
    with open("assistant_config.json", "w") as f:
        json.dump(assistant, f, indent=2)
    print("[vapi] Config saved to assistant_config.json")

    attach_phone_number(assistant["id"])

    print("\n✅ Setup complete!")
    print(f"   Assistant ID: {assistant['id']}")
    print(f"   Name: {assistant['name']}")
    print(f"\nAdd to your .env:")
    print(f"   VAPI_ASSISTANT_ID={assistant['id']}")
