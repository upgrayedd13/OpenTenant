FROM python:3.14-slim

WORKDIR /app

ENV PYTHONPATH=/app/src
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./
RUN uv pip install --system --no-cache

COPY src/ src/
COPY docker/cron/crontab /etc/cron.d/app-cron

RUN chmod 0644 /etc/cron.d/app-cron

CMD ["cron", "-f"]