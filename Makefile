SHELL := /bin/bash
CODE_REVIEW_GRAPH_VERSION ?= 2.3.9
DOCKER_COMPOSE ?= sudo docker compose

.PHONY: help mcp api phoenix dev test migrate ingest start sandbox

help:
	@printf '%s\n' \
		'make mcp  - Start the GitHub MCP domains on port 9000' \
		'make api  - Start the REST API on port 8000' \
		'make phoenix - Start the Phoenix UI on port 6006' \
		'make migrate - Apply database migrations' \
		'make start - Start the app, migrate, and ingest RAG documents' \
		'make sandbox - Build the isolated sandbox image' \
		'make dev  - Start the MCP server and REST API together' \
		'make ingest - Ingest RAG documents into the database' \
		'make test - Run unit tests with coverage (minimum 90%)'

test:
	uv run --all-packages --with pytest --with pytest-cov pytest tests/unit \
		--cov=agents --cov=api --cov=github_mcp_tools \
		--cov-report=term-missing --cov-report=xml:coverage.xml \
		--cov-fail-under=90

migrate:
	@set -a; \
	if [ -f .env ]; then . ./.env; fi; \
	set +a; \
	alembic upgrade head

ingest:
	@set -a; \
	if [ -f .env ]; then . ./.env; fi; \
	set +a; \
	python -m scripts.ingest_rag

start:
	@set -eu; \
	set -a; \
	if [ -f .env ]; then . ./.env; fi; \
	set +a; \
	db_user="$${DB_USER:-postgres}"; \
	db_name="$${DB_NAME:-pr_reviewer}"; \
	attempt=0; \
	$(DOCKER_COMPOSE) up -d --build; \
	until $(DOCKER_COMPOSE) exec -T pgvector pg_isready -U "$$db_user" -d "$$db_name" >/dev/null 2>&1; do \
		attempt=$$((attempt + 1)); \
		if [ "$$attempt" -ge 60 ]; then \
			echo "PostgreSQL did not become ready within 120 seconds" >&2; \
			exit 1; \
		fi; \
		sleep 2; \
	done; \
	$(MAKE) migrate; \
	$(MAKE) ingest

sandbox:
	docker build \
		--build-arg CODE_REVIEW_GRAPH_VERSION=$(CODE_REVIEW_GRAPH_VERSION) \
		-t pr-reviewer-sandbox:ci -f Dockerfile.sandbox .

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
