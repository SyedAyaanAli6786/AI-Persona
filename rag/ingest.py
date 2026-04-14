#!/usr/bin/env python3
"""
RAG Ingestion Pipeline — Gemini Edition
Reads resume.txt + GitHub repos and stores embeddings in ChromaDB using Gemini embeddings.
"""
import os
import re
import sys
import json
import time
import uuid
from pathlib import Path
from typing import List, Dict

from google import genai
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import chromadb

load_dotenv()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
client = genai.Client(api_key=GOOGLE_API_KEY)
EMBED_MODEL = "gemini-embedding-001"
GITHUB_USERNAME = os.environ.get("GITHUB_USERNAME", "SyedAyaanAli6786")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
CHROMA_PERSIST_DIR = os.environ.get("CHROMA_PERSIST_DIR", "./chroma_db")

# ── Text splitter ─────────────────────────────────────────────────────────────
splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,
    chunk_overlap=60,
    length_function=len,
)

def chunk_text(text: str, source: str) -> List[Dict]:
    chunks = splitter.split_text(text)
    return [{"text": c, "source": source, "id": str(uuid.uuid4())} for c in chunks if c.strip()]

def embed_texts(texts: List[str]) -> List[List[float]]:
    """Batch embed texts using Gemini."""
    embeddings = []
    # Gemini embeddings handle batches
    BATCH = 50
    for i in range(0, len(texts), BATCH):
        batch = texts[i : i + BATCH]
        try:
            res = client.models.embed_content(
                model=EMBED_MODEL,
                contents=batch,
                config={"task_type": "RETRIEVAL_DOCUMENT"}
            )
            embeddings.extend([e.values for e in res.embeddings])
        except Exception as e:
            print(f"Embedding error: {e}")
            # Fallback to zeros if error to avoid crashing
            embeddings.extend([[0.0]*768 for _ in batch])
        time.sleep(0.5)
    return embeddings

# ── Resume ingestion ──────────────────────────────────────────────────────────
def ingest_resume(file_path: str) -> List[Dict]:
    path = Path(file_path)
    print(f"[ingest] Reading resume: {path}")
    full_text = path.read_text(encoding="utf-8")
    chunks = chunk_text(full_text, source="resume.txt")
    print(f"[ingest] Resume → {len(chunks)} chunks")
    return chunks

# ── GitHub ingestion ──────────────────────────────────────────────────────────
import requests
GH_API = "https://api.github.com"

def gh_headers() -> Dict:
    h = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return h

def fetch_repos() -> List[Dict]:
    url = f"{GH_API}/users/{GITHUB_USERNAME}/repos?per_page=100&sort=updated"
    resp = requests.get(url, headers=gh_headers(), timeout=15)
    resp.raise_for_status()
    return resp.json()

def fetch_readme(owner: str, repo: str) -> str:
    url = f"{GH_API}/repos/{owner}/{repo}/readme"
    resp = requests.get(url, headers={**gh_headers(), "Accept": "application/vnd.github.raw"}, timeout=15)
    if resp.status_code == 404: return ""
    resp.raise_for_status()
    return resp.text

def ingest_github() -> List[Dict]:
    try:
        repos = fetch_repos()
    except Exception as e:
        print(f"[ingest] Error fetching repos (possibly rate limit): {e}")
        return []
    
    chunks = []
    for repo in repos:
        if repo.get("fork"): continue
        name = repo["name"]
        print(f"[ingest] Processing repo: {name}")
        summary = f"Repository: {name}\nDescription: {repo.get('description') or ''}\nLanguage: {repo.get('language') or 'Unknown'}\nURL: {repo.get('html_url', '')}\n"
        
        try:
            readme = fetch_readme(GITHUB_USERNAME, name)
            combined = summary + "\n\n" + readme[:3000]
        except Exception as e:
            print(f"[ingest]   Failed to fetch README for {name} (rate limit?): {e}")
            combined = summary

        chunks.extend(chunk_text(combined, source=f"github:{name}"))
    return chunks

# ── Store ─────────────────────────────────────────────────────────────────────
def store_chunks(chunks: List[Dict]):
    chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    col = chroma_client.get_or_create_collection(name="ayaan_persona", metadata={"hnsw:space": "cosine"})
    
    # Clear old data
    if col.count() > 0:
        col.delete(where={"source": {"$ne": "__placeholder__"}})

    if not chunks: return

    texts = [c["text"] for c in chunks]
    ids = [c["id"] for c in chunks]
    metas = [{"source": c["source"], "text": c["text"]} for c in chunks]

    embeddings = embed_texts(texts)
    
    BATCH = 100
    for i in range(0, len(ids), BATCH):
        col.add(
            ids=ids[i:i+BATCH],
            embeddings=embeddings[i:i+BATCH],
            documents=texts[i:i+BATCH],
            metadatas=metas[i:i+BATCH]
        )
    print(f"[ingest] ✅ Stored {col.count()} vectors.")

if __name__ == "__main__":
    all_chunks = []
    res_path = Path("data/resume.txt")
    if res_path.exists():
        all_chunks.extend(ingest_resume(str(res_path)))
    if GITHUB_USERNAME:
        all_chunks.extend(ingest_github())
    store_chunks(all_chunks)
