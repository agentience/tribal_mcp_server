# Technical Context: Tribal

## Technology Stack

### Core Technologies
| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Language | Python | 3.12+ | Main implementation language |
| API Framework | FastAPI | 0.110.0+ | REST API implementation |
| Vector Database | ChromaDB | 0.4.22+ | Vector storage and similarity search |
| Authentication | Python-Jose | 3.3.0+ | JWT token handling |
| MCP Protocol | MCP SDK | 1.3.0+ | Model Context Protocol implementation |
| Package Manager | uv | Latest | Dependency management |
| Testing | pytest | Latest | Test framework |
| CI/CD | GitHub Actions | N/A | Continuous integration and deployment |

### Dependencies
- **pydantic**: Data validation and settings management
- **numpy**: Mathematical operations for vector handling
- **uvicorn**: ASGI server implementation
- **python-multipart**: Form data parsing
- **tokenizers**: Text tokenization for vector embeddings

## Development Environment

### Prerequisites
- Python 3.12 or later
- uv package manager (recommended)
- Docker and Docker Compose (for containerized deployment)

### Configuration
The project uses environment variables for configuration:

#### FastAPI Server
- `PERSIST_DIRECTORY`: ChromaDB storage path (default: "./chroma_db")
- `API_KEY`: Authentication key (default: "dev-api-key")
- `SECRET_KEY`: JWT signing key (default: "insecure-dev-key-change-in-production")
- `REQUIRE_AUTH`: Authentication requirement (default: "false")
- `PORT`: Server port (default: 8000)

#### MCP Server
- `MCP_API_URL`: FastAPI server URL (default: "http://localhost:8000")
- `MCP_PORT`: MCP server port (default: 5000)
- `MCP_HOST`: Host to bind to (default: "0.0.0.0")
- `API_KEY`: FastAPI access key (default: "dev-api-key")
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_BUCKET`: For AWS integration

### Version Control
- **System**: Git
- **Repository**: GitHub
- **Branching Strategy**: GitFlow-inspired (see `.clinerules` and `VERSIONING.md`)
- **Version Management**: bump2version

## Project Structure

```
tribal/
├── src/
│   ├── mcp_server_tribal/      # Core package
│   │   ├── api/                # FastAPI endpoints
│   │   ├── cli/                # Command-line interface
│   │   ├── models/             # Pydantic models
│   │   ├── services/           # Service layer
│   │   │   ├── aws/            # AWS integrations
│   │   │   └── chroma_storage.py # ChromaDB implementation
│   │   └── utils/              # Utility functions
│   └── examples/               # Example usage code
├── tests/                      # pytest test suite
├── docker-compose.yml          # Docker production setup
├── pyproject.toml              # Project configuration
├── VERSIONING.md               # Versioning strategy documentation
├── CHANGELOG.md                # Version history
├── .bumpversion.cfg            # Version bumping configuration
└── README.md                   # Project documentation
```

## Technical Constraints

### Performance Constraints
- **Response Time**: < 200ms for vector similarity searches
- **Storage Efficiency**: Optimized vector embeddings to balance accuracy and storage
- **Scalability**: Must handle growing knowledge bases efficiently

### Security Constraints
- **Authentication**: JWT token-based authentication for API access
- **API Keys**: Required for production deployments
- **Input Validation**: All user inputs strictly validated

### Compatibility Constraints
- **Python Version**: Supports Python 3.12+
- **Schema Versioning**: Database schema must maintain compatibility
- **MCP Protocol**: Maintains compatibility with MCP specification

## Integration Points

### Claude Integration
- **Method**: Native MCP protocol integration
- **Configuration**: Claude desktop and CLI configuration options
- **Usage Pattern**: Automatic error detection and storage

### REST API
- **Authentication**: Bearer token authentication
- **Documentation**: OpenAPI/Swagger documentation
- **Versioning**: API versioning through URL path

### Storage Backends
- **Primary**: ChromaDB for vector storage and search
- **Alternative**: S3 for file-based storage
- **Future**: DynamoDB for AWS-native deployment

## Deployment Options

### Local Development
- Direct installation with pip/uv
- Development mode with auto-reload

### Docker Deployment
- Docker Compose for local deployment
- Production-ready container configuration

### Cloud Deployment
- AWS deployment support
- S3 and DynamoDB integration

## Technical Debt and Known Issues

### Current Technical Debt
- Schema migration automation needs improvement
- Test coverage for AWS integrations is incomplete
- Performance optimizations for large datasets

### Known Limitations
- Single-node deployment only (no clustering)
- Limited customization of vector embedding strategies
- Basic authentication without OAuth flows

## Future Technical Directions

### Planned Enhancements
- Improved schema migration framework
- Performance optimizations for large datasets
- Additional storage backends
- OAuth-based authentication

### Technical Explorations
- Distributed deployments for high availability
- Custom embedding model integration
- Real-time collaboration features
