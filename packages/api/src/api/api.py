from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated
from uuid import uuid4

from agents.internal.protocol import AgentRequest
from agents.review_pipeline import ReviewPipeline
from fastapi import Depends, FastAPI
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from api.dependencies import get_pipeline
from api.observability import configure_tracing
from api.schemas import UserQuestion

github_bearer = HTTPBearer(auto_error=False)


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI) -> AsyncIterator[None]:
    configure_tracing()
    try:
        fastapi_app.state.pipeline = await ReviewPipeline.create_pipeline()
        yield
    finally:
        fastapi_app.state.pipeline = None


app = FastAPI(lifespan=lifespan)


@app.post("/review")
async def review(
    request: UserQuestion,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(github_bearer)],
    pipeline: Annotated[ReviewPipeline, Depends(get_pipeline)],
):
    pr = request.pull_request
    github_token = credentials.credentials if credentials else None
    internal_request = AgentRequest(
        task_objective=request.question,
        focus=[
            f"Repository owner: {pr.repository_owner}",
            f"Repository name: {pr.repository_name}",
            f"Pull request number: {pr.pull_number}",
        ],
    )

    async def stream_review() -> AsyncIterator[str]:
        async for response in pipeline.astream(
            internal_request,
            github_token=github_token,
            thread_id=str(uuid4()),
        ):
            yield f"data: {response.model_dump_json()}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        stream_review(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"},
    )
