# Ekko - backend Dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 1. install Python deps
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# 2. copy source
COPY . .

EXPOSE 8000
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
