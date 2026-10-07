import asyncio
from types import SimpleNamespace

from github_mcp_tools.domains import common, orchestrator


def run(coroutine):
    return asyncio.run(coroutine)


class FakeClient:
    async def fetch_pr_infos(self, pull_number):
        return SimpleNamespace(model_dump=lambda: {"number": pull_number})

    async def fetch_pr_comments(self, pull_number, page):
        return SimpleNamespace(
            model_dump=lambda **_: {"page": page, "kind": "comments"}
        )

    async def fetch_pr_reviews(self, pull_number, page):
        return SimpleNamespace(model_dump=lambda **_: {"page": page, "kind": "reviews"})

    async def fetch_pr_review_comments(self, pull_number, page):
        return SimpleNamespace(model_dump=lambda **_: {"page": page, "kind": "inline"})


def test_common_client_reads_request_scoped_token(monkeypatch):
    monkeypatch.setattr(
        common,
        "get_http_headers",
        lambda include: {"x-github-token": "secret"},
    )

    github_client = common.get_client("acme", "payments")
    assert github_client.github_request.repository_owner == "acme"
    assert github_client.github_request.access_token == "secret"


def test_orchestrator_domain_tools_delegate_to_client(monkeypatch):
    fake_client = FakeClient()
    monkeypatch.setattr(orchestrator, "get_client", lambda *_: fake_client)

    assert run(orchestrator.get_pr_info(42, "acme", "payments")) == {"number": 42}
    assert run(orchestrator.get_pr_comments(42, "acme", "payments", 2)) == {
        "page": 2,
        "kind": "comments",
    }
    assert run(orchestrator.get_pr_reviews(42, "acme", "payments", 3)) == {
        "page": 3,
        "kind": "reviews",
    }
    assert run(orchestrator.get_pr_review_comments(42, "acme", "payments", 4)) == {
        "page": 4,
        "kind": "inline",
    }
