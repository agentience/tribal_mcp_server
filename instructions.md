# Claude Code Integration with Learned Knowledge MCP

This document provides instructions for configuring Claude Code to automatically store and retrieve programming errors using the Learned Knowledge MCP server.

## Prerequisites

1. The Learned Knowledge MCP server should be running (locally or in Docker)
2. You should have access to the API key if authentication is enabled

## Setup Instructions

### 1. Create a Claude Code Integration Script

Create a new Python script called `claude_mcp_integration.py` with the following content:

```python
"""
Claude Code integration script for Learned Knowledge MCP.
This script provides functions for storing and retrieving error records.
"""

import os
import re
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

import requests

# Configuration - Update these values
MCP_BASE_URL = "http://localhost:8000"  # Update if your server runs on a different host/port
MCP_API_KEY = os.environ.get("MCP_API_KEY", "")  # Set this in your environment or directly here

class ClaudeMCPClient:
    """Client for interacting with the MCP API from Claude Code."""
    
    def __init__(self, base_url: str = MCP_BASE_URL, api_key: Optional[str] = MCP_API_KEY):
        """Initialize the MCP client."""
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        
        # Add authorization header if API key is provided
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
            
    def store_error_solution(
        self,
        error_type: str,
        language: str,
        error_message: str,
        solution_description: str,
        solution_explanation: str,
        framework: Optional[str] = None,
        code_snippet: Optional[str] = None,
        task_description: Optional[str] = None,
        code_fix: Optional[str] = None,
        references: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Store an error record with its solution.
        
        Args:
            error_type: Type of the error (e.g. "TypeError", "SyntaxError")
            language: Programming language (e.g. "python", "javascript")
            error_message: The error message text
            solution_description: Brief description of the solution
            solution_explanation: Detailed explanation of the solution
            framework: Optional framework name (e.g. "fastapi", "react")
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
            }
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
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/errors/",
                headers=self.headers,
                json=error_record,
                timeout=10
            )
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Failed to store error solution: {str(e)}")
            return {}
    
    def find_similar_errors(self, query_text: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for error records with similar text content.
        
        Args:
            query_text: Text to search for (error message or code snippet)
            max_results: Maximum number of results to return
            
        Returns:
            List of similar error records
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/errors/similar/",
                headers=self.headers,
                params={
                    "query": query_text,
                    "max_results": max_results,
                },
                timeout=10
            )
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Failed to find similar errors: {str(e)}")
            return []

    def parse_error(self, error_text: str) -> Tuple[str, str]:
        """
        Parse an error message to extract error type and message.
        
        Args:
            error_text: Raw error text
            
        Returns:
            Tuple of (error_type, error_message)
        """
        # Common pattern for Python errors
        python_match = re.search(r'([A-Za-z]+Error|Exception): (.+?)(\n|$)', error_text)
        if python_match:
            return python_match.group(1), python_match.group(2)
        
        # Common pattern for JavaScript errors
        js_match = re.search(r'([A-Za-z]+Error): (.+?)(\n|$)', error_text)
        if js_match:
            return js_match.group(1), js_match.group(2)
            
        # If no specific pattern matches, return the whole text
        # and a generic error type
        return "UnknownError", error_text

# Create a global instance for easy access
mcp_client = ClaudeMCPClient()

def store_solution(
    error_text: str,
    solution_description: str,
    solution_explanation: str,
    language: str = "python",
    framework: Optional[str] = None,
    code_snippet: Optional[str] = None,
    task_description: Optional[str] = None,
    code_fix: Optional[str] = None,
    references: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Parse an error and store its solution.
    
    Args:
        error_text: The raw error text
        solution_description: Brief description of the solution
        solution_explanation: Detailed explanation of the solution
        language: Programming language
        framework: Optional framework name
        code_snippet: Optional code snippet that caused the error
        task_description: Optional description of the task being performed
        code_fix: Optional code that fixes the error
        references: Optional list of reference URLs
        
    Returns:
        The created error record
    """
    error_type, error_message = mcp_client.parse_error(error_text)
    
    return mcp_client.store_error_solution(
        error_type=error_type,
        language=language,
        error_message=error_message,
        solution_description=solution_description,
        solution_explanation=solution_explanation,
        framework=framework,
        code_snippet=code_snippet,
        task_description=task_description,
        code_fix=code_fix,
        references=references
    )

def find_solutions(error_text: str, max_results: int = 3) -> List[Dict[str, Any]]:
    """
    Find solutions for an error.
    
    Args:
        error_text: The raw error text
        max_results: Maximum number of results to return
        
    Returns:
        List of error records with solutions
    """
    return mcp_client.find_similar_errors(error_text, max_results)
```

