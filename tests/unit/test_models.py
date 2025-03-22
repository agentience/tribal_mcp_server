# filename: {filename}
# description:
#
# Copyright (c) 2025 Agentience.ai
# Author: Troy Molander
# License: MIT License - See LICENSE file for details
#
# Version: 0.1.0

"""Tests for the data models."""

from uuid import UUID

from mcp_server_tribal.models.error_record import (
    ErrorContext,
    ErrorQuery,
    ErrorRecord,
    ErrorSolution,
)


def test_error_context():
    """Test the ErrorContext model."""
    context = ErrorContext(
        language="python",
        framework="fastapi",
        error_message="No module named 'fastapi'",
        code_snippet="from fastapi import FastAPI",
        task_description="Setting up a FastAPI server",
    )

    assert context.language == "python"
    assert context.framework == "fastapi"
    assert context.error_message == "No module named 'fastapi'"
    assert context.code_snippet == "from fastapi import FastAPI"
    assert context.task_description == "Setting up a FastAPI server"


def test_error_solution():
    """Test the ErrorSolution model."""
    solution = ErrorSolution(
        description="Install FastAPI package",
        code_fix="pip install fastapi",
        explanation="The fastapi package needs to be installed before importing it",
        references=["https://fastapi.tiangolo.com/tutorial/"],
    )

    assert solution.description == "Install FastAPI package"
    assert solution.code_fix == "pip install fastapi"
    assert (
        solution.explanation
        == "The fastapi package needs to be installed before importing it"
    )
    assert solution.references == ["https://fastapi.tiangolo.com/tutorial/"]


def test_error_record():
    """Test the ErrorRecord model."""
    context = ErrorContext(
        language="python",
        framework="fastapi",
        error_message="No module named 'fastapi'",
    )

    solution = ErrorSolution(
        description="Install FastAPI package",
        explanation="The fastapi package needs to be installed before importing it",
    )

    record = ErrorRecord(
        error_type="ImportError",
        context=context,
        solution=solution,
    )

    assert record.error_type == "ImportError"
    assert record.context.language == "python"
    assert record.solution.description == "Install FastAPI package"
    assert isinstance(record.id, UUID)
    assert record.created_at is not None
    assert record.updated_at is not None


def test_error_query():
    """Test the ErrorQuery model."""
    query = ErrorQuery(
        error_type="ImportError",
        language="python",
        framework="fastapi",
        error_message="No module named",
        max_results=10,
    )

    assert query.error_type == "ImportError"
    assert query.language == "python"
    assert query.framework == "fastapi"
    assert query.error_message == "No module named"
    assert query.max_results == 10
