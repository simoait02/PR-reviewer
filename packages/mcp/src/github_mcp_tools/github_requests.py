import base64
from collections.abc import Callable
from typing import Any

import httpx
from fastmcp.exceptions import ToolError
from pydantic import BaseModel, Field


class GithubRequest(BaseModel):
    repository_owner: str = Field(...)
    repository_name: str = Field(...)
    access_token: str = Field(default="")


class PRReview(BaseModel):
    author: str | None = None
    body: str = ""
    state: str = "UNKNOWN"
    submitted_at: str | None = None


class PRReviewComment(BaseModel):
    author: str | None = None
    body: str = ""
    path: str | None = None
    line: int | None = None
    diff_hunk: str | None = None
    in_reply_to_id: int | None = None


class PaginatedResponse[T](BaseModel):
    items: list[T]
    page: int
    has_next_page: bool


class PRFile(BaseModel):
    filename: str
    sha: str  # blob sha of the file's content after the change
    status: str  # "added", "removed", "modified", "renamed"
    previous_filename: str | None = None  # only set when status == "renamed"


class RepositoryCodeMatch(BaseModel):
    path: str
    sha: str
    score: float | None = None
    html_url: str | None = None


class RepositoryCodeSearchResult(BaseModel):
    total_count: int
    incomplete_results: bool = False
    items: list[RepositoryCodeMatch]


class PRComment(BaseModel):
    author: str | None = None
    body: str = ""
    created_at: str | None = None


class PullRequest(BaseModel):
    number: int
    title: str
    body: str
    base_branch: str
    base_sha: str
    head_branch: str
    head_sha: str


class GithubAPIError(ToolError):
    """A safe, client-visible error from the GitHub API."""


