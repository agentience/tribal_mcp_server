# filename: {filename}
# description:
#
# Copyright (c) 2025 Agentience.ai
# Author: Troy Molander
# License: MIT License - See LICENSE file for details
#
# Version: 0.1.0

# filename: tests/unit/test_migration_framework.py
#
# Copyright (c) 2025 Agentience.ai
# Author: Troy Molander
# License: MIT License - See LICENSE file for details
#
# Version: 0.1.0

"""Comprehensive tests for the migration framework."""

import unittest
from unittest.mock import MagicMock, patch

from tests.unit.helpers.migration_test_helpers import (
    MockStorage,
    assert_migration_path_correct,
    create_migration_test_manager,
    create_test_migration,
    register_test_migrations,
    setup_complex_migration_scenario,
)


class TestMigrationFramework(unittest.TestCase):
    """Comprehensive tests for the migration framework."""

    def setUp(self):
        """Set up test case."""
        self.manager = create_migration_test_manager()

    def test_linear_migration_path(self):
        """Test migration along a simple linear path."""
        # Create a linear migration path: 1.0.0 -> 1.1.0 -> 1.2.0 -> 2.0.0
        versions = ["1.0.0", "1.1.0", "1.2.0", "2.0.0"]
        register_test_migrations(self.manager, versions)

        # Test migrating from 1.0.0 to 2.0.0
        storage = MockStorage("1.0.0")
        result = self.manager.execute_migration(storage, "1.0.0", "2.0.0")

        # Check the migration was successful
        self.assertTrue(result)
        self.assertEqual(storage.get_schema_version(), "2.0.0")

        # Check the migration path taken was correct
        expected_path = [
            ("1.0.0", "1.1.0"),
            ("1.1.0", "1.2.0"),
            ("1.2.0", "2.0.0"),
        ]
        assert_migration_path_correct(storage, expected_path)

    def test_partial_migration(self):
        """Test migration along part of a linear path."""
        # Create a linear migration path: 1.0.0 -> 1.1.0 -> 1.2.0 -> 2.0.0
        versions = ["1.0.0", "1.1.0", "1.2.0", "2.0.0"]
        register_test_migrations(self.manager, versions)

        # Test migrating from 1.1.0 to 1.2.0
        storage = MockStorage("1.1.0")
        result = self.manager.execute_migration(storage, "1.1.0", "1.2.0")

        # Check the migration was successful
        self.assertTrue(result)
        self.assertEqual(storage.get_schema_version(), "1.2.0")

        # Check the migration path taken was correct
        expected_path = [("1.1.0", "1.2.0")]
        assert_migration_path_correct(storage, expected_path)

    def test_complex_migration_paths(self):
        """Test migration with multiple possible paths."""
        # Set up a complex migration scenario
        setup_complex_migration_scenario(self.manager)

        # Test path through 1.0.0 -> 1.1.0 -> 1.2.0 -> 2.0.0
        storage1 = MockStorage("1.0.0")
        result1 = self.manager.execute_migration(storage1, "1.0.0", "2.0.0")
        self.assertTrue(result1)
        self.assertEqual(storage1.get_schema_version(), "2.0.0")

        # The BFS algorithm should find this path as it's the shortest
        expected_path1 = [
            ("1.0.0", "1.1.0"),
            ("1.1.0", "1.2.0"),
            ("1.2.0", "2.0.0"),
        ]
        assert_migration_path_correct(storage1, expected_path1)

        # Test path from 1.0.1 -> 1.0.2 -> 1.2.0
        storage2 = MockStorage("1.0.1")
        result2 = self.manager.execute_migration(storage2, "1.0.1", "1.2.0")
        self.assertTrue(result2)
        self.assertEqual(storage2.get_schema_version(), "1.2.0")

        # The migration should take the direct path
        expected_path2 = [
            ("1.0.1", "1.0.2"),
            ("1.0.2", "1.2.0"),
        ]
        assert_migration_path_correct(storage2, expected_path2)

    def test_migration_from_different_branch(self):
        """Test migration from one branch to another."""
        # Set up a complex migration scenario
        setup_complex_migration_scenario(self.manager)

        # Test path from 1.0.3 (leaf of one branch) to 1.2.0 (on another branch)
        storage = MockStorage("1.0.3")

        # Add a direct path between these versions for testing
        self.manager.register_migration(
            "1.0.3", "1.2.0", create_test_migration("1.0.3", "1.2.0")
        )

        result = self.manager.execute_migration(storage, "1.0.3", "1.2.0")
        self.assertTrue(result)
        self.assertEqual(storage.get_schema_version(), "1.2.0")

        # The migration should take the direct path we just added
        expected_path = [("1.0.3", "1.2.0")]
        assert_migration_path_correct(storage, expected_path)

    def test_no_migration_path(self):
        """Test attempting to migrate when no path exists."""
        # Create a linear migration path: 1.0.0 -> 1.1.0 -> 1.2.0
        versions = ["1.0.0", "1.1.0", "1.2.0"]
        register_test_migrations(self.manager, versions)

        # Test migrating to a version not in the path
        storage = MockStorage("1.0.0")
        result = self.manager.execute_migration(storage, "1.0.0", "2.0.0")

        # Check the migration failed
        self.assertFalse(result)
        self.assertEqual(storage.get_schema_version(), "1.0.0")

        # Check no migrations were applied
        if hasattr(storage, "_migrations_called"):
            self.assertEqual(storage._migrations_called, [])

    def test_same_version_migration(self):
        """Test migrating to the same version (should be a no-op)."""
        # Create a linear migration path
        versions = ["1.0.0", "1.1.0"]
        register_test_migrations(self.manager, versions)

        # Test migrating to the same version
        storage = MockStorage("1.0.0")
        result = self.manager.execute_migration(storage, "1.0.0", "1.0.0")

        # Check the migration was successful (no-op)
        self.assertTrue(result)
        self.assertEqual(storage.get_schema_version(), "1.0.0")

        # Check no migrations were applied
        if hasattr(storage, "_migrations_called"):
            self.assertEqual(storage._migrations_called, [])

    def test_migration_with_error(self):
        """Test a migration that encounters an error."""
        # Create a migration that fails
        self.manager.register_migration(
            "1.0.0", "1.1.0", MagicMock(side_effect=Exception("Migration failed"))
        )

        # Test migrating
        storage = MockStorage("1.0.0")
        result = self.manager.execute_migration(storage, "1.0.0", "1.1.0")

        # Check the migration failed
        self.assertFalse(result)
        self.assertEqual(storage.get_schema_version(), "1.0.0")

    def test_compatibility_matching(self):
        """Test compatibility checking between app and schema versions."""
        # Set up compatibility matrix
        self.manager.compatibility_matrix = {
            "0.1.0": ["1.0.0", "1.1.0"],
            "0.2.0": ["1.2.0", "2.0.0"],
        }

        # Test compatible versions
        self.assertTrue(self.manager.is_compatible("1.0.0", "0.1.0"))
        self.assertTrue(self.manager.is_compatible("1.1.0", "0.1.0"))
        self.assertTrue(self.manager.is_compatible("1.2.0", "0.2.0"))
        self.assertTrue(self.manager.is_compatible("2.0.0", "0.2.0"))

        # Test incompatible versions
        self.assertFalse(self.manager.is_compatible("1.2.0", "0.1.0"))
        self.assertFalse(self.manager.is_compatible("1.0.0", "0.2.0"))

    @patch("mcp_server_tribal.services.migration.__version__", "0.1.0")
    def test_compatibility_with_current_version(self):
        """Test compatibility checking using the current app version."""
        # Set up compatibility matrix
        self.manager.compatibility_matrix = {
            "0.1.0": ["1.0.0", "1.1.0"],
            "0.2.0": ["1.2.0", "2.0.0"],
        }

        # Test compatible and incompatible versions
        self.assertTrue(
            self.manager.is_compatible("1.0.0")
        )  # Should use patched version
        self.assertTrue(self.manager.is_compatible("1.1.0"))
        self.assertFalse(self.manager.is_compatible("1.2.0"))
        self.assertFalse(self.manager.is_compatible("2.0.0"))


