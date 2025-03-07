# Learned Knowledge MCP

A Model Context Protocol (MCP) server for storing and retrieving error information from Claude Code sessions.

## Features

- Store and retrieve error information with context and solutions
- Vector-based similarity search for finding relevant past errors
- RESTful API with JSON data format
- Secure authentication using API keys
- Local storage with ChromaDB
- Extensible architecture for cloud deployment (AWS)

## Installation

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/learned_knowledge_mcp.git
cd learned_knowledge_mcp
```

2. Install Poetry if you don't have it already:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install dependencies:
```bash
poetry install
```

4. Activate the virtual environment:
```bash
poetry shell
```

## Usage

### Running the Server

There are several ways to run the server:

#### Using Poetry

Start the FastAPI server:

```bash
poetry run mcp-api
```

Start the MCP server (for Claude integration):

```bash
poetry run mcp-server
```

#### Using Python module

```bash
# FastAPI server
poetry run python -m learned_knowledge_mcp.app

# MCP server
poetry run python -m learned_knowledge_mcp.mcp_app
```

#### Command-line Options

For development mode with auto-reload:

```bash
poetry run mcp-api --reload
poetry run mcp-server --reload
```

To specify a custom port:

```bash
poetry run mcp-api --port 8080
poetry run mcp-server --port 5000
```

To automatically find an available port if the specified port is in use:

```bash
poetry run mcp-api --auto-port
poetry run mcp-server --auto-port
```

The FastAPI server will be available at http://localhost:8000 (or your specified port), with API documentation at http://localhost:8000/docs.
The MCP server will be available at http://localhost:5000 (or your specified port) for Claude and other MCP-compatible LLMs.

#### Environment Variables

You can set various environment variables to configure the servers:

```bash
# For the FastAPI server
PORT=8080 poetry run mcp-api

# For the MCP server
MCP_PORT=5000 MCP_API_URL=http://localhost:8080 poetry run mcp-server
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
- `API_KEY`: API key for accessing the FastAPI server (default: "dev-api-key")

### API Endpoints

- `POST /api/v1/errors/`: Create a new error record
- `GET /api/v1/errors/{error_id}`: Get an error record by ID
- `PUT /api/v1/errors/{error_id}`: Update an error record
- `DELETE /api/v1/errors/{error_id}`: Delete an error record
- `GET /api/v1/errors/`: Search for error records
- `GET /api/v1/errors/similar/`: Search for similar error records
- `POST /api/v1/token`: Get an authentication token

### Using the Client

The package includes a command-line client for interacting with the API:

```bash
# Add a new error record
poetry run mcp-client --action add --error-type ImportError --language python --error-message "No module named 'requests'" --solution-description "Install requests" --solution-explanation "You need to install the requests package"

# Get an error by ID
poetry run mcp-client --action get --id <error-id>

# Search for errors
poetry run mcp-client --action search --error-type ImportError --language python

# Find similar errors
poetry run mcp-client --action similar --query "ModuleNotFoundError: No module named 'pandas'"
```

For more options, run:

```bash
poetry run mcp-client --help
```

### Integration with Development Sessions

You can integrate the MCP server with your development workflow to automatically store and retrieve error information:

1. Start the MCP server using Docker:

```bash
poetry run docker-start
```

2. Use the API client in your code to record errors:

