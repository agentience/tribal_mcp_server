# Claude Code Integration with Tribal Knowledge MCP

This document provides instructions for configuring Claude Code to use the Tribal Knowledge MCP for tracking programming errors and solutions.

## Overview

Tribal is a knowledge tracking tool that helps Claude remember and learn from programming errors and solutions. It uses the stdio-based Model Context Protocol (MCP) for seamless integration.

## Installation

### Prerequisites

- Python 3.12+
- Claude Code CLI

### Install Tribal

```bash
# Install globally with uv
uv tool install tribal

# Or install with pip
pip install tribal
```

### Configure Claude Code

Add Tribal as an MCP to Claude Code:

```bash
# Add to current project
claude mcp add tribal tribal

# Add globally (recommended)
claude mcp add --scope global tribal tribal
```

Verify it's configured correctly:

```bash
claude mcp list
```

## Using Tribal with Claude

When you start a Claude Code session, Tribal is automatically available through MCP. No extra code or imports are needed.

Claude will automatically:
1. Store programming errors and solutions
2. Search for similar errors when you encounter problems
3. Build a knowledge base specific to your coding patterns

### Available MCP Tools

Tribal provides these MCP tools to Claude:

1. `track_error` - Track a new error with its context
2. `find_similar_errors` - Find errors similar to a given query
3. `search_errors` - Search for errors by type, language, etc.
4. `get_error_by_id` - Get a specific error by ID
5. `delete_error` - Remove an error from the database
6. `get_api_status` - Check if the server is running

### Example Usage with Claude

When Claude encounters an error, it can:

```
I'll track this error and look for similar problems in our knowledge base.
```

When Claude finds a solution, it stores it for future reference:

```
I've found a solution! I'll store this in our knowledge base for next time.
```

### Commands for Claude

You can ask Claude to:

- "Look for similar errors in our Tribal knowledge base"
- "Store this solution to our error database"
- "Check if we've seen this error before"

## How It Works

1. Tribal uses ChromaDB to store error records and solutions
2. When Claude encounters an error, it sends the error details to Tribal
3. Tribal vectorizes the error and searches for similar ones
4. Claude gets back relevant solutions to suggest
5. New solutions are stored for future reference

## Customizing Tribal

You can customize the Tribal server by setting environment variables:

- `PERSIST_DIRECTORY` - Where to store the database (default: ./chroma_db)
- `API_KEY` - For authentication (default: dev-api-key)
- `REQUIRE_AUTH` - Whether to require authentication (default: false)

## Troubleshooting

If you encounter issues:

1. Make sure Tribal is installed: `which tribal`
2. Check it's properly configured: `claude mcp list`
3. Try running Tribal directly: `tribal version`
4. Look for error messages in the Claude output
5. Check the database directory exists and has proper permissions

For more help, visit the Tribal GitHub repository or consult the documentation.