# syntax=docker/dockerfile:1
FROM python:3.12-slim@sha256:dddfd7e07f9d15aeeca61529320492139d21cac7f0070c00609243e51e4e0016 AS dependencies

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_PATH=/data/jogo.db

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

FROM dependencies AS backend-tests
ENV DATABASE_PATH=/tmp/test-jogo.db COVERAGE_FILE=/tmp/.coverage
COPY app.py db.py jogo.py pytest.ini ./
COPY src/ ./src/
COPY tests/ ./tests/
COPY static/ ./static/
CMD ["python", "-m", "pytest", "-p", "no:cacheprovider", "--junitxml=reports/backend/junit.xml", "--cov=app", "--cov=db", "--cov=jogo", "--cov=src", "--cov-report=term-missing", "--cov-report=xml:reports/backend/coverage.xml", "--cov-report=html:reports/backend/htmlcov"]

# Último estágio: padrão usado pelo Railway.
FROM dependencies AS runtime

RUN apt-get update \
    && apt-get install -y --no-install-recommends gosu \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --no-create-home --shell /usr/sbin/nologin app \
    && mkdir /data \
    && chown app:app /data

COPY app.py db.py jogo.py ./
COPY src/ ./src/
COPY static/ ./static/
COPY --chmod=755 docker/entrypoint.sh /usr/local/bin/entrelinhas-entrypoint
RUN sed -i 's/\r$//' /usr/local/bin/entrelinhas-entrypoint

USER app
EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.environ.get('PORT', '5000') + '/health', timeout=3).close()"

ENTRYPOINT ["entrelinhas-entrypoint"]
CMD ["gunicorn", "--workers", "1", "--threads", "4", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
