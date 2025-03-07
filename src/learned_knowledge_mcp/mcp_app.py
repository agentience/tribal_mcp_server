"""Main application module for the MCP server using FastMCP."""

import argparse
import json
import logging
import os
from typing import Dict, List, Optional
from uuid import UUID

import uvicorn
from fastmcp import FastMCP

from .models.error_record import ErrorQuery, ErrorRecord
from .services.chroma_storage import ChromaStorage
from .services.storage_interface import StorageInterface

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastMCP instance
mcp = FastMCP(
    title="Learned Knowledge MCP",
    description="Model Context Protocol server for storing and retrieving error information",
    version="0.1.0",
)

# Create storage instance
def get_settings() -> Dict:
    """Get application settings from environment variables."""
    
    # Parse port from environment or use default
    try:
        default_port = int(os.environ.get("PORT", 8000))
    except ValueError:
        default_port = 8000
        logger.warning(f"Invalid PORT value, using default: {default_port}")
    
    return {
        "persist_directory": os.environ.get("PERSIST_DIRECTORY", "./chroma_db"),
        "api_key": os.environ.get("API_KEY", "dev-api-key"),
        "secret_key": os.environ.get("SECRET_KEY", "insecure-dev-key-change-in-production"),
        "require_auth": os.environ.get("REQUIRE_AUTH", "false").lower() == "true",
        "default_port": default_port,
    }

settings = get_settings()
storage = ChromaStorage(persist_directory=settings["persist_directory"])

# Create API key validator
def validate_api_key(api_key: str) -> bool:
    """Validate API key."""
    if not settings["require_auth"]:
        return True
    return api_key == settings["api_key"]

# Define MCP tools
@mcp.tool()
async def track_error(
    error_type: str,
    error_message: str,
    language: str,
    framework: Optional[str] = None,
    code_snippet: Optional[str] = None,
    task_description: Optional[str] = None,
    solution_description: str = "",
    solution_code_fix: Optional[str] = None,
    solution_explanation: str = "",
    solution_references: Optional[List[str]] = None,
) -> Dict:
    """
    Track an error and its solution in the knowledge base.
    
    Args:
        error_type: Type of error (e.g., ImportError, TypeError)
        error_message: The error message
        language: Programming language (e.g., python, javascript)
        framework: Framework used (e.g., fastapi, react)
        code_snippet: The code that caused the error
        task_description: What the user was trying to accomplish
        solution_description: Brief description of the solution
        solution_code_fix: Code that fixes the error
        solution_explanation: Detailed explanation of why the solution works
        solution_references: List of reference links
        
    Returns:
        The created error record
    """
    if not solution_references:
        solution_references = []
    
    error_data = ErrorRecord(
        error_type=error_type,
        context={
            "language": language,
            "error_message": error_message,
            "framework": framework,
            "code_snippet": code_snippet,
            "task_description": task_description
        },
        solution={
            "description": solution_description,
            "code_fix": solution_code_fix,
            "explanation": solution_explanation,
            "references": solution_references
        }
    )
    
    error_record = await storage.add_error(error_data)
    return json.loads(error_record.model_dump_json())


@mcp.tool()
async def find_similar_errors(query: str, max_results: int = 5) -> List[Dict]:
    """
    Find errors similar to the given query.
    
    Args:
        query: Text to search for in the knowledge base
        max_results: Maximum number of results to return
        
    Returns:
        List of similar error records
    """
    records = await storage.search_similar(query, max_results)
    return [json.loads(record.model_dump_json()) for record in records]


