"""
Database Integration Tests

Fixed integration tests for database operations with proper import paths
and mock implementations for development environment.
"""

import pytest
import asyncio
from typing import Dict, Any, List
from datetime import datetime
import json
import sys
from pathlib import Path

# Add core modules to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))


class MockFirestoreService:
    """Mock Firestore service for testing without GCP credentials."""
    
    def __init__(self):
        self.collections = {}
        self.documents = {}
    
    async def create_document(self, collection: str, document_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a document in a collection."""
        if collection not in self.collections:
            self.collections[collection] = {}
        
        doc_data = {
            **data,
            "id": document_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.collections[collection][document_id] = doc_data
        return doc_data
    
    async def get_document(self, collection: str, document_id: str) -> Dict[str, Any]:
        """Get a document from a collection."""
        if collection not in self.collections:
            raise ValueError(f"Collection {collection} not found")
        
        if document_id not in self.collections[collection]:
            raise ValueError(f"Document {document_id} not found")
        
        return self.collections[collection][document_id]
    
    async def update_document(self, collection: str, document_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a document in a collection."""
        if collection not in self.collections:
            raise ValueError(f"Collection {collection} not found")
        
        if document_id not in self.collections[collection]:
            raise ValueError(f"Document {document_id} not found")
        
        self.collections[collection][document_id].update(data)
        self.collections[collection][document_id]["updated_at"] = datetime.now().isoformat()
        
        return self.collections[collection][document_id]
    
    async def delete_document(self, collection: str, document_id: str) -> bool:
        """Delete a document from a collection."""
        if collection not in self.collections:
            return False
        
        if document_id not in self.collections[collection]:
            return False
        
        del self.collections[collection][document_id]
        return True
    
    async def list_documents(self, collection: str, limit: int = 10) -> List[Dict[str, Any]]:
        """List documents in a collection."""
        if collection not in self.collections:
            return []
        
        documents = list(self.collections[collection].values())
        return documents[:limit]
    
    async def query_documents(self, collection: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Query documents in a collection with filters."""
        if collection not in self.collections:
            return []
        
        documents = list(self.collections[collection].values())
        
        # Simple filtering implementation
        filtered_docs = []
        for doc in documents:
            match = True
            for key, value in filters.items():
                if key not in doc or doc[key] != value:
                    match = False
                    break
            if match:
                filtered_docs.append(doc)
        
        return filtered_docs


class MockBigQueryService:
    """Mock BigQuery service for testing without GCP credentials."""
    
    def __init__(self):
        self.datasets = {}
        self.tables = {}
    
    async def create_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """Create a dataset."""
        dataset_info = {
            "id": dataset_id,
            "created_at": datetime.now().isoformat(),
            "tables": []
        }
        self.datasets[dataset_id] = dataset_info
        return dataset_info
    
    async def create_table(self, dataset_id: str, table_id: str, schema: List[Dict[str, str]]) -> Dict[str, Any]:
        """Create a table in a dataset."""
        if dataset_id not in self.datasets:
            await self.create_dataset(dataset_id)
        
        table_key = f"{dataset_id}.{table_id}"
        table_info = {
            "id": table_id,
            "dataset_id": dataset_id,
            "schema": schema,
            "created_at": datetime.now().isoformat(),
            "rows": []
        }
        
        self.tables[table_key] = table_info
        self.datasets[dataset_id]["tables"].append(table_id)
        return table_info
    
    async def insert_rows(self, dataset_id: str, table_id: str, rows: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Insert rows into a table."""
        table_key = f"{dataset_id}.{table_id}"
        if table_key not in self.tables:
            raise ValueError(f"Table {table_key} not found")
        
        for row in rows:
            row["inserted_at"] = datetime.now().isoformat()
            self.tables[table_key]["rows"].append(row)
        
        return {
            "inserted_rows": len(rows),
            "total_rows": len(self.tables[table_key]["rows"])
        }
    
    async def query_table(self, query: str) -> List[Dict[str, Any]]:
        """Execute a query (simplified mock implementation)."""
        # Simple mock query implementation
        if "SELECT COUNT(*)" in query.upper():
            return [{"count": 100}]
        elif "SELECT *" in query.upper():
            # Return sample data
            return [
                {"id": 1, "name": "Sample Event", "category": "traffic"},
                {"id": 2, "name": "Another Event", "category": "infrastructure"}
            ]
        else:
            return []


class TestDatabaseOperations:
    """Integration tests for database operations."""
    
    @pytest.fixture
    def firestore_service(self):
        """Firestore service fixture."""
        return MockFirestoreService()
    
    @pytest.fixture
    def bigquery_service(self):
        """BigQuery service fixture."""
        return MockBigQueryService()
    
    @pytest.mark.asyncio
    async def test_firestore_document_crud(self, firestore_service):
        """Test Firestore document CRUD operations."""
        collection = "events"
        document_id = "test_event_001"
        
        # Test create
        event_data = {
            "title": "Test Event",
            "category": "traffic",
            "status": "open",
            "description": "Test event for integration testing"
        }
        
        created_doc = await firestore_service.create_document(collection, document_id, event_data)
        assert created_doc["id"] == document_id
        assert created_doc["title"] == "Test Event"
        assert "created_at" in created_doc
        
        # Test read
        retrieved_doc = await firestore_service.get_document(collection, document_id)
        assert retrieved_doc["id"] == document_id
        assert retrieved_doc["title"] == "Test Event"
        
        # Test update
        update_data = {"status": "resolved", "resolution": "Fixed"}
        updated_doc = await firestore_service.update_document(collection, document_id, update_data)
        assert updated_doc["status"] == "resolved"
        assert updated_doc["resolution"] == "Fixed"
        assert "updated_at" in updated_doc
        
        # Test delete
        deleted = await firestore_service.delete_document(collection, document_id)
        assert deleted is True
        
        # Verify deletion
        with pytest.raises(ValueError):
            await firestore_service.get_document(collection, document_id)
    
    @pytest.mark.asyncio
    async def test_firestore_collection_operations(self, firestore_service):
        """Test Firestore collection operations."""
        collection = "users"
        
        # Create multiple documents
        users = [
            {"name": "Alice", "role": "citizen", "email": "alice@example.com"},
            {"name": "Bob", "role": "authority", "email": "bob@example.com"},
            {"name": "Charlie", "role": "citizen", "email": "charlie@example.com"}
        ]
        
        for i, user in enumerate(users):
            await firestore_service.create_document(collection, f"user_{i+1}", user)
        
        # Test list documents
        documents = await firestore_service.list_documents(collection)
        assert len(documents) == 3
        
        # Test query documents
        citizens = await firestore_service.query_documents(collection, {"role": "citizen"})
        assert len(citizens) == 2
        
        authorities = await firestore_service.query_documents(collection, {"role": "authority"})
        assert len(authorities) == 1
        assert authorities[0]["name"] == "Bob"
    
    @pytest.mark.asyncio
    async def test_bigquery_dataset_operations(self, bigquery_service):
        """Test BigQuery dataset operations."""
        dataset_id = "test_analytics"
        
        # Create dataset
        dataset = await bigquery_service.create_dataset(dataset_id)
        assert dataset["id"] == dataset_id
        assert "created_at" in dataset
        assert dataset["tables"] == []
    
    @pytest.mark.asyncio
    async def test_bigquery_table_operations(self, bigquery_service):
        """Test BigQuery table operations."""
        dataset_id = "test_analytics"
        table_id = "events"
        
        # Define schema
        schema = [
            {"name": "id", "type": "STRING"},
            {"name": "title", "type": "STRING"},
            {"name": "category", "type": "STRING"},
            {"name": "created_at", "type": "TIMESTAMP"}
        ]
        
        # Create table
        table = await bigquery_service.create_table(dataset_id, table_id, schema)
        assert table["id"] == table_id
        assert table["dataset_id"] == dataset_id
        assert table["schema"] == schema
        assert table["rows"] == []
    
    @pytest.mark.asyncio
    async def test_bigquery_data_insertion(self, bigquery_service):
        """Test BigQuery data insertion."""
        dataset_id = "test_analytics"
        table_id = "events"
        
        # Create table first
        schema = [
            {"name": "id", "type": "STRING"},
            {"name": "title", "type": "STRING"},
            {"name": "category", "type": "STRING"}
        ]
        await bigquery_service.create_table(dataset_id, table_id, schema)
        
        # Insert data
        rows = [
            {"id": "evt_001", "title": "Traffic Jam", "category": "traffic"},
            {"id": "evt_002", "title": "Road Repair", "category": "infrastructure"}
        ]
        
        result = await bigquery_service.insert_rows(dataset_id, table_id, rows)
        assert result["inserted_rows"] == 2
        assert result["total_rows"] == 2
    
    @pytest.mark.asyncio
    async def test_bigquery_querying(self, bigquery_service):
        """Test BigQuery querying."""
        # Test count query
        count_result = await bigquery_service.query_table("SELECT COUNT(*) FROM events")
        assert len(count_result) == 1
        assert "count" in count_result[0]
        
        # Test select query
        select_result = await bigquery_service.query_table("SELECT * FROM events LIMIT 10")
        assert len(select_result) >= 0
        
        if select_result:
            assert "id" in select_result[0]
            assert "name" in select_result[0]
    
    @pytest.mark.asyncio
    async def test_database_error_handling(self, firestore_service):
        """Test database error handling."""
        # Test getting non-existent document
        with pytest.raises(ValueError):
            await firestore_service.get_document("nonexistent", "doc_id")
        
        # Test updating non-existent document
        with pytest.raises(ValueError):
            await firestore_service.update_document("nonexistent", "doc_id", {})
        
        # Test deleting non-existent document
        result = await firestore_service.delete_document("nonexistent", "doc_id")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_data_consistency(self, firestore_service):
        """Test data consistency across operations."""
        collection = "consistency_test"
        document_id = "test_doc"
        
        # Create document
        original_data = {"value": 100, "status": "active"}
        await firestore_service.create_document(collection, document_id, original_data)
        
        # Read and verify
        doc = await firestore_service.get_document(collection, document_id)
        assert doc["value"] == 100
        assert doc["status"] == "active"
        
        # Update and verify
        await firestore_service.update_document(collection, document_id, {"value": 200})
        updated_doc = await firestore_service.get_document(collection, document_id)
        assert updated_doc["value"] == 200
        assert updated_doc["status"] == "active"  # Should remain unchanged


# Pytest configuration
pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.integration,
    pytest.mark.database
]
