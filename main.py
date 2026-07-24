import os

from fastmcp import FastMCP
from fastmcp.tools import Tool
from fastmcp.client.transports import StdioTransport
from fastmcp.server import create_proxy
from fastmcp.tools.tool_transform import ArgTransform
from fastmcp.server.middleware.rate_limiting import RateLimitingMiddleware

if __name__ == "__main__":
    import asyncio

    transport = StdioTransport(command="agent-browser", args=["mcp"])
    proxy = create_proxy(transport, name="AgentBrowserProxy")

    mcp = FastMCP("AgentBrowser")

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

        mcp.add_middleware(
            RateLimitingMiddleware(max_requests_per_second=10.0, burst_capacity=20)
        )

    asyncio.run(setup())

    mcp.run(transport=os.getenv("MCP_TRANSPORT", "sse"), host="0.0.0.0", port=8000)
