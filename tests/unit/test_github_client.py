import asyncio
import base64

import httpx
import pytest
from github_mcp_tools.github_requests import (
    GithubAPIError,
    GithubClient,
    GithubRequest,
    PRFile,
    PullRequest,
)


def run(coroutine):
    return asyncio.run(coroutine)


def response(payload, *, status=200, headers=None, url="https://api.github.com/test"):
    return httpx.Response(
        status,
        json=payload,
        headers=headers,
        request=httpx.Request("GET", url),
    )


def client(token="secret"):
    return GithubClient(
        GithubRequest(
            repository_owner="acme",
            repository_name="payments",
            access_token=token,
        )
    )


def test_github_client_builds_base_url_and_auth_headers():
    authenticated = client()
    anonymous = client("")

    assert authenticated._base_url.endswith("/repos/acme/payments")
    assert authenticated._headers["Authorization"] == "Bearer secret"
    assert "Authorization" not in anonymous._headers


def test_get_wraps_timeout_http_and_request_errors(monkeypatch):
    class FakeAsyncClient:
        def __init__(self, error):
            self.error = error

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_):
            return None

        async def get(self, *_args, **_kwargs):
            raise self.error

    for error, expected in (
        (httpx.TimeoutException("slow"), "timed out"),
        (httpx.ConnectError("down"), "request failed"),
    ):
        monkeypatch.setattr(
            "github_mcp_tools.github_requests.httpx.AsyncClient",
            lambda error=error, **_: FakeAsyncClient(error),
        )
        with pytest.raises(GithubAPIError, match=expected):
            run(client()._get("https://api.github.com/test"))


def test_get_wraps_github_http_status_error(monkeypatch):
    github_response = response({"message": "Bad credentials"}, status=401)

    class FakeAsyncClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *_):
            return None

        async def get(self, *_args, **_kwargs):
            return github_response

    monkeypatch.setattr(
        "github_mcp_tools.github_requests.httpx.AsyncClient",
        lambda **_: FakeAsyncClient(),
    )

    with pytest.raises(GithubAPIError, match="401: Bad credentials"):
        run(client()._get("https://api.github.com/test"))


def test_get_returns_success_and_sends_client_configuration(monkeypatch):
    captured = {}
    github_response = response({"ok": True})

    class FakeAsyncClient:
        def __init__(self, **kwargs):
            captured.update(kwargs)

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_):
            return None

        async def get(self, url, params=None):
            captured["url"] = url
            captured["params"] = params
            return github_response

    monkeypatch.setattr(
        "github_mcp_tools.github_requests.httpx.AsyncClient",
        FakeAsyncClient,
    )

    result = run(client()._get("https://api.github.com/test", {"page": 2}))
    assert result is github_response
    assert captured["headers"]["Authorization"] == "Bearer secret"
    assert captured["params"] == {"page": 2}


def test_fetch_paginated_validates_page_and_detects_next_page(monkeypatch):
    github_client = client()
    pages = [
        response(
            [{"filename": "a.py", "sha": "a", "status": "modified"}],
            headers={"Link": '<next>; rel="next"'},
        ),
        response(
            [{"filename": "b.py", "sha": "b", "status": "added"}],
            headers={},
        ),
    ]

    async def fake_get(*, url, params):
        assert params["page"] in (1, 2)
        return pages[params["page"] - 1]

    monkeypatch.setattr(github_client, "_get", fake_get)
    first = run(github_client.fetch_pr_files(42, page=1))
    second = run(github_client.fetch_pr_files(42, page=2))

    assert first.items == [PRFile(filename="a.py", sha="a", status="modified")]
    assert first.has_next_page is True
    assert second.items[0].filename == "b.py"
    assert second.has_next_page is False
    with pytest.raises(ValueError, match="page"):
        run(github_client.fetch_pr_files(42, page=0))


def test_fetch_comment_review_and_file_parsers(monkeypatch):
    github_client = client()
    payloads = {
        "comments": [{"user": {"login": "alice"}, "body": None, "created_at": "today"}],
        "review_comments": [
            {
                "user": {"login": "bob"},
                "body": "inline",
                "path": "a.py",
                "line": 4,
                "diff_hunk": "@@",
                "in_reply_to_id": 7,
            }
        ],
        "reviews": [{"user": {"login": "carol"}, "body": None, "state": None}],
    }

    async def fake_get(*, url, params):
        if "issues" in url:
            return response(payloads["comments"])
        if "reviews" in url and "comments" not in url:
            return response(payloads["reviews"])
        return response(payloads["review_comments"])

    monkeypatch.setattr(github_client, "_get", fake_get)
    comments = run(github_client.fetch_pr_comments(42))
    review_comments = run(github_client.fetch_pr_review_comments(42))
    reviews = run(github_client.fetch_pr_reviews(42))

    assert comments.items[0].author == "alice"
    assert comments.items[0].body == ""
    assert review_comments.items[0].line == 4
    assert reviews.items[0].state == "UNKNOWN"


def test_fetch_pr_info_search_diff_and_blob(monkeypatch):
    github_client = client()
    pr = PullRequest(
        number=42,
        title="Improve payments",
        body="",
        base_branch="main",
        base_sha="base",
        head_branch="feature",
        head_sha="head",
    )
    changed_file = PRFile(
        filename="new.py", sha="blob", status="renamed", previous_filename="old.py"
    )

    async def fake_get(*, url, params=None):
        if "/pulls/42" in url:
            return response(
                {
                    "number": 42,
                    "title": "Improve payments",
                    "body": None,
                    "base": {"ref": "main", "sha": "base"},
                    "head": {"ref": "feature", "sha": "head"},
                }
            )
        if url.endswith("search/code"):
            return response(
                {
                    "total_count": 1,
                    "incomplete_results": False,
                    "items": [{"path": "new.py", "sha": "blob", "score": 1.0}],
                }
            )
        if "/compare/" in url:
            return response({"files": [{"filename": "old.py", "patch": "@@"}]})
        return response({"content": base64.b64encode(b"hello").decode()})

    monkeypatch.setattr(github_client, "_get", fake_get)
    fetched_pr = run(github_client.fetch_pr_infos(42))
    search = run(github_client.search_repository_code("payment", max_results=3))
    diff = run(github_client.fetch_diff_content(pr, changed_file))
    blob = run(github_client.fetch_file_blob("blob"))

    assert fetched_pr == pr
    assert search.total_count == 1
    assert search.items[0].path == "new.py"
    assert diff == {"filename": "old.py", "patch": "@@"}
    assert blob == "hello"


def test_fetch_diff_returns_none_and_blob_rejects_missing_content(monkeypatch):
    github_client = client()
    pr = PullRequest(
        number=42,
        title="Title",
        body="",
        base_branch="main",
        base_sha="base",
        head_branch="feature",
        head_sha="head",
    )
    changed_file = PRFile(filename="new.py", sha="blob", status="modified")

    async def fake_get(*, url, params=None):
        if "/compare/" in url:
            return response({"files": []})
        return response({})

    monkeypatch.setattr(github_client, "_get", fake_get)
    assert run(github_client.fetch_diff_content(pr, changed_file)) is None
    with pytest.raises(GithubAPIError, match="no blob content"):
        run(github_client.fetch_file_blob("blob"))