class GithubClient:
    def __init__(self, github_request: GithubRequest) -> None:
        self.github_request = github_request

    @property
    def _base_url(self) -> str:
        return f"https://api.github.com/repos/{self.github_request.repository_owner}/{self.github_request.repository_name}"

    @property
    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10",
        }

        if self.github_request.access_token:
            headers["Authorization"] = f"Bearer {self.github_request.access_token}"

        return headers

    async def _get(
        self,
        url: str,
        params: dict[str, int | str] | None = None,
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
        return response.json()

    async def _fetch_paginated[T](
        self,
        *,
        url: str,
        page: int,
        page_size: int,
        parser: Callable[[dict[str, Any]], T],
    ) -> PaginatedResponse[T]:
        if page < 1:
            raise ValueError("page must be greater than or equal to 1")

        response = await self._get(
            url=url,
            params={"per_page": page_size, "page": page},
        )
        payload = self._json(response)
        items = [parser(item) for item in payload]

        link_header = response.headers.get("Link", "")
        return PaginatedResponse(
            items=items,
            page=page,
            has_next_page=('rel="next"' in link_header or len(payload) == page_size),
        )

    @staticmethod
    def _parse_pr_comment(comment: dict[str, Any]) -> PRComment:
        return PRComment(
            author=(comment.get("user") or {}).get("login"),
            body=comment.get("body") or "",
            created_at=comment.get("created_at"),
        )

    @staticmethod
    def _parse_pr_review_comment(comment: dict[str, Any]) -> PRReviewComment:
        return PRReviewComment(
            author=(comment.get("user") or {}).get("login"),
            body=comment.get("body") or "",
            path=comment.get("path"),
            line=comment.get("line"),
            diff_hunk=comment.get("diff_hunk"),
            in_reply_to_id=comment.get("in_reply_to_id"),
        )

    @staticmethod
    def _parse_pr_review(review: dict[str, Any]) -> PRReview:
        return PRReview(
            author=(review.get("user") or {}).get("login"),
            body=review.get("body") or "",
            state=review.get("state") or "UNKNOWN",
            submitted_at=review.get("submitted_at"),
        )

    @staticmethod
    def _parse_pr_file(file: dict[str, Any]) -> PRFile:
        return PRFile.model_validate(file)

    async def fetch_pr_comments(
        self,
        pull_number: int,
        page: int = 1,
    ) -> PaginatedResponse[PRComment]:
        """Fetch one page of conversation comments."""
        return await self._fetch_paginated(
            url=f"{self._base_url}/issues/{pull_number}/comments",
            page=page,
            page_size=100,
            parser=self._parse_pr_comment,
        )

    async def fetch_pr_review_comments(
        self,
        pull_number: int,
        page: int = 1,
    ) -> PaginatedResponse[PRReviewComment]:
        """Fetch one page of inline pull request review comments."""
        return await self._fetch_paginated(
            url=f"{self._base_url}/pulls/{pull_number}/comments",
            page=page,
            page_size=100,
            parser=self._parse_pr_review_comment,
        )

    async def fetch_pr_files(
        self,
        pull_number: int,
        page: int = 1,
    ) -> PaginatedResponse[PRFile]:
        """Fetch one page of changed files, with 15 files per page."""
        return await self._fetch_paginated(
            url=f"{self._base_url}/pulls/{pull_number}/files",
            page=page,
            page_size=15,
            parser=self._parse_pr_file,
        )

    async def search_repository_code(
        self,
        query: str,
        max_results: int = 20,
    ) -> RepositoryCodeSearchResult:
        """Search indexed repository code and return compact file matches."""
        response = await self._get(
            url="https://api.github.com/search/code",
            params={
                "q": f"{query} repo:{self.github_request.repository_owner}/"
                f"{self.github_request.repository_name}",
                "per_page": max_results,
            },
        )
        payload = self._json(response)
        return RepositoryCodeSearchResult(
            total_count=payload["total_count"],
            incomplete_results=payload["incomplete_results"],
            items=[
                RepositoryCodeMatch.model_validate(item) for item in payload["items"]
            ],
        )

    async def fetch_pr_infos(self, pull_number: int) -> PullRequest:
        response = await self._get(
            url=f"{self._base_url}/pulls/{pull_number}",
        )
        response = self._json(response)
        return PullRequest(
            number=response["number"],
            title=response["title"],
            body=response["body"] or "",
            base_branch=response["base"]["ref"],
            base_sha=response["base"]["sha"],
            head_branch=response["head"]["ref"],
            head_sha=response["head"]["sha"],
        )

    async def fetch_diff_content(
        self,
        pr: PullRequest,
        file: PRFile,
    ) -> dict[str, Any] | None:
        response = await self._get(
            url=f"{self._base_url}/compare/{pr.base_sha}...{pr.head_sha}",
        )
        data = self._json(response)
        files_by_filename = {
            file_diff["filename"]: file_diff
            for file_diff in data["files"]
            if file_diff.get("filename")
        }

        file_diff = files_by_filename.get(file.filename)
        if file_diff is None and file.previous_filename:
            file_diff = files_by_filename.get(file.previous_filename)

        if file_diff is not None:
            return {
                "filename": file_diff.get("filename") or file.filename,
                "patch": file_diff.get("patch"),
            }

        return None

    async def fetch_pr_reviews(
        self,
        pull_number: int,
        page: int = 1,
    ) -> PaginatedResponse[PRReview]:
        """Fetch one page of submitted pull request reviews."""
        return await self._fetch_paginated(
            url=f"{self._base_url}/pulls/{pull_number}/reviews",
            page=page,
            page_size=100,
            parser=self._parse_pr_review,
        )

    async def fetch_file_blob(self, file_sha: str) -> str:
        response = await self._get(
            url=f"{self._base_url}/git/blobs/{file_sha}",
        )

        content = self._json(response).get("content")
        if not isinstance(content, str):
            raise GithubAPIError("GitHub returned no blob content")

        return base64.b64decode(content).decode("utf-8")
