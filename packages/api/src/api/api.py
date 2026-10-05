from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated
from uuid import uuid4

from agents.internal.protocol import AgentRequest
from agents.review_pipeline import ReviewPipeline
from fastapi import Depends, FastAPI, Header, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.sse import EventSourceResponse, ServerSentEvent

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID"],
)


@app.post("/review", response_class=EventSourceResponse)
async def review(
    request: UserQuestion,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(github_bearer)],
    pipeline: Annotated[ReviewPipeline, Depends(get_pipeline)],
    response: Response,
    correlation_id: Annotated[str | None, Header(alias="X-Correlation-ID")] = None,
) -> AsyncIterator[ServerSentEvent]:
    thread_id = (correlation_id or "").strip() or str(uuid4())
    response.headers["X-Correlation-ID"] = thread_id

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

    async for event_name, payload in pipeline.astream(
        internal_request,
        github_token=github_token,
        thread_id=thread_id,
    ):
        yield ServerSentEvent(event=event_name, data=payload)

    yield ServerSentEvent(event="done", data={})
