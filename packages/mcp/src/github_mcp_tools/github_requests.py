from typing import Any

import httpx
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
    patch: str | None = None
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


class GithubAPIError(RuntimeError):
    """Raised when a GitHub API request fails."""


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

    async def _get(
        self,
        url: str,
        params: dict[str, int] | None = None,
    ) -> httpx.Response:
        try:
            async with httpx.AsyncClient(
                headers=self._headers,
                timeout=5.0,
            ) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise GithubAPIError("GitHub API request timed out") from exc
        except httpx.HTTPStatusError as exc:
            try:
                message = exc.response.json().get("message", exc.response.text)
            except ValueError:
                message = exc.response.text
            raise GithubAPIError(
                f"GitHub API returned {exc.response.status_code}: {message}"
            ) from exc
        except httpx.RequestError as exc:
            raise GithubAPIError(f"GitHub API request failed: {exc}") from exc

        return response

    @staticmethod
    def _json(response: httpx.Response) -> Any:
        try:
            return response.json()
        except ValueError as exc:
            raise GithubAPIError("GitHub API returned invalid JSON") from exc

    async def fetch_pr_comments(self, pull_number: int) -> list[PRComment]:
        response = await self._get(
            url=f"{self._base_url}/issues/{pull_number}/comments",
        )
        comments = self._json(response)
        if not isinstance(comments, list):
            raise GithubAPIError("GitHub returned an invalid comments response")
        return [
            PRComment(
                id=comment["id"],
                author=comment["user"]["login"],
                body=comment["body"],
                created_at=comment["created_at"],
                author_association=comment["author_association"],
            )
            for comment in comments
        ]

    async def fetch_pr_files(
        self,
        pull_number: int,
        page: int = 1,
    ) -> list[PRFile]:
        """Fetch one page of changed files, with 15 files per page."""
        if page < 1:
            raise ValueError("page must be greater than or equal to 1")

        response = await self._get(
            url=f"{self._base_url}/pulls/{pull_number}/files",
            params={"per_page": 15, "page": page},
        )
        batch = self._json(response)
        if not isinstance(batch, list):
            raise GithubAPIError("GitHub returned an invalid files response")
        return [PRFile(**file) for file in batch]

    async def fetch_pr_infos(self, pull_number: int) -> PullRequest:
        response = await self._get(
            url=f"{self._base_url}/pulls/{pull_number}",
        )
        response = self._json(response)
        if not isinstance(response, dict):
            raise GithubAPIError("GitHub returned an invalid pull request response")
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
        response = await self._get(
            url=f"{self._base_url}/compare/{pr.base_sha}...{pr.head_sha}",
        )
        data = self._json(response)
        if not isinstance(data, dict) or not isinstance(data.get("files", []), list):
            raise GithubAPIError("GitHub returned an invalid comparison response")
        return [
            file_diff
            for file_diff in data.get("files", [])
            if file_diff.get("sha") == file.sha
        ]
