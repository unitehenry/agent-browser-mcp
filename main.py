import os

from fastmcp import FastMCP
from fastmcp.tools import Tool
from fastmcp.client.transports import StdioTransport
from fastmcp.server import create_proxy
from fastmcp.tools.tool_transform import ArgTransform
from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware
from fastmcp.server.middleware import Middleware, MiddlewareContext
from fastmcp.exceptions import AuthorizationError
from fastmcp.server.auth import OAuthProxy
from fastmcp.server.auth.providers.jwt import JWTVerifier
from fastmcp.server.dependencies import get_access_token
from fastmcp.server.auth.providers.github import GitHubProvider

class AuthMiddleware(Middleware):
    async def on_request(self, context: MiddlewareContext, call_next):
        token = get_access_token()

        if token is None:
            raise AuthorizationError("Unauthorized")

        if token.claims.get("login") != "unitehenry":
            print(token.claims)

        result = await call_next(context)

        return result

def auth():
    if not os.getenv("GITHUB_CLIENT_ID"): return None
    if not os.getenv("GITHUB_CLIENT_SECRET"): return None
    if not os.getenv("BASE_URL"): return None

    return GitHubProvider(
        client_id=os.getenv("GITHUB_CLIENT_ID"),
        client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
        base_url=os.getenv("BASE_URL")
    )

if __name__ == "__main__":
    import asyncio

    transport = StdioTransport(command="agent-browser", args=["mcp"])
    proxy = create_proxy(transport, name="AgentBrowserProxy")

    mcp = FastMCP("AgentBrowser", auth=auth())

    async def setup():
        for tool in await proxy.list_tools():
            mcp.add_tool(
                Tool.from_tool(
                    tool,
                    transform_args={
                        "extraArgs": ArgTransform(
                            default=["--cdp", os.getenv("CDP_PORT")]
                            if os.getenv("CDP_PORT")
                            else []
                        ),
                    },
                )
            )

        if mcp.auth:
            mcp.add_middleware(AuthMiddleware())

    asyncio.run(setup())

    mcp.run(transport=os.getenv("MCP_TRANSPORT", "sse"), host="0.0.0.0", port=8000)
