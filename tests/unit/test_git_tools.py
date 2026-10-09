import asyncio

import pytest
from fastmcp.exceptions import ToolError
from github_mcp_tools.servers import security
from github_mcp_tools.tools import git as git_tools


def run(coroutine):
    return asyncio.run(coroutine)


class FakeSandbox:
    def __init__(self):
        self.calls = []

    async def exec(self, sandbox_id, command, *, workdir, environment):
        self.calls.append(
            {
                "sandbox_id": sandbox_id,
                "command": command,
                "workdir": workdir,
                "environment": environment,
            }
        )
        return 0, "stdout", "stderr"


def test_git_status_uses_fixed_repository_workdir_and_path_separator(monkeypatch):
    sandbox = FakeSandbox()
    monkeypatch.setattr(git_tools.Sandbox, "get_instance", lambda: sandbox)

    result = run(git_tools.git_status("sandbox-id", paths=["-filename.py"]))

    assert result.exit_code == 0
    assert result.stdout == "stdout"
    assert sandbox.calls == [
        {
            "sandbox_id": "sandbox-id",
            "command": [
                "git",
                "status",
                "--short",
                "--untracked-files=all",
                "--",
                "-filename.py",
            ],
            "workdir": "/workspace/repo",
            "environment": git_tools.GIT_ENV,
        }
    ]


def test_git_log_validation_raises_tool_error(monkeypatch):
    sandbox = FakeSandbox()
    monkeypatch.setattr(git_tools.Sandbox, "get_instance", lambda: sandbox)

    with pytest.raises(ToolError, match="max_count must be greater than zero"):
        run(git_tools.git_log("sandbox-id", max_count=0))

    assert sandbox.calls == []


def test_git_read_commands_build_safe_commands(monkeypatch):
    sandbox = FakeSandbox()
    monkeypatch.setattr(git_tools.Sandbox, "get_instance", lambda: sandbox)

    run(git_tools.git_log("sandbox-id", revision="HEAD~1", max_count=3))
    run(git_tools.git_show("sandbox-id", revision="HEAD", paths=["src/app.py"]))
    run(
        git_tools.git_diff(
            "sandbox-id",
            revision="base",
            compare_revision="head",
            context_lines=5,
        )
    )
    run(
        git_tools.git_grep(
            "sandbox-id",
            pattern="dangerous_call",
            revision="HEAD",
            regex=True,
        )
    )

    assert sandbox.calls[0]["command"] == [
        "git",
        "log",
        "--oneline",
        "--no-decorate",
        "--max-count=3",
        "HEAD~1",
        "--",
    ]
    assert sandbox.calls[1]["command"][-3:] == ["HEAD", "--", "src/app.py"]
    assert "--unified=5" in sandbox.calls[2]["command"]
    assert "--extended-regexp" in sandbox.calls[3]["command"]


def test_git_diff_and_grep_validate_arguments(monkeypatch):
    sandbox = FakeSandbox()
    monkeypatch.setattr(git_tools.Sandbox, "get_instance", lambda: sandbox)

    with pytest.raises(ToolError, match="revision is required"):
        run(git_tools.git_diff("sandbox-id", compare_revision="head"))
    with pytest.raises(ToolError, match="context_lines must not be negative"):
        run(git_tools.git_diff("sandbox-id", context_lines=-1))
    with pytest.raises(ToolError, match="pattern must not be empty"):
        run(git_tools.git_grep("sandbox-id", pattern=""))
    with pytest.raises(ToolError, match="invalid Git revision"):
        run(git_tools.git_log("sandbox-id", revision="--config=bad"))

    assert sandbox.calls == []


def test_git_tools_register_all_read_only_tools():
    registered = []

    class FakeMCP:
        def tool(self):
            return lambda function: registered.append(function)

    git_tools.register_read_only_git_tools(FakeMCP())

    assert [function.__name__ for function in registered] == [
        "git_status",
        "git_ls_files",
        "git_log",
        "git_show",
        "git_diff",
        "git_grep",
    ]


def test_git_output_is_truncated(monkeypatch):
    class LongOutputSandbox(FakeSandbox):
        async def exec(self, sandbox_id, command, *, workdir, environment):
            return 0, "x" * (git_tools.MAX_OUTPUT_CHARS + 1), ""

    sandbox = LongOutputSandbox()
    monkeypatch.setattr(git_tools.Sandbox, "get_instance", lambda: sandbox)

    result = run(git_tools.git_status("sandbox-id"))

    assert result.stdout.endswith("... [output truncated]")


def test_git_tools_reject_paths_outside_repository(monkeypatch):
    sandbox = FakeSandbox()
    monkeypatch.setattr(git_tools.Sandbox, "get_instance", lambda: sandbox)

    with pytest.raises(ToolError, match="repository-relative"):
        run(git_tools.git_ls_files("sandbox-id", paths=["../secrets.txt"]))

    assert sandbox.calls == []


def test_semgrep_uses_separator_before_changed_files(monkeypatch):
    captured = {}

    async def fake_run_security_command(sandbox_id, command):
        captured["sandbox_id"] = sandbox_id
        captured["command"] = command
        return security.SecurityCommandResponse(
            sandbox_id=sandbox_id,
            command=command,
            exit_code=0,
            stdout="{}",
            stderr="",
            status="succeeded",
        )

    monkeypatch.setattr(security, "_run_security_command", fake_run_security_command)

    result = run(
        security._run_semgrep(
            "sandbox-id",
            "a" * 40,
            ["-config=unexpected.yml"],
            "security",
        )
    )

    assert result.exit_code == 0
    assert captured["command"][-2:] == ["--", "-config=unexpected.yml"]


def test_semgrep_rejects_non_repository_targets(monkeypatch):
    with pytest.raises(ToolError, match="repository-relative"):
        run(
            security._run_semgrep(
                "sandbox-id",
                "a" * 40,
                ["/etc/passwd"],
                "security",
            )
        )
