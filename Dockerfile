FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_PATH=/data/jogo.db

WORKDIR /app

COPY requirements-runtime.txt ./
RUN pip install --no-cache-dir -r requirements-runtime.txt

RUN apt-get update \
    && apt-get install -y --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --no-create-home app \
    && mkdir /data \
    && chown app:app /data

COPY app.py db.py jogo.py ./
COPY src/ ./src/
COPY static/ ./static/
COPY docker/entrypoint.sh /usr/local/bin/entrelinhas-entrypoint
RUN sed -i 's/\r$//' /usr/local/bin/entrelinhas-entrypoint \
    && chmod +x /usr/local/bin/entrelinhas-entrypoint

USER app
EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.environ.get('PORT', '5000') + '/health', timeout=3).close()"

ENTRYPOINT ["entrelinhas-entrypoint"]
CMD ["gunicorn", "--workers", "1", "--threads", "4", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
