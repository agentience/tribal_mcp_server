#!/usr/bin/env python3
# filename: {filename}
# description:
#
# Copyright (c) 2025 Agentience.ai
# Author: Troy Molander
# License: MIT License - See LICENSE file for details
#
# Version: 0.1.0

# filename: scripts/check_version_consistency.py
#
# Copyright (c) 2025 Agentience.ai
# Author: Troy Molander
# License: MIT License - See LICENSE file for details
#
# Version: 0.1.0

"""
Script to check version consistency across the project.

This script verifies that all version references in the codebase are consistent.
It checks:
- __version__ in __init__.py
- version in pyproject.toml
- schema version in models/error_record.py
- schema version in services/chroma_storage.py
- compatibility matrix in services/migration.py
"""

import os
import re
import sys
import tomli
from typing import List, Tuple


def check_init_version() -> Tuple[bool, str]:
    """Check the version in __init__.py."""
    init_path = os.path.join("src", "mcp_server_tribal", "__init__.py")
    version_pattern = re.compile(r'__version__ = "([\d\.]+(-[a-zA-Z0-9]+)?)"')

    with open(init_path, "r") as f:
        content = f.read()

    match = version_pattern.search(content)
    if not match:
        return False, f"Could not find __version__ in {init_path}"

    version = match.group(1)
    return True, version


def check_pyproject_version() -> Tuple[bool, str]:
    """Check the version in pyproject.toml."""
    pyproject_path = "pyproject.toml"

    try:
        with open(pyproject_path, "rb") as f:
            pyproject = tomli.load(f)

        version = pyproject.get("project", {}).get("version")
        if not version:
            return False, f"Could not find project.version in {pyproject_path}"

        return True, version
    except Exception as e:
        return False, f"Error reading {pyproject_path}: {e}"


def check_error_record_schema_version() -> Tuple[bool, str]:
    """Check the schema version in models/error_record.py."""
    error_record_path = os.path.join(
        "src", "mcp_server_tribal", "models", "error_record.py"
    )
    schema_version_pattern = re.compile(r'SCHEMA_VERSION = "([\d\.]+)"')

    with open(error_record_path, "r") as f:
        content = f.read()

    match = schema_version_pattern.search(content)
    if not match:
        return False, f"Could not find SCHEMA_VERSION in {error_record_path}"

    version = match.group(1)
    return True, version


def check_chroma_storage_schema_version() -> Tuple[bool, str]:
    """Check the schema version in services/chroma_storage.py."""
    chroma_storage_path = os.path.join(
        "src", "mcp_server_tribal", "services", "chroma_storage.py"
    )
    schema_version_pattern = re.compile(r'SCHEMA_VERSION = "([\d\.]+)"')

    with open(chroma_storage_path, "r") as f:
        content = f.read()

    match = schema_version_pattern.search(content)
    if not match:
        return False, f"Could not find SCHEMA_VERSION in {chroma_storage_path}"

    version = match.group(1)
    return True, version


def check_migration_compatibility_matrix(
    app_version: str, schema_version: str
) -> Tuple[bool, str]:
    """Check the compatibility matrix in services/migration.py."""
    migration_path = os.path.join(
        "src", "mcp_server_tribal", "services", "migration.py"
    )

    with open(migration_path, "r") as f:
        content = f.read()

    # This is a simplistic approach - in a real implementation, we might use AST parsing
    compatibility_pattern = re.compile(
        r"self\.compatibility_matrix: Dict.*?{(.*?)}", re.DOTALL
    )
    match = compatibility_pattern.search(content)

    if not match:
        return False, f"Could not find compatibility_matrix in {migration_path}"

    matrix_str = match.group(1)

    # Check if the app version is in the matrix
    app_version_pattern = re.compile(rf'"{app_version}": \[(.*?)\]')
    app_match = app_version_pattern.search(matrix_str)

    if not app_match:
        return False, f"App version {app_version} not found in compatibility matrix"

    # Check if the schema version is listed for the app version
    schema_versions_str = app_match.group(1)
    if f'"{schema_version}"' not in schema_versions_str:
        return (
            False,
            f"Schema version {schema_version} not compatible with app version {app_version}",
        )

    return (
        True,
        f"App version {app_version} is compatible with schema version {schema_version}",
    )


