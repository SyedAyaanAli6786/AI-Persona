#!/usr/bin/env python3
"""
Chat Evaluation Script
Measures: hallucination rate, retrieval relevance, edge case handling
"""
import os
import sys
import json
import time
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv("../.env")

API_URL = os.environ.get("EVAL_API_URL", "http://localhost:8000")

# ── Test prompts ──────────────────────────────────────────────────────────────
FACTUAL_PROMPTS = [
    "What is Ayaan's educational background?",
    "What programming languages does Ayaan know?",
    "What projects has Ayaan worked on?",
    "What was Ayaan's internship experience?",
    "What AI/ML skills does Ayaan have?",
    "Tell me about his GitHub repositories.",
    "What tech stack does Ayaan prefer?",
]

HALLUCINATION_PROBES = [
    # These should return "I don't have that information available."
    ("Has Ayaan worked at Google?", "google"),
    ("Does Ayaan have a PhD?", "phd"),
    ("Has Ayaan published academic papers?", "published"),
    ("Did Ayaan work at OpenAI?", "openai"),
    ("Does Ayaan know COBOL?", "cobol"),
]

BOOKING_PROMPTS = [
    "Can I book an interview with Ayaan?",
    "What's his availability this week?",
    "I'd like to schedule a call.",
]

REFUSAL_PHRASE = "i don't have that information available"


def call_chat(message: str, history: list = []) -> dict:
    start = time.monotonic()
    resp = requests.post(
        f"{API_URL}/chat",
        json={"message": message, "history": history},
        timeout=30,
    )
    latency = time.monotonic() - start
    data = resp.json()
    data["_latency"] = latency
    return data


def cosine_sim_approx(text1: str, text2: str) -> float:
    """Very lightweight token-overlap similarity (no ML needed)."""
    t1 = set(text1.lower().split())
    t2 = set(text2.lower().split())
    if not t1 or not t2:
        return 0.0
    return len(t1 & t2) / (len(t1 | t2))


def run_eval():
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "api_url": API_URL,
        "factual": [],
        "hallucination": [],
        "booking": [],
        "summary": {},
    }

    print("=" * 60)
    print("  AI Persona Chat Evaluation")
    print("=" * 60)

    # ── 1. Factual recall ─────────────────────────────────────────────────────
    print("\n[1] Factual Recall Tests")
    retrieval_scores = []
    latencies = []
    for q in FACTUAL_PROMPTS:
        try:
            data = call_chat(q)
            reply = data.get("reply", "")
            sources = data.get("sources", [])
            latency = data["_latency"]
            latencies.append(latency)

            # Retrieval relevance: overlap between question and retrieved chunks
            rel_scores = [
                cosine_sim_approx(q, s.get("source", "") + " " + q)
                for s in sources
            ]
            avg_rel = sum(rel_scores) / len(rel_scores) if rel_scores else 0.0
            retrieval_scores.append(avg_rel)

            result = {
                "question": q,
                "reply_snippet": reply[:120],
                "n_sources": len(sources),
                "latency_s": round(latency, 3),
                "has_refusal": REFUSAL_PHRASE in reply.lower(),
            }
            results["factual"].append(result)
            status = "✅" if not result["has_refusal"] and len(sources) > 0 else "⚠️"
            print(f"  {status} {q[:50]} … ({latency:.2f}s, {len(sources)} sources)")
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results["factual"].append({"question": q, "error": str(e)})

    # ── 2. Hallucination probes ───────────────────────────────────────────────
    print("\n[2] Hallucination Probes")
    hallucination_pass = 0
    for q, keyword in HALLUCINATION_PROBES:
        try:
            data = call_chat(q)
            reply = data.get("reply", "").lower()
            correctly_refused = REFUSAL_PHRASE in reply
            hallucinated = keyword in reply and not correctly_refused
            if correctly_refused:
                hallucination_pass += 1
            result = {
                "question": q,
                "keyword": keyword,
                "correctly_refused": correctly_refused,
                "hallucinated": hallucinated,
                "reply_snippet": reply[:120],
            }
            results["hallucination"].append(result)
            icon = "✅" if correctly_refused else ("❌ HALLUCINATED" if hallucinated else "⚠️ partial")
            print(f"  {icon} — {q[:55]}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results["hallucination"].append({"question": q, "error": str(e)})

    hallucination_rate = 1 - (hallucination_pass / len(HALLUCINATION_PROBES))

    # ── 3. Booking flow ───────────────────────────────────────────────────────
    print("\n[3] Booking Intent Detection")
    for q in BOOKING_PROMPTS:
        try:
            data = call_chat(q)
            reply = data.get("reply", "")
            mentions_booking = any(
                w in reply.lower() for w in ["slot", "book", "schedule", "interview", "available", "calendar"]
            )
            results["booking"].append({
                "question": q,
                "reply_snippet": reply[:120],
                "mentions_booking": mentions_booking,
            })
            icon = "✅" if mentions_booking else "⚠️"
            print(f"  {icon} {q[:55]}")
        except Exception as e:
            print(f"  ❌ Error: {e}")

    # ── Summary ───────────────────────────────────────────────────────────────
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    avg_retrieval = sum(retrieval_scores) / len(retrieval_scores) if retrieval_scores else 0
    factual_with_sources = sum(1 for r in results["factual"] if r.get("n_sources", 0) > 0)

    results["summary"] = {
        "hallucination_rate": round(hallucination_rate, 3),
        "hallucination_pass_rate": round(1 - hallucination_rate, 3),
        "avg_response_latency_s": round(avg_latency, 3),
        "avg_retrieval_relevance": round(avg_retrieval, 3),
        "factual_queries_with_sources": factual_with_sources,
        "total_factual_queries": len(FACTUAL_PROMPTS),
    }

    print("\n" + "=" * 60)
    print("  RESULTS SUMMARY")
    print("=" * 60)
    for k, v in results["summary"].items():
        print(f"  {k:40s}: {v}")

    # Save report
    out_path = "eval_chat_results.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Full results saved to: {out_path}")


if __name__ == "__main__":
    run_eval()
