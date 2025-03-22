# filename: mcp_server_tribal/models/error_record.py
#
# Copyright (c) 2025 Agentience.ai
# Author: Troy Molander
# License: MIT License - See LICENSE file for details
#
# Version: 0.1.0

"""Data models for error records."""


from datetime import datetime, UTC
from typing import List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

# Current schema version - must match the one in chroma_storage.py
SCHEMA_VERSION = "1.0.0"


class ErrorContext(BaseModel):
    """Contextual information about an error."""

    language: str
    framework: Optional[str] = None
    error_message: str
    code_snippet: Optional[str] = None
    stack_trace: Optional[str] = None
    task_description: Optional[str] = None


class ErrorSolution(BaseModel):
    """Solution for an error."""

    description: str
    code_fix: Optional[str] = None
    explanation: str
    references: Optional[List[str]] = None


class ErrorRecord(BaseModel):
    """Record of an error with context and solution."""

    id: UUID = Field(default_factory=uuid4)
    error_type: str
    context: ErrorContext
    solution: ErrorSolution
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    metadata: dict = Field(default_factory=dict)
    schema_version: str = Field(default=SCHEMA_VERSION, description="Schema version for data migration")

    model_config = {
        "json_schema_extra": {
            "example": {
                "error_type": "ImportError",
                "context": {
                    "language": "python",
                    "framework": "fastapi",
                    "error_message": "No module named 'fastapi'",
                    "code_snippet": "from fastapi import FastAPI\napp = FastAPI()",
                    "task_description": "Setting up a FastAPI server",
                },
                "solution": {
                    "description": "Install FastAPI package",
                    "code_fix": "pip install fastapi",
                    "explanation": "The fastapi package needs to be installed before importing it",
                    "references": ["https://fastapi.tiangolo.com/tutorial/"],
                },
            }
        }
    }


class ErrorQuery(BaseModel):
    """Query parameters for searching error records."""

    error_type: Optional[str] = None
    language: Optional[str] = None
    framework: Optional[str] = None
    error_message: Optional[str] = None
    code_snippet: Optional[str] = None
    task_description: Optional[str] = None
    max_results: int = Field(default=5, ge=1, le=50)
