# Tribal - Knowledge Service

Tribal is an MCP (Model Context Protocol) server implementation for error knowledge tracking and retrieval. It provides both REST API and native MCP interfaces for integration with tools like Claude Code and Cline.

## Features

- Store and retrieve error records with full context
- Vector similarity search using ChromaDB
- REST API (FastAPI) and native MCP interfaces
- JWT authentication with API keys
- Local storage (ChromaDB) and AWS integration
- Docker-compose deployment
- CLI client integration

## Overview

Tribal helps Claude remember and learn from programming errors. When you start a Claude Code session, Tribal is automatically available through MCP without additional imports.

Claude will:
1. Store programming errors and solutions
2. Search for similar errors when you encounter problems
3. Build a knowledge base specific to your coding patterns

## Packaging and Installing Tribal with uv

### Prerequisites

- Python 3.12+
- uv package manager (recommended)

### Build and Install Steps

#### Option 1: Direct installation with uv

The simplest approach is to install directly from the current directory:

```bash
# From the project root directory
cd /path/to/tribal

# Install using uv
uv pip install .
```

#### Option 2: Development Installation

For development work where you want changes to be immediately reflected:

```bash
# From the project root directory
cd /path/to/tribal

# Install in development mode
uv pip install -e .
```

#### Option 3: Build the package first

If you want to build a distributable package:

```bash
# Make sure you're in the project root directory
cd /path/to/tribal

# Install the build package if needed
uv pip install build

# Build the package
python -m build

# This creates distribution files in the dist/ directory
# Now install the wheel file
uv pip install dist/tribal-0.1.0-py3-none-any.whl
```

#### Option 4: Using the `uv tool install` command

You can also use the tool installation approach:

```bash
# Install as a global tool
cd /path/to/tribal
uv tool install .

# Or install in development mode
uv tool install -e .
```

### Verification

After installation, verify that the tool is properly installed:

```bash
# Check the installation
which tribal

# Check the version
tribal version
```

### Integration with Claude

After installation, you can integrate with Claude:

```bash
# Add Tribal to Claude Code
claude mcp add tribal --launch "tribal"

# Verify the configuration
claude mcp list

# For Docker container
claude mcp add tribal http://localhost:5000
```

## Usage

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

When Claude encounters an error:
```
I'll track this error and look for similar problems in our knowledge base.
```

When Claude finds a solution:
```
I've found a solution! I'll store this in our knowledge base for next time.
```

### Commands for Claude

You can ask Claude to:
- "Look for similar errors in our Tribal knowledge base"
- "Store this solution to our error database"
- "Check if we've seen this error before"

### Running the Server

#### Using the tribal command

```bash
# Run the server
tribal

# Get help
tribal help

# Show version
tribal version

# Run with options
tribal server --port 5000 --auto-port
```

#### Using Python modules

```bash
# Run the Tribal server
python -m mcp_server_tribal.mcp_app

# Run the FastAPI backend server
python -m mcp_server_tribal.app
```

#### Using legacy entry points

```bash
# Legacy MCP server
mcp-server

# Legacy FastAPI server
mcp-api
```

### Command-line Options

```bash
# Development mode with auto-reload
mcp-api --reload
mcp-server --reload

# Custom port
mcp-api --port 8080
mcp-server --port 5000

# Auto port selection
mcp-api --auto-port
mcp-server --auto-port
```

The FastAPI server will be available at http://localhost:8000 with API documentation at /docs.
The MCP server will be available at http://localhost:5000 for Claude and other MCP-compatible LLMs.

### Environment Variables

#### FastAPI Server
- `PERSIST_DIRECTORY`: ChromaDB storage path (default: "./chroma_db")
- `API_KEY`: Authentication key (default: "dev-api-key")
- `SECRET_KEY`: JWT signing key (default: "insecure-dev-key-change-in-production")
- `REQUIRE_AUTH`: Authentication requirement (default: "false")
- `PORT`: Server port (default: 8000)

#### MCP Server
- `MCP_API_URL`: FastAPI server URL (default: "http://localhost:8000")
- `MCP_PORT`: MCP server port (default: 5000)
- `MCP_HOST`: Host to bind to (default: "0.0.0.0")
- `API_KEY`: FastAPI access key (default: "dev-api-key")
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_BUCKET`: For AWS integration

### API Endpoints

- `POST /errors`: Create new error record
- `GET /errors/{error_id}`: Get error by ID
- `PUT /errors/{error_id}`: Update error record
- `DELETE /errors/{error_id}`: Delete error
- `GET /errors`: Search errors by criteria
- `GET /errors/similar`: Find similar errors
- `POST /token`: Get authentication token

### Using the Client

```bash
# Add a new error record
mcp-client --action add --error-type ImportError --language python --error-message "No module named 'requests'" --solution-description "Install requests" --solution-explanation "You need to install the requests package"

