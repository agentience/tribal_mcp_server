# filename: {filename}
# description:
#
# Copyright (c) 2025 Agentience.ai
# Author: Troy Molander
# License: MIT License - See LICENSE file for details
#
# Version: 0.1.0

# filename: tests/integration/test_migration_integration.py
#
# Copyright (c) 2025 Agentience.ai
# Author: Troy Molander
# License: MIT License - See LICENSE file for details
#
# Version: 0.1.0

"""Integration tests for schema migrations."""

import unittest
from typing import Dict, List
from unittest.mock import patch

from tests.unit.helpers.migration_test_helpers import (
    MockStorage,
    create_migration_test_manager,
)


class TestMigrationIntegration(unittest.TestCase):
    """Integration tests for the migration system with realistic schema changes."""

    def setUp(self):
        """Set up test case."""
        self.manager = create_migration_test_manager()
        # Register compatibility
        self.manager.register_compatibility("0.1.0", ["1.0.0"])
        self.manager.register_compatibility("0.2.0", ["1.0.0", "1.1.0"])
        self.manager.register_compatibility("0.3.0", ["1.1.0", "1.2.0"])

    def test_schema_evolution_add_field(self):
        """Test migration that adds a new field to the schema."""
        # Initial schema (version 1.0.0)
        initial_records = [
            {
                "id": "1",
                "error_type": "TypeError",
                "context": {
                    "language": "python",
                    "framework": "fastapi",
                    "error_message": "Cannot read property of undefined",
                },
                "solution": {
                    "description": "Check if variable exists before accessing",
                },
            },
            {
                "id": "2",
                "error_type": "ImportError",
                "context": {
                    "language": "python",
                    "framework": "django",
                    "error_message": "No module named 'xyz'",
                },
                "solution": {
                    "description": "Install the missing module",
                },
            },
        ]

        # Create mock storage with initial records
        storage = self._create_storage_with_records("1.0.0", initial_records)

        # Define migration to add severity field to records
        def migrate_v1_to_v1_1(storage):
            """Migration to add severity field to error records."""
            # In a real migration, we would update all records
            # Here we just update the collection metadata version
            storage.collection.modify(metadata={"schema_version": "1.1.0"})

            # Simulate updating each record with a default severity
            for record_id in storage.collection.documents:
                doc = storage.collection.documents[record_id]
                # Parse the document JSON
                import json

                record = json.loads(doc)

                # Add severity field (in a real migration)
                if "severity" not in record:
                    record["severity"] = "medium"

                # Update the document
                storage.collection.documents[record_id] = json.dumps(record)

        # Register the migration
        self.manager.register_migration("1.0.0", "1.1.0", migrate_v1_to_v1_1)

        # Execute the migration
        result = self.manager.execute_migration(storage, "1.0.0", "1.1.0")
        self.assertTrue(result)
        self.assertEqual(storage.get_schema_version(), "1.1.0")

        # Verify the migration effects (would check all records in a real test)
        import json

        record1 = json.loads(storage.collection.documents["1"])
        self.assertIn("severity", record1)
        self.assertEqual(record1["severity"], "medium")

    def test_schema_evolution_change_structure(self):
        """Test migration that changes the structure of records."""
        # Initial records with the old structure (version 1.1.0)
        initial_records = [
            {
                "id": "1",
                "error_type": "ValueError",
                "severity": "high",
                "context": {
                    "language": "javascript",
                    "framework": "react",
                    "error_message": "Expected array but got object",
                },
                "solution": {
                    "description": "Convert object to array",
                },
            },
        ]

        # Create mock storage with initial records
        storage = self._create_storage_with_records("1.1.0", initial_records)

        # Define migration to restructure context fields
        def migrate_v1_1_to_v1_2(storage):
            """Migration that restructures context to separate error_details and environment."""
            storage.collection.modify(metadata={"schema_version": "1.2.0"})

            # Simulate restructuring each record
            for record_id in storage.collection.documents:
                doc = storage.collection.documents[record_id]
                import json

                record = json.loads(doc)

                # Extract fields from old structure
                old_context = record.get("context", {})

                # Create new structure
                record["context"] = {
                    "environment": {
                        "language": old_context.get("language", ""),
                        "framework": old_context.get("framework", ""),
                    },
                    "error_details": {
                        "message": old_context.get("error_message", ""),
                        "code_snippet": old_context.get("code_snippet", ""),
                    },
                }

                # Update the document
                storage.collection.documents[record_id] = json.dumps(record)

        # Register the migration
        self.manager.register_migration("1.1.0", "1.2.0", migrate_v1_1_to_v1_2)

        # Execute the migration
        result = self.manager.execute_migration(storage, "1.1.0", "1.2.0")
        self.assertTrue(result)
        self.assertEqual(storage.get_schema_version(), "1.2.0")

        # Verify the migration effects
        import json

        record = json.loads(storage.collection.documents["1"])
        self.assertIn("environment", record["context"])
        self.assertIn("error_details", record["context"])
        self.assertEqual(record["context"]["environment"]["language"], "javascript")
        self.assertEqual(
            record["context"]["error_details"]["message"],
            "Expected array but got object",
        )

    @patch("mcp_server_tribal.services.migration.__version__", "0.3.0")
    def test_multi_step_migration(self):
        """Test a migration that requires multiple steps."""
        # Register migrations using the helper function that tracks migrations
        from tests.unit.helpers.migration_test_helpers import create_test_migration

        # Use the helper function that properly tracks migrations
        migrate_v1_to_v1_1 = create_test_migration("1.0.0", "1.1.0")
        migrate_v1_1_to_v1_2 = create_test_migration("1.1.0", "1.2.0")

        self.manager.register_migration("1.0.0", "1.1.0", migrate_v1_to_v1_1)
        self.manager.register_migration("1.1.0", "1.2.0", migrate_v1_1_to_v1_2)

        # Create storage with initial version
        storage = MockStorage("1.0.0")

        # Initialize the migrations tracking list
        storage._migrations_called = []

        # Execute multi-step migration
        result = self.manager.execute_migration(storage, "1.0.0", "1.2.0")
        self.assertTrue(result)
        self.assertEqual(storage.get_schema_version(), "1.2.0")

        # Check the migration path (both steps should have been executed)
        self.assertEqual(len(storage._migrations_called), 2)
        self.assertEqual(storage._migrations_called[0], ("1.0.0", "1.1.0"))
        self.assertEqual(storage._migrations_called[1], ("1.1.0", "1.2.0"))

    def test_migrate_fresh_installation(self):
        """Test migrating a fresh installation to the latest schema version."""

        # Register initial migration
        def migrate_initial_to_v1(storage):
            """Set up initial schema."""
            storage.collection.modify(metadata={"schema_version": "1.0.0"})

        self.manager.register_migration("0.0.0", "1.0.0", migrate_initial_to_v1)

        # Create storage with no schema version
        storage = MockStorage("0.0.0")

        # Execute migration
        result = self.manager.execute_migration(storage, "0.0.0", "1.0.0")
        self.assertTrue(result)
        self.assertEqual(storage.get_schema_version(), "1.0.0")

    def _create_storage_with_records(
        self, version: str, records: List[Dict]
    ) -> MockStorage:
        """Create a mock storage with the given schema version and records."""
        storage = MockStorage(version)

        # Add records to the mock storage
        import json

        for record in records:
            storage.collection.add(
                ids=[record["id"]],
                documents=[json.dumps(record)],
                metadatas=[{"error_type": record["error_type"]}],
            )

        return storage


if __name__ == "__main__":
    unittest.main()
