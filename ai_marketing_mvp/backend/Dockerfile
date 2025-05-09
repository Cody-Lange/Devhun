# backend/Dockerfile
FROM python:3.11-slim

# 1. system deps first (faiss needs libgomp)
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential wget libgomp1 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. copy *only* requirements first so this layer can be cached
COPY requirements.txt .

RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 3. copy the rest of the source
COPY . .

EXPOSE 8000
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
