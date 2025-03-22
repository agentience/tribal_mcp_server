# Project Brief: Tribal

## Overview
Tribal is an MCP (Model Context Protocol) server implementation for error knowledge tracking and retrieval. It provides both REST API and native MCP interfaces for integration with tools like Claude Code and Cline.

## Core Purpose
Tribal helps Claude and other AI assistants remember and learn from programming errors. It acts as a persistent memory store for error solutions, allowing AI assistants to:
1. Store programming errors and solutions
2. Search for similar errors when encountering problems
3. Build a knowledge base specific to coding patterns

## Key Features
- Store and retrieve error records with full context
- Vector similarity search using ChromaDB
- JWT authentication with API keys
- Local storage (ChromaDB) and AWS integration
- Docker-compose deployment
- CLI client integration

## Project Goals
1. Prevent repetitive problem-solving by AI assistants
2. Create a shared knowledge base for development teams
3. Preserve context across different AI assistant sessions
4. Enable AI assistants to learn from past solutions
5. Standardize error handling approaches

## Project Scope
### In Scope
- Error storage and retrieval mechanisms
- Semantic similarity search
- MCP server implementation
- REST API endpoints
- Authentication and authorization
- Local and cloud storage options
- CLI and API client interfaces

### Out of Scope
- Training of AI models
- IDE integrations (will be handled by separate projects)
- Metrics and analytics dashboard (future enhancement)

## Success Criteria
1. AI assistants can store and retrieve error solutions
2. Semantic similarity search accurately identifies relevant past solutions
3. Multiple storage backends are supported
4. API and MCP interfaces perform reliably
5. Low-latency responses for error lookups
