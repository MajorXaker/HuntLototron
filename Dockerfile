# Build stage - includes build tools and dependencies
FROM ghcr.io/astral-sh/uv:python3.14-alpine AS builder

ENV WORKDIR_PATH=/app
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR $WORKDIR_PATH

# Install build dependencies
RUN apk add --no-cache build-base

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install dependencies only (not the project itself yet)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Copy the rest of the application
COPY . .

# Final sync to install the project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Runtime stage - minimal image with only runtime dependencies
FROM python:3.14-alpine AS runtime

ENV WORKDIR_PATH=/app
ENV PATH="$WORKDIR_PATH/.venv/bin:$PATH"

WORKDIR $WORKDIR_PATH

# Copy only the virtual environment from builder
COPY --from=builder $WORKDIR_PATH/.venv $WORKDIR_PATH/.venv

# Copy application code
COPY --from=builder --chmod=0444 $WORKDIR_PATH $WORKDIR_PATH

# Create non-root user
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser && \
    chown -R appuser:appuser $WORKDIR_PATH

USER appuser

CMD ["sh", "-c", "alembic upgrade head && python main.py"]
