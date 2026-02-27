# --- STAGE 1: Builder ---
FROM python:3.12-slim AS builder

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

WORKDIR /app

# Install only the system tools needed to compile C extensions (like psycopg2)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry and dependencies
RUN pip install "poetry==$POETRY_VERSION"
COPY pyproject.toml poetry.lock ./
# Install only production dependencies into the .venv folder
RUN poetry install --only main --no-root

# --- STAGE 2: Runtime ---
FROM python:3.12-slim AS runtime

WORKDIR /app

# Install only the runtime library for PostgreSQL (no compilers needed here)
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security (Standard Best Practice)
RUN useradd -m -r appuser && chown -R appuser /app

# Copy ONLY the virtual environment and your code from the builder stage
COPY --from=builder /app/.venv /app/.venv
COPY . /app/

# Ensure the app uses the virtual environment's Python
ENV PATH="/app/.venv/bin:$PATH"

USER appuser

EXPOSE 8000

CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "core.asgi:application"]