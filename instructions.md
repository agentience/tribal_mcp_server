# Claude Code Integration with Tribal

This document provides instructions for configuring Claude Code to use the Tribal server for tracking programming errors and solutions.

## Overview

Tribal is a production-ready MCP implementation that helps Claude remember and learn from programming errors. It provides both REST API and native MCP interfaces.

## Installation

### Prerequisites

- Python 3.12+
- Claude Code CLI
- Docker (for production deployment)

### Install Tribal

```bash
# Install globally with uv
uv tool install tribal

# Or install with pip
pip install tribal
```

### Configure Claude Code

Add the MCP server to Claude Code:

```bash
# Add with Docker (recommended)
claude mcp add knowledge --launch "docker-compose up -d"

# Add directly
claude mcp add knowledge --launch "tribal"
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

Tribal provides these MCP tools:

1. `add_error` - Create new error record (POST /errors)
2. `get_error` - Retrieve error by UUID (GET /errors/{id})
3. `update_error` - Modify existing error (PUT /errors/{id})
4. `delete_error` - Remove error record (DELETE /errors/{id})
5. `search_errors` - Find errors by criteria (GET /errors)
6. `find_similar` - Semantic similarity search (GET /errors/similar)
7. `get_token` - Obtain JWT token (POST /token)

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

## Configuration Options

Configure the MCP server with these environment variables:

- `MCP_PORT`: Server port (default: 5000)
- `MCP_API_URL`: Backend API URL (default: http://localhost:8000)
- `PERSIST_DIRECTORY`: ChromaDB storage path (default: ./chroma_db)
- `API_KEY`: Authentication key (required if REQUIRE_AUTH=true)
- `SECRET_KEY`: JWT signing key
- `AWS_ACCESS_KEY_ID`: For S3/DynamoDB integration
- `AWS_SECRET_ACCESS_KEY`: For cloud storage
- `AWS_S3_BUCKET`: For S3 persistence

## Troubleshooting

If you encounter issues:

1. Verify Tribal installation: `which tribal`
2. Check configuration: `claude mcp list`
3. Test server status: `tribal status`
4. Look for error messages in the Claude output
5. Check the database directory exists and has proper permissions

For more help, visit the Tribal GitHub repository or consult the documentation.
