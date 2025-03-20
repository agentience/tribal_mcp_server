# Tribal - Knowledge Tracking Implementation

Tribal is an MCP (Model Context Protocol) server implementation for error knowledge tracking and retrieval. Provides both REST API and native MCP interfaces for integration with tools like Claude Code and Cline.

## Features

- Store and retrieve error records with full context
- Vector similarity search using ChromaDB
- REST API (FastAPI) and native MCP interfaces
- JWT authentication with API keys
- Local storage (ChromaDB) and AWS integration
- Docker-compose deployment
- CLI client integration

## Installation

### Using uv (Recommended)

If you have uv installed (https://github.com/astral-sh/uv), you can use it to install Tribal as a tool:

```bash
# Install as a global tool (recommended)
uv tool install tribal

# Or install in development mode
cd /path/to/tribal
uv tool install -e .
```

### Using pip

Alternatively, you can use pip:

```bash
# Install with pip
pip install tribal

# Or install in development mode
cd /path/to/tribal
pip install -e .
```

### Integration with Claude

```bash
# Add to Claude
claude mcp add knowledge --launch "tribal"

# Test the connection
claude mcp test knowledge
```

### Developer Installation

If you want to contribute or modify the code:

1. Prerequisites:
   - Python 3.12 or higher
   - uv package manager

2. Clone the repository:
   ```bash
   git clone https://github.com/yourorg/tribal.git
   cd tribal
   ```

3. Install uv if you don't have it already:
   ```bash
   curl -fsSL https://install.uv.tools | sh
   ```

4. Create a virtual environment and install dependencies:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt -r requirements-dev.txt
   uv pip install -e .
   ```

## Usage

### Running the Server

There are several ways to run the server:

#### Using the tribal command

The simplest way to run the server:

```bash
# Run the server (default)
tribal

# Get help
tribal help

# Show version
tribal version

# Run with specific options
tribal server --port 5000 --auto-port
```

#### Using Python modules

You can also run the server using Python modules:

```bash
# Run the Tribal server
python -m mcp_server_tribal.mcp_app

# Run the FastAPI backend server
python -m mcp_server_tribal.app
```


#### Command-line Options

For development mode with auto-reload:

```bash
mcp-api --reload
mcp-server --reload
```

To specify a custom port:

```bash
mcp-api --port 8080
mcp-server --port 5000
```

To automatically find an available port if the specified port is in use:

```bash
mcp-api --auto-port
mcp-server --auto-port
```

The FastAPI server will be available at http://localhost:8000 (or your specified port), with API documentation at http://localhost:8000/docs.
The MCP server will be available at http://localhost:5000 (or your specified port) for Claude and other MCP-compatible LLMs.

#### Environment Variables

You can set various environment variables to configure the servers:

```bash
# For the FastAPI server
PORT=8080 mcp-api

# For the MCP server
MCP_PORT=5000 MCP_API_URL=http://localhost:8080 mcp-server
```

### Environment Variables

#### FastAPI Server
- `PERSIST_DIRECTORY`: Directory for ChromaDB storage (default: "./chroma_db")
- `API_KEY`: API key for authentication (default: "dev-api-key")
- `SECRET_KEY`: Secret key for JWT token generation (default: "insecure-dev-key-change-in-production")
- `REQUIRE_AUTH`: Whether to require authentication (default: "false")
- `PORT`: Default port to use for the server (default: 8000)

#### MCP Server
- `MCP_API_URL`: URL of the FastAPI server (default: "http://localhost:8000")
- `MCP_PORT`: Default port for the MCP server (default: 5000)
- `MCP_HOST`: Host to bind the MCP server to (default: "0.0.0.0")

### API Endpoints

- `POST /errors`: Create new error record
- `GET /errors/{error_id}`: Get error by ID
- `PUT /errors/{error_id}`: Update error record
- `DELETE /errors/{error_id}`: Delete error
- `GET /errors`: Search errors by criteria
- `GET /errors/similar`: Find similar errors
- `POST /token`: Get authentication token

### Using the Client

The package includes a command-line client for interacting with the API:

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

For more options, run:

```bash
mcp-client --help
```

## Development

### Running Tests

```bash
pytest
```

For a specific test:

```bash
pytest tests/path_to_test.py::test_name
```

### Linting and Type Checking

```bash
ruff check .
mypy .
black .
```

### Development Installation

To install the package in development mode with all dependencies:

```bash
uv pip install -e .
uv pip install -r requirements-dev.txt
```

To set up pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

### Project Structure

This project follows the modern Python package structure with a `src` layout:

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
└── README.md                   # Project documentation
```

### Managing Dependencies

Add a new dependency:

```bash
uv pip add <package-name>
# Then update requirements.txt to include the new package
```

Add a development dependency:

```bash
uv pip add <package-name>
# Then update requirements-dev.txt to include the new package
```

Update dependencies:

```bash
uv pip sync requirements.txt requirements-dev.txt
```

## Deployment

### Docker Deployment

The project includes standard Docker Compose support:

```bash
# Build and start containers
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop containers
docker-compose down

# Restart with clean build
docker-compose down && docker-compose up -d --build
```

You can customize the deployment using environment variables:

```bash
API_PORT=8080 MCP_PORT=5000 REQUIRE_AUTH=true API_KEY=your-secret-key docker-start
```

Or you can use docker-compose directly:

```bash
# Build and start the containers
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the containers
docker-compose down
```

#### Claude for Desktop Integration

There are two ways to connect the MCP server to Claude for Desktop:

##### Option 1: Let Claude for Desktop Launch the Server

1. Open your Claude for Desktop App configuration at `~/Library/Application Support/Claude/claude_desktop_config.json` (create it if it doesn't exist)

2. Add the MCP server configuration:
   ```json
   {
     "mcpServers": [
       {
         "name": "knowledge",
         "launchCommand": "cd /path/to/tribal && python -m mcp_server_tribal.mcp_app"
       }
     ]
   }
   ```

3. Restart Claude for Desktop

##### Option 2: Connect to Running Docker Container (Recommended for Production)

1. Ensure the Docker container is running:
   ```bash
   cd /path/to/tribal
   docker-start
   ```

2. Verify the container is running correctly:
   ```bash
   docker ps | grep mcp
   ```
   You should see the container running with port 5000 exposed.

3. Open your Claude for Desktop App configuration at `~/Library/Application Support/Claude/claude_desktop_config.json`

4. Add the MCP server configuration pointing to the Docker container:
   ```json
   {
     "mcpServers": [
       {
         "name": "knowledge",
         "url": "http://localhost:5000"
       }
     ]
   }
   ```

5. Restart Claude for Desktop

6. In Claude for Desktop, you should now see a notification that it's connected to the "knowledge" MCP server

**Note:** The Docker container is configured to stay running continuously for reliable production use.

##### Claude Code CLI Integration

You can also connect the Claude Code CLI to your MCP server:

```bash
# For Docker container
claude mcp add knowledge http://localhost:5000

# For directly launched server
claude mcp add knowledge --launch "cd /path/to/tribal && python -m mcp_server_tribal.mcp_app"
```

To test the connection:
```bash
claude mcp list    # Verify your server is listed
claude mcp test knowledge
```

##### Using MCP Tools in Claude

Once connected, you can use the MCP tools in Claude by asking questions like:
- "Track this error: ImportError: No module named 'pandas'"
- "Find similar errors to 'TypeError: cannot convert the series to int'"
- "Get the error record with ID 123e4567-e89b-12d3-a456-426614174000"

### Cloud Deployment

The project includes placeholder implementations for AWS services:

- `S3Storage`: For storing error records in Amazon S3
- `DynamoDBStorage`: For using DynamoDB as the database

To use these implementations, extend the classes and configure AWS credentials as per AWS SDK requirements.

## License

[MIT License](LICENSE)
