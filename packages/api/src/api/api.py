from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import Depends, FastAPI

from agents.internal.protocol import AgentRequest
from agents.orchestrator.agent import CodeReviewOrchestrator
from agents.orchestrator.base import BaseOrchestrator
from api.dependencies import get_orchestrator
from api.schemas import UserQuestion


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.orchestrator = (
        await CodeReviewOrchestrator.create_orchestrator()
    )

    try:
        yield
    finally:
        app.state.orchestrator = None


app = FastAPI(lifespan=lifespan)


@app.post("/review")
async def review(
    request: UserQuestion,
    orchestrator: BaseOrchestrator = Depends(get_orchestrator),
):
    internal_request = AgentRequest(
        objective=request.question,
        facts=[],
    )
    return await orchestrator.ainvoke_structured(internal_request)