```python
from examples.api_client import MCPClient

# Exception handler that records errors to MCP
def handle_exception(exc_type, exc_value, exc_traceback):
    import traceback
    
    # Get the error details
    error_type = exc_type.__name__
    error_message = str(exc_value)
    stack_trace = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    # Initialize the client
    client = MCPClient("http://localhost:8000")
    
    # First, search for similar errors
    similar_errors = client.search_similar(f"{error_type}: {error_message}")
    
    if similar_errors:
        print("\n🔍 Found similar errors in the database:")
        for i, error in enumerate(similar_errors[:3], 1):
            print(f"\n--- Solution {i} ---")
            print(f"Description: {error['solution']['description']}")
            if error['solution'].get('code_fix'):
                print(f"Code fix: {error['solution']['code_fix']}")
            print(f"Explanation: {error['solution']['explanation']}")
    else:
        print("\n❓ No similar errors found in the database.")
        
        # Ask to save this error for future reference
        save = input("\nWould you like to save this error for future reference? (y/n): ")
        if save.lower() == 'y':
            solution_desc = input("Brief solution description: ")
            solution_explanation = input("Solution explanation: ")
            code_fix = input("Code fix (optional): ")
            
            # Save the error
            client.add_error(
                error_type=error_type,
                language="python",  # Modify as needed
                error_message=error_message,
                solution_description=solution_desc,
                solution_explanation=solution_explanation,
                code_fix=code_fix if code_fix else None,
                code_snippet=None,  # Add code snippet extraction if needed
                task_description="Error encountered during development"
            )
            print("✅ Error saved successfully!")
    
    # Print the original traceback
    traceback.__print_exception(exc_type, exc_value, exc_traceback)

# Set the exception handler
import sys
sys.excepthook = handle_exception
```

3. For interactive sessions like Jupyter notebooks, add this code to a cell:

```python
%load_ext autoreload
%autoreload 2

from examples.api_client import MCPClient

# Initialize the client
mcp_client = MCPClient("http://localhost:8000")

def search_error(error_message):
    """Search for solutions to an error."""
    results = mcp_client.search_similar(error_message)
    
    if results:
        print("\n🔍 Found similar errors:")
        for i, error in enumerate(results[:3], 1):
            print(f"\n--- Solution {i} ---")
            print(f"Description: {error['solution']['description']}")
            if error['solution'].get('code_fix'):
                print(f"Code fix: {error['solution']['code_fix']}")
            print(f"Explanation: {error['solution']['explanation']}")
    else:
        print("❓ No similar errors found.")
        
# Usage example:
# search_error("TypeError: cannot convert the series to int")
```

## Development

### Running Tests

```bash
poetry run pytest
```

For a specific test:

```bash
poetry run pytest tests/path_to_test.py::test_name
```

### Linting and Type Checking

```bash
poetry run ruff check .
poetry run mypy .
poetry run black .
```

### Development Installation

To install the package in development mode with all dependencies:

```bash
poetry install
```

To set up pre-commit hooks:

```bash
pip install pre-commit
pre-commit install
```

### Project Structure

This project follows the modern Python package structure with a `src` layout:

```
learned_knowledge_mcp/
├── src/
│   ├── learned_knowledge_mcp/  # Main package
│   │   ├── api/                # API endpoints
│   │   ├── models/             # Data models
│   │   ├── services/           # Business logic
│   │   └── utils/              # Utilities
│   └── examples/               # Example code and clients
├── tests/                      # Test suite
├── pyproject.toml              # Project metadata and dependencies
└── README.md                   # Documentation
```

Using a src layout provides several benefits:
- Ensures you're always testing the installed version of your package
- Prevents import confusion and accidental relative imports
- Creates a cleaner separation between your package and development files

### Managing Dependencies

Add a new dependency:

```bash
poetry add <package-name>
```

Add a development dependency:

```bash
poetry add --group dev <package-name>
```

Update dependencies:

```bash
poetry update
```

## Deployment

### Docker Deployment

The project includes Docker support with convenient poetry commands:

```bash
# Build and start the containers
poetry run docker-start

# View logs
poetry run docker-logs

# Stop the containers
poetry run docker-stop

# Rebuild and restart the containers (after code changes)
poetry run docker-redeploy
```

You can customize the deployment using environment variables:

```bash
API_PORT=8080 MCP_PORT=5000 REQUIRE_AUTH=true API_KEY=your-secret-key poetry run docker-start
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
         "launchCommand": "cd /path/to/learned_knowledge_mcp && poetry run mcp-server"
       }
     ]
   }
   ```

3. Restart Claude for Desktop

##### Option 2: Connect to Running Docker Container (Recommended for Production)

1. Ensure the Docker container is running:
   ```bash
   cd /path/to/learned_knowledge_mcp
   poetry run docker-start
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
claude mcp add knowledge --launch "cd /path/to/learned_knowledge_mcp && poetry run mcp-server"
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