import json

from fastmcp import FastMCP
from fastmcp.tools import Tool, tool
from fastmcp.client.transports import StdioTransport
from fastmcp.server import create_proxy
from fastmcp.server.transforms import ToolTransform
from fastmcp.tools.tool_transform import ToolTransformConfig, ArgTransformConfig, ArgTransform

if __name__ == "__main__":
    import asyncio

    transport = StdioTransport(command="agent-browser", args=["mcp"])
    proxy = create_proxy(transport, name="AgentBrowserProxy")

    mcp = FastMCP("AgentBrowser")

    async def main():
        for tool in await proxy.list_tools():
            mcp.add_tool(Tool.from_tool(tool, transform_args={
                "extraArgs": ArgTransform(default=["--cdp", "9222"]),
            }))

    asyncio.run(main())

    mcp.run(transport="sse", port=8000)
