import asyncio
from types import SimpleNamespace

import pytest
from fastmcp.exceptions import ToolError
from github_mcp_tools.infrastructure.github import auth as common
from github_mcp_tools.servers import impact, orchestrator, reviewer, security


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


class FakeSandbox:
    def __init__(self, *, destroy_result=True):
        self.destroy_result = destroy_result
        self.calls = []

    async def exec(self, sandbox_id, command, *, workdir, environment):
        self.calls.append((sandbox_id, command, workdir, environment))
        return 0, "line one\nline two\n", ""

    async def create_sandbox(self):
        return "sandbox-id"

    async def clone(self, *args, **kwargs):
        self.calls.append(("clone", args, kwargs))
        return 0, "head-sha", ""

    async def destroy_sandbox(self, sandbox_id):
        self.calls.append(("destroy", sandbox_id))
        return self.destroy_result


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


def test_orchestrator_sandbox_tools_delegate_to_sandbox(monkeypatch):
    sandbox = FakeSandbox()
    monkeypatch.setattr(orchestrator.Sandbox, "get_instance", lambda: sandbox)
    monkeypatch.setattr(orchestrator, "get_github_token", lambda: "token")

    assert run(orchestrator.create_sandbox()).sandbox_id == "sandbox-id"
    cloned = run(
        orchestrator.clone_sandbox_repository(
            "sandbox-id",
            "acme",
            "payments",
            42,
            "a" * 40,
            "head-sha",
        )
    )
    assert cloned.path == "/workspace/repo"

    graph = run(orchestrator.build_code_graph("sandbox-id"))
    assert graph.command == ["code-review-graph", "build"]
    assert run(orchestrator.destroy_sandbox("sandbox-id")).status == "destroyed"

    sandbox.destroy_result = False
    assert run(orchestrator.destroy_sandbox("sandbox-id")).status == "not_found"


def test_impact_tools_run_graph_commands(monkeypatch):
    sandbox = FakeSandbox()
    monkeypatch.setattr(impact.Sandbox, "get_instance", lambda: sandbox)

    result = run(
        impact.get_code_graph_impact(
            "sandbox-id",
            "base",
            changed_files=["src/app.py"],
            max_depth=3,
        )
    )
    assert result.changed_files == ["src/app.py"]
    assert "--files" in sandbox.calls[0][1]

    result = run(impact.get_code_graph_impact("sandbox-id", "base"))
    assert result.changed_files == []

    query = run(
        impact.query_code_graph(
            "sandbox-id",
            impact.GraphQueryPattern.CALLERS_OF,
            "module.function",
        )
    )
    assert query.target == "module.function"
    assert query.pattern is impact.GraphQueryPattern.CALLERS_OF


def test_security_tools_read_repository_evidence(monkeypatch):
    sandbox = FakeSandbox()
    monkeypatch.setattr(security.Sandbox, "get_instance", lambda: sandbox)

    diff = run(security.read_diff("sandbox-id", "base", "head"))
    assert diff.diff == "line one\nline two\n"

    file_result = run(
        security.read_file(
            "sandbox-id",
            "head",
            "src/app.py",
            start_line=2,
            end_line=2,
        )
    )
    assert file_result.content == "line two\n"

    search = run(
        security.search_code(
            "sandbox-id",
            "head",
            "query",
            paths=["src/app.py"],
            regex=True,
        )
    )
    assert search.paths == ["src/app.py"]


def test_security_tools_validate_inputs_and_run_profiles(monkeypatch):
    sandbox = FakeSandbox()
    monkeypatch.setattr(security.Sandbox, "get_instance", lambda: sandbox)

    with pytest.raises(Exception, match="context_lines"):
        run(security.read_diff("sandbox-id", "base", "head", context_lines=-1))
    with pytest.raises(Exception, match="line range"):
        run(
            security.read_file("sandbox-id", "head", "app.py", start_line=2, end_line=1)
        )
    with pytest.raises(Exception, match="query"):
        run(security.search_code("sandbox-id", "head", "  "))

    assert (
        run(security.run_semgrep_security_scan("sandbox-id", "base")).profile
        == "security"
    )
    assert run(security.check_auth_coverage("sandbox-id", "base")).profile == "auth"
    assert (
        run(security.check_input_validation("sandbox-id", "base")).profile
        == "input_validation"
    )


def test_reviewer_search_validates_and_queries_best_practices(monkeypatch):
    calls = []

    class FakeRetriever:
        async def search(self, **kwargs):
            calls.append(kwargs)
            return ["guidance"]

    monkeypatch.setattr(
        reviewer,
        "get_best_practices_retriever",
        lambda: FakeRetriever(),
    )

    with pytest.raises(ToolError, match="query must not be empty"):
        run(reviewer.search_best_practices("  "))

    with pytest.raises(ToolError, match="limit must be greater than zero"):
        run(reviewer.search_best_practices("authentication", limit=0))

    result = run(
        reviewer.search_best_practices(
            "authentication requirements",
            limit=3,
        )
    )

    assert result == ["guidance"]
    assert calls == [
        {
            "query": "authentication requirements",
            "category": None,
            "limit": 3,
        }
    ]
