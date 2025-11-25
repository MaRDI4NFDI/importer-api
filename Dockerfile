FROM python:3.13-slim as builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.13-slim

WORKDIR /app

RUN useradd -m -u 1000 appuser

COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

COPY --chown=appuser:appuser server ./server
COPY --chown=appuser:appuser wsgi.py .
COPY --chown=appuser:appuser gunicorn.conf.py .

ENV PATH=/home/appuser/.local/bin:$PATH

USER appuser

HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=2)"

EXPOSE 8000

CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:app"]