### 2. Set Up Your Environment

1. Save the script to an accessible location on your system
2. If authentication is enabled, set the `MCP_API_KEY` environment variable:

```bash
export MCP_API_KEY="your-api-key-here"
```

### 3. Create a Claude Code Script for Claude Integration

Create a file named `claude_mcp_plugin.py` with the following content:

```python
"""
Claude Code plugin for Learned Knowledge MCP integration.
This script should be loaded in Claude Code sessions to enable error tracking.
"""

import sys
import traceback
from typing import Dict, List, Optional, Any

# Import the integration module
# Adjust the path if needed
try:
    from claude_mcp_integration import store_solution, find_solutions
except ImportError:
    print("Could not import claude_mcp_integration module.")
    print("Please ensure the module is in your Python path.")
    sys.exit(1)

class ErrorHandler:
    """Error handler that integrates with the MCP server."""
    
    def __init__(self):
        """Initialize the error handler."""
        self.current_error = None
        self.current_code = None
        self.current_task = None
    
    def track_error(self, error_text: str, code_snippet: Optional[str] = None, task: Optional[str] = None):
        """
        Track an error for potential solution storage.
        
        Args:
            error_text: The error message
            code_snippet: Code that caused the error
            task: Description of what the user was trying to do
        """
        self.current_error = error_text
        self.current_code = code_snippet
        self.current_task = task
        
        # Look for existing solutions
        solutions = find_solutions(error_text)
        if solutions:
            print("\n🔍 Found similar errors in the MCP database:")
            for i, solution in enumerate(solutions[:3], 1):
                print(f"\n--- Solution {i} ---")
                print(f"Error Type: {solution['error_type']}")
                print(f"Error: {solution['context']['error_message']}")
                print(f"Solution: {solution['solution']['description']}")
                print(f"Explanation: {solution['solution']['explanation']}")
                if solution['solution'].get('code_fix'):
                    print(f"Code Fix: {solution['solution']['code_fix']}")
    
    def store_solution(
        self,
        solution_description: str,
        solution_explanation: str,
        language: str = "python",
        framework: Optional[str] = None,
        code_fix: Optional[str] = None,
        references: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Store the solution for the currently tracked error.
        
        Args:
            solution_description: Brief description of the solution
            solution_explanation: Detailed explanation of the solution
            language: Programming language
            framework: Optional framework name
            code_fix: Optional code that fixes the error
            references: Optional list of reference URLs
            
        Returns:
            The created error record
        """
        if not self.current_error:
            print("No error is currently being tracked.")
            return {}
        
        result = store_solution(
            error_text=self.current_error,
            solution_description=solution_description,
            solution_explanation=solution_explanation,
            language=language,
            framework=framework,
            code_snippet=self.current_code,
            task_description=self.current_task,
            code_fix=code_fix,
            references=references
        )
        
        if result:
            print(f"✅ Solution stored in MCP database with ID: {result.get('id')}")
        
        # Reset the current error
        self.reset()
        
        return result
    
    def reset(self):
        """Reset the current error tracking."""
        self.current_error = None
        self.current_code = None
        self.current_task = None

# Create a global instance for Claude to use
error_handler = ErrorHandler()

# Define functions that Claude can call
def mcp_track_error(error_text, code_snippet=None, task=None):
    """
    Track an error and check for existing solutions.
    Claude should call this when a new error is encountered.
    """
    error_handler.track_error(error_text, code_snippet, task)

def mcp_store_solution(
    solution_description, 
    solution_explanation, 
    language="python", 
    framework=None,
    code_fix=None, 
    references=None
):
    """
    Store a solution for the currently tracked error.
    Claude should call this when a solution has been found.
    """
    return error_handler.store_solution(
        solution_description=solution_description,
        solution_explanation=solution_explanation,
        language=language,
        framework=framework,
        code_fix=code_fix,
        references=references
    )

def mcp_find_solutions(error_text, max_results=3):
    """
    Directly find solutions for an error.
    Claude can call this at any time to search for solutions.
    """
    return find_solutions(error_text, max_results)

print("🔌 MCP integration loaded. Error tracking and solution storage enabled.")
```

