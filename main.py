import json

from pydantic import Field
from fastmcp.client.transports import StdioTransport
from fastmcp.server import create_proxy
from fastmcp.server.transforms import ToolTransform
from fastmcp.tools.tool_transform import ToolTransformConfig, ArgTransformConfig


transport = StdioTransport(command="agent-browser", args=["mcp"])

proxy = create_proxy(transport, name="AgentBrowser")

if __name__ == "__main__":
    import asyncio

    async def main():
        tools = await proxy.list_tools()
        for tool in tools:
            transform = {}
            transform[tool.name] = ToolTransformConfig(arguments={"extraArgs": ArgTransformConfig(hide=False, default=json.dumps(["--cdp", "9222"]))})
            proxy.add_transform(ToolTransform(transform))

    asyncio.run(main())
    proxy.run(transport="sse", port=8000)
