# filename: examples/api_client.py
#
# Copyright (c) 2025 Agentience.ai
# Author: Troy Molander
# License: MIT License - See LICENSE file for details
#
# Version: 0.1.0

"""Example script demonstrating how to use the MCP API."""


import argparse
import json

import requests


class MCPClient:
    """Client for interacting with the MCP API."""

    def __init__(self, base_url, api_key=None):
        """
        Initialize the MCP client.

        Args:
            base_url: Base URL of the MCP API
            api_key: API key for authentication (optional if auth is disabled)
        """
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}

        # Add authorization header if API key is provided
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

        # Check if authentication is required
        self.auth_required = True
        try:
            self.check_auth_required()
        except requests.RequestException:
            # If we can't check, assume auth is required
            pass

    def check_auth_required(self):
        """Check if the API requires authentication."""
        try:
            response = requests.get(f"{self.base_url}/api/v1/auth/status")
            if response.status_code == 200:
                data = response.json()
                self.auth_required = data.get("auth_required", True)
                if not self.auth_required:
                    print("Authentication is disabled for this API.")
        except requests.RequestException:
            # If we can't check, assume auth is required
            pass

    def add_error(
        self,
        error_type,
        language,
        error_message,
        solution_description,
        solution_explanation,
        framework=None,
        code_snippet=None,
        task_description=None,
        code_fix=None,
        references=None,
    ):
        """
        Add a new error record.

        Args:
            error_type: Type of the error
            language: Programming language
            error_message: Error message
            solution_description: Brief description of the solution
            solution_explanation: Detailed explanation of the solution
            framework: Optional framework name
            code_snippet: Optional code snippet that caused the error
            task_description: Optional description of the task being performed
            code_fix: Optional code that fixes the error
            references: Optional list of reference URLs

        Returns:
            The created error record
        """
        error_record = {
            "error_type": error_type,
            "context": {
                "language": language,
                "error_message": error_message,
            },
            "solution": {
                "description": solution_description,
                "explanation": solution_explanation,
            },
        }

        # Add optional fields
        if framework:
            error_record["context"]["framework"] = framework
        if code_snippet:
            error_record["context"]["code_snippet"] = code_snippet
        if task_description:
            error_record["context"]["task_description"] = task_description
        if code_fix:
            error_record["solution"]["code_fix"] = code_fix
        if references:
            error_record["solution"]["references"] = references

        response = requests.post(
            f"{self.base_url}/api/v1/errors/",
            headers=self.headers,
            json=error_record,
        )

        response.raise_for_status()
        return response.json()

    def get_error(self, error_id):
        """
        Get an error record by ID.

        Args:
            error_id: UUID of the error record

        Returns:
            The error record
        """
        response = requests.get(
            f"{self.base_url}/api/v1/errors/{error_id}",
            headers=self.headers,
        )

        response.raise_for_status()
        return response.json()

    def search_similar(self, query_text, max_results=5):
        """
        Search for error records with similar text content.

        Args:
            query_text: Text to search for
            max_results: Maximum number of results to return

        Returns:
            List of similar error records
        """
        response = requests.get(
            f"{self.base_url}/api/v1/errors/similar/",
            headers=self.headers,
            params={
                "query": query_text,
                "max_results": max_results,
            },
        )

        response.raise_for_status()
        return response.json()

    def search_errors(self, **kwargs):
        """
        Search for error records.

        Args:
            **kwargs: Search parameters (error_type, language, framework, etc.)

        Returns:
            List of matching error records
        """
        response = requests.get(
            f"{self.base_url}/api/v1/errors/",
            headers=self.headers,
            params=kwargs,
        )

        response.raise_for_status()
        return response.json()


