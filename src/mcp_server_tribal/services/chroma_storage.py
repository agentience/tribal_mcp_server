# filename: mcp_server_tribal/services/chroma_storage.py
#
# Copyright (c) 2025 Agentience.ai
# Author: Troy Molander
# License: MIT License - See LICENSE file for details
#
# Version: 0.1.0

"""ChromaDB implementation of storage interface."""


import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

import chromadb

from ..models.error_record import ErrorQuery, ErrorRecord
from .migration import migration_manager
from .storage_interface import StorageInterface
from mcp_server_tribal import __version__

# Configure logging
logger = logging.getLogger(__name__)

# Current schema version - this should be updated when the schema changes
SCHEMA_VERSION = "1.0.0"


class ChromaStorage(StorageInterface):
    """ChromaDB implementation of error record storage."""

    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize ChromaDB storage.

        Args:
            persist_directory: Directory to store ChromaDB data
        """
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)

        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="error_records",
            metadata={
                "hnsw:space": "cosine",
                "schema_version": SCHEMA_VERSION
            }
        )

        # Validate schema version on startup
        self._validate_schema_version()

    def _error_to_document(self, error: ErrorRecord) -> Dict[str, Any]:
        """Convert ErrorRecord to document format for ChromaDB."""
        return json.loads(error.model_dump_json())

    def _document_to_error(self, document: Dict[str, Any]) -> ErrorRecord:
        """Convert document from ChromaDB to ErrorRecord."""
        return ErrorRecord.model_validate(document)

    def _create_embedding_text(self, error: ErrorRecord) -> str:
        """Create text for embedding from ErrorRecord.

        Note: This method is kept for future use, but not currently used as
        ChromaDB auto-generates embeddings from documents.
        """
        context_parts = [
            error.error_type,
            error.context.language,
            error.context.framework or "",
            error.context.error_message,
            error.context.code_snippet or "",
            error.context.task_description or "",
        ]

        solution_parts = [
            error.solution.description,
            error.solution.code_fix or "",
            error.solution.explanation,
        ]

        return " ".join(context_parts + solution_parts)

    async def add_error(self, error: ErrorRecord) -> ErrorRecord:
        """Add a new error record to storage."""
        document = self._error_to_document(error)

        # Store the document and metadata
        self.collection.add(
            ids=[str(error.id)],
            documents=[json.dumps(document)],
            metadatas=[
                {
                    "error_type": error.error_type,
                    "language": error.context.language,
                    "framework": error.context.framework or "",
                }
            ],
            # ChromaDB will auto-generate embeddings from the documents
        )

        return error

    async def get_error(self, error_id: UUID) -> Optional[ErrorRecord]:
        """Retrieve an error record by ID."""
        try:
            result = self.collection.get(
                ids=[str(error_id)], include=["documents", "metadatas"]
            )
            if not result["documents"]:
                return None

            document = json.loads(result["documents"][0])
            return self._document_to_error(document)
        except Exception:
            return None

    async def update_error(
        self, error_id: UUID, error: ErrorRecord
    ) -> Optional[ErrorRecord]:
        """Update an existing error record."""
        # Check if the error exists
        existing_error = await self.get_error(error_id)
        if not existing_error:
            return None

        # Ensure the ID matches
        error.id = error_id
        error.created_at = existing_error.created_at

        # Update the record
        document = self._error_to_document(error)

        self.collection.update(
            ids=[str(error_id)],
            documents=[json.dumps(document)],
            metadatas=[
                {
                    "error_type": error.error_type,
                    "language": error.context.language,
                    "framework": error.context.framework or "",
                }
            ],
            # ChromaDB will auto-generate embeddings from the documents
        )

        return error

    async def delete_error(self, error_id: UUID) -> bool:
        """Delete an error record by ID."""
        try:
            result = self.collection.get(ids=[str(error_id)])
            if not result["ids"]:
                return False

            self.collection.delete(ids=[str(error_id)])
            return True
        except Exception:
            return False

    async def search_errors(self, query: ErrorQuery) -> List[ErrorRecord]:
        """Search for error records based on the provided query."""
        # Build metadata filter
        filter_clauses = []

        if query.error_type:
            filter_clauses.append({"error_type": query.error_type})

        if query.language:
            filter_clauses.append({"language": query.language})

        if query.framework:
            filter_clauses.append({"framework": query.framework})

        # Combine text for semantic search
        search_text = " ".join(
            [
                query.error_message or "",
                query.code_snippet or "",
                query.task_description or "",
            ]
        ).strip()

        # If we have text to search, do a similarity search
        if search_text:
            results = self.collection.query(
                query_texts=[search_text],
                n_results=query.max_results,
                where=filter_clauses if filter_clauses else None,
                include=["documents"],
            )
        else:
            # Otherwise, just get records matching the metadata filters
            results = self.collection.get(
                where=filter_clauses if filter_clauses else None,
                limit=query.max_results,
                include=["documents"],
            )

        # Convert results to ErrorRecord objects
        error_records = []
        if results.get("documents"):
            for doc_str in results["documents"][0]:
                document = json.loads(doc_str)
                error_records.append(self._document_to_error(document))

        return error_records

    def _validate_schema_version(self) -> None:
        """Validate and potentially migrate the schema version."""
        try:
            collection_info = self.client.get_collection(name="error_records")
            current_version = collection_info.metadata.get("schema_version", "0.0.0")

            if current_version != SCHEMA_VERSION:
                logger.warning(
                    f"Schema version mismatch: found {current_version}, expected {SCHEMA_VERSION}"
                )

                # Check compatibility
                if migration_manager.is_compatible(current_version):
                    # Try to migrate if possible
                    migration_result = migration_manager.execute_migration(
                        self, current_version, SCHEMA_VERSION
                    )

                    if not migration_result:
                        logger.warning(
                            f"Cannot automatically migrate from schema version {current_version} "
                            f"to {SCHEMA_VERSION}, but versions are compatible."
                        )
                else:
                    raise ValueError(
                        f"Incompatible schema version: {current_version}. "
                        f"This version of Tribal requires schema version {SCHEMA_VERSION}."
                    )
        except Exception as e:
            # For first-time startup, this is normal
            logger.info(f"Schema validation startup: {e}")

    async def search_similar(
        self, text_query: str, max_results: int = 5
    ) -> List[ErrorRecord]:
        """Search for error records with similar text content."""
        results = self.collection.query(
            query_texts=[text_query],
            n_results=max_results,
            include=["documents", "distances"],
        )

        # Convert results to ErrorRecord objects
        error_records = []
        if results.get("documents") and results["documents"][0]:
            for doc_str in results["documents"][0]:
                document = json.loads(doc_str)
                error_records.append(self._document_to_error(document))

        return error_records