# Get an error by ID
mcp-client --action get --id <error-id>

# Search for errors
mcp-client --action search --error-type ImportError --language python

# Find similar errors
mcp-client --action similar --query "ModuleNotFoundError: No module named 'pandas'"
```

### How It Works

1. Tribal uses ChromaDB to store error records and solutions
2. When Claude encounters an error, it sends the error details to Tribal
3. Tribal vectorizes the error and searches for similar ones
4. Claude gets back relevant solutions to suggest
5. New solutions are stored for future reference

## Development

### Running Tests

```bash
pytest
pytest tests/path_to_test.py::test_name  # For specific tests
```

### Linting and Type Checking

```bash
ruff check .
mypy .
black .
```

### GitHub Workflow

This project uses GitHub Actions for continuous integration and deployment. The workflow automatically runs tests, linting, and type checking on push to main and pull requests.

#### Workflow Steps

1. **Test**: Runs linting, type checking, and unit tests
   - Uses Python 3.12
   - Installs dependencies with uv
   - Runs ruff, black, mypy, and pytest

2. **Build and Publish**: Builds and publishes the package to PyPI
   - Triggered only on push to main branch
   - Uses Python's build system
   - Publishes to PyPI using twine

#### Testing Locally

You can test the GitHub workflow locally using the provided script:

```bash
# Make the script executable
chmod +x scripts/test-workflow.sh

# Run the workflow locally
./scripts/test-workflow.sh
```

This script simulates the GitHub workflow steps on your local machine:
- Checks Python version (3.12 recommended)
- Installs dependencies using uv
- Runs linting with ruff
- Checks formatting with black
- Runs type checking with mypy
- Runs tests with pytest
- Builds the package

Note: The script skips the publishing step for local testing.

### Project Structure

```
tribal/
├── src/
│   ├── mcp_server_tribal/      # Core package
│   │   ├── api/                # FastAPI endpoints
│   │   ├── cli/                # Command-line interface
│   │   ├── models/             # Pydantic models
│   │   ├── services/           # Service layer
│   │   │   ├── aws/            # AWS integrations
│   │   │   └── chroma_storage.py # ChromaDB implementation
│   │   └── utils/              # Utility functions
│   └── examples/               # Example usage code
├── tests/                      # pytest test suite
├── docker-compose.yml          # Docker production setup
├── pyproject.toml              # Project configuration
├── VERSIONING.md               # Versioning strategy documentation
├── CHANGELOG.md                # Version history
├── .bumpversion.cfg            # Version bumping configuration
└── README.md                   # Project documentation
```

## Versioning

Tribal follows [Semantic Versioning](https://semver.org/). See [VERSIONING.md](VERSIONING.md) for complete details about:

- Version numbering (MAJOR.MINOR.PATCH)
- Schema versioning for database compatibility
- Branch naming conventions
- Release and hotfix procedures

Check the version with:

```bash
# Display version information
tribal version
```

### Managing Dependencies

```bash
# Add a dependency
uv pip add <package-name>

# Add a development dependency
uv pip add <package-name>

# Update dependencies
uv pip sync requirements.txt requirements-dev.txt
```

## Deployment

### Docker Deployment

```bash
# Build and start containers
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop containers
docker-compose down

# With custom environment variables
API_PORT=8080 MCP_PORT=5000 REQUIRE_AUTH=true API_KEY=your-secret-key docker-start
```

### Claude for Desktop Integration

#### Option 1: Let Claude for Desktop Launch the Server

1. Open `~/Library/Application Support/Claude/claude_desktop_config.json`

2. Add the MCP server configuration (assumes Tribal tool is already installed):
   ```json
   {
     "mcpServers": [
       {
         "name": "tribal",
         "launchCommand": "tribal"
       }
     ]
   }
   ```

3. Restart Claude for Desktop

#### Option 2: Connect to Running Docker Container

1. Start the container:
   ```bash
   cd /path/to/tribal
   docker-start
   ```

2. Configure Claude for Desktop:
   ```json
   {
     "mcpServers": [
       {
         "name": "tribal",
         "url": "http://localhost:5000"
       }
     ]
   }
   ```

### Claude Code CLI Integration

```bash
# For Docker container
claude mcp add tribal http://localhost:5000

# For directly launched server
claude mcp add tribal --launch "tribal"

# Test the connection
claude mcp list
claude mcp test tribal
```

## Troubleshooting

1. Verify Tribal installation: `which tribal`
2. Check configuration: `claude mcp list`
3. Test server status: `tribal status`
4. Look for error messages in the Claude output
5. Check the database directory exists and has proper permissions

## Cloud Deployment

The project includes placeholder implementations for AWS services:
- `S3Storage`: For storing error records in Amazon S3
- `DynamoDBStorage`: For using DynamoDB as the database

## License

[MIT License](LICENSE)
