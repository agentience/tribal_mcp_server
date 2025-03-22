# filename: mcp_server_tribal/_scripts/__init__.py
#
# Copyright (c) 2025 Agentience.ai
# Author: Troy Molander
# License: MIT License - See LICENSE file for details
#
# Version: 0.1.0

"""Docker management scripts for Tribal."""


import os
import subprocess
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Get the project root directory."""
    # This assumes the script is in src/mcp_server_tribal/_scripts
    return Path(__file__).parent.parent.parent.parent


def run_command(command: str, description: str) -> int:
    """Run a shell command and print its output."""
    print(f"{description}...")

    # Get the project root directory
    root_dir = get_project_root()

    # Create data directory if it doesn't exist
    data_dir = root_dir / "data"
    data_dir.mkdir(exist_ok=True)

    # Run the command
    process = subprocess.run(
        command,
        shell=True,
        cwd=str(root_dir),
        text=True,
        capture_output=True,
    )

    # Print the output
    if process.stdout:
        print(process.stdout)

    # Print any errors
    if process.returncode != 0:
        print(f"Error: {process.stderr}", file=sys.stderr)

    return process.returncode


def docker_start() -> None:
    """Start the Docker containers."""
    exit_code = run_command("docker-compose up -d", "Starting MCP services in Docker")

    if exit_code == 0:
        # Get port values
        api_port = os.environ.get("API_PORT", "8000")
        mcp_port = os.environ.get("MCP_PORT", "5000")

        print("\nMCP services are running in Docker")
        print(f"FastAPI server is available at http://localhost:{api_port}")
        print(f"API Documentation is available at http://localhost:{api_port}/docs")
        print(f"MCP server is available at http://localhost:{mcp_port}")
        print("\nUse the following commands:")
        print("  - poetry run docker-logs: View server logs")
        print("  - poetry run docker-stop: Stop the servers")
        print("  - poetry run docker-redeploy: Rebuild and restart the servers")

    sys.exit(exit_code)


def docker_stop() -> None:
    """Stop the Docker containers."""
    exit_code = run_command("docker-compose down", "Stopping MCP services in Docker")

    if exit_code == 0:
        print("\nMCP services have been stopped")

    sys.exit(exit_code)


def docker_redeploy() -> None:
    """Redeploy the Docker containers."""
    # First down the containers
    exit_code = run_command(
        "docker-compose down", "Stopping MCP services for redeployment"
    )

    if exit_code != 0:
        sys.exit(exit_code)

    # Then rebuild and start them
    exit_code = run_command(
        "docker-compose up --build -d", "Rebuilding and starting MCP services in Docker"
    )

    if exit_code == 0:
        # Get port values
        api_port = os.environ.get("API_PORT", "8000")
        mcp_port = os.environ.get("MCP_PORT", "5000")

        print("\nMCP services have been redeployed")
        print(f"FastAPI server is available at http://localhost:{api_port}")
        print(f"API Documentation is available at http://localhost:{api_port}/docs")
        print(f"MCP server is available at http://localhost:{mcp_port}")

    sys.exit(exit_code)


def docker_logs() -> None:
    """Show the Docker container logs."""
    service = os.environ.get("SERVICE", "")

    if service and service in ["mcp-api", "mcp-server"]:
        exit_code = run_command(
            f"docker-compose logs --tail=100 -f {service}",
            f"Showing logs for {service}",
        )
    else:
        exit_code = run_command(
            "docker-compose logs --tail=100 -f", "Showing logs for all MCP services"
        )

    sys.exit(exit_code)
