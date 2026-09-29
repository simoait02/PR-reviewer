from agents.orchestrator.base import BaseOrchestrator
from fastapi import HTTPException, Request


def get_orchestrator(request: Request) -> BaseOrchestrator:
    orchestrator = getattr(request.app.state, "orchestrator", None)

    if orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail="Orchestrator is not initialized",
        )

    return orchestrator
