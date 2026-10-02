from fastapi import FastAPI
from fastmcp.utilities.lifespan import combine_lifespans

from github_mcp_tools.domains import DOMAINS


def build_app() -> FastAPI:
    domain_apps = {
        name: server.http_app(
            path="/mcp",
            stateless_http=True,
        )
        for name, server in DOMAINS.items()
    }

    combined_lifespan = combine_lifespans(
        *(domain_app.lifespan for domain_app in domain_apps.values())
    )

    fastapi_app = FastAPI(lifespan=combined_lifespan)
    for name, domain_app in domain_apps.items():
        fastapi_app.mount(f"/{name}", domain_app)
    return fastapi_app


app = build_app()