def check_version_references_in_codebase(app_version: str) -> List[Tuple[bool, str]]:
    """Check for version references throughout the codebase."""
    results = []

    for root, _, files in os.walk("src"):
        for file in files:
            if not file.endswith((".py", ".md")):
                continue

            file_path = os.path.join(root, file)
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Skip __init__.py as it's already checked
            if file == "__init__.py" and root.endswith("mcp_server_tribal"):
                continue

            # Look for version strings in format "x.y.z" that don't match app_version
            version_pattern = re.compile(r"(\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?)")
            for match in version_pattern.finditer(content):
                found_version = match.group(1)

                # Skip schema versions (1.x.x)
                if found_version.startswith("1.") and app_version.startswith("0."):
                    continue

                # If we find a version that doesn't match and isn't in a comment
                line = content[
                    content.rfind("\n", 0, match.start())
                    + 1 : content.find("\n", match.end())
                ]
                if (
                    found_version != app_version
                    and not line.strip().startswith("#")
                    and not line.strip().startswith('"""')
                    and "SCHEMA_VERSION" not in line
                    and "schema_version" not in line
                    and "compatibility_matrix" not in line
                ):
                    results.append(
                        (
                            False,
                            f"Found inconsistent version {found_version} in {file_path}",
                        )
                    )

    return results


def main() -> int:
    """Main function to check version consistency."""
    print("Checking version consistency...")
    all_consistent = True

    # Check __init__.py version
    init_success, init_version = check_init_version()
    if not init_success:
        print(f"ERROR: {init_version}")
        return 1

    print(f"App version from __init__.py: {init_version}")

    # Check pyproject.toml version
    pyproject_success, pyproject_version = check_pyproject_version()
    if not pyproject_success:
        print(f"ERROR: {pyproject_version}")
        return 1

    print(f"App version from pyproject.toml: {pyproject_version}")

    # Check versions match
    if init_version != pyproject_version:
        print(
            f"ERROR: Version mismatch between __init__.py ({init_version}) and pyproject.toml ({pyproject_version})"
        )
        all_consistent = False

    # Check schema versions
    error_record_success, error_record_schema = check_error_record_schema_version()
    if not error_record_success:
        print(f"ERROR: {error_record_schema}")
        return 1

    print(f"Schema version from error_record.py: {error_record_schema}")

    chroma_success, chroma_schema = check_chroma_storage_schema_version()
    if not chroma_success:
        print(f"ERROR: {chroma_schema}")
        return 1

    print(f"Schema version from chroma_storage.py: {chroma_schema}")

    # Check schema versions match
    if error_record_schema != chroma_schema:
        print(
            f"ERROR: Schema version mismatch between error_record.py ({error_record_schema}) and chroma_storage.py ({chroma_schema})"
        )
        all_consistent = False

    # Check compatibility matrix
    compat_success, compat_message = check_migration_compatibility_matrix(
        init_version, error_record_schema
    )
    if not compat_success:
        print(f"ERROR: {compat_message}")
        all_consistent = False
    else:
        print(f"Compatibility: {compat_message}")

    # Check for version references throughout the codebase
    print("\nChecking for version references in codebase...")
    reference_checks = check_version_references_in_codebase(init_version)
    for success, message in reference_checks:
        if not success:
            print(f"WARNING: {message}")
            # Don't fail the build for these warnings

    # Final result
    if all_consistent:
        print("\nSUCCESS: All versions are consistent!")
        return 0
    else:
        print("\nERROR: Version inconsistencies found. See above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