class TestChromaDBMigration(unittest.TestCase):
    """Tests for ChromaDB-specific migrations."""

    def test_initial_migration(self):
        """Test the initial migration for ChromaDB."""
        manager = create_migration_test_manager()

        # Create mock storage with no schema version (initial state)
        storage = MockStorage("0.0.0")

        # Create a migration that updates the schema version
        def migrate_initial_to_v1(storage):
            storage.collection.modify(metadata={"schema_version": "1.0.0"})

        manager.register_migration("0.0.0", "1.0.0", migrate_initial_to_v1)
        manager.register_compatibility("0.1.0", ["1.0.0"])

        # Execute the migration
        result = manager.execute_migration(storage, "0.0.0", "1.0.0")

        # Check the migration was successful
        self.assertTrue(result)
        self.assertEqual(storage.get_schema_version(), "1.0.0")

    @patch("mcp_server_tribal.services.migration.__version__", "0.1.0")
    def test_schema_validation(self):
        """Test schema validation during storage initialization."""
        manager = create_migration_test_manager()

        # Register compatibility
        manager.register_compatibility("0.1.0", ["1.0.0"])

        # Test with compatible version
        storage1 = MockStorage("1.0.0")
        self.assertTrue(manager.is_compatible(storage1.get_schema_version()))

        # Test with incompatible version
        storage2 = MockStorage("2.0.0")
        self.assertFalse(manager.is_compatible(storage2.get_schema_version()))


if __name__ == "__main__":
    unittest.main()
