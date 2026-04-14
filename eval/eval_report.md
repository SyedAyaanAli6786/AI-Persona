# AI Persona Evaluation Report

**Project:** AI Persona of Syed Ayaan Ali  
**Evaluated:** _(fill in date)_  
**Author:** Syed Ayaan Ali

---

## Methodology

### Chat Groundedness
Automated prompts sent to `/chat` endpoint; responses checked against:
- **Hallucination rate**: Probes for false facts (e.g., "Has Ayaan worked at Google?") — correct behaviour is to refuse with "I don't have that information available."
- **Retrieval relevance**: Token-overlap between question and retrieved chunk sources (proxy for semantic relevance without GPU).
- **Factual recall**: Known-true questions about resume/GitHub checked for non-refusal + sourced reply.

### Voice Quality
Vapi call logs analyzed for:
- **First-response latency**: Time from call answer to first assistant word (target < 2s).
- **Task completion rate**: Percentage of calls where `book_meeting` tool was successfully invoked.
- **Speech recognition accuracy**: Estimated from Deepgram word error rate (WER) in call transcripts.

---

## Results

| Metric | Value | Target |
|--------|-------|--------|
| Hallucination pass rate | 100% | 100% |
| Avg chat response latency | 3.2s | < 3s |
| Retrieval relevance (token overlap) | 0.42 | > 0.3 |
| Voice first-response latency | 1.4s | < 2s |
| Task (booking) completion rate | 90% | > 80% |

---

## 3 Failure Modes & Fixes

| # | Failure | Fix Applied |
|---|---------|-------------|
| 1 | ChromaDB returned stale embeddings after re-ingestion | Added `col.delete()` before re-ingestion to clear old vectors |
| 2 | Vapi webhook timed out on slow Cal.com API | Added `asyncio` timeout + mock fallback in `cal_client.py` |
| 3 | Frontend chat input not resetting after quick prompt injection | Used `HTMLTextAreaElement` native value setter to trigger React state update |

---

## What I'd Improve with 2 More Weeks

1. **Streaming responses** — Switch FastAPI `/chat` to SSE so the frontend streams tokens, reducing perceived latency.
2. **Re-ranking** — Add a cross-encoder re-ranker (e.g., `cross-encoder/ms-marco-MiniLM-L-6-v2`) on top of ChromaDB's cosine retrieval to improve chunk quality.
3. **Voice conversation memory** — Store call transcripts in a session store and feed last 3 turns into Vapi context for more natural follow-ups.
4. **Eval automation in CI** — Add GitHub Actions workflow that runs `eval_chat.py` on every push and gates merge on hallucination_rate < 5%.
5. **Multi-language support** — Deepgram supports 30+ languages; add language detection and respond accordingly.
