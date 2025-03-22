# filename: mcp_server_tribal/mcp_server.py
#
# Copyright (c) 2025 Agentience.ai
# Author: Troy Molander
# License: MIT License - See LICENSE file for details
#
# Version: 0.1.0

"""MCP server implementation for the Tribal API."""


import json
import logging
import os
from typing import Dict, List, Optional

import httpx
from fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Initialize FastMCP instance
mcp = FastMCP()

# Get environment variables
API_URL = os.environ.get("MCP_API_URL", "http://localhost:8000")
API_KEY = os.environ.get("MCP_API_KEY", "dev-api-key")


async def make_api_request(
    method: str,
    endpoint: str,
    data: Optional[Dict] = None,
    params: Optional[Dict] = None,
) -> dict:
    """
    Make an API request to the Tribal API.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        endpoint: API endpoint
        data: Request data
        params: Query parameters

    Returns:
        API response
    """
    url = f"{API_URL}{endpoint}"
    headers = {"X-API-Key": API_KEY}

    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(url, headers=headers, params=params)
        elif method == "POST":
            response = await client.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = await client.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = await client.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        if response.status_code >= 400:
            logger.error(f"API request failed: {response.status_code} {response.text}")
            response.raise_for_status()

        if response.status_code == 204:  # No content
            return {}

        return response.json()


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

    error_data = {
        "error_type": error_type,
        "context": {
            "language": language,
            "error_message": error_message,
            "framework": framework,
            "code_snippet": code_snippet,
            "task_description": task_description,
        },
        "solution": {
            "description": solution_description,
            "code_fix": solution_code_fix,
            "explanation": solution_explanation,
            "references": solution_references,
        },
    }

    return await make_api_request("POST", "/api/v1/errors/", data=error_data)


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
    params = {"query": query, "max_results": max_results}
    return await make_api_request("GET", "/api/v1/errors/similar/", params=params)


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
    params = {
        "error_type": error_type,
        "language": language,
        "framework": framework,
        "error_message": error_message,
        "code_snippet": code_snippet,
        "task_description": task_description,
        "max_results": max_results,
    }
    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}

    return await make_api_request("GET", "/api/v1/errors/", params=params)


@mcp.tool()
async def get_error_by_id(error_id: str) -> Dict:
    """
    Get an error record by its ID.

    Args:
        error_id: UUID of the error record

    Returns:
        The error record
    """
    return await make_api_request("GET", f"/api/v1/errors/{error_id}")


@mcp.tool()
async def get_api_status() -> Dict:
    """
    Check the API status.

    Returns:
        API status information
    """
    return await make_api_request("GET", "/health")


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
    elif tool_name == "get_api_status":
        return await get_api_status()
    else:
        logger.error(f"Unknown tool: {tool_name}")
        raise ValueError(f"Unknown tool: {tool_name}")


def main():
    """Start the MCP server."""
    import uvicorn

    # Get port from environment or use default
    port = int(os.environ.get("MCP_PORT", 5000))
    host = os.environ.get("MCP_HOST", "0.0.0.0")

    logger.info(f"Starting MCP server on {host}:{port}")
    logger.info(f"API URL: {API_URL}")

    # Check if API is available
    try:
        import asyncio

        asyncio.run(get_api_status())
        logger.info("Successfully connected to API")
    except Exception as e:
        logger.warning(f"Could not connect to API: {e}")
        logger.warning(f"Make sure the docker container is running on {API_URL}")

    uvicorn.run(mcp.app, host=host, port=port)


if __name__ == "__main__":
    main()