def main():
    """Run the example script."""
    parser = argparse.ArgumentParser(description="MCP API Client Example")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL of the MCP API",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key for authentication (not needed if authentication is disabled)",
    )
    parser.add_argument(
        "--action",
        choices=["add", "get", "search", "similar"],
        required=True,
        help="Action to perform",
    )

    # Parse arguments
    args, remaining_args = parser.parse_known_args()

    # Create client
    client = MCPClient(args.url, args.api_key)

    # Perform action
    if args.action == "add":
        # Parse additional arguments for add action
        add_parser = argparse.ArgumentParser(description="Add Error Record")
        add_parser.add_argument("--error-type", required=True, help="Type of the error")
        add_parser.add_argument(
            "--language", required=True, help="Programming language"
        )
        add_parser.add_argument("--error-message", required=True, help="Error message")
        add_parser.add_argument(
            "--solution-description", required=True, help="Solution description"
        )
        add_parser.add_argument(
            "--solution-explanation", required=True, help="Solution explanation"
        )
        add_parser.add_argument("--framework", help="Framework name")
        add_parser.add_argument("--code-snippet", help="Code snippet")
        add_parser.add_argument("--task-description", help="Task description")
        add_parser.add_argument("--code-fix", help="Code fix")
        add_parser.add_argument(
            "--references", help="References (comma-separated URLs)"
        )

        add_args = add_parser.parse_args(remaining_args)

        # Process references
        references = None
        if add_args.references:
            references = add_args.references.split(",")

        # Add error record
        result = client.add_error(
            error_type=add_args.error_type,
            language=add_args.language,
            error_message=add_args.error_message,
            solution_description=add_args.solution_description,
            solution_explanation=add_args.solution_explanation,
            framework=add_args.framework,
            code_snippet=add_args.code_snippet,
            task_description=add_args.task_description,
            code_fix=add_args.code_fix,
            references=references,
        )

        print(f"Created error record with ID: {result['id']}")
        print(json.dumps(result, indent=2))

    elif args.action == "get":
        # Parse additional arguments for get action
        get_parser = argparse.ArgumentParser(description="Get Error Record")
        get_parser.add_argument("--id", required=True, help="Error record ID")

        get_args = get_parser.parse_args(remaining_args)

        # Get error record
        result = client.get_error(get_args.id)
        print(json.dumps(result, indent=2))

    elif args.action == "search":
        # Parse additional arguments for search action
        search_parser = argparse.ArgumentParser(description="Search Error Records")
        search_parser.add_argument("--error-type", help="Type of the error")
        search_parser.add_argument("--language", help="Programming language")
        search_parser.add_argument("--framework", help="Framework name")
        search_parser.add_argument("--error-message", help="Error message")
        search_parser.add_argument(
            "--max-results", type=int, default=5, help="Maximum number of results"
        )

        search_args = search_parser.parse_args(remaining_args)

        # Build search parameters
        search_params = {}
        if search_args.error_type:
            search_params["error_type"] = search_args.error_type
        if search_args.language:
            search_params["language"] = search_args.language
        if search_args.framework:
            search_params["framework"] = search_args.framework
        if search_args.error_message:
            search_params["error_message"] = search_args.error_message
        if search_args.max_results:
            search_params["max_results"] = search_args.max_results

        # Search error records
        results = client.search_errors(**search_params)
        print(f"Found {len(results)} error records:")
        for result in results:
            print(f"  - {result['error_type']}: {result['context']['error_message']}")

        if results:
            print("\nFirst result:")
            print(json.dumps(results[0], indent=2))

    elif args.action == "similar":
        # Parse additional arguments for similar action
        similar_parser = argparse.ArgumentParser(
            description="Find Similar Error Records"
        )
        similar_parser.add_argument("--query", required=True, help="Text to search for")
        similar_parser.add_argument(
            "--max-results", type=int, default=5, help="Maximum number of results"
        )

        similar_args = similar_parser.parse_args(remaining_args)

        # Search similar error records
        results = client.search_similar(similar_args.query, similar_args.max_results)
        print(f"Found {len(results)} similar error records:")
        for result in results:
            print(f"  - {result['error_type']}: {result['context']['error_message']}")

        if results:
            print("\nFirst result:")
            print(json.dumps(results[0], indent=2))


if __name__ == "__main__":
    main()
