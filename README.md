# Agent Browser MCP

Proxy [`agent-browser mcp`](https://github.com/vercel-labs/agent-browser#setup) stdio over HTTP/SSE using [FastMCP](https://gofastmcp.com/servers/providers/proxy).

## Getting Started

```sh
# Build the image
podman build -t agent-browser-mcp .

# Start the MCP server
podman run -e CDP_PORT=9222 -p 8000:8000 agent-browser-mcp
```

## Environment Variables

|Variable|Default|Description|
|:-:|:-:|:-:|
|`MCP_TRANSPORT`|`sse`|The [FastMCP transport](https://gofastmcp.com/v3/servers/server#running-the-server) to use. (STDIO, HTTP, SSE)|
|`CDP_PORT`||The Chrome DevTools Protocol for `agent-browser` connect to.|

## Formatter

```sh
uvx ruff format
```

## Debugging

```sh
# Useful inspector tool for debugging
npx @modelcontextprotocol/inspector
```
