FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY rag/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY rag/ingest.py rag/retriever.py ./

# data/ and chroma_db/ mounted via docker-compose volumes
CMD ["python", "ingest.py"]
