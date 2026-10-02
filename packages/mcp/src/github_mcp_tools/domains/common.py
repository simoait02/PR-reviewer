from fastmcp.server.dependencies import get_http_headers

from github_mcp_tools.github_requests import GithubClient, GithubRequest


def get_github_token() -> str:
    headers = get_http_headers(include={"x-github-token"})
    return headers.get("x-github-token", "")


def get_client(
    repository_owner: str,
    repository_name: str,
) -> GithubClient:
    return GithubClient(
        GithubRequest(
            repository_owner=repository_owner,
            repository_name=repository_name,
            access_token=get_github_token(),
        )
    )