### 4. Configure Claude to Auto-Load the Integration

Add instructions to your project's `CLAUDE.md` file to tell Claude Code to use the MCP integration:

```markdown
# MCP Integration Instructions

## Error Tracking Integration

Claude should automatically load and use the MCP integration for tracking errors and solutions.

At the start of each session, Claude should:

1. Import the MCP plugin:
   ```python
   import sys
   sys.path.append('/path/to/directory/containing/script')  # Adjust path as needed
   import claude_mcp_plugin
   ```

2. When encountering an error:
   - Track the error using `claude_mcp_plugin.mcp_track_error(error_text, code_snippet, task_description)`
   - Look for similar errors automatically

3. After providing a solution that fixed an error:
   - Store the solution using:
   ```python
   claude_mcp_plugin.mcp_store_solution(
       solution_description="Brief description",
       solution_explanation="Detailed explanation of why this works",
       language="python",  # or js, rust, etc.
       framework="fastapi",  # optional
       code_fix="fixed code",  # optional
       references=["https://docs.example.com"]  # optional
   )
   ```

## Usage Examples

Example workflow for tracking and storing errors:

```python
# Track an error
claude_mcp_plugin.mcp_track_error(
    "TypeError: Cannot read property 'value' of undefined",
    "const result = user.preferences.value;",
    "Accessing nested properties in JavaScript"
)

# After solving the problem, store the solution
claude_mcp_plugin.mcp_store_solution(
    solution_description="Check if properties exist before accessing nested values",
    solution_explanation="In JavaScript, accessing properties of undefined results in this error. Always check if parent objects exist.",
    language="javascript",
    code_fix="const result = user && user.preferences ? user.preferences.value : null;",
    references=["https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Optional_chaining"]
)
```

Directly searching for solutions:

```python
solutions = claude_mcp_plugin.mcp_find_solutions("ModuleNotFoundError: No module named 'fastapi'")
for solution in solutions:
    print(solution['solution']['description'])
```
```

## Using the Integration

Once everything is set up, Claude Code will automatically:

1. Track errors encountered during your coding sessions
2. Check the MCP database for similar errors and their solutions
3. Store successful solutions for future reference

### Commands for Claude Code

When an error occurs, you can instruct Claude to:

- "Please track this error and check if there are known solutions"
- "Store this solution in the MCP database"
- "Search for similar errors in the MCP database"

### Example Workflow

1. You encounter an error while writing code
2. Claude tracks the error and checks for existing solutions
3. If a solution is found, Claude presents it
4. If no solution is found, Claude helps solve the problem
5. Once solved, Claude stores the solution for future reference

## Maintaining Your Knowledge Base

Over time, your MCP database will grow with solved errors, creating a valuable knowledge base specific to your coding patterns and projects. You can:

1. Search for specific error types using the MCP API
2. Export your error database for backup or sharing
3. Use the insights to improve your coding practices and documentation

## Troubleshooting

If you encounter issues with the integration:

1. Check that the MCP server is running and accessible
2. Verify that your API key is correct (if authentication is enabled)
3. Check the Python paths in your integration scripts
4. Ensure requests to the MCP server aren't blocked by a firewall

For further assistance, consult the MCP documentation or project maintainers.