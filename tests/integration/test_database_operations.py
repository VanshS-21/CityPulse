"""
Integration tests for CityPulse database operations.
Tests Firestore and BigQuery integrations, data consistency, and transactions.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, Any, List
import json

from google.cloud import firestore, bigquery
from google.cloud.firestore_v1.base_query import FieldFilter
from google.api_core import exceptions as gcp_exceptions

from data_models.services.firestore_service import FirestoreService
from data_models.firestore_models import Event, UserProfile, Feedback
from data_models.firestore_models.event import EventCategory, EventSeverity, EventStatus


class TestFirestoreIntegration:
    """Integration tests for Firestore operations."""
    
    def setup_method(self):
        """Setup for each test method."""
        # Mock Firestore client
        self.mock_client = Mock(spec=firestore.Client)
        self.service = FirestoreService()
        self.service.client = self.mock_client
    
    def test_firestore_connection(self):
        """Test Firestore connection and client initialization."""
        with patch('google.cloud.firestore.Client') as mock_client_class:
            mock_client_instance = Mock()
            mock_client_class.return_value = mock_client_instance
            
            # Test service initialization
            service = FirestoreService()
            
            # Verify client was created
            mock_client_class.assert_called_once()
            assert service.client == mock_client_instance
    
    def test_document_crud_operations(self):
        """Test complete CRUD operations for documents."""
        # Setup mock collection and document
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc_snapshot = Mock()
        
        self.mock_client.collection.return_value = mock_collection
        mock_collection.document.return_value = mock_doc_ref
        
        # Test data
        test_data = {
            "title": "Integration Test Event",
            "category": "infrastructure",
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Test CREATE operation
        mock_doc_ref.set.return_value = None
        result = self.service.set("events", "test-doc-id", test_data)
        
        # Verify set was called
        mock_doc_ref.set.assert_called_once_with(test_data)
        assert result is True
        
        # Test READ operation
        mock_doc_snapshot.exists = True
        mock_doc_snapshot.to_dict.return_value = test_data
        mock_doc_ref.get.return_value = mock_doc_snapshot
        
        retrieved_data = self.service.get("events", "test-doc-id")
        
        # Verify get was called and data matches
        mock_doc_ref.get.assert_called_once()
        assert retrieved_data == test_data
        
        # Test UPDATE operation
        update_data = {"status": "resolved", "updated_at": datetime.utcnow()}
        mock_doc_ref.update.return_value = None
        
        update_result = self.service.update("events", "test-doc-id", update_data)
        
        # Verify update was called
        mock_doc_ref.update.assert_called_once_with(update_data)
        assert update_result is True
        
        # Test DELETE operation
        mock_doc_ref.delete.return_value = None
        
        delete_result = self.service.delete("events", "test-doc-id")
        
        # Verify delete was called
        mock_doc_ref.delete.assert_called_once()
        assert delete_result is True
    
    def test_query_operations(self):
        """Test complex query operations."""
        # Setup mock collection and query
        mock_collection = Mock()
        mock_query = Mock()
        
        # Mock query results
        mock_doc1 = Mock()
        mock_doc1.id = "doc1"
        mock_doc1.to_dict.return_value = {
            "title": "Event 1",
            "category": "infrastructure",
            "status": "active"
        }
        
        mock_doc2 = Mock()
        mock_doc2.id = "doc2"
        mock_doc2.to_dict.return_value = {
            "title": "Event 2",
            "category": "infrastructure",
            "status": "resolved"
        }
        
        mock_query.stream.return_value = [mock_doc1, mock_doc2]
        mock_collection.where.return_value = mock_query
        self.mock_client.collection.return_value = mock_collection
        
        # Test single condition query
        results = self.service.query("events", "category", "==", "infrastructure")
        
        # Verify query was constructed correctly
        mock_collection.where.assert_called_once_with("category", "==", "infrastructure")
        mock_query.stream.assert_called_once()
        
        # Verify results
        assert len(results) == 2
        assert results[0]["title"] == "Event 1"
        assert results[1]["title"] == "Event 2"
    
    def test_multiple_condition_query(self):
        """Test queries with multiple conditions."""
        # Setup mock query chain
        mock_collection = Mock()
        mock_query1 = Mock()
        mock_query2 = Mock()
        
        mock_collection.where.return_value = mock_query1
        mock_query1.where.return_value = mock_query2
        mock_query2.stream.return_value = []
        
        self.mock_client.collection.return_value = mock_collection
        
        # Test multiple conditions
        conditions = [
            ("category", "==", "infrastructure"),
            ("status", "==", "active"),
            ("priority", "==", "high")
        ]
        
        results = self.service.query_multiple("events", conditions)
        
        # Verify query chain was built correctly
        mock_collection.where.assert_called_once_with("category", "==", "infrastructure")
        mock_query1.where.assert_called_once_with("status", "==", "active")
        mock_query2.where.assert_called_once_with("priority", "==", "high")
    
    def test_batch_operations(self):
        """Test batch operations for multiple documents."""
        # Setup mock batch
        mock_batch = Mock()
        self.mock_client.batch.return_value = mock_batch
        
        # Setup mock document references
        mock_doc_ref1 = Mock()
        mock_doc_ref2 = Mock()
        mock_collection = Mock()
        mock_collection.document.side_effect = [mock_doc_ref1, mock_doc_ref2]
        self.mock_client.collection.return_value = mock_collection
        
        # Test batch operations
        operations = [
            ("set", "events", "doc1", {"title": "Event 1", "status": "active"}),
            ("update", "events", "doc2", {"status": "resolved"})
        ]
        
        result = self.service.batch_operations(operations)
        
        # Verify batch operations were added
        mock_batch.set.assert_called_once_with(mock_doc_ref1, {"title": "Event 1", "status": "active"})
        mock_batch.update.assert_called_once_with(mock_doc_ref2, {"status": "resolved"})
        mock_batch.commit.assert_called_once()
        
        assert result is True
    
    def test_transaction_operations(self):
        """Test transaction operations."""
        # Setup mock transaction
        mock_transaction = Mock()
        mock_context_manager = Mock()
        mock_context_manager.__enter__ = Mock(return_value=mock_transaction)
        mock_context_manager.__exit__ = Mock(return_value=None)
        self.mock_client.transaction.return_value = mock_context_manager
        
        # Setup mock document references
        mock_doc_ref = Mock()
        mock_collection = Mock()
        mock_collection.document.return_value = mock_doc_ref
        self.mock_client.collection.return_value = mock_collection
        
        # Mock document snapshot for read
        mock_snapshot = Mock()
        mock_snapshot.exists = True
        mock_snapshot.to_dict.return_value = {"counter": 5}
        mock_doc_ref.get.return_value = mock_snapshot
        
        # Test transaction function
        def increment_counter(transaction):
            doc_ref = self.service.client.collection("counters").document("test-counter")
            snapshot = doc_ref.get(transaction=transaction)
            
            if snapshot.exists:
                current_value = snapshot.to_dict()["counter"]
                new_value = current_value + 1
                transaction.update(doc_ref, {"counter": new_value})
                return new_value
            else:
                transaction.set(doc_ref, {"counter": 1})
                return 1
        
        # Execute transaction
        with self.service.client.transaction() as transaction:
            result = increment_counter(transaction)
        
        # Verify transaction was used
        assert result == 6  # 5 + 1
    
    def test_error_handling(self):
        """Test error handling for database operations."""
        # Setup mock that raises exceptions
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_collection.document.return_value = mock_doc_ref
        self.mock_client.collection.return_value = mock_collection
        
        # Test handling of Firestore exceptions
        mock_doc_ref.set.side_effect = gcp_exceptions.PermissionDenied("Access denied")
        
        result = self.service.set("events", "test-doc", {"title": "Test"})
        
        # Should handle exception gracefully
        assert result is False
        
        # Test handling of network errors
        mock_doc_ref.get.side_effect = gcp_exceptions.ServiceUnavailable("Service unavailable")
        
        result = self.service.get("events", "test-doc")
        
        # Should handle exception gracefully
        assert result is None


class TestBigQueryIntegration:
    """Integration tests for BigQuery operations."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.mock_client = Mock(spec=bigquery.Client)
        
    def test_bigquery_connection(self):
        """Test BigQuery connection and client initialization."""
        with patch('google.cloud.bigquery.Client') as mock_client_class:
            mock_client_instance = Mock()
            mock_client_class.return_value = mock_client_instance
            
            # Test client initialization
            client = bigquery.Client()
            
            # Verify client was created
            mock_client_class.assert_called_once()
            assert client == mock_client_instance
    
    def test_table_operations(self):
        """Test BigQuery table operations."""
        # Mock dataset and table
        mock_dataset = Mock()
        mock_table = Mock()
        mock_table_ref = Mock()
        
        self.mock_client.dataset.return_value = mock_dataset
        mock_dataset.table.return_value = mock_table_ref
        self.mock_client.get_table.return_value = mock_table
        
        # Test table existence check
        table_ref = self.mock_client.dataset("test_dataset").table("test_table")
        table = self.mock_client.get_table(table_ref)
        
        # Verify calls
        self.mock_client.dataset.assert_called_once_with("test_dataset")
        mock_dataset.table.assert_called_once_with("test_table")
        self.mock_client.get_table.assert_called_once_with(table_ref)
        
        assert table == mock_table
    
    def test_query_execution(self):
        """Test BigQuery query execution."""
        # Mock query job and results
        mock_job = Mock()
        mock_row1 = Mock()
        mock_row1.values.return_value = ("event-1", "Traffic Incident", "infrastructure", "active")
        mock_row2 = Mock()
        mock_row2.values.return_value = ("event-2", "Broken Light", "infrastructure", "resolved")
        
        mock_job.result.return_value = [mock_row1, mock_row2]
        self.mock_client.query.return_value = mock_job
        
        # Test query execution
        query = """
        SELECT id, title, category, status
        FROM `project.dataset.events`
        WHERE category = 'infrastructure'
        LIMIT 10
        """
        
        job = self.mock_client.query(query)
        results = job.result()
        
        # Verify query was executed
        self.mock_client.query.assert_called_once_with(query)
        mock_job.result.assert_called_once()
        
        # Verify results
        assert len(list(results)) == 2
    
    def test_data_insertion(self):
        """Test BigQuery data insertion."""
        # Mock table for insertion
        mock_table = Mock()
        self.mock_client.get_table.return_value = mock_table
        
        # Mock insertion result
        mock_errors = []
        mock_table.insert_rows_json.return_value = mock_errors
        
        # Test data insertion
        rows_to_insert = [
            {
                "id": "event-123",
                "title": "New Event",
                "category": "infrastructure",
                "status": "active",
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": "event-124",
                "title": "Another Event",
                "category": "safety",
                "status": "pending",
                "created_at": datetime.utcnow().isoformat()
            }
        ]
        
        table_ref = self.mock_client.dataset("test_dataset").table("events")
        table = self.mock_client.get_table(table_ref)
        errors = table.insert_rows_json(rows_to_insert)
        
        # Verify insertion
        mock_table.insert_rows_json.assert_called_once_with(rows_to_insert)
        assert errors == []
    
    def test_streaming_insert(self):
        """Test BigQuery streaming insert operations."""
        # Mock streaming insert
        mock_table = Mock()
        self.mock_client.get_table.return_value = mock_table
        mock_table.insert_rows_json.return_value = []
        
        # Test streaming data
        streaming_data = {
            "id": "stream-event-1",
            "title": "Streaming Event",
            "category": "infrastructure",
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "location": {"lat": 40.7128, "lng": -74.0060}
        }
        
        # Insert single row
        table_ref = self.mock_client.dataset("analytics").table("events")
        table = self.mock_client.get_table(table_ref)
        errors = table.insert_rows_json([streaming_data])
        
        # Verify streaming insert
        assert errors == []
        mock_table.insert_rows_json.assert_called_once()
    
    def test_query_with_parameters(self):
        """Test parameterized BigQuery queries."""
        # Mock parameterized query
        mock_job = Mock()
        mock_job.result.return_value = []
        self.mock_client.query.return_value = mock_job
        
        # Test parameterized query
        query = """
        SELECT *
        FROM `project.dataset.events`
        WHERE category = @category
        AND created_at >= @start_date
        AND created_at <= @end_date
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("category", "STRING", "infrastructure"),
                bigquery.ScalarQueryParameter("start_date", "TIMESTAMP", datetime(2024, 1, 1)),
                bigquery.ScalarQueryParameter("end_date", "TIMESTAMP", datetime(2024, 1, 31))
            ]
        )
        
        job = self.mock_client.query(query, job_config=job_config)
        results = job.result()
        
        # Verify parameterized query
        self.mock_client.query.assert_called_once_with(query, job_config=job_config)
    
    def test_analytics_queries(self):
        """Test analytics and aggregation queries."""
        # Mock analytics query results
        mock_job = Mock()
        mock_row = Mock()
        mock_row.values.return_value = ("infrastructure", 150, 120, 80.0)
        mock_job.result.return_value = [mock_row]
        self.mock_client.query.return_value = mock_job
        
        # Test analytics query
        analytics_query = """
        SELECT 
            category,
            COUNT(*) as total_events,
            COUNTIF(status = 'resolved') as resolved_events,
            ROUND(COUNTIF(status = 'resolved') * 100.0 / COUNT(*), 2) as resolution_rate
        FROM `project.dataset.events`
        WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
        GROUP BY category
        ORDER BY total_events DESC
        """
        
        job = self.mock_client.query(analytics_query)
        results = list(job.result())
        
        # Verify analytics query
        assert len(results) == 1
        category, total, resolved, rate = results[0].values()
        assert category == "infrastructure"
        assert total == 150
        assert resolved == 120
        assert rate == 80.0


class TestDataConsistency:
    """Integration tests for data consistency between Firestore and BigQuery."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.mock_firestore = Mock()
        self.mock_bigquery = Mock()
    
    def test_event_data_sync(self):
        """Test data synchronization between Firestore and BigQuery."""
        # Mock event data
        event_data = {
            "id": "sync-test-event",
            "title": "Sync Test Event",
            "category": "infrastructure",
            "status": "active",
            "location": {"lat": 40.7128, "lng": -74.0060},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Mock Firestore operations
        self.mock_firestore.set.return_value = True
        self.mock_firestore.get.return_value = event_data
        
        # Mock BigQuery operations
        mock_table = Mock()
        mock_table.insert_rows_json.return_value = []
        self.mock_bigquery.get_table.return_value = mock_table
        
        # Test data sync workflow
        # 1. Save to Firestore
        firestore_result = self.mock_firestore.set("events", event_data["id"], event_data)
        assert firestore_result is True
        
        # 2. Sync to BigQuery
        bigquery_data = {
            **event_data,
            "created_at": event_data["created_at"].isoformat(),
            "updated_at": event_data["updated_at"].isoformat()
        }
        
        table = self.mock_bigquery.get_table("project.dataset.events")
        bigquery_errors = table.insert_rows_json([bigquery_data])
        assert bigquery_errors == []
        
        # 3. Verify data consistency
        retrieved_data = self.mock_firestore.get("events", event_data["id"])
        assert retrieved_data["title"] == event_data["title"]
        assert retrieved_data["category"] == event_data["category"]
    
    def test_transaction_consistency(self):
        """Test transaction consistency across operations."""
        # Mock transaction context
        mock_transaction = Mock()
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_transaction)
        mock_context.__exit__ = Mock(return_value=None)
        self.mock_firestore.transaction.return_value = mock_context
        
        # Test transactional operations
        def update_event_and_stats(transaction):
            # Update event status
            event_ref = self.mock_firestore.collection("events").document("event-123")
            transaction.update(event_ref, {"status": "resolved"})
            
            # Update statistics
            stats_ref = self.mock_firestore.collection("statistics").document("daily-stats")
            transaction.update(stats_ref, {"resolved_count": firestore.Increment(1)})
            
            return True
        
        # Execute transaction
        with self.mock_firestore.transaction() as transaction:
            result = update_event_and_stats(transaction)
        
        assert result is True
    
    def test_data_validation_consistency(self):
        """Test data validation consistency across systems."""
        # Test data that should be valid in both systems
        valid_event = {
            "id": "valid-event-123",
            "title": "Valid Event",
            "category": "infrastructure",
            "status": "active",
            "priority": "medium",
            "location": {"lat": 40.7128, "lng": -74.0060},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Validate for Firestore (mock validation)
        def validate_for_firestore(data):
            required_fields = ["id", "title", "category", "status"]
            return all(field in data for field in required_fields)
        
        # Validate for BigQuery (mock validation)
        def validate_for_bigquery(data):
            # BigQuery requires ISO format timestamps
            if isinstance(data.get("created_at"), datetime):
                data["created_at"] = data["created_at"].isoformat()
            if isinstance(data.get("updated_at"), datetime):
                data["updated_at"] = data["updated_at"].isoformat()
            return True
        
        # Test validation
        assert validate_for_firestore(valid_event) is True
        assert validate_for_bigquery(valid_event.copy()) is True


# Test fixtures
@pytest.fixture
def firestore_service():
    """Fixture providing FirestoreService with mocked client."""
    service = FirestoreService()
    service.client = Mock(spec=firestore.Client)
    return service


@pytest.fixture
def bigquery_client():
    """Fixture providing mocked BigQuery client."""
    return Mock(spec=bigquery.Client)


@pytest.fixture
def sample_event_data():
    """Fixture providing sample event data for testing."""
    return {
        "id": "test-event-123",
        "title": "Integration Test Event",
        "description": "Event for integration testing",
        "category": "infrastructure",
        "status": "active",
        "priority": "medium",
        "location": {"lat": 40.7128, "lng": -74.0060},
        "user_id": "user-456",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


class TestDatabaseIntegrationScenarios:
    """End-to-end database integration scenarios."""
    
    def test_complete_data_pipeline(self, firestore_service, bigquery_client, sample_event_data):
        """Test complete data pipeline from Firestore to BigQuery."""
        # Mock successful Firestore operations
        firestore_service.client.collection.return_value.document.return_value.set.return_value = None
        firestore_service.client.collection.return_value.document.return_value.get.return_value.exists = True
        firestore_service.client.collection.return_value.document.return_value.get.return_value.to_dict.return_value = sample_event_data
        
        # Mock successful BigQuery operations
        mock_table = Mock()
        mock_table.insert_rows_json.return_value = []
        bigquery_client.get_table.return_value = mock_table
        
        # Execute pipeline
        # 1. Save to Firestore
        firestore_result = firestore_service.set("events", sample_event_data["id"], sample_event_data)
        assert firestore_result is True
        
        # 2. Retrieve from Firestore
        retrieved_data = firestore_service.get("events", sample_event_data["id"])
        assert retrieved_data == sample_event_data
        
        # 3. Transform for BigQuery
        bigquery_data = {
            **retrieved_data,
            "created_at": retrieved_data["created_at"].isoformat(),
            "updated_at": retrieved_data["updated_at"].isoformat()
        }
        
        # 4. Insert to BigQuery
        table = bigquery_client.get_table("project.dataset.events")
        errors = table.insert_rows_json([bigquery_data])
        assert errors == []
        
        # Verify all operations completed successfully
        mock_table.insert_rows_json.assert_called_once_with([bigquery_data])
    
    def test_error_recovery_scenarios(self, firestore_service, bigquery_client):
        """Test error recovery in database operations."""
        # Test Firestore failure recovery
        firestore_service.client.collection.return_value.document.return_value.set.side_effect = Exception("Firestore error")
        
        result = firestore_service.set("events", "test-id", {"title": "Test"})
        assert result is False
        
        # Test BigQuery failure recovery
        mock_table = Mock()
        mock_table.insert_rows_json.return_value = [{"index": 0, "errors": [{"reason": "invalid"}]}]
        bigquery_client.get_table.return_value = mock_table
        
        table = bigquery_client.get_table("project.dataset.events")
        errors = table.insert_rows_json([{"id": "test", "title": "Test"}])
        
        # Should return errors for failed insertions
        assert len(errors) > 0
        assert "errors" in errors[0]
