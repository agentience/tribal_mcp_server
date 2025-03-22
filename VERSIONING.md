# Tribal Versioning Strategy

This document outlines the versioning strategy used by the Tribal project, including application version, database schema version, and compatibility guidelines.

## Semantic Versioning

Tribal follows [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH[-PRERELEASE]
```

- **MAJOR**: Incremented for incompatible API changes
- **MINOR**: Incremented for backward-compatible new functionality
- **PATCH**: Incremented for backward-compatible bug fixes
- **PRERELEASE**: Optional tag for pre-release versions (alpha, beta, rc)

### Version Progression

```
0.1.0      # Initial development version
0.1.1      # Bug fixes
0.2.0      # New features, no breaking changes
0.2.1-beta # Beta version with some fixes
1.0.0      # First stable release (API considered stable)
1.1.0      # New features added
2.0.0      # Breaking changes to API
```

### Versioning Rules

#### Pre-1.0 Development (Current Phase)

While in 0.x.y stage:
- **MINOR** version indicates significant new features
- **PATCH** version indicates bug fixes and minor enhancements
- API should be considered unstable and subject to change

#### Post-1.0 Stable Release

After reaching 1.0.0:
- **MAJOR** version indicates breaking changes:
  - Incompatible API changes
  - Removal of deprecated functionality
  - Major architectural changes
- **MINOR** version indicates new functionality:
  - New API endpoints
  - New optional parameters
  - New tools or resources
  - Backward-compatible changes
- **PATCH** version indicates bug fixes:
  - Security patches
  - Performance improvements
  - Bug fixes without API changes

## Schema Versioning

The database schema has its own version, which follows the same semantic versioning principles:

```
MAJOR.MINOR.PATCH
```

The current schema version is `1.0.0`.

### Schema Compatibility Matrix

The following table shows which schema versions are compatible with which application versions:

| App Version | Compatible Schema Versions |
|-------------|----------------------------|
| 0.1.0       | 1.0.0                     |

## Version Management

### Single Source of Truth

The version is maintained in the following files:
- `src/mcp_server_tribal/__init__.py` - Primary source of truth
- `pyproject.toml` - For packaging

### Automated Version Bumping

Use bump2version to update versions consistently:

```bash
# Increment patch version (0.1.0 -> 0.1.1)
bump2version patch

# Increment minor version (0.1.0 -> 0.2.0)
bump2version minor

# Increment major version (0.1.0 -> 1.0.0)
bump2version major

# Create pre-release version (0.1.0 -> 0.1.0-beta)
bump2version --new-version 0.1.0-beta pre
```

## Branching Strategy

The branching strategy is designed to support the versioning approach. See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed information about our branching strategy.

### Branch Types and Version Bumping

| Branch Type | Purpose                   | From Branch | Merges To      | Version Bump |
|-------------|---------------------------|-------------|----------------|--------------|
| feature/*   | New feature development   | develop     | develop        | None         |
| bugfix/*    | Non-critical bug fixes    | develop     | develop        | None         |
| release/*   | Release preparation       | develop     | main, develop  | Minor/Major  |
| hotfix/*    | Critical production fixes | main        | main, develop  | Patch        |
| docs/*      | Documentation changes     | develop     | develop        | None         |

## Release Process

1. Prepare release:
   - Create a release branch from develop
   - Bump version with `bump2version`
   - Update CHANGELOG.md
   - Run final tests

2. Finalize release:
   - Merge release branch to main (via PR)
   - Tag version on main
   - Merge changes back to develop

3. Publish release:
   - CI builds and publishes package based on version tag
   - Generate release notes

## Hotfix Process

For emergency hotfixes:

1. Create a hotfix branch from the relevant main tag
2. Implement and test the fix
3. Bump patch version
4. Merge to main via PR
5. Tag the new version
6. Merge back to develop

## Version Display

Version information is available through:
- CLI: `tribal version`
- API: Response headers and status endpoint
- Logs: Displayed on server startup
