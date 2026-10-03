from agents.review_pipeline import ReviewPipeline
from fastapi import HTTPException, Request


def get_pipeline(request: Request) -> ReviewPipeline:
    pipeline = getattr(request.app.state, "pipeline", None)

    if pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="Review pipeline is not initialized",
        )

    return pipeline
