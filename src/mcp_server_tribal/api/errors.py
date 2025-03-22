# filename: mcp_server_tribal/api/errors.py
#
# Copyright (c) 2025 Agentience.ai
# Author: Troy Molander
# License: MIT License - See LICENSE file for details
#
# Version: 0.1.0

"""API routes for error records."""


import os
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..models.error_record import ErrorQuery, ErrorRecord
from ..services.auth import ApiKeyAuth
from ..services.storage_interface import StorageInterface

router = APIRouter(prefix="/errors", tags=["errors"])

# Get authentication configuration
require_auth = os.environ.get("REQUIRE_AUTH", "false").lower() == "true"
api_key_auth = ApiKeyAuth(require_auth=require_auth)


@router.post("/", response_model=ErrorRecord, status_code=status.HTTP_201_CREATED)
async def create_error(
    error: ErrorRecord,
    storage: StorageInterface = Depends(),
    _: str = Depends(api_key_auth),
) -> ErrorRecord:
    """
    Create a new error record.

    Args:
        error: The error record to create
        storage: Storage service dependency
        _: API key authentication dependency

    Returns:
        The created error record
    """
    return await storage.add_error(error)


@router.get("/{error_id}", response_model=ErrorRecord)
async def read_error(
    error_id: UUID,
    storage: StorageInterface = Depends(),
    _: str = Depends(api_key_auth),
) -> ErrorRecord:
    """
    Get an error record by ID.

    Args:
        error_id: The UUID of the error record
        storage: Storage service dependency
        _: API key authentication dependency

    Returns:
        The error record

    Raises:
        HTTPException: If the error record is not found
    """
    error = await storage.get_error(error_id)
    if error is None:
        raise HTTPException(status_code=404, detail="Error record not found")
    return error


@router.put("/{error_id}", response_model=ErrorRecord)
async def update_error(
    error_id: UUID,
    error: ErrorRecord,
    storage: StorageInterface = Depends(),
    _: str = Depends(api_key_auth),
) -> ErrorRecord:
    """
    Update an error record.

    Args:
        error_id: The UUID of the error record
        error: The updated error record
        storage: Storage service dependency
        _: API key authentication dependency

    Returns:
        The updated error record

    Raises:
        HTTPException: If the error record is not found
    """
    updated_error = await storage.update_error(error_id, error)
    if updated_error is None:
        raise HTTPException(status_code=404, detail="Error record not found")
    return updated_error


@router.delete("/{error_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_error(
    error_id: UUID,
    storage: StorageInterface = Depends(),
    _: str = Depends(api_key_auth),
) -> None:
    """
    Delete an error record.

    Args:
        error_id: The UUID of the error record
        storage: Storage service dependency
        _: API key authentication dependency

    Raises:
        HTTPException: If the error record is not found
    """
    deleted = await storage.delete_error(error_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Error record not found")


@router.get("/", response_model=List[ErrorRecord])
async def search_errors(
    error_type: Optional[str] = None,
    language: Optional[str] = None,
    framework: Optional[str] = None,
    error_message: Optional[str] = None,
    code_snippet: Optional[str] = None,
    task_description: Optional[str] = None,
    max_results: int = Query(default=5, ge=1, le=50),
    storage: StorageInterface = Depends(),
    _: str = Depends(api_key_auth),
) -> List[ErrorRecord]:
    """
    Search for error records.

    Args:
        error_type: The error type to filter by
        language: The language to filter by
        framework: The framework to filter by
        error_message: The error message to search for
        code_snippet: The code snippet to search for
        task_description: The task description to search for
        max_results: Maximum number of results to return
        storage: Storage service dependency
        _: API key authentication dependency

    Returns:
        A list of matching error records
    """
    query = ErrorQuery(
        error_type=error_type,
        language=language,
        framework=framework,
        error_message=error_message,
        code_snippet=code_snippet,
        task_description=task_description,
        max_results=max_results,
    )

    return await storage.search_errors(query)


@router.get("/similar/", response_model=List[ErrorRecord])
async def search_similar(
    query: str,
    max_results: int = Query(default=5, ge=1, le=50),
    storage: StorageInterface = Depends(),
    _: str = Depends(api_key_auth),
) -> List[ErrorRecord]:
    """
    Search for error records with similar text content.

    Args:
        query: The text to search for
        max_results: Maximum number of results to return
        storage: Storage service dependency
        _: API key authentication dependency

    Returns:
        A list of similar error records
    """
    return await storage.search_similar(query, max_results)
