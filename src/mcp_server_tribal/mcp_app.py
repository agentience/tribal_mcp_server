# filename: mcp_server_tribal/mcp_app.py
#
# Copyright (c) 2025 Agentience.ai
# Author: Troy Molander
# License: MIT License - See LICENSE file for details
#
# Version: 0.1.0

"""Main application module for Tribal - Knowledge tracking tools for Claude and other LLMs."""


import argparse
import json
import logging
import os
import sys
from typing import Dict, List, Optional
from uuid import UUID

from mcp.server.fastmcp import FastMCP

from .models.error_record import ErrorQuery, ErrorRecord
from .services.chroma_storage import ChromaStorage

# Configure logging
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastMCP instance
from mcp_server_tribal import __version__

mcp = FastMCP(
    title="Tribal",
    description="Knowledge tracking tools for Claude and other LLMs",
    version=__version__,
)


# Add system instructions for Claude
@mcp.resource(uri="tribal://instructions/system", name="Tribal System Instructions")
async def get_system_instructions():
    """Provide system instructions to Claude when the MCP server initializes."""
    return """
    # Tribal Knowledge System Instructions

    When working with software projects:

    - ALWAYS log issues and their solutions to the tribal knowledge system using the track_error tool
    - ALWAYS check the tribal knowledge system for similar errors and their solutions using the find_similar_errors tool before attempting to solve a problem

    These practices help build a collective knowledge base of common issues and proven solutions.
    """


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
        "secret_key": os.environ.get(
            "SECRET_KEY", "insecure-dev-key-change-in-production"
        ),
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
            "task_description": task_description,
        },
        solution={
            "description": solution_description,
            "code_fix": solution_code_fix,
            "explanation": solution_explanation,
            "references": solution_references,
        },
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
        max_results=max_results,
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
    from mcp_server_tribal import __version__

    return {
        "status": "ok",
        "name": "Tribal",
        "version": __version__,
    }


# FastMCP 1.3.0 doesn't need an explicit handle_execution
# The handle_execution functionality is now built in to FastMCP


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
    raise RuntimeError(
        f"Could not find an available port after {max_attempts} attempts"
    )


def parse_args(args=None):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Tribal - Knowledge tracking tools for Claude and other LLMs"
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Server command (default)
    server_parser = subparsers.add_parser(
        "server", help="Run the knowledge tracking server"
    )
    server_parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind the server to",
    )
    server_parser.add_argument(
        "--port",
        type=int,
        default=settings["default_port"],
        help=f"Port to bind the server to (default: {settings['default_port']})",
    )
    server_parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development",
    )
    server_parser.add_argument(
        "--auto-port",
        action="store_true",
        help="Automatically find an available port if the specified port is in use",
    )

    # Version command
    subparsers.add_parser("version", help="Show version information")

    # Help command
    subparsers.add_parser("help", help="Show help information")

    # Parse args
    parsed_args = parser.parse_args(args)

    # If no command is specified, default to "server"
    if not parsed_args.command:
        parsed_args.command = "server"
        # Add default server arguments if they're needed
        if not hasattr(parsed_args, "host"):
            parsed_args.host = "0.0.0.0"
        if not hasattr(parsed_args, "port"):
            parsed_args.port = settings["default_port"]
        if not hasattr(parsed_args, "reload"):
            parsed_args.reload = False
        if not hasattr(parsed_args, "auto_port"):
            parsed_args.auto_port = False

    return parsed_args


def main(sys_args=None):
    """Run the application."""
    args = parse_args(sys_args)

    # Handle different commands
    if args.command == "version":
        from mcp_server_tribal.cli.commands import print_version
        print_version()
        return 0

    if args.command == "help":
        parser = argparse.ArgumentParser(
            description="Tribal - Knowledge tracking tools for Claude and other LLMs"
        )
        parser.parse_args(["--help"])
        return 0

    # Handle server command (default)
    if args.command == "server":
        port = args.port

        # Auto-select port if requested and the specified port is not available
        if args.auto_port and not is_port_available(args.host, port):
            original_port = port
            port = find_available_port(args.host, original_port)
            logger.info(f"Port {original_port} is in use, using port {port} instead")

        logger.info(f"Starting Tribal Knowledge server on {args.host}:{port}")

        try:
            # In MCP 1.3.0, we use mcp.run() with 'sse' transport for HTTP connections
            # The transport parameter determines the protocol used (stdio or sse)
            mcp.run(transport="stdio")
            return 0
        except OSError as e:
            if "Address already in use" in str(e) and not args.auto_port:
                logger.error(
                    f"Port {port} is already in use. Use --auto-port to automatically select an available port."
                )
                next_port = find_available_port(args.host, port + 1)
                logger.info(
                    f"You can try using port {next_port} which appears to be available."
                )
            raise

    # Should never reach here if the command is valid
    return 1


if __name__ == "__main__":
    main()
