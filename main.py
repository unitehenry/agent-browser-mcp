import os

from fastmcp import FastMCP
from fastmcp.client.transports import StdioTransport
from fastmcp.exceptions import AuthorizationError
from fastmcp.server import create_proxy
from fastmcp.server.auth.providers.github import GitHubProvider
from fastmcp.server.dependencies import get_access_token
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.tools import Tool
from fastmcp.tools.tool_transform import ArgTransform
from starlette.requests import Request
from starlette.responses import PlainTextResponse, RedirectResponse


def resolve_hostname(url):
    import socket
    from urllib.parse import urlparse, urlunparse

    parsed = urlparse(url)

    if not parsed.hostname:
        return url

    try:
        ip = socket.gethostbyname(parsed.hostname)
    except socket.gaierror:
        return url

    # Rebuild netloc (host:port)
    netloc = ip

    if parsed.port is not None:
        netloc = f"{ip}:{parsed.port}"

    new_parsed = parsed._replace(netloc=netloc)

    return urlunparse(new_parsed)

class AuthMiddleware(Middleware):
    async def on_request(self, context: MiddlewareContext, call_next):
        token = get_access_token()

        if token is None:
            raise AuthorizationError("Unauthorized")

        if token.claims.get("login") != os.getenv("GITHUB_USERNAME", "").strip():
            raise AuthorizationError("Unauthorized")

        result = await call_next(context)

        return result


def auth():
    if not os.getenv("GITHUB_CLIENT_ID"):
        return None
    if not os.getenv("GITHUB_CLIENT_SECRET"):
        return None
    if not os.getenv("GITHUB_USERNAME"):
        return None
    if not os.getenv("BASE_URL"):
        return None

    return GitHubProvider(
        client_id=os.getenv("GITHUB_CLIENT_ID"),
        client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
        base_url=os.getenv("BASE_URL"),
    )


if __name__ == "__main__":
    import asyncio

    transport = StdioTransport(command="agent-browser", args=["mcp"])
    proxy = create_proxy(transport, name="AgentBrowserProxy")

    mcp = FastMCP("AgentBrowser", auth=auth())

    @mcp.custom_route("/healthz", methods=["GET"])
    async def health_check(request: Request) -> PlainTextResponse:
        return PlainTextResponse("OK")

    @mcp.custom_route("/", methods=["GET"])
    async def redirect(request: Request) -> PlainTextResponse:
        if os.getenv("REDIRECT_URL"):
          return RedirectResponse(url=os.getenv("REDIRECT_URL"), status_code=301)
        return PlainTextResponse("OK")

    async def setup():
        for tool in await proxy.list_tools():
            mcp.add_tool(
                Tool.from_tool(
                    tool,
                    transform_args={
                        "extraArgs": ArgTransform(
                            hide = True,
                            default_factory=lambda: ["--cdp", resolve_hostname(os.getenv("CDP_PORT"))]
                            if os.getenv("CDP_PORT")
                            else list
                        ),
                    },
                )
            )

        if mcp.auth:
            mcp.add_middleware(AuthMiddleware())

    asyncio.run(setup())

    mcp.run(transport=os.getenv("MCP_TRANSPORT", "sse"), host="0.0.0.0", port=8000, path=os.getenv("MCP_PATH", None))
