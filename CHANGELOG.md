# Changelog

All notable changes to Tribal will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Schema versioning for ChromaDB storage
- Automatic schema version validation on startup
- Schema migration framework for future upgrades
- Compatibility matrix between app and schema versions

### Changed
- Made version references consistent throughout the codebase
- Improved version command output

## [0.1.0] - 2025-03-22

### Added
- Initial release
- Error tracking and retrieval functionality
- ChromaDB integration for vector similarity search
- JWT authentication with API keys
- Local storage (ChromaDB) and AWS integration
- Docker-compose deployment
- REST API (FastAPI) and native MCP interfaces
- CLI client integration
