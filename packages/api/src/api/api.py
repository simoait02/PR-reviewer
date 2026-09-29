from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from starlette import status

from agents.internal.protocol import AgentRequest
from agents.orchestrator.agent import CodeReviewOrchestrator
from agents.orchestrator.base import BaseOrchestrator
from fastapi import Depends, FastAPI, HTTPException, Header

from api.dependencies import get_orchestrator
from api.observability import configure_tracing
from api.schemas import UserQuestion

def extract_bearer_token(authorization: str | None) -> str | None:
    if authorization is None:
        return None

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    token = authorization.removeprefix("Bearer ") .strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    return token

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_tracing()
    app.state.orchestrator = await CodeReviewOrchestrator.create_orchestrator()

    try:
        yield
    finally:
        app.state.orchestrator = None


app = FastAPI(lifespan=lifespan)


@app.post("/review")
async def review(
    request: UserQuestion,
    authorization: str | None = Header(default=None),
    orchestrator: BaseOrchestrator = Depends(get_orchestrator),
):
    pr = request.pull_request
    github_token = extract_bearer_token(authorization)
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

    return await orchestrator.ainvoke_structured(internal_request,github_token= github_token)
