FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    AETHERAI_OPEN_BROWSER=0

WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt \
    && playwright install --with-deps chromium

COPY . .
RUN mkdir -p workspace/uploads workspace/downloads workspace/chromadb_store
EXPOSE 8000
CMD ["python", "main.py"]
