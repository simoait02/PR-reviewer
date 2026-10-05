SHELL := /bin/bash

.PHONY: help mcp api phoenix dev test

help:
	@printf '%s\n' \
		'make mcp  - Start the GitHub MCP domains on port 9000' \
		'make api  - Start the REST API on port 8000' \
		'make phoenix - Start the Phoenix UI on port 6006' \
		'make dev  - Start the MCP server and REST API together' \
		'make test - Run unit tests with coverage (minimum 90%)'

test:
	uv run --with pytest --with pytest-cov pytest tests/unit \
		--cov=agents --cov=api --cov=github_mcp_tools --cov=rag \
		--cov-report=term-missing --cov-report=xml:coverage.xml \
		--cov-fail-under=90

mcp:
	@set -a; \
	if [ -f .env ]; then . ./.env; fi; \
	set +a; \
	uv run --package github-mcp-tools mcp

api:
	@set -a; \
	if [ -f .env ]; then . ./.env; fi; \
	set +a; \
	uv run --package api uvicorn api.api:app --host 0.0.0.0 --port 8000

phoenix:
	docker compose up phoenix

dev:
	@set -a; \
	if [ -f .env ]; then . ./.env; fi; \
	set +a; \
	uv run --package github-mcp-tools mcp & mcp_pid=$$!; \
	uv run --package api uvicorn api.api:app --host 0.0.0.0 --port 8000 & api_pid=$$!; \
	trap 'kill $$mcp_pid $$api_pid 2>/dev/null || true' INT TERM EXIT; \
	wait
