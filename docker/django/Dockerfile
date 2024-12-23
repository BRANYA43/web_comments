FROM python:3.12-slim

COPY docker/django/healthcheck.sh /usr/local/bin/

RUN apt-get update; \
    apt-get install -y --no-install-recommends build-essential libpq-dev gcc nano curl; \
    rm -rf /var/lib/apt/lists/*; \
    python -m venv /opt/.venv; \
    chmod +x /usr/local/bin/healthcheck.sh


ENV PATH="/opt/.venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR opt/src/

COPY pyproject.toml ../.

RUN pip install --upgrade pip; \
    pip install --no-cache-dir poetry; \
    poetry env use /opt/.venv/bin/python; \
    poetry install

COPY src/ .
