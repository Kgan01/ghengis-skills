# MCP Patterns -- Evaluation

## TC-1: Configure npx MCP Server
- **prompt:** "I want to add Context7 as an MCP server in my Claude Code project"
- **context:** User has an existing `.claude/settings.json` and wants to connect to Context7 for library documentation lookups.
- **assertions:**
  - Output includes a valid JSON config block with `"command": "npx"` and `"args": ["-y", "@upstash/context7-mcp"]`
  - Server is declared under `"mcpServers"` key
  - No hardcoded API keys or tokens -- environment variables used if auth is needed
  - Mentions verifying the server appears in `ToolSearch` results after configuration
- **passing_grade:** 3/4 assertions must pass

## TC-2: Context7 Two-Step Lookup
- **prompt:** "Look up how dynamic routes work in Next.js using Context7"
- **context:** Context7 MCP server is already configured. User expects the skill to enforce the resolve-then-query pattern.
- **assertions:**
  - Calls `resolve-library-id` first with a library name (e.g., `"next.js"`)
  - Uses the resolved library ID in the subsequent `query-docs` call
  - Does not attempt to guess or hardcode the library ID
  - Returns documentation content relevant to the query topic
- **passing_grade:** 3/4 assertions must pass

## TC-3: Remote SSE Server with Auth
- **prompt:** "Set up a remote MCP server at https://tools.mycompany.com/sse that requires a bearer token"
- **context:** User wants to connect to a self-hosted SSE-based MCP server with authentication.
- **assertions:**
  - Config uses `"url"` field (not `"command"`) pointing to the SSE endpoint
  - Includes `"headers"` with `"Authorization": "Bearer ${MCP_TOKEN}"` referencing an environment variable
  - Uses HTTPS (not HTTP) for the remote URL
  - Warns against hardcoding the token value directly in the config
- **passing_grade:** 4/4 assertions must pass

## TC-4: Meta-Tool Pattern Explanation
- **prompt:** "I have an MCP server with 60 tools and my context window is getting huge. How do I fix this?"
- **context:** User is experiencing context bloat from registering too many individual tool schemas from a single MCP server.
- **assertions:**
  - Explains the meta-tool pattern (single routing tool instead of 60 individual registrations)
  - Quantifies the benefit (mentions context reduction, e.g., 10-50x fewer schemas)
  - Recommends using `ToolSearch` for deferred/on-demand loading in Claude Code
  - Does not recommend registering all 60 tools individually
- **passing_grade:** 3/4 assertions must pass

## TC-5: Duplicate Server Registration
- **prompt:** "I keep getting connection errors when my code registers MCP servers. What's wrong?"
- **context:** User's code registers the same MCP server multiple times in a loop without checking for existing registration.
- **assertions:**
  - Identifies duplicate registration as a likely cause of connection errors and resource leaks
  - Recommends checking `registered_servers` (or equivalent) before calling register
  - Provides a guard pattern (e.g., `if "server_name" not in registered_servers`)
  - Does not suggest disabling error handling or ignoring the errors
- **passing_grade:** 3/4 assertions must pass
