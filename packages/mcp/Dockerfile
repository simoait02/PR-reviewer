FROM astral/uv:python3.12-trixie-slim AS builder

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY packages/agents/pyproject.toml packages/agents/pyproject.toml
COPY packages/api/pyproject.toml packages/api/pyproject.toml
COPY packages/mcp/pyproject.toml packages/mcp/pyproject.toml
COPY packages/mcp/README.md packages/mcp/README.md

RUN uv sync --locked --package github-mcp-tools --no-dev --no-install-workspace

COPY packages/mcp/src packages/mcp/src

RUN uv sync --locked --package github-mcp-tools --no-dev

FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        passwd \
        util-linux \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/packages/mcp/src /app/packages/mcp/src

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN useradd --create-home appuser

COPY packages/mcp/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 9000

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["mcp"]
