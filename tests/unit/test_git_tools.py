import asyncio

import pytest
from fastmcp.exceptions import ToolError

from github_mcp_tools.domains import git_tools, security


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
