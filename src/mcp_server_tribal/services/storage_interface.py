# filename: mcp_server_tribal/services/storage_interface.py
#
# Copyright (c) 2025 Agentience.ai
# Author: Troy Molander
# License: MIT License - See LICENSE file for details
#
# Version: 0.1.0

"""Storage interface for error records."""


import abc
from typing import List, Optional
from uuid import UUID

from ..models.error_record import ErrorQuery, ErrorRecord


class StorageInterface(abc.ABC):
    """Abstract interface for error record storage."""

    @abc.abstractmethod
    async def add_error(self, error: ErrorRecord) -> ErrorRecord:
        """
        Add a new error record to storage.

        Args:
            error: The error record to add

        Returns:
            The added error record with any storage-specific fields populated
        """
        pass

    @abc.abstractmethod
    async def get_error(self, error_id: UUID) -> Optional[ErrorRecord]:
        """
        Retrieve an error record by ID.

        Args:
            error_id: The UUID of the error record

        Returns:
            The error record if found, None otherwise
        """
        pass

    @abc.abstractmethod
    async def update_error(
        self, error_id: UUID, error: ErrorRecord
    ) -> Optional[ErrorRecord]:
        """
        Update an existing error record.

        Args:
            error_id: The UUID of the error record to update
            error: The updated error record

        Returns:
            The updated error record if found, None otherwise
        """
        pass

    @abc.abstractmethod
    async def delete_error(self, error_id: UUID) -> bool:
        """
        Delete an error record by ID.

        Args:
            error_id: The UUID of the error record to delete

        Returns:
            True if the error was deleted, False otherwise
        """
        pass

    @abc.abstractmethod
    async def search_errors(self, query: ErrorQuery) -> List[ErrorRecord]:
        """
        Search for error records based on the provided query.

        Args:
            query: Search parameters

        Returns:
            A list of matching error records
        """
        pass

    @abc.abstractmethod
    async def search_similar(
        self, text_query: str, max_results: int = 5
    ) -> List[ErrorRecord]:
        """
        Search for error records with similar text content.

        Args:
            text_query: The text to search for
            max_results: Maximum number of results to return

        Returns:
            A list of matching error records ordered by similarity
        """
        pass
