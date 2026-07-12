FROM python:3.14-slim

WORKDIR /app

# Environment
ENV PYTHONPATH=/app/src
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies with uv
RUN uv sync --frozen

# Copy application code
COPY src/ src/

# Run via uv
CMD ["uv", "run", "python", "-m", "src.OpenTenant_app.scheduler.runner"]