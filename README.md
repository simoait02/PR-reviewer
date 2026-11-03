# PR Reviewer

* * *

PR Reviewer is an AI-assisted service for reviewing GitHub pull requests. It gathers evidence from a repository, delegates focused correctness, impact, and security checks, and streams a concise review report back to the caller.

The project combines a FastAPI API, domain-specific MCP services, isolated Docker sandboxes, and a PostgreSQL/pgvector knowledge base for engineering-practice guidance.

* * *

## To start using PR Reviewer

The quickest way to run the complete development stack is with Docker Compose. You need Python 3.12, [uv](https://docs.astral.sh/uv/), Docker Engine with Docker Compose, and an OpenAI API key.

Create a local environment file and set the required values:

```bash
cp .env.example .env
```

```dotenv
DB_USER=postgres
DB_PASSWORD=choose-a-local-password
DB_NAME=pr_reviewer
DB_PORT=5432
OPENAI_API_KEY=your_openai_api_key
```

Build the sandbox and start the application:

```bash
make sandbox
make start
```

The startup command builds the API and MCP images, starts PostgreSQL, applies migrations, and ingests the engineering-practice documents used by retrieval. It may take a little longer the first time because ingestion calls the OpenAI embeddings API.

Once the stack is running:

- API: <http://localhost:8000>
- OpenAPI documentation: <http://localhost:8000/docs>
- Phoenix observability: <http://localhost:6006>
- MCP domains: <http://localhost:9000>

Submit a review with the REST API:

```bash
curl -N http://localhost:8000/review \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer YOUR_GITHUB_TOKEN' \
  -d '{
    "question": "Review this PR for correctness and security issues.",
    "pull_request": {
      "repository_owner": "octocat",
      "repository_name": "Hello-World",
      "pull_number": 1
    }
  }'
```

The response is a Server-Sent Events stream. It can include status, summary, findings, limitations, and a final `done` event. The GitHub token is supplied for the current request and is not stored by the application.

To stop the services:

```bash
docker compose down
```

Use `docker compose down -v` only when you intentionally want to remove the local database and sandbox volumes.

## To start developing PR Reviewer

Install the workspace dependencies:

```bash
uv sync
```

With PostgreSQL running and `.env` configured, the main development commands are:

| Command | Description |
| --- | --- |
| `make dev` | Start the MCP server and API together |
| `make mcp` | Start MCP domains on port 9000 |
| `make api` | Start the API on port 8000 |
| `make migrate` | Apply Alembic migrations |
| `make ingest` | Ingest or update documents from `docs/` |
| `make test` | Run unit tests with the 90% coverage threshold |
| `make rag-eval` | Run the DeepEval retrieval evaluation |
| `make sandbox` | Build the isolated review sandbox image |

The optional React/Vite client is in [`ui/`](ui/). Run it separately:

```bash
cp ui/.env.example ui/.env
cd ui
npm install
npm run dev
```

Set `VITE_API_BASE_URL=http://localhost:8000` in `ui/.env`. The client is served at <http://localhost:5173>.

## Architecture

```text
Client
  │ POST /review (SSE)
  ▼
FastAPI API ──► Review pipeline ──► Orchestrator
                                      │
                        ┌─────────────┼─────────────┐
                        ▼             ▼             ▼
                    Reviewer       Impact        Security
                        │             │             │
                        └──── MCP services / isolated sandbox ────► GitHub
                                      │
                                      ▼
                                Synthesizer
                                      │
                                      ▼
                                streamed report
```

The repository is organized as follows:

```text
packages/api/       FastAPI endpoint and SSE response handling
packages/agents/    Review pipeline, specialists, and synthesis
packages/mcp/       GitHub, Git, RAG, sandbox, impact, and security tools
packages/logging/   Shared structured logging utilities
docs/               Engineering-practice source documents
scripts/            Database helpers and RAG ingestion
security-rules/     Semgrep rules for authentication and input validation
tests/              Unit tests and retrieval evaluations
ui/                 Optional React/Vite client
```

## Support and security

For local setup problems, check that Docker is running, `.env` contains `OPENAI_API_KEY` and database values, and the database has completed its health check before running migrations or ingestion.

Review sandboxes are isolated containers, but the Compose configuration is intended for development rather than hardened production deployment. Do not commit `.env`, API tokens, or database passwords.

Questions, bug reports, and improvements are welcome through the project's issue tracker and pull requests.

## Project status

PR Reviewer is an actively developed project. Interfaces, MCP domains, and the web client may change as the review pipeline evolves.
