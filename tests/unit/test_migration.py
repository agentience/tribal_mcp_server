# filename: {filename}
# description:
#
# Copyright (c) 2025 Agentience.ai
# Author: Troy Molander
# License: MIT License - See LICENSE file for details
#
# Version: 0.1.0

# filename: tests/unit/test_migration.py
#
# Copyright (c) 2025 Agentience.ai
# Author: Troy Molander
# License: MIT License - See LICENSE file for details
#
# Version: 0.1.0

"""Tests for the schema migration framework."""


from unittest.mock import MagicMock, patch

from mcp_server_tribal.services.migration import MigrationManager


class TestMigrationManager:
    """Tests for the migration manager."""

    def test_register_migration(self):
        """Test registering a migration function."""
        manager = MigrationManager()
        migration_fn = MagicMock()

        manager.register_migration("1.0.0", "1.1.0", migration_fn)

        assert "1.0.0" in manager.migrations
        assert "1.1.0" in manager.migrations["1.0.0"]
        assert manager.migrations["1.0.0"]["1.1.0"] == migration_fn

    def test_get_direct_migration_path(self):
        """Test finding a direct migration path."""
        manager = MigrationManager()
        migration_fn = MagicMock()

        manager.register_migration("1.0.0", "1.1.0", migration_fn)
        path = manager.get_migration_path("1.0.0", "1.1.0")

        assert path is not None
        assert len(path) == 1
        assert path[0] == ("1.0.0", "1.1.0", migration_fn)

    def test_get_indirect_migration_path(self):
        """Test finding an indirect migration path."""
        manager = MigrationManager()
        migration_fn1 = MagicMock()
        migration_fn2 = MagicMock()

        manager.register_migration("1.0.0", "1.0.5", migration_fn1)
        manager.register_migration("1.0.5", "1.1.0", migration_fn2)
        path = manager.get_migration_path("1.0.0", "1.1.0")

        assert path is not None
        assert len(path) == 2
        assert path[0] == ("1.0.0", "1.0.5", migration_fn1)
        assert path[1] == ("1.0.5", "1.1.0", migration_fn2)

    def test_get_nonexistent_migration_path(self):
        """Test finding a nonexistent migration path."""
        manager = MigrationManager()
        migration_fn = MagicMock()

        manager.register_migration("1.0.0", "1.1.0", migration_fn)
        path = manager.get_migration_path("1.0.0", "2.0.0")

        assert path is None

    def test_execute_migration_direct(self):
        """Test executing a direct migration."""
        manager = MigrationManager()
        migration_fn = MagicMock()
        storage = MagicMock()

        manager.register_migration("1.0.0", "1.1.0", migration_fn)
        result = manager.execute_migration(storage, "1.0.0", "1.1.0")

        assert result is True
        migration_fn.assert_called_once_with(storage)

    def test_execute_migration_indirect(self):
        """Test executing an indirect migration."""
        manager = MigrationManager()
        migration_fn1 = MagicMock()
        migration_fn2 = MagicMock()
        storage = MagicMock()

        manager.register_migration("1.0.0", "1.0.5", migration_fn1)
        manager.register_migration("1.0.5", "1.1.0", migration_fn2)
        result = manager.execute_migration(storage, "1.0.0", "1.1.0")

        assert result is True
        migration_fn1.assert_called_once_with(storage)
        migration_fn2.assert_called_once_with(storage)

    def test_execute_migration_fails(self):
        """Test executing a migration that fails."""
        manager = MigrationManager()
        migration_fn = MagicMock(side_effect=Exception("Migration failed"))
        storage = MagicMock()

        manager.register_migration("1.0.0", "1.1.0", migration_fn)
        result = manager.execute_migration(storage, "1.0.0", "1.1.0")

        assert result is False
        migration_fn.assert_called_once_with(storage)

    def test_execute_migration_no_path(self):
        """Test executing a migration with no path."""
        manager = MigrationManager()
        migration_fn = MagicMock()
        storage = MagicMock()

        manager.register_migration("1.0.0", "1.1.0", migration_fn)
        result = manager.execute_migration(storage, "1.0.0", "2.0.0")

        assert result is False
        migration_fn.assert_not_called()

    def test_execute_migration_same_version(self):
        """Test executing a migration with same source and target version."""
        manager = MigrationManager()
        migration_fn = MagicMock()
        storage = MagicMock()

        manager.register_migration("1.0.0", "1.1.0", migration_fn)
        result = manager.execute_migration(storage, "1.0.0", "1.0.0")

        assert result is True
        migration_fn.assert_not_called()

    def test_is_compatible(self):
        """Test checking compatibility between schema and app versions."""
        manager = MigrationManager()

        # Set up compatibility matrix for testing
        manager.compatibility_matrix = {
            "0.1.0": ["1.0.0", "1.0.1"],
            "0.2.0": ["1.1.0"],
        }

        # Test compatible versions
        assert manager.is_compatible("1.0.0", "0.1.0") is True
        assert manager.is_compatible("1.0.1", "0.1.0") is True
        assert manager.is_compatible("1.1.0", "0.2.0") is True

        # Test incompatible versions
        assert manager.is_compatible("1.1.0", "0.1.0") is False
        assert manager.is_compatible("1.0.0", "0.2.0") is False
        assert manager.is_compatible("2.0.0", "0.1.0") is False

    def test_register_compatibility(self):
        """Test registering compatible schema versions for an app version."""
        manager = MigrationManager()

        manager.register_compatibility("0.2.0", ["1.1.0", "1.1.1"])

        assert "0.2.0" in manager.compatibility_matrix
        assert manager.compatibility_matrix["0.2.0"] == ["1.1.0", "1.1.1"]
        assert manager.is_compatible("1.1.0", "0.2.0") is True
        assert manager.is_compatible("1.1.1", "0.2.0") is True
        assert manager.is_compatible("1.0.0", "0.2.0") is False


class TestMigrationIntegration:
    """Integration tests for the migration system."""

    @patch("mcp_server_tribal.services.migration.__version__", "0.1.0")
    def test_initial_migration(self):
        """Test the migration manager with an initial migration."""
        manager = MigrationManager()

        # Create mock storage with collection
        storage = MagicMock()
        storage.collection = MagicMock()

        # Register the initial migration
        def migrate_initial_to_v1(storage):
            storage.collection.modify(metadata={"schema_version": "1.0.0"})

        manager.register_migration("0.0.0", "1.0.0", migrate_initial_to_v1)

        # Configure compatibility matrix
        manager.register_compatibility("0.1.0", ["1.0.0"])

        # Execute the migration
        result = manager.execute_migration(storage, "0.0.0", "1.0.0")

        assert result is True
        storage.collection.modify.assert_called_once_with(
            metadata={"schema_version": "1.0.0"}
        )

        # Check compatibility
        assert manager.is_compatible("1.0.0") is True
        assert manager.is_compatible("0.0.0") is False
