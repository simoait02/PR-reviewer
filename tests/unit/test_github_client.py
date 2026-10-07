import asyncio

import httpx
import pytest
from github_mcp_tools.github_requests import (
    GithubAPIError,
    GithubClient,
    GithubRequest,
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


def test_fetch_comment_and_review_parsers(monkeypatch):
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


def test_fetch_pr_info(monkeypatch):
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
        raise AssertionError(f"unexpected URL: {url}")

    monkeypatch.setattr(github_client, "_get", fake_get)
    fetched_pr = run(github_client.fetch_pr_infos(42))

    assert fetched_pr == pr
