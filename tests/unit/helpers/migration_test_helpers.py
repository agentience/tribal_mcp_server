# filename: {filename}
# description:
#
# Copyright (c) 2025 Agentience.ai
# Author: Troy Molander
# License: MIT License - See LICENSE file for details
#
# Version: 0.1.0

# filename: tests/unit/helpers/migration_test_helpers.py
#
# Copyright (c) 2025 Agentience.ai
# Author: Troy Molander
# License: MIT License - See LICENSE file for details
#
# Version: 0.1.0

"""Helpers for testing schema migrations."""

from typing import Any, Callable, Dict, List, Optional

from mcp_server_tribal.services.migration import MigrationManager


class MockChromaCollection:
    """Mock ChromaDB collection for testing migrations."""

    def __init__(self, schema_version: str = "0.0.0"):
        """Initialize with a specific schema version."""
        self.metadata = {"schema_version": schema_version}
        self.documents: Dict[str, str] = {}
        self.metadatas: Dict[str, Dict[str, Any]] = {}
        self.embeddings: Dict[str, List[float]] = {}

    def modify(self, metadata: Dict[str, Any]) -> None:
        """Update the collection metadata."""
        self.metadata.update(metadata)

    def add(
        self,
        ids: List[str],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        embeddings: Optional[List[List[float]]] = None,
    ) -> None:
        """Add documents to the collection."""
        for i, doc_id in enumerate(ids):
            self.documents[doc_id] = documents[i]
            self.metadatas[doc_id] = metadatas[i]
            if embeddings:
                self.embeddings[doc_id] = embeddings[i]

    def get(self, ids: Optional[List[str]] = None, **kwargs) -> Dict[str, Any]:
        """Get documents from the collection."""
        if not ids:
            # Return all documents
            return {
                "ids": list(self.documents.keys()),
                "documents": list(self.documents.values()),
                "metadatas": list(self.metadatas.values()),
            }

        # Return only requested documents
        result_ids = []
        result_docs = []
        result_metas = []

        for doc_id in ids:
            if doc_id in self.documents:
                result_ids.append(doc_id)
                result_docs.append(self.documents[doc_id])
                result_metas.append(self.metadatas[doc_id])

        return {
            "ids": result_ids,
            "documents": result_docs,
            "metadatas": result_metas,
        }


class MockChromaClient:
    """Mock ChromaDB client for testing migrations."""

    def __init__(self):
        """Initialize with empty collections."""
        self.collections: Dict[str, MockChromaCollection] = {}

    def get_or_create_collection(
        self, name: str, metadata: Optional[Dict[str, Any]] = None
    ) -> MockChromaCollection:
        """Get or create a collection with the given name."""
        if name not in self.collections:
            self.collections[name] = MockChromaCollection()
            if metadata:
                self.collections[name].metadata = metadata
        return self.collections[name]

    def get_collection(self, name: str) -> MockChromaCollection:
        """Get a collection by name."""
        if name not in self.collections:
            raise ValueError(f"Collection {name} does not exist")
        return self.collections[name]


class MockStorage:
    """Mock storage for testing migrations."""

    def __init__(self, schema_version: str = "0.0.0"):
        """Initialize with a specific schema version."""
        self.client = MockChromaClient()
        self.collection = self.client.get_or_create_collection(
            name="error_records",
            metadata={"schema_version": schema_version},
        )

    def get_schema_version(self) -> str:
        """Get the current schema version."""
        return self.collection.metadata.get("schema_version", "0.0.0")


def create_migration_test_manager() -> MigrationManager:
    """Create a migration manager for testing."""
    manager = MigrationManager()
    # Clear any existing migrations and compatibility entries
    manager.migrations = {}
    manager.compatibility_matrix = {}
    return manager


def create_test_migration(from_version: str, to_version: str) -> Callable[[Any], None]:
    """Create a test migration function with tracking."""

    def migration_fn(storage: Any) -> None:
        # Update schema version in the collection metadata
        if hasattr(storage, "collection"):
            storage.collection.modify(metadata={"schema_version": to_version})

        # Track that this migration was called
        if not hasattr(storage, "_migrations_called"):
            storage._migrations_called = []
        storage._migrations_called.append((from_version, to_version))

    return migration_fn


def register_test_migrations(
    manager: MigrationManager, versions: List[str], app_version: str = "0.1.0"
) -> None:
    """
    Register test migrations between consecutive versions.

    Args:
        manager: The migration manager
        versions: List of schema versions in order
        app_version: App version to register compatibility for
    """
    # Register migrations between consecutive versions
    for i in range(len(versions) - 1):
        from_ver = versions[i]
        to_ver = versions[i + 1]
        manager.register_migration(
            from_ver, to_ver, create_test_migration(from_ver, to_ver)
        )

    # Register compatibility with the app version
    manager.register_compatibility(app_version, versions)


def setup_complex_migration_scenario(
    manager: MigrationManager, app_version: str = "0.1.0"
) -> None:
    """
    Set up a complex migration scenario with multiple paths.

    This creates a migration graph with multiple possible paths:

    1.0.0 -> 1.1.0 -> 1.2.0 -> 2.0.0
      |                 ^
      v                 |
    1.0.1 -> 1.0.2 -----+
      |
      v
    1.0.3 -> 1.0.4

    Args:
        manager: The migration manager
        app_version: App version to register compatibility for
    """
    versions = ["1.0.0", "1.0.1", "1.0.2", "1.0.3", "1.0.4", "1.1.0", "1.2.0", "2.0.0"]

    # Register all migrations
    migrations = [
        ("1.0.0", "1.1.0"),
        ("1.1.0", "1.2.0"),
        ("1.2.0", "2.0.0"),
        ("1.0.0", "1.0.1"),
        ("1.0.1", "1.0.2"),
        ("1.0.2", "1.2.0"),
        ("1.0.1", "1.0.3"),
        ("1.0.3", "1.0.4"),
    ]

    for from_ver, to_ver in migrations:
        manager.register_migration(
            from_ver, to_ver, create_test_migration(from_ver, to_ver)
        )

    # Register compatibility with the app version
    manager.register_compatibility(app_version, versions)


def assert_migration_path_correct(
    storage: MockStorage,
    expected_path: List[tuple],
) -> None:
    """
    Assert that the migration path taken matches the expected path.

    Args:
        storage: The storage that was migrated
        expected_path: List of (from_version, to_version) tuples
    """
    if not hasattr(storage, "_migrations_called"):
        assert not expected_path, "No migrations were called, but expected some"
        return

    assert storage._migrations_called == expected_path, (
        f"Migration path does not match expected. "
        f"Got: {storage._migrations_called}, Expected: {expected_path}"
    )
