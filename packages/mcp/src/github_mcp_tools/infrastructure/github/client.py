from collections.abc import Callable
from typing import Any

import httpx
from fastmcp.exceptions import ToolError
from pydantic import BaseModel, Field
from pr_logging.core import get_logger

logger = get_logger(__name__)


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

        logger.debug(
            "Initialized GitHub client for {}/{} with authentication={}",
            github_request.repository_owner,
            github_request.repository_name,
            bool(github_request.access_token),
        )

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
        logger.debug(
            "Sending GitHub GET request to '{}' with {} parameters",
            url,
            len(params or {}),
        )

        try:
            async with httpx.AsyncClient(
                headers=self._headers,
                timeout=5.0,
            ) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            logger.opt(exception=True).warning(
                "GitHub API request timed out"
            )
            raise GithubAPIError("GitHub API request timed out") from exc
        except httpx.HTTPStatusError as exc:
            logger.opt(exception=True).warning(
                "GitHub API returned HTTP status {}",
                exc.response.status_code,
            )
            try:
                message = exc.response.json().get("message", exc.response.text)
            except ValueError:
                message = exc.response.text
            raise GithubAPIError(
                f"GitHub API returned {exc.response.status_code}: {message}"
            ) from exc
        except httpx.RequestError as exc:
            logger.opt(exception=True).warning("GitHub API request failed")
            raise GithubAPIError(f"GitHub API request failed: {exc}") from exc

        logger.debug(
            "GitHub GET request completed with status {}",
            response.status_code,
        )

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
            logger.warning(
                "Rejected GitHub pagination request with invalid page {}",
                page,
            )
            raise ValueError("page must be greater than or equal to 1")

        response = await self._get(
            url=url,
            params={"per_page": page_size, "page": page},
        )
        payload = self._json(response)
        items = [parser(item) for item in payload]

        link_header = response.headers.get("Link", "")
        result = PaginatedResponse(
            items=items,
            page=page,
            has_next_page=('rel="next"' in link_header or len(payload) == page_size),
        )

        logger.debug(
            "Fetched {} GitHub items for page {} with has_next_page={}",
            len(result.items),
            page,
            result.has_next_page,
        )

        return result

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

    async def fetch_pr_infos(self, pull_number: int) -> PullRequest:
        response = await self._get(
            url=f"{self._base_url}/pulls/{pull_number}",
        )
        response = self._json(response)
        result = PullRequest(
            number=response["number"],
            title=response["title"],
            body=response["body"] or "",
            base_branch=response["base"]["ref"],
            base_sha=response["base"]["sha"],
            head_branch=response["head"]["ref"],
            head_sha=response["head"]["sha"],
        )

        logger.debug(
            "Fetched GitHub pull request #{} metadata",
            pull_number,
        )

        return result

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
