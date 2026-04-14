"""
Cal.com API v2 client — fetch slots and create bookings.
"""
import os
from datetime import datetime, timedelta, timezone
from typing import List, Dict

import httpx
from dotenv import load_dotenv

load_dotenv()

CAL_API_KEY      = os.environ.get("CAL_API_KEY", "")
CAL_EVENT_TYPE_ID = os.environ.get("CAL_EVENT_TYPE_ID", "")
CAL_USERNAME     = os.environ.get("CAL_USERNAME", "")

CAL_BASE = "https://api.cal.com/v2"


def _headers() -> Dict:
    return {
        "Authorization": f"Bearer {CAL_API_KEY}",
        "cal-api-version": "2024-08-13",
        "Content-Type": "application/json",
    }


async def get_available_slots(days_ahead: int = 7) -> List[Dict]:
    """Fetch available booking slots from Cal.com for the next `days_ahead` days."""
    if not CAL_API_KEY or not CAL_EVENT_TYPE_ID:
        # Return mock slots if cal.com not configured
        return _mock_slots(days_ahead)

    now = datetime.now(timezone.utc)
    start_time = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time   = (now + timedelta(days=days_ahead)).strftime("%Y-%m-%dT%H:%M:%SZ")

    params = {
        "eventTypeId": CAL_EVENT_TYPE_ID,
        "startTime": start_time,
        "endTime": end_time,
    }
    if CAL_USERNAME:
        params["username"] = CAL_USERNAME

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{CAL_BASE}/slots/available", params=params, headers=_headers())
        resp.raise_for_status()
        data = resp.json()

    slots = []
    for date_key, date_slots in data.get("data", {}).get("slots", {}).items():
        for s in date_slots:
            slots.append({
                "start": s["time"],
                "label": _format_slot(s["time"]),
            })
    return slots[:10]  # return at most 10


async def book_interview(name: str, email: str, start_time: str) -> Dict:
    """Create a booking on Cal.com."""
    if not CAL_API_KEY or not CAL_EVENT_TYPE_ID:
        return _mock_booking(name, email, start_time)

    payload = {
        "eventTypeId": int(CAL_EVENT_TYPE_ID),
        "start": start_time,
        "attendee": {
            "name": name,
            "email": email,
            "timeZone": "UTC",
        },
    }

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(f"{CAL_BASE}/bookings", json=payload, headers=_headers())
        resp.raise_for_status()
        data = resp.json()

    booking_data = data.get("data", data)
    return {
        "id": booking_data.get("id"),
        "uid": booking_data.get("uid"),
        "status": booking_data.get("status"),
        "start": booking_data.get("start"),
        "meetingUrl": booking_data.get("meetingUrl"),
        "title": booking_data.get("title"),
    }


# ── Mock helpers (when Cal.com keys not configured) ───────────────────────────
def _mock_slots(days_ahead: int) -> List[Dict]:
    slots = []
    base = datetime.now(timezone.utc).replace(hour=10, minute=0, second=0, microsecond=0)
    for d in range(1, min(days_ahead + 1, 5)):
        for h in [10, 14, 16]:
            slot_dt = (base + timedelta(days=d)).replace(hour=h)
            iso = slot_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            slots.append({"start": iso, "label": _format_slot(iso)})
    return slots[:6]


def _mock_booking(name: str, email: str, start_time: str) -> Dict:
    return {
        "id": "mock-123",
        "uid": "mock-uid-abc",
        "status": "ACCEPTED",
        "start": start_time,
        "meetingUrl": "https://meet.google.com/mock-link",
        "title": f"Interview with {name}",
        "note": "⚠️ Mock booking — Cal.com not configured",
    }


def _format_slot(iso: str) -> str:
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%A, %b %d at %I:%M %p UTC")
    except Exception:
        return iso
