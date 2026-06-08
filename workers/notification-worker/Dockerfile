# Multi-stage Dockerfile for Notification Worker

FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*
COPY ./workers/notification-worker/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appgroup ./workers/notification-worker/src ./src
COPY --chown=appuser:appgroup ./common /common
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app:/common
USER appuser
CMD ["python", "src/worker.py"]
