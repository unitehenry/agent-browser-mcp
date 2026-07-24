## Environment Variables

|Variable|Default|Description|
|:-:|:-:|:-:|
|`MCP_TRANSPORT`|`sse`|The [FastMCP transport](https://gofastmcp.com/v3/servers/server#running-the-server) to use. (STDIO, HTTP, SSE)|
|`CDP_PORT`|`9222`|The Chrome DevTools Protocol for `agent-browser` connect to.|

## Formatter

```sh
uvx ruff format
```

## Debugging

```sh
# Useful inspector tool for debugging
npx @modelcontextprotocol/inspector
```
