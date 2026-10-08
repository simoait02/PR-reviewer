import asyncio
import base64
import re
from typing import ClassVar, Literal, Self

import docker
from docker.errors import NotFound
from pydantic import BaseModel


class SandboxError(Exception):
    """Anything that goes wrong inside the sandbox layer."""


class CreateSandboxResponse(BaseModel):
    sandbox_id: str
    status: Literal["running"]


class CloneSandboxResponse(BaseModel):
    sandbox_id: str
    repository_owner: str
    repository_name: str
    pull_number: int
    base_sha: str
    head_sha: str
    path: str
    status: Literal["cloned"]


class DestroySandboxResponse(BaseModel):
    sandbox_id: str
    status: Literal["destroyed", "not_found"]


class Sandbox:
    _MANAGED_LABEL = "com.pr-reviewer.sandbox"
    _MANAGED_VALUE = "true"
    _instance: ClassVar[Self | None] = None

    @classmethod
    def get_instance(cls) -> Self:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self, image="pr-reviewer-sandbox:ci", cpus=2, memory="6g"):
        self.client = docker.from_env()
        self.image = image
        self.cpus = cpus
        self.memory = memory

    async def create_sandbox(self):
        container = await asyncio.to_thread(
            self.client.containers.run,
            image=self.image,
            command=["sleep", "infinity"],
            working_dir="/workspace",
            nano_cpus=int(self.cpus * 1_000_000_000),
            mem_limit=self.memory,
            labels={self._MANAGED_LABEL: self._MANAGED_VALUE},
            detach=True,
        )
        return container.id

    async def _get_container(self, sandbox_id, missing_ok=False):
        try:
            container = await asyncio.to_thread(
                self.client.containers.get,
                sandbox_id,
            )
            await asyncio.to_thread(container.reload)
        except NotFound:
            if missing_ok:
                return None
            raise SandboxError("sandbox does not exist") from None

        if container.labels.get(self._MANAGED_LABEL) != self._MANAGED_VALUE:
            raise SandboxError("container is not managed by the sandbox")
        return container

    async def exec(self, sandbox_id, cmd, workdir=None, environment=None):
        container = await self._get_container(sandbox_id)

        result = await asyncio.to_thread(
            container.exec_run,
            cmd,
            workdir=workdir,
            environment=environment,
            demux=True,
        )
        stdout, stderr = result.output
        return result.exit_code, self._decode(stdout), self._decode(stderr)

    async def clone(
        self,
        sandbox_id,
        owner,
        repo,
        pull_number,
        base_sha,
        head_sha,
        access_token=None,
    ):
        if pull_number < 1:
            raise SandboxError("pull number must be greater than zero")
        if not re.fullmatch(r"[0-9a-fA-F]{40}", base_sha):
            raise SandboxError("base_sha must be a full 40-character commit SHA")
        if not re.fullmatch(r"[0-9a-fA-F]{40}", head_sha):
            raise SandboxError("head_sha must be a full 40-character commit SHA")

        url = f"https://github.com/{owner}/{repo}.git"
        environment = None
        if access_token:
            credentials = base64.b64encode(
                f"x-access-token:{access_token}".encode()
            ).decode()
            environment = {
                "GIT_CONFIG_COUNT": "1",
                "GIT_CONFIG_KEY_0": "http.extraHeader",
                "GIT_CONFIG_VALUE_0": f"Authorization: Basic {credentials}",
            }
        commands = [
            (["git", "init", "repo"], "/workspace"),
            (["git", "remote", "add", "origin", url], "/workspace/repo"),
            (
                [
                    "git",
                    "fetch",
                    "--depth",
                    "1",
                    "--no-tags",
                    "origin",
                    base_sha,
                ],
                "/workspace/repo",
            ),
            (
                [
                    "git",
                    "fetch",
                    "--depth",
                    "1",
                    "--no-tags",
                    "origin",
                    f"refs/pull/{pull_number}/head",
                ],
                "/workspace/repo",
            ),
            (["git", "checkout", "--detach", "FETCH_HEAD"], "/workspace/repo"),
        ]

        for command, workdir in commands:
            result = await self.exec(
                sandbox_id,
                command,
                workdir=workdir,
                environment=environment,
            )
            if result[0] != 0:
                return result

        result = await self.exec(
            sandbox_id,
            ["git", "rev-parse", "HEAD"],
            workdir="/workspace/repo",
            environment=environment,
        )
        if result[0] != 0:
            return result

        actual_sha = result[1].strip()
        if actual_sha.lower() != head_sha.lower():
            return (
                1,
                actual_sha,
                f"checked out commit {actual_sha}, expected {head_sha}",
            )

        return 0, actual_sha, result[2]

    # --------------------------------------------------------------- teardown

    async def destroy_sandbox(self, sandbox_id):
        container = await self._get_container(sandbox_id, missing_ok=True)
        if container is None:
            return False

        try:
            await asyncio.to_thread(
                container.remove,
                force=True,
                v=True,
            )
        except NotFound:
            return False
        return True

    @staticmethod
    def _decode(value):
        return value.decode("utf-8", errors="replace") if value else ""
