FROM astral/uv:python3.12-trixie-slim AS builder

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY packages/agents/pyproject.toml packages/agents/pyproject.toml
COPY packages/agents/README.md packages/agents/README.md
COPY packages/api/pyproject.toml packages/api/pyproject.toml
COPY packages/api/README.md packages/api/README.md
COPY packages/mcp/pyproject.toml packages/mcp/pyproject.toml

RUN uv sync --locked --package api --no-dev --no-install-workspace

COPY packages/agents/src packages/agents/src
COPY packages/api/src packages/api/src

RUN uv sync --locked --package api --no-dev

FROM python:3.12-slim
WORKDIR /app

RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/packages/agents/src /app/packages/agents/src
COPY --from=builder /app/packages/api/src /app/packages/api/src

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

ENTRYPOINT ["uvicorn", "api.api:app", "--host", "0.0.0.0", "--port", "8000"]
