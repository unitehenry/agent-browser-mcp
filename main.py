import os

from fastmcp import FastMCP
from fastmcp.tools import Tool
from fastmcp.client.transports import StdioTransport
from fastmcp.server import create_proxy
from fastmcp.tools.tool_transform import ArgTransform

if __name__ == "__main__":
    import asyncio

    transport = StdioTransport(command="agent-browser", args=["mcp"])
    proxy = create_proxy(transport, name="AgentBrowserProxy")

    mcp = FastMCP("AgentBrowser")

    async def main():
        for tool in await proxy.list_tools():
            mcp.add_tool(
                Tool.from_tool(
                    tool,
                    transform_args={
                        "extraArgs": ArgTransform(
                            default=["--cdp", os.getenv("CDP_PORT", "9222")]
                        ),
                    },
                )
            )

    asyncio.run(main())

    mcp.run(transport="sse", port=8000)
