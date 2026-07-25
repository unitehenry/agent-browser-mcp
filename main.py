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

if __name__ == "__main__":
    import asyncio

    transport = StdioTransport(command="agent-browser", args=["mcp"])
    proxy = create_proxy(transport, name="AgentBrowserProxy")

    auth = GitHubProvider(
        client_id="Ov23liCRP7viT9hrgP0E",
        client_secret="74c442d0b92e762f09891ce5c060032e9e4a1228",
        base_url="https://dc92-172-92-31-26.ngrok-free.app"
    )

    mcp = FastMCP("AgentBrowser", auth=auth)

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

        mcp.add_middleware(AuthMiddleware())

    asyncio.run(setup())

    mcp.run(transport=os.getenv("MCP_TRANSPORT", "sse"), host="0.0.0.0", port=8000)
