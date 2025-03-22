# filename: mcp_server_tribal/cli/commands.py
#
# Copyright (c) 2025 Agentience.ai
# Author: Troy Molander
# License: MIT License - See LICENSE file for details
#
# Version: 0.1.0

"""CLI commands for mcp_server_tribal"""

import argparse
import sys
from typing import List


def run_mcp_server(args: List[str]) -> int:
    """Run the MCP server, forwarding all arguments"""
    from mcp_server_tribal.mcp_app import main

    return main(args)


def uvx_main() -> int:
    """Entry point for the uvx command"""
    parser = argparse.ArgumentParser(
        description="UVX command line interface for extensible tools"
    )
    parser.add_argument("command", help="The command to run (e.g. 'tribal')")

    # First, handle the case where no arguments are provided
    if len(sys.argv) == 1:
        parser.print_help()
        return 0

    args, remaining = parser.parse_known_args()

    # Handle different commands
    if args.command == "tribal":
        return run_mcp_server(remaining)
    elif args.command == "help":
        parser.print_help()
        return 0
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        return 1


def print_version() -> None:
    """Print version information for the package and dependencies"""
    from mcp_server_tribal import __version__
    from mcp_server_tribal.services.chroma_storage import SCHEMA_VERSION, SCHEMA_COMPATIBILITY

    print(f"Tribal Version: {__version__}")
    print(f"Database Schema: {SCHEMA_VERSION}")

    # Show compatible schema versions
    compatible_versions = SCHEMA_COMPATIBILITY.get(__version__, [])
    if compatible_versions:
        print(f"Compatible Schema Versions: {', '.join(compatible_versions)}")

    # Print dependency versions
    try:
        from mcp import __version__ as mcp_version
        print(f"MCP Version: {mcp_version}")
    except ImportError:
        print("MCP: Not installed")

    # Print Python version
    print(f"Python: {sys.version.split()[0]}")

    # Print versioning info
    print("\nVersioning Strategy:")
    print("- Application follows Semantic Versioning (MAJOR.MINOR.PATCH)")
    print("- See VERSIONING.md for more information")


if __name__ == "__main__":
    sys.exit(uvx_main())
