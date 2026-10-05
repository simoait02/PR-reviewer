import asyncio
from types import SimpleNamespace
from uuid import UUID

import httpx
import pytest
from api.api import app, review
from api.dependencies import get_pipeline
from api.schemas import UserQuestion
from fastapi import HTTPException, Response
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import ValidationError


class FakePipeline:
    def __init__(self):
        self.calls = []

    async def astream(self, request, *, github_token, thread_id):
        self.calls.append(
            {
                "request": request,
                "github_token": github_token,
                "thread_id": thread_id,
            }
        )
        yield "status", {"status": "completed"}
        yield "summary", {"summary": "All good."}
        yield "done_from_pipeline", {"unexpected": True}


def valid_payload() -> dict:
    return {
        "question": "Review this pull request",
        "pull_request": {
            "repository_owner": "acme",
            "repository_name": "payments",
            "pull_number": 42,
        },
    }


def run_request(fake_pipeline, *, headers=None, method="POST", path="/review"):
    app.dependency_overrides[get_pipeline] = lambda: fake_pipeline

    async def request():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://test"
        ) as client:
            return await client.request(
                method,
                path,
                headers=headers,
                json=valid_payload() if method == "POST" else None,
            )

    try:
        return asyncio.run(request())
    finally:
        app.dependency_overrides.clear()


def collect_review(pipeline, *, correlation_id=None):
    async def collect():
        response = Response()
        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="github-token"
        )
        events = [
            event
            async for event in review(
                UserQuestion.model_validate(valid_payload()),
                credentials,
                pipeline,
                response,
                correlation_id,
            )
        ]
        return events, response

    return asyncio.run(collect())


def test_review_streams_named_synthesizer_events_and_forwards_context():
    pipeline = FakePipeline()
    events, response = collect_review(pipeline, correlation_id="sender-123")

    assert response.headers["x-correlation-id"] == "sender-123"
    assert [event.event for event in events] == [
        "status",
        "summary",
        "done_from_pipeline",
        "done",
    ]
    assert events[0].data == {"status": "completed"}
    assert events[-1].data == {}
    assert pipeline.calls[0]["github_token"] == "github-token"
    assert pipeline.calls[0]["thread_id"] == "sender-123"
    assert pipeline.calls[0]["request"].task_objective == "Review this pull request"
    assert pipeline.calls[0]["request"].focus == [
        "Repository owner: acme",
        "Repository name: payments",
        "Pull request number: 42",
    ]


def test_review_generates_and_returns_correlation_id_when_missing():
    pipeline = FakePipeline()
    _, response = collect_review(pipeline)

    correlation_id = response.headers["x-correlation-id"]
    UUID(correlation_id)
    assert pipeline.calls[0]["thread_id"] == correlation_id


def test_review_handles_cors_preflight():
    response = run_request(
        FakePipeline(),
        method="OPTIONS",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,x-correlation-id",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert (
        "x-correlation-id" in response.headers["access-control-allow-headers"].lower()
    )


def test_review_rejects_invalid_request():
    with pytest.raises(ValidationError):
        UserQuestion.model_validate({})


def test_pipeline_dependency_returns_service_unavailable_when_missing():
    with pytest.raises(HTTPException) as error:
        get_pipeline(
            SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(pipeline=None)))
        )

    assert error.value.status_code == 503
    assert error.value.detail == "Review pipeline is not initialized"
