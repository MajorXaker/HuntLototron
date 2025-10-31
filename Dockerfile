# Build stage
FROM ghcr.io/astral-sh/uv:python3.14-alpine AS builder

# Optimize uv for Docker
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache build-base

# Copy only dependency files first for layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies with cache mount
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Copy application code
COPY . .

# Runtime stage
FROM ghcr.io/astral-sh/uv:python3.14-alpine

# Create non-root user
RUN addgroup -g 1000 appgroup && \
    adduser -D -u 1000 -G appgroup appuser

ENV WORKDIR_PATH=/app \
    PATH="/app/.venv/bin:$PATH"

WORKDIR $WORKDIR_PATH

# Copy virtual environment and application from builder
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appgroup /app /app

# Switch to non-root user
USER appuser

# Use proper signal handling with exec form
CMD uv run alembic upgrade head && uv run main.py
