from fastapi import FastAPI
from fastmcp.utilities.lifespan import combine_lifespans

from github_mcp_tools.servers import DOMAINS
from pr_logging.core import get_logger

logger = get_logger(__name__)


def build_app() -> FastAPI:
    logger.info(
        "Building MCP application with {} domains",
        len(DOMAINS),
    )

    domain_apps = {
        name: server.http_app(
            path="/mcp",
            stateless_http=True,
        )
        for name, server in DOMAINS.items()
    }

    for name in domain_apps:
        logger.debug(
            "Configured MCP domain '{}'",
            name,
        )

    combined_lifespan = combine_lifespans(
        *(domain_app.lifespan for domain_app in domain_apps.values())
    )

    fastapi_app = FastAPI(lifespan=combined_lifespan)
    for name, domain_app in domain_apps.items():
        fastapi_app.mount(f"/{name}", domain_app)

    logger.info("Built MCP application")

    return fastapi_app


app = build_app()
