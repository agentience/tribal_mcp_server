"""CLI commands for mcp_server_tribal"""
import argparse
import sys
import importlib
from typing import List, Optional
import subprocess

def run_mcp_server(args: List[str]) -> int:
    """Run the MCP server, forwarding all arguments"""
    from mcp_server_tribal.mcp_app import main
    return main(args)

def uvx_main() -> int:
    """Entry point for the uvx command"""
    parser = argparse.ArgumentParser(
        description="UVX command line interface for extensible tools"
    )
    parser.add_argument(
        "command", help="The command to run (e.g. 'tribal')"
    )
    
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
    print(f"tribal: {__version__}")
    try:
        from mcp import __version__ as mcp_version
        print(f"mcp: {mcp_version}")
    except ImportError:
        print("mcp: Not installed")
    
    # Print Python version
    print(f"Python: {sys.version.split()[0]}")

if __name__ == "__main__":
    sys.exit(uvx_main())