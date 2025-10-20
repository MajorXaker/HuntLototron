FROM ghcr.io/astral-sh/uv:python3.14-alpine

ENV WORKDIR_PATH /app
ENV XDG_DATA_HOME=${WORKDIR_PATH}
ENV UV_CACHE_DIR=./.uv-cache

WORKDIR $WORKDIR_PATH

COPY ./pyproject.toml .
COPY ./uv.lock .

RUN apk add --no-cache build-base
RUN uv sync --frozen --no-dev

COPY --chmod=0444 . .
RUN find $WORKDIR_PATH -type d -exec chown $USER_CONTAINER:$USER_CONTAINER {} \;
RUN find $WORKDIR_PATH -type d -exec chmod 755 {} \;

USER $USER_CONTAINER
CMD uv run alembic upgrade head && uv run app.py
