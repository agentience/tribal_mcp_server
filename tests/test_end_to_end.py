"""End-to-end tests for the MCP server."""

import os
import tempfile
import pytest
import shutil
import uuid
from typing import Dict, List, Optional
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from learned_knowledge_mcp.app import app
from learned_knowledge_mcp.models.error_record import ErrorContext, ErrorQuery, ErrorRecord, ErrorSolution
from learned_knowledge_mcp.services.storage_interface import StorageInterface


# Create a mock storage service that doesn't depend on ChromaDB
class MockStorage(StorageInterface):
    """Mock implementation of storage interface for testing."""
    
    def __init__(self):
        """Initialize the mock storage."""
        self.errors = {}  # Dictionary to store errors by ID
    
    async def add_error(self, error: ErrorRecord) -> ErrorRecord:
        """Add a new error record to storage."""
        self.errors[str(error.id)] = error
        return error
    
    async def get_error(self, error_id: uuid.UUID) -> Optional[ErrorRecord]:
        """Retrieve an error record by ID."""
        return self.errors.get(str(error_id))
    
    async def update_error(self, error_id: uuid.UUID, error: ErrorRecord) -> Optional[ErrorRecord]:
        """Update an existing error record."""
        if str(error_id) not in self.errors:
            return None
        error.id = error_id
        self.errors[str(error_id)] = error
        return error
    
    async def delete_error(self, error_id: uuid.UUID) -> bool:
        """Delete an error record by ID."""
        if str(error_id) not in self.errors:
            return False
        del self.errors[str(error_id)]
        return True
    
    async def search_errors(self, query: ErrorQuery) -> List[ErrorRecord]:
        """Search for error records based on the provided query."""
        results = []
        
        for error in self.errors.values():
            # Check if the error matches the query criteria
            if query.error_type and error.error_type != query.error_type:
                continue
            if query.language and error.context.language != query.language:
                continue
            if query.framework and error.context.framework != query.framework:
                continue
            
            # Add the error to the results if it passes all criteria
            results.append(error)
            
            # Limit the number of results
            if len(results) >= query.max_results:
                break
        
        return results
    
    async def search_similar(self, text_query: str, max_results: int = 5) -> List[ErrorRecord]:
        """Search for error records with similar text content."""
        # For mocking similarity search, we'll do a simple substring match
        # In a real implementation, this would use embeddings and vector search
        results = []
        
        for error in self.errors.values():
            # Create a combined text from the error for searching
            error_text = (
                f"{error.error_type} {error.context.language} {error.context.framework or ''} "
                f"{error.context.error_message} {error.context.code_snippet or ''} "
                f"{error.solution.description} {error.solution.explanation}"
            ).lower()
            
            # Check if the query text appears in the error text
            query_lower = text_query.lower()
            if any(term in error_text for term in query_lower.split()):
                results.append(error)
            
            # Limit the number of results
            if len(results) >= max_results:
                break
        
        return results


@pytest.fixture
def client(monkeypatch):
    """Create a test client for the API with a mock storage."""
    # Mock the environment variables
    monkeypatch.setenv("REQUIRE_AUTH", "false")
    
    # Create a mock storage instance
    mock_storage = MockStorage()
    
    # Override the storage dependency
    def get_test_storage() -> StorageInterface:
        return mock_storage
    
    app.dependency_overrides[StorageInterface] = get_test_storage
    
    return TestClient(app)


@pytest.fixture
def sample_error_records():
    """Create sample error records for testing."""
    return [
        ErrorRecord(
            error_type="ImportError",
            context=ErrorContext(
                language="python",
                framework="fastapi",
                error_message="No module named 'fastapi'",
                code_snippet="from fastapi import FastAPI\napp = FastAPI()",
                task_description="Setting up a FastAPI server",
            ),
            solution=ErrorSolution(
                description="Install FastAPI package",
                code_fix="pip install fastapi",
                explanation="The fastapi package needs to be installed before importing it",
                references=["https://fastapi.tiangolo.com/tutorial/"],
            ),
        ),
        ErrorRecord(
            error_type="TypeError",
            context=ErrorContext(
                language="python",
                framework="pandas",
                error_message="cannot convert the series to <class 'int'>",
                code_snippet="df['age'] = int(df['age'])",
                task_description="Converting a pandas Series to integers",
            ),
            solution=ErrorSolution(
                description="Use the astype method",
                code_fix="df['age'] = df['age'].astype(int)",
                explanation="To convert a pandas Series to integers, use the astype method instead of int()",
                references=["https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.astype.html"],
            ),
        ),
        ErrorRecord(
            error_type="SyntaxError",
            context=ErrorContext(
                language="python",
                error_message="invalid syntax",
                code_snippet="print 'Hello, world!'",
                task_description="Printing a message",
            ),
            solution=ErrorSolution(
                description="Use parentheses with print",
                code_fix="print('Hello, world!')",
                explanation="In Python 3, print is a function and requires parentheses",
                references=["https://docs.python.org/3/whatsnew/3.0.html#print-is-a-function"],
            ),
        ),
    ]


