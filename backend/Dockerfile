FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install backend deps
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Install rag deps (retriever uses chromadb + openai)
COPY rag/requirements.txt ./rag/requirements.txt
RUN pip install --no-cache-dir -r rag/requirements.txt

# Copy source
COPY backend/ ./backend/
COPY rag/retriever.py ./rag/retriever.py

WORKDIR /app/backend

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
