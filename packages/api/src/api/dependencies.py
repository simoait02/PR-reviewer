from agents.review_pipeline import ReviewPipeline
from fastapi import HTTPException, Request
from pr_logging.core import get_logger

logger = get_logger(__name__)


def get_pipeline(request: Request) -> ReviewPipeline:
    pipeline = getattr(request.app.state, "pipeline", None)

    if pipeline is None:
        logger.error("Review pipeline is not initialized")
        raise HTTPException(
            status_code=503,
            detail="Review pipeline is not initialized",
        )

    logger.debug("Retrieved review pipeline dependency")

    return pipeline
