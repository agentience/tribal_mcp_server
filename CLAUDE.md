# Tribal - CLAUDE.md

## Build/Lint/Test Commands
- Setup: `uv pip install -e .` - Install package in development mode
- Install dependencies: `uv pip install -r requirements.txt`
- Install dev dependencies: `uv pip install -r requirements-dev.txt`
- Create/update venv: `uv venv`
- Run server: `tribal` or `python -m mcp_server_tribal.mcp_app`
- Lint: `ruff check .`
- Type check: `mypy .`
- Run tests: `pytest`
- Run single test: `pytest tests/path_to_test.py::test_name`

## MCP Server Notes

### Docker Configuration
- Docker container name: `tribal`
- Docker exposed port: 8000 (mapped to internal port 5000)
- Docker image name: `tribal-mcp`
- Current state: Running in standard mode

### FastMCP Version Information
- **Server**: Using FastMCP 1.3.0+
  - Modern version with improved API
  - Supports the `mcp.run(transport='stdio')` interface for stdio MCPs
  - No need for the `@mcp.handle_execution` decorator anymore

### Claude Integration
- Claude Code CLI: Configure via `claude mcp add tribal tribal`
- For global installation: `claude mcp add --scope global tribal tribal`
- Server runs on demand when Claude needs it (stdio protocol)

## Code Style Guidelines
- **Framework**: FastAPI for REST API development
- **Imports**: Group imports (stdlib, 3rd-party, local) with blank lines between groups
- **Formatting**: Black for code formatting, line length 88
- **Types**: Use type annotations for all function definitions
- **Naming**: Snake_case for variables/functions, PascalCase for classes
- **Error Handling**: Use explicit exception handling with appropriate status codes
- **Documentation**: All public APIs should have docstrings in Google format
- **Structure**: Organize code into models, services, api, and utils modules

## Editor Config
- Use 4 spaces for indentation
- UTF-8 encoding for all files

## MCP Integration Instructions

### Error Tracking Integration

Claude should automatically load and use the MCP integration for tracking errors and solutions.

At the start of each session, Claude should:

1. Import the MCP plugin:
   ```python
   import sys
   sys.path.append('/path/to/directory/containing/script')  # Adjust path as needed
   import claude_mcp_plugin
   ```

2. When encountering an error:
   - Track the error using `claude_mcp_plugin.mcp_track_error(error_text, code_snippet, task_description)`
   - Look for similar errors automatically

3. After providing a solution that fixed an error:
   - Store the solution using:
   ```python
   claude_mcp_plugin.mcp_store_solution(
       solution_description="Brief description",
       solution_explanation="Detailed explanation of why this works",
       language="python",  # or js, rust, etc.
       framework="fastapi",  # optional
       code_fix="fixed code",  # optional
       references=["https://docs.example.com"]  # optional
   )
   ```
