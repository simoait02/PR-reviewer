import asyncio
import json
from typing import Any

import requests
from pydantic import BaseModel, Field


class GithubRequest(BaseModel):
    repository_owner: str = Field(...)
    repository_name: str = Field(...)
    access_token: str = Field(default="")


class PRFile(BaseModel):
    filename: str
    sha: str  # blob sha of the file's content after the change
    status: str  # "added", "removed", "modified", "renamed"
    additions: int
    deletions: int
    changes: int
    previous_filename: str | None = None  # only set when status == "renamed"


class PRComment(BaseModel):
    id: int
    author: str
    body: str
    created_at: str
    author_association: str


class PullRequest(BaseModel):
    number: int
    title: str
    body: str
    base_branch: str
    base_sha: str
    head_branch: str
    head_sha: str


class GithubClient:
    def __init__(self, github_request: GithubRequest) -> None:
        self.github_request = github_request

    @property
    def _base_url(self) -> str:
        return f"https://api.github.com/repos/{self.github_request.repository_owner}/{self.github_request.repository_name}"

    @property
    def _headers(self) -> dict[str, str]:
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.github_request.access_token}" if self.github_request.access_token else "",
            "X-GitHub-Api-Version": "2026-03-10",
        }

    async def fetch_pr_comments(self, pull_number: int) -> list[PRComment]:
        response = requests.get(
            url=f"{self._base_url}/issues/{pull_number}/comments",
            headers=self._headers,
        )
        return [
            PRComment(
                id=comment["id"],
                author=comment["user"]["login"],
                body=comment["body"],
                created_at=comment["created_at"],
                author_association=comment["author_association"],
            )
            for comment in response.json()
        ]

    async def fetch_pr_files(
        self,
        pull_number: int,
        page: int = 1,
    ) -> list[PRFile]:
        """Fetch one page of changed files, with 100 files per page."""
        response = requests.get(
            url=f"{self._base_url}/pulls/{pull_number}/files",
            headers=self._headers,
            params={"per_page": 100, "page": page},
        )
        response.raise_for_status()
        batch = response.json()
        return [PRFile(**file) for file in batch]

    async def fetch_pr_infos(self, pull_number: int) -> PullRequest:
        response = requests.get(
            url=f"{self._base_url}/pulls/{pull_number}",
            headers=self._headers,
        )
        response.raise_for_status()
        response = response.json()
        return PullRequest(
            number=response["number"],
            title=response["title"],
            body=response["body"],
            base_branch=response["base"]["ref"],
            base_sha=response["base"]["sha"],
            head_branch=response["head"]["ref"],
            head_sha=response["head"]["sha"],
        )

    async def fetch_diff_content(
        self,
        pr: PullRequest,
        file: PRFile,
    ) -> list[dict[str, Any]]:
        response = requests.get(
            url=f"{self._base_url}/compare/{pr.base_sha}...{pr.head_sha}",
            headers=self._headers,
        )
        response.raise_for_status()
        data = response.json()
        return [file_diff for file_diff in data.get("files", []) if file_diff["sha"] == file.sha]


async def run() -> None:
    github_request = GithubRequest(
        repository_owner="kubernetes",
        repository_name="kubernetes",
    )
    client = GithubClient(github_request)

    pr = await client.fetch_pr_infos(142409)

    files = await client.fetch_pr_files(142409)
    first_file = files[0]
    res = await client.fetch_diff_content(pr, first_file)
    print(json.dumps(res, indent=2))


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