@mcp.tool()
async def search_errors(
    error_type: Optional[str] = None,
    language: Optional[str] = None,
    framework: Optional[str] = None,
    error_message: Optional[str] = None,
    code_snippet: Optional[str] = None,
    task_description: Optional[str] = None,
    max_results: int = 5,
) -> List[Dict]:
    """
    Search for errors in the knowledge base.
    
    Args:
        error_type: Type of error to filter by
        language: Programming language to filter by
        framework: Framework to filter by
        error_message: Error message to search for
        code_snippet: Code snippet to search for
        task_description: Task description to search for
        max_results: Maximum number of results to return
        
    Returns:
        List of matching error records
    """
    query = ErrorQuery(
        error_type=error_type,
        language=language,
        framework=framework,
        error_message=error_message,
        code_snippet=code_snippet,
        task_description=task_description,
        max_results=max_results
    )
    
    records = await storage.search_errors(query)
    return [json.loads(record.model_dump_json()) for record in records]


@mcp.tool()
async def get_error_by_id(error_id: str) -> Optional[Dict]:
    """
    Get an error record by its ID.
    
    Args:
        error_id: UUID of the error record
        
    Returns:
        The error record or None if not found
    """
    try:
        uuid_id = UUID(error_id)
        record = await storage.get_error(uuid_id)
        if record:
            return json.loads(record.model_dump_json())
        return None
    except ValueError:
        return None


@mcp.tool()
async def delete_error(error_id: str) -> bool:
    """
    Delete an error record.
    
    Args:
        error_id: UUID of the error record
        
    Returns:
        True if deleted, False if not found
    """
    try:
        uuid_id = UUID(error_id)
        return await storage.delete_error(uuid_id)
    except ValueError:
        return False


@mcp.tool()
async def get_api_status() -> Dict:
    """
    Check the API status.
    
    Returns:
        API status information
    """
    return {
        "status": "ok",
        "name": "Learned Knowledge MCP",
        "version": "0.1.0",
    }


@mcp.handle_execution
async def handle_execution(tool_name: str, params: Dict) -> Dict:
    """
    Handle tool execution.
    
    Args:
        tool_name: Name of the tool to execute
        params: Tool parameters
        
    Returns:
        Tool execution result
    """
    logger.info(f"Executing tool: {tool_name} with params: {json.dumps(params)}")
    
    if tool_name == "track_error":
        return await track_error(**params)
    elif tool_name == "find_similar_errors":
        return await find_similar_errors(**params)
    elif tool_name == "search_errors":
        return await search_errors(**params)
    elif tool_name == "get_error_by_id":
        return await get_error_by_id(**params)
    elif tool_name == "delete_error":
        return await delete_error(**params)
    elif tool_name == "get_api_status":
        return await get_api_status()
    else:
        logger.error(f"Unknown tool: {tool_name}")
        raise ValueError(f"Unknown tool: {tool_name}")


def is_port_available(host, port):
    """Check if a port is available."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except socket.error:
            return False


def find_available_port(host, start_port, max_attempts=100):
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(host, port):
            return port
    raise RuntimeError(f"Could not find an available port after {max_attempts} attempts")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the MCP server")
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind the server to",
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=settings["default_port"], 
        help=f"Port to bind the server to (default: {settings['default_port']})"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development",
    )
    parser.add_argument(
        "--auto-port",
        action="store_true",
        help="Automatically find an available port if the specified port is in use",
    )
    return parser.parse_args()


def main():
    """Run the application."""
    args = parse_args()
    port = args.port
    
    # Auto-select port if requested and the specified port is not available
    if args.auto_port and not is_port_available(args.host, port):
        original_port = port
        port = find_available_port(args.host, original_port)
        logger.info(f"Port {original_port} is in use, using port {port} instead")
    
    logger.info(f"Starting MCP server on {args.host}:{port}")
    
    try:
        uvicorn.run(
            mcp.app,
            host=args.host,
            port=port,
            reload=args.reload,
        )
    except OSError as e:
        if "Address already in use" in str(e) and not args.auto_port:
            logger.error(f"Port {port} is already in use. Use --auto-port to automatically select an available port.")
            next_port = find_available_port(args.host, port + 1)
            logger.info(f"You can try using port {next_port} which appears to be available.")
        raise


if __name__ == "__main__":
    main()