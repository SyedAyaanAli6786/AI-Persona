"""
RAG Retriever — Gemini Edition
"""
import os
from pathlib import Path
from typing import List, Dict
from google import genai
import chromadb
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent
load_dotenv(dotenv_path=ROOT / ".env")

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
client = genai.Client(api_key=GOOGLE_API_KEY)
CHROMA_PERSIST_DIR = os.environ.get("CHROMA_PERSIST_DIR", str(ROOT / "chroma_db"))
EMBED_MODEL = "gemini-embedding-001"

def retrieve(query: str, n_results: int = 5) -> List[Dict]:
    """Embed query via Gemini and search ChromaDB."""
    try:
        # 1. Embed query
        res = client.models.embed_content(
            model=EMBED_MODEL,
            contents=[query],
            config={"task_type": "RETRIEVAL_QUERY"}
        )
        query_embedding = res.embeddings[0].values

        # 2. Search Chroma
        chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        col = chroma_client.get_or_create_collection(name="ayaan_persona")
        
        results = col.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
        )

        # 3. Format
        chunks = []
        if results["documents"] and results["documents"][0]:
            for i in range(len(results["documents"][0])):
                chunks.append({
                    "text": results["documents"][0][i],
                    "source": results["metadatas"][0][i]["source"],
                    "distance": results["distances"][0][i] if results["distances"] else 0,
                })
        return chunks
    except Exception as e:
        print(f"Retrieval error: {e}")
        return []