async def populate_test_data(client, sample_error_records):
    """Populate the database with test data."""
    created_records = []
    
    for record in sample_error_records:
        response = client.post(
            "/api/v1/errors/",
            json=record.model_dump(mode="json"),
        )
        assert response.status_code == 201
        created_records.append(response.json())
    
    return created_records


def test_create_and_get_error(client, sample_error_records):
    """Test creating and retrieving an error record."""
    # Create an error record
    record = sample_error_records[0]
    response = client.post(
        "/api/v1/errors/",
        json=record.model_dump(mode="json"),
    )
    assert response.status_code == 201
    created_record = response.json()
    assert created_record["error_type"] == record.error_type
    assert created_record["context"]["language"] == record.context.language
    assert created_record["solution"]["description"] == record.solution.description
    
    # Get the error record by ID
    error_id = created_record["id"]
    response = client.get(f"/api/v1/errors/{error_id}")
    assert response.status_code == 200
    retrieved_record = response.json()
    assert retrieved_record["id"] == error_id
    assert retrieved_record["error_type"] == record.error_type
    assert retrieved_record["context"]["language"] == record.context.language
    assert retrieved_record["solution"]["description"] == record.solution.description


def test_search_by_exact_match(client, sample_error_records):
    """Test searching for error records by exact match."""
    # Populate the database with test data
    created_records = client.post(
        "/api/v1/errors/",
        json=sample_error_records[0].model_dump(mode="json"),
    ).json()
    
    # Search by error type
    response = client.get(
        "/api/v1/errors/",
        params={"error_type": "ImportError"}
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    assert results[0]["error_type"] == "ImportError"
    
    # Search by language
    response = client.get(
        "/api/v1/errors/",
        params={"language": "python"}
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    assert results[0]["context"]["language"] == "python"
    
    # Search by framework
    response = client.get(
        "/api/v1/errors/",
        params={"framework": "fastapi"}
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    assert results[0]["context"]["framework"] == "fastapi"


def test_search_by_similar_message(client, sample_error_records):
    """Test searching for error records by similar message."""
    # Create error records
    for record in sample_error_records:
        client.post(
            "/api/v1/errors/",
            json=record.model_dump(mode="json"),
        )
    
    # Search by similar error message
    response = client.get(
        "/api/v1/errors/similar/",
        params={
            "query": "cannot import FastAPI module", 
            "max_results": 2
        }
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    
    # The most similar result should be related to ImportError for FastAPI
    assert any(r["error_type"] == "ImportError" and "fastapi" in r["context"]["error_message"].lower() for r in results)


def test_real_world_workflow(client, sample_error_records):
    """Test a real-world workflow of storing an error and finding a solution for a similar error."""
    # 1. Store several errors in the database
    for record in sample_error_records:
        client.post(
            "/api/v1/errors/",
            json=record.model_dump(mode="json"),
        )
    
    # 2. Simulate a new user encountering a pandas type conversion error
    query = """
    I'm getting this error in pandas:
    TypeError: Cannot convert Series to int
    Here's my code:
    ages = int(df['age_column'])
    I'm trying to convert a column to integers.
    """
    
    # 3. Search for similar errors
    response = client.get(
        "/api/v1/errors/similar/",
        params={"query": query, "max_results": 3}
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    
    # 4. The top result should be the pandas TypeError
    found_pandas_solution = False
    for result in results:
        if (result["error_type"] == "TypeError" and 
            "pandas" in result["context"].get("framework", "").lower() and
            "astype" in result["solution"].get("code_fix", "").lower()):
            found_pandas_solution = True
            break
    
    assert found_pandas_solution, "Should find the pandas solution with astype"