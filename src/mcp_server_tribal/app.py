# filename: mcp_server_tribal/app.py
#
# Copyright (c) 2025 Agentience.ai
# Author: Troy Molander
# License: MIT License - See LICENSE file for details
#
# Version: 0.1.0

"""Main application module for the MCP server."""


import argparse
import logging
import os
from typing import Dict

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .api import api_router
from .services.chroma_storage import ChromaStorage
from .services.storage_interface import StorageInterface

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


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


def get_storage() -> StorageInterface:
    """
    Get the storage service.

    This function serves as a FastAPI dependency that provides
    the storage service to API routes.

    Returns:
        An instance of the storage service
    """
    settings = get_settings()
    return ChromaStorage(persist_directory=settings["persist_directory"])


# Create FastAPI application
app = FastAPI(
    title="Tribal",
    description="Knowledge tracking tools for Claude and other LLMs",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register dependencies
app.dependency_overrides[StorageInterface] = get_storage

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root() -> Dict:
    """Root endpoint for the API."""
    return {
        "name": "Tribal",
        "version": "0.1.0",
        "description": "Knowledge tracking tools for Claude and other LLMs",
    }


@app.get("/health")
async def health_check() -> Dict:
    """Health check endpoint for the API."""
    return {"status": "ok"}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests."""
    logger.info(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    return response


def parse_args():
    """Parse command line arguments."""
    settings = get_settings()

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
        help=f"Port to bind the server to (default: {settings['default_port']})",
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


def main():
    """Run the application."""
    args = parse_args()
    port = args.port

    # Auto-select port if requested and the specified port is not available
    if args.auto_port and not is_port_available(args.host, port):
        original_port = port
        port = find_available_port(args.host, original_port)
        logger.info(f"Port {original_port} is in use, using port {port} instead")

    logger.info(f"Starting server on {args.host}:{port}")
    logger.info(f"Documentation available at http://{args.host}:{port}/docs")

    try:
        uvicorn.run(
            "mcp_server_tribal.app:app",
            host=args.host,
            port=port,
            reload=args.reload,
        )
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


if __name__ == "__main__":
    main()
