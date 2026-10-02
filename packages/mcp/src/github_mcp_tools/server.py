import uvicorn

from github_mcp_tools.app import app


def main() -> None:
    uvicorn.run(
        "github_mcp_tools.app:app",
        host="0.0.0.0",
        port=9000,
    )


__all__ = ["app", "main"]
