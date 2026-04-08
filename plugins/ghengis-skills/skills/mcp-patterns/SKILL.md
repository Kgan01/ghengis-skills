---
name: mcp-patterns
description: Use when working with MCP (Model Context Protocol) servers -- covers server types, registration patterns, the meta-tool pattern for context reduction, Context7 integration, and common anti-patterns
---

# MCP Patterns

Model Context Protocol (MCP) is the standard for connecting AI assistants to external tool providers. This skill covers server types, configuration patterns, the meta-tool pattern for context reduction, Context7 library documentation lookups, and common anti-patterns.

## When This Applies

- Configuring or connecting to an MCP server
- Calling tools exposed by an MCP server (e.g., Context7, Supabase, Cloudflare)
- Reducing context size by consolidating tool schemas
- Debugging MCP server connection or tool call failures

## Key Concepts

### Server Types

| Type | Transport | Use Case | Example |
|------|-----------|----------|---------|
| **npx** | stdin/stdout | npm-published servers, run via `npx` | Context7, Supabase, Vercel |
| **stdio** | stdin/stdout | Local process servers | Custom Python/Node servers |
| **SSE** | HTTP Server-Sent Events | Remote HTTP servers | Self-hosted or cloud servers |

### Configuration in Claude Code

MCP servers are declared in `.claude/settings.json` or project-level `mcp_config.json`. Claude Code manages the lifecycle.

**npx server (most common)**
```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}
```

**Local stdio server**
```json
{
  "mcpServers": {
    "my-local-tool": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": {
        "API_KEY": "${MY_API_KEY}"
      }
    }
  }
}
```

**Remote SSE server**
```json
{
  "mcpServers": {
    "remote-tools": {
      "url": "https://my-mcp-server.example.com/sse",
      "headers": {
        "Authorization": "Bearer ${MCP_TOKEN}"
      }
    }
  }
}
```

### Meta-Tool Pattern

Instead of registering every tool from an MCP server as an individual schema (which can mean 50-200 tool definitions flooding the context window), use a single meta-tool that routes to the right server and tool at call time.

**Why it matters:**
- An MCP server with 50 tools = 50 individual tool schemas in context
- A meta-tool pattern reduces this to 1 schema + a tool catalog lookup
- Achieves 10-50x context reduction depending on server complexity

**How to implement:**
```python
# Instead of 50 individual tool registrations:
# register_tool("context7_resolve_library")
# register_tool("context7_query_docs")
# ... 48 more

# Use a single meta-tool:
def mcp_call(server: str, tool: str, args: dict) -> dict:
    """Route a tool call to the named MCP server."""
    return mcp_client.call_tool(server, tool, args)
```

**In Claude Code:** Claude Code already manages MCP tool exposure through its built-in MCP client. When you add a server to settings, its tools appear via `ToolSearch`. Use `ToolSearch` to discover available tools without loading all schemas upfront.

### Tool Schema Structure

Every MCP tool follows this structure:
```json
{
  "name": "query-docs",
  "description": "Search library documentation",
  "inputSchema": {
    "type": "object",
    "properties": {
      "libraryId": { "type": "string" },
      "query": { "type": "string" }
    },
    "required": ["libraryId", "query"]
  }
}
```

## Common Patterns

### Context7 Two-Step Lookup

Context7 provides up-to-date library documentation. Always use the two-step pattern:

```
Step 1: Resolve the library name to an ID
  Tool: resolve-library-id
  Input: { "libraryName": "next.js" }
  Output: { "id": "/vercel/next.js" }

Step 2: Query the docs with the resolved ID
  Tool: query-docs
  Input: { "libraryId": "/vercel/next.js", "query": "app router dynamic routes" }
  Output: { "content": "..." }
```

Never skip the resolution step -- library IDs are not guessable.

### Preventing Duplicate Registration

When programmatically managing MCP servers, check before registering:
```python
if "context7" not in registered_servers:
    register_server("context7", ...)
```

Duplicate registration causes connection errors and resource leaks.

### Discovering Available Tools

In Claude Code, use `ToolSearch` to find tools from configured MCP servers:
```
ToolSearch: "context7"  -> lists all context7 tools
ToolSearch: "supabase"  -> lists all Supabase tools
```

This loads tool schemas on demand rather than flooding the context.

## Anti-Patterns

| Anti-Pattern | Why It's Bad | What to Do Instead |
|-------------|-------------|-------------------|
| Registering the same server twice | Connection errors, resource leaks | Check `registered_servers` before calling register |
| Using MCP for tools already available natively | Unnecessary latency, duplicate functionality | Prefer built-in tools (Bash, Read, Write, Grep, etc.) |
| Exposing SSE servers without auth | Security vulnerability -- anyone can call your tools | Always require `Authorization` headers for remote servers |
| Registering all tools individually | Context window bloat (50-200 schemas) | Use meta-tool pattern or deferred loading via ToolSearch |
| Hardcoding server URLs or tokens | Secrets leak, breaks across environments | Read from environment variables |
| Skipping Context7 resolve step | `query-docs` fails with invalid library ID | Always call `resolve-library-id` first |

## Validation Checklist

### After Configuring an MCP Server
- [ ] Server appears in `ToolSearch` results
- [ ] At least one tool call succeeds with expected response
- [ ] Environment variables are set (not hardcoded)
- [ ] No duplicate server names in configuration

### After Calling an MCP Tool
- [ ] Response is non-empty and matches expected schema
- [ ] Error cases return structured error messages (not connection failures)
- [ ] For Context7: `resolve-library-id` was called before `query-docs`

### Security
- [ ] Remote SSE servers require authentication headers
- [ ] API keys and tokens come from environment variables
- [ ] Server URLs use HTTPS for remote connections
- [ ] Sensitive data is not logged in tool call arguments
