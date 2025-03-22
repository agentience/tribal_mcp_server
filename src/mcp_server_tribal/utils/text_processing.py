# filename: mcp_server_tribal/utils/text_processing.py
#
# Copyright (c) 2025 Agentience.ai
# Author: Troy Molander
# License: MIT License - See LICENSE file for details
#
# Version: 0.1.0

"""Utility functions for text processing."""


import re
from typing import List, Optional


def clean_code_snippet(snippet: str) -> str:
    """
    Clean a code snippet for better matching.

    Args:
        snippet: The code snippet to clean

    Returns:
        Cleaned code snippet
    """
    # Remove comments
    snippet = re.sub(r"#.*$", "", snippet, flags=re.MULTILINE)
    snippet = re.sub(r"//.*$", "", snippet, flags=re.MULTILINE)
    snippet = re.sub(r"/\*.*?\*/", "", snippet, flags=re.DOTALL)

    # Normalize whitespace
    snippet = re.sub(r"\s+", " ", snippet)

    return snippet.strip()


def extract_error_type(error_message: str) -> Optional[str]:
    """
    Extract the error type from an error message.

    Args:
        error_message: The error message to extract from

    Returns:
        The extracted error type, or None if not found
    """
    # Common patterns for error messages
    patterns = [
        r"^([A-Za-z0-9_]+Error):",  # Python-style: TypeError: message
        r"Exception of type \'([A-Za-z0-9_]+Error)\'",  # Exception of type 'ValueError'
        r"Uncaught ([A-Za-z0-9_]+Error):",  # JavaScript: Uncaught ReferenceError: message
        r"java\.lang\.([A-Za-z0-9_]+Exception)",  # Java: java.lang.NullPointerException
        r"([A-Za-z0-9_]+Exception):",  # Generic: SomeException: message
    ]

    for pattern in patterns:
        match = re.search(pattern, error_message)
        if match:
            return match.group(1)

    return None


def tokenize_code(code: str) -> List[str]:
    """
    Tokenize code into a list of tokens.

    Args:
        code: The code to tokenize

    Returns:
        List of tokens
    """
    # Simple tokenization by splitting on whitespace and punctuation
    tokens = re.findall(r"[A-Za-z0-9_]+|[^\s\w]", code)
    return [token for token in tokens if token.strip()]


def normalize_error_message(message: str) -> str:
    """
    Normalize an error message for better matching.

    Args:
        message: The error message to normalize

    Returns:
        Normalized error message
    """
    # Replace specific filenames, line numbers, and variable names with placeholders
    message = re.sub(r'File ".*?", line \d+', 'File "FILE", line N', message)
    message = re.sub(r"line \d+", "line N", message)
    message = re.sub(r"at line \d+", "at line N", message)
    message = re.sub(r"\'[a-zA-Z0-9_]+\'", "'VAR'", message)
    message = re.sub(r'"[a-zA-Z0-9_]+"', '"VAR"', message)

    return message.strip()
