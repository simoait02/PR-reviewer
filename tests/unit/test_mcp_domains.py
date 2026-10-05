import asyncio
from types import SimpleNamespace

import pytest
from github_mcp_tools.domains import common, impact, orchestrator, patch, reviewer
from github_mcp_tools.github_requests import PRFile, PullRequest
from github_mcp_tools.rag.models import BestPracticeResult, Category


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

    async def fetch_pr_files(self, pull_number, page):
        return SimpleNamespace(model_dump=lambda **_: {"page": page, "kind": "files"})

    async def fetch_diff_content(self, pr, file):
        return {"filename": file.filename, "patch": "@@"}

    async def search_repository_code(self, query, max_results):
        return SimpleNamespace(
            model_dump=lambda **_: {"query": query, "limit": max_results}
        )

    async def fetch_file_blob(self, file_sha):
        return f"content:{file_sha}"


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


def test_reviewer_domain_tools_validate_and_delegate(monkeypatch):
    fake_client = FakeClient()
    monkeypatch.setattr(reviewer, "get_client", lambda *_: fake_client)

    async def search(**_):
        return [
            BestPracticeResult(
                title="Testing",
                category=Category.TESTING,
                content="Use tests.",
                distance=0.1,
            )
        ]

    monkeypatch.setattr(
        reviewer,
        "get_best_practices_retriever",
        lambda: SimpleNamespace(search=search),
    )

    with pytest.raises(ValueError, match="must not be empty"):
        run(reviewer.search_best_practices("  "))
    assert run(reviewer.search_best_practices("testing"))[0].title == "Testing"
    assert run(reviewer.get_pr_files(42, "acme", "payments")) == {
        "page": 1,
        "kind": "files",
    }
    assert run(
        reviewer.get_diff_content(
            PullRequest(
                number=42,
                title="Title",
                body="",
                base_branch="main",
                base_sha="base",
                head_branch="feature",
                head_sha="head",
            ),
            PRFile(filename="a.py", sha="sha", status="modified"),
            "acme",
            "payments",
        )
    ) == {"filename": "a.py", "patch": "@@"}


def test_impact_domain_tools_delegate_to_client(monkeypatch):
    fake_client = FakeClient()
    monkeypatch.setattr(impact, "get_client", lambda *_: fake_client)
    pull_request = PullRequest(
        number=42,
        title="Title",
        body="",
        base_branch="main",
        base_sha="base",
        head_branch="feature",
        head_sha="head",
    )
    file = PRFile(filename="a.py", sha="sha", status="modified")

    assert run(impact.get_pr_files(42, "acme", "payments"))["kind"] == "files"
    assert run(impact.search_repository_code("Payment", "acme", "payments")) == {
        "query": "Payment",
        "limit": 20,
    }
    assert run(impact.get_diff_content(pull_request, file, "acme", "payments")) == {
        "filename": "a.py",
        "patch": "@@",
    }


def test_patch_domain_tools_delegate_and_validate_sha(monkeypatch):
    fake_client = FakeClient()
    monkeypatch.setattr(patch, "get_client", lambda *_: fake_client)
    pull_request = PullRequest(
        number=42,
        title="Title",
        body="",
        base_branch="main",
        base_sha="base",
        head_branch="feature",
        head_sha="head",
    )
    file = PRFile(filename="a.py", sha="sha", status="modified")

    assert run(patch.get_pr_files(42, "acme", "payments"))["kind"] == "files"
    assert run(patch.get_diff_content(pull_request, file, "acme", "payments")) == {
        "filename": "a.py",
        "patch": "@@",
    }
    assert run(patch.get_file_content("sha", "acme", "payments")) == "content:sha"
    with pytest.raises(ValueError, match="file_sha"):
        run(patch.get_file_content("", "acme", "payments"))
