# filename: mcp_server_tribal/services/migration.py
#
# Copyright (c) 2025 Agentience.ai
# Author: Troy Molander
# License: MIT License - See LICENSE file for details
#
# Version: 0.1.0

"""Schema migration framework for Tribal database."""


import logging
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from mcp_server_tribal import __version__

# Configure logging
logger = logging.getLogger(__name__)

# Type definitions
MigrationFn = Callable[[Any], None]
MigrationPath = List[Tuple[str, str, MigrationFn]]


class MigrationManager:
    """Manages schema migrations between versions."""

    def __init__(self):
        """Initialize the migration manager."""
        self.migrations: Dict[str, Dict[str, MigrationFn]] = {}
        self.compatibility_matrix: Dict[str, List[str]] = {
            "0.1.0": ["1.0.0"],  # App version 0.1.0 works with schema 1.0.0
        }

    def register_migration(self, from_version: str, to_version: str, migration_fn: MigrationFn) -> None:
        """
        Register a migration function between two schema versions.

        Args:
            from_version: Source schema version
            to_version: Target schema version
            migration_fn: Migration function to execute
        """
        if from_version not in self.migrations:
            self.migrations[from_version] = {}

        self.migrations[from_version][to_version] = migration_fn
        logger.info(f"Registered migration path: {from_version} -> {to_version}")

    def get_migration_path(self, from_version: str, to_version: str) -> Optional[MigrationPath]:
        """
        Find a migration path between two schema versions.

        Args:
            from_version: Source schema version
            to_version: Target schema version

        Returns:
            List of migration steps (from_version, to_version, migration_fn) if a path exists,
            None otherwise
        """
        # Direct migration path
        if from_version in self.migrations and to_version in self.migrations[from_version]:
            return [(from_version, to_version, self.migrations[from_version][to_version])]

        # BFS to find a migration path
        visited = {from_version}
        queue = [(from_version, [])]

        while queue:
            current, path = queue.pop(0)

            if current not in self.migrations:
                continue

            for next_version, migration_fn in self.migrations[current].items():
                if next_version == to_version:
                    full_path = path + [(current, next_version, migration_fn)]
                    logger.info(f"Found migration path: {from_version} -> {to_version}")
                    return full_path

                if next_version not in visited:
                    visited.add(next_version)
                    queue.append((next_version, path + [(current, next_version, migration_fn)]))

        logger.warning(f"No migration path from {from_version} to {to_version}")
        return None

    def execute_migration(self, storage: Any, from_version: str, to_version: str) -> bool:
        """
        Execute migration between two schema versions.

        Args:
            storage: Storage instance to migrate
            from_version: Source schema version
            to_version: Target schema version

        Returns:
            True if migration was successful, False otherwise
        """
        if from_version == to_version:
            logger.info("No migration needed: versions are identical")
            return True

        migration_path = self.get_migration_path(from_version, to_version)
        if not migration_path:
            return False

        try:
            for step_from, step_to, migration_fn in migration_path:
                logger.info(f"Executing migration step: {step_from} -> {step_to}")
                migration_fn(storage)
                logger.info(f"Migration step completed: {step_from} -> {step_to}")

            return True
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return False

    def is_compatible(self, schema_version: str, app_version: Optional[str] = None) -> bool:
        """
        Check if a schema version is compatible with an application version.

        Args:
            schema_version: The schema version to check
            app_version: The application version to check against, defaults to current version

        Returns:
            True if compatible, False otherwise
        """
        app_version = app_version or __version__
        compatible_versions = self.compatibility_matrix.get(app_version, [])
        result = schema_version in compatible_versions

        if not result:
            logger.warning(
                f"Schema version {schema_version} is not compatible with app version {app_version}. "
                f"Compatible versions: {compatible_versions}"
            )

        return result

    def register_compatibility(self, app_version: str, schema_versions: List[str]) -> None:
        """
        Register compatible schema versions for an application version.

        Args:
            app_version: Application version
            schema_versions: List of compatible schema versions
        """
        self.compatibility_matrix[app_version] = schema_versions
        logger.info(f"Registered compatibility for app version {app_version}: {schema_versions}")


# Initialize the global migration manager
migration_manager = MigrationManager()

# Register migrations

# Initial schema migration (0.0.0 -> 1.0.0)
def migrate_initial_to_v1(storage: Any) -> None:
    """Migrate from initial schema (0.0.0) to version 1.0.0."""
    # For ChromaDB this is just updating the metadata
    if hasattr(storage, 'collection'):
        storage.collection.modify(metadata={"schema_version": "1.0.0"})
        logger.info("Updated schema version to 1.0.0")

migration_manager.register_migration("0.0.0", "1.0.0", migrate_initial_to_v1)

# Example migration for future use (1.0.0 -> 1.1.0)
# def migrate_v1_to_v1_1(storage: Any) -> None:
#     """Migrate from schema 1.0.0 to 1.1.0."""
#     # Example: Add new fields, update embeddings, etc.
#     pass
#
# migration_manager.register_migration("1.0.0", "1.1.0", migrate_v1_to_v1_1)
