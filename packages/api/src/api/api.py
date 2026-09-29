from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from agents.internal.protocol import AgentRequest
from agents.orchestrator.agent import CodeReviewOrchestrator
from agents.orchestrator.base import BaseOrchestrator
from fastapi import Depends, FastAPI
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.dependencies import get_orchestrator
from api.observability import configure_tracing
from api.schemas import UserQuestion

github_bearer = HTTPBearer(auto_error=False)

@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncIterator[None]:
    configure_tracing()
    fastapi_app.state.orchestrator = await CodeReviewOrchestrator.create_orchestrator()

    try:
        yield
    finally:
        fastapi_app.state.orchestrator = None


app = FastAPI(lifespan=lifespan)


@app.post("/review")
async def review(
    request: UserQuestion,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(github_bearer)],
    orchestrator: Annotated[BaseOrchestrator, Depends(get_orchestrator)],
):
    pr = request.pull_request
    github_token = credentials.credentials if credentials else None
    internal_request = AgentRequest(
        objective=request.question,
        facts=[
            f"Repository owner: {pr.repository_owner}",
            f"Repository name: {pr.repository_name}",
            f"Pull request number: {pr.pull_number}",
            (
                "Use the GitHub MCP tools to retrieve the pull request details, "
                "comments, and changed files before deciding."
            ),
        ],
    )

    return await orchestrator.ainvoke_structured(
        internal_request,
        github_token=github_token,
    )
