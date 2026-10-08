import asyncio
from types import SimpleNamespace

import pytest
from docker.errors import NotFound
from github_mcp_tools.sandbox import Sandbox, SandboxError


def run(coroutine):
    return asyncio.run(coroutine)


class FakeContainer:
    def __init__(self, *, managed=True):
        self.id = "sandbox-id"
        self.labels = {"com.pr-reviewer.sandbox": "true"} if managed else {}
        self.removed = False
        self.reloaded = False

    def reload(self):
        self.reloaded = True

    def exec_run(self, command, *, workdir, environment, demux):
        return SimpleNamespace(exit_code=0, output=(b"stdout", b"stderr"))

    def remove(self, *, force, v):
        self.removed = True


class FakeContainers:
    def __init__(self, container):
        self.container = container
        self.run_kwargs = None

    def run(self, **kwargs):
        self.run_kwargs = kwargs
        return self.container

    def get(self, sandbox_id):
        if sandbox_id != self.container.id:
            raise NotFound("missing")
        return self.container


def make_sandbox(container=None):
    container = container or FakeContainer()
    sandbox = Sandbox.__new__(Sandbox)
    sandbox.client = SimpleNamespace(containers=FakeContainers(container))
    sandbox.image = "sandbox-image"
    sandbox.cpus = 2
    sandbox.memory = "6g"
    return sandbox


def test_sandbox_create_exec_and_destroy():
    sandbox = make_sandbox()

    assert run(sandbox.create_sandbox()) == "sandbox-id"
    assert sandbox.client.containers.run_kwargs["image"] == "sandbox-image"

    result = run(sandbox.exec("sandbox-id", ["git", "status"]))
    assert result == (0, "stdout", "stderr")

    assert run(sandbox.destroy_sandbox("sandbox-id")) is True


def test_sandbox_rejects_unmanaged_container():
    sandbox = make_sandbox(FakeContainer(managed=False))

    with pytest.raises(SandboxError, match="not managed"):
        run(sandbox.exec("sandbox-id", ["git", "status"]))


def test_sandbox_missing_container_is_handled():
    sandbox = make_sandbox()

    assert run(sandbox.destroy_sandbox("missing")) is False
    with pytest.raises(SandboxError, match="does not exist"):
        run(sandbox.exec("missing", ["git", "status"]))


def test_clone_fetches_base_and_pull_head_with_token():
    sandbox = make_sandbox()
    calls = []
    base_sha = "a" * 40
    head_sha = "b" * 40

    async def fake_exec(sandbox_id, command, workdir=None, environment=None):
        calls.append((command, workdir, environment))
        if command == ["git", "rev-parse", "HEAD"]:
            return 0, head_sha, ""
        return 0, "", ""

    sandbox.exec = fake_exec
    result = run(
        sandbox.clone(
            "sandbox-id",
            "acme",
            "payments",
            42,
            base_sha,
            head_sha,
            access_token="token",
        )
    )

    assert result == (0, head_sha, "")
    commands = [call[0] for call in calls]
    assert ["git", "fetch", "--depth", "1", "--no-tags", "origin", base_sha] in commands
    assert [
        "git",
        "fetch",
        "--depth",
        "1",
        "--no-tags",
        "origin",
        "refs/pull/42/head",
    ] in commands
    fetch_environment = calls[2][2]
    assert "Authorization: Basic" in fetch_environment["GIT_CONFIG_VALUE_0"]


def test_clone_validates_pull_number_and_shas():
    sandbox = make_sandbox()

    with pytest.raises(SandboxError, match="pull number"):
        run(sandbox.clone("sandbox-id", "acme", "payments", 0, "a" * 40, "b" * 40))
    with pytest.raises(SandboxError, match="base_sha"):
        run(sandbox.clone("sandbox-id", "acme", "payments", 1, "base", "b" * 40))
    with pytest.raises(SandboxError, match="head_sha"):
        run(sandbox.clone("sandbox-id", "acme", "payments", 1, "a" * 40, "head"))
