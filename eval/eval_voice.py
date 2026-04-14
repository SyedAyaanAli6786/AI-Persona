#!/usr/bin/env python3
"""
Voice Evaluation Script
Measures: first-response latency, task completion via Vapi call logs
"""
import os
import time
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv("../.env")

VAPI_API_KEY      = os.environ.get("VAPI_API_KEY", "")
VAPI_ASSISTANT_ID = os.environ.get("VAPI_ASSISTANT_ID", "")
PHONE_NUMBER_ID   = os.environ.get("VAPI_PHONE_NUMBER_ID", "")

VAPI_BASE = "https://api.vapi.ai"
HEADERS   = {"Authorization": f"Bearer {VAPI_API_KEY}", "Content-Type": "application/json"}


def fetch_recent_calls(limit: int = 10) -> list:
    resp = requests.get(f"{VAPI_BASE}/call?limit={limit}", headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()
    return data if isinstance(data, list) else data.get("results", [])


def analyze_call(call: dict) -> dict:
    call_id = call.get("id")
    status  = call.get("status")
    started = call.get("startedAt")
    ended   = call.get("endedAt")

    # First response latency (from call start to first assistant message)
    messages = call.get("messages", [])
    first_assistant_ts = None
    for m in messages:
        if m.get("role") == "assistant":
            first_assistant_ts = m.get("time")
            break

    latency_s = None
    if started and first_assistant_ts:
        try:
            from datetime import datetime as dt
            start_dt = dt.fromisoformat(started.replace("Z", "+00:00"))
            msg_dt   = dt.fromisoformat(str(first_assistant_ts).replace("Z", "+00:00"))
            latency_s = (msg_dt - start_dt).total_seconds()
        except Exception:
            pass

    # Task completion: did a booking happen?
    tool_calls = [m for m in messages if m.get("role") == "tool_call"]
    booking_completed = any("book_meeting" in str(tc) for tc in tool_calls)
    slots_fetched     = any("get_slots" in str(tc) for tc in tool_calls)

    transcript = " ".join(
        m.get("message", "") or m.get("content", "")
        for m in messages
        if m.get("role") in ("user", "assistant")
    )

    return {
        "call_id": call_id,
        "status": status,
        "first_response_latency_s": round(latency_s, 3) if latency_s else None,
        "latency_under_2s": (latency_s < 2.0) if latency_s else None,
        "slots_fetched": slots_fetched,
        "booking_completed": booking_completed,
        "message_count": len(messages),
        "transcript_snippet": transcript[:300],
    }


def run_eval():
    print("=" * 60)
    print("  AI Persona Voice Evaluation")
    print("=" * 60)

    if not VAPI_API_KEY:
        print("  ⚠️  VAPI_API_KEY not set — skipping live call analysis.")
        print("  Mock metrics shown below:\n")
        mock = {
            "note": "VAPI_API_KEY not configured — using mock data",
            "mock_latency_s": 1.4,
            "mock_task_completion_rate": 0.8,
            "mock_hallucination_rate": 0.0,
        }
        print(json.dumps(mock, indent=2))
        return

    print("\nFetching recent call logs from Vapi…")
    try:
        calls = fetch_recent_calls(limit=20)
        # Filter to our assistant
        if VAPI_ASSISTANT_ID:
            calls = [c for c in calls if c.get("assistantId") == VAPI_ASSISTANT_ID]

        print(f"  Analyzing {len(calls)} calls…\n")

        if not calls:
            print("  No calls found for this assistant yet.")
            return

        results = [analyze_call(c) for c in calls]

        latencies = [r["first_response_latency_s"] for r in results if r["first_response_latency_s"]]
        completions = [r["booking_completed"] for r in results]
        under_2s    = [r["latency_under_2s"] for r in results if r["latency_under_2s"] is not None]

        summary = {
            "total_calls_analyzed": len(results),
            "avg_first_response_latency_s": round(sum(latencies) / len(latencies), 3) if latencies else None,
            "pct_latency_under_2s": round(sum(under_2s) / len(under_2s), 3) if under_2s else None,
            "task_completion_rate": round(sum(completions) / len(completions), 3) if completions else None,
        }

        print("  PER-CALL DETAILS:")
        for r in results:
            icon = "✅" if r["booking_completed"] else "📞"
            lat  = f"{r['first_response_latency_s']}s" if r["first_response_latency_s"] else "N/A"
            print(f"  {icon} {r['call_id']} | latency={lat} | booked={r['booking_completed']}")

        print("\n  SUMMARY:")
        for k, v in summary.items():
            print(f"  {k:45s}: {v}")

        out = {"timestamp": datetime.utcnow().isoformat(), "summary": summary, "calls": results}
        with open("eval_voice_results.json", "w") as f:
            json.dump(out, f, indent=2)
        print("\n  Results saved to: eval_voice_results.json")

    except Exception as e:
        print(f"  ❌ Error fetching calls: {e}")


if __name__ == "__main__":
    run_eval()
