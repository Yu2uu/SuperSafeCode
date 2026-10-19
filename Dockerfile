FROM python:3.14-slim-trixie@sha256:a2b82f3c48559aa0a8446d9af49826b6e2b2016f4cd2afabfe6013ec53729170

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get purge -y mount \
    && rm -rf /var/lib/apt/lists/*

# Remove unused entry points; package records remain for vulnerability auditing purposes
RUN rm /usr/bin/infocmp /usr/bin/nsenter

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

RUN groupadd --gid 10001 appuser \
    && useradd --uid 10001 --gid appuser --no-create-home appuser \
    && mkdir -p /data \
    && chown appuser:appuser /data

ENV NOTES_DB_PATH=/data/notes.db

USER 10001:10001

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "1", "--access-logfile", "-", "--error-logfile", "-", "app.main:app"]
