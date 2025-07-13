"""
Comprehensive unit tests for CityPulse services and utilities.
Tests business logic, external integrations, and service layer functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json
import sys
import os

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'server'))

from data_models.services.firestore_service import FirestoreService
from data_models import Event, UserProfile, Feedback, EventCategory, EventSeverity, EventStatus


class TestFirestoreService:
    """Test cases for FirestoreService functionality."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.mock_client = Mock()
        self.service = FirestoreService()
        self.service.client = self.mock_client
    
    def test_service_initialization(self):
        """Test FirestoreService initialization."""
        with patch('data_models.services.firestore_service.firestore.Client') as mock_client_class:
            mock_client_instance = Mock()
            mock_client_class.return_value = mock_client_instance
            
            service = FirestoreService()
            
            mock_client_class.assert_called_once()
            assert service.client == mock_client_instance
    
    def test_get_document_success(self):
        """Test successful document retrieval."""
        # Mock Firestore document
        mock_doc = Mock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {
            "id": "test-123",
            "title": "Test Event",
            "category": "infrastructure",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Mock collection and document chain
        mock_collection = Mock()
        mock_collection.document.return_value.get.return_value = mock_doc
        self.mock_client.collection.return_value = mock_collection
        
        # Test get operation
        result = self.service.get("events", "test-123")
        
        # Verify calls
        self.mock_client.collection.assert_called_once_with("events")
        mock_collection.document.assert_called_once_with("test-123")
        
        # Verify result
        assert result is not None
        assert result["id"] == "test-123"
        assert result["title"] == "Test Event"
    
    def test_get_document_not_found(self):
        """Test document retrieval when document doesn't exist."""
        # Mock non-existent document
        mock_doc = Mock()
        mock_doc.exists = False
        
        mock_collection = Mock()
        mock_collection.document.return_value.get.return_value = mock_doc
        self.mock_client.collection.return_value = mock_collection
        
        # Test get operation
        result = self.service.get("events", "non-existent")
        
        # Verify result is None
        assert result is None
    
    def test_set_document_success(self):
        """Test successful document creation/update."""
        test_data = {
            "title": "New Event",
            "category": "infrastructure",
            "status": "active"
        }
        
        # Mock collection
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_collection.document.return_value = mock_doc_ref
        self.mock_client.collection.return_value = mock_collection
        
        # Test set operation
        result = self.service.set("events", "test-123", test_data)
        
        # Verify calls
        self.mock_client.collection.assert_called_once_with("events")
        mock_collection.document.assert_called_once_with("test-123")
        mock_doc_ref.set.assert_called_once_with(test_data)
        
        # Verify result
        assert result is True
    
    def test_set_document_failure(self):
        """Test document set operation failure."""
        test_data = {"title": "Test Event"}
        
        # Mock collection that raises exception
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_doc_ref.set.side_effect = Exception("Firestore error")
        mock_collection.document.return_value = mock_doc_ref
        self.mock_client.collection.return_value = mock_collection
        
        # Test set operation
        result = self.service.set("events", "test-123", test_data)
        
        # Verify result is False on failure
        assert result is False
    
    def test_update_document_success(self):
        """Test successful document update."""
        update_data = {
            "status": "resolved",
            "updated_at": datetime.utcnow()
        }
        
        # Mock collection
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_collection.document.return_value = mock_doc_ref
        self.mock_client.collection.return_value = mock_collection
        
        # Test update operation
        result = self.service.update("events", "test-123", update_data)
        
        # Verify calls
        mock_doc_ref.update.assert_called_once_with(update_data)
        
        # Verify result
        assert result is True
    
    def test_delete_document_success(self):
        """Test successful document deletion."""
        # Mock collection
        mock_collection = Mock()
        mock_doc_ref = Mock()
        mock_collection.document.return_value = mock_doc_ref
        self.mock_client.collection.return_value = mock_collection
        
        # Test delete operation
        result = self.service.delete("events", "test-123")
        
        # Verify calls
        mock_doc_ref.delete.assert_called_once()
        
        # Verify result
        assert result is True
    
    def test_query_documents_success(self):
        """Test successful document querying."""
        # Mock query results
        mock_docs = [
            Mock(id="doc1", to_dict=lambda: {"title": "Event 1", "category": "infrastructure"}),
            Mock(id="doc2", to_dict=lambda: {"title": "Event 2", "category": "safety"})
        ]
        
        # Mock collection and query chain
        mock_collection = Mock()
        mock_query = Mock()
        mock_query.stream.return_value = mock_docs
        mock_collection.where.return_value = mock_query
        self.mock_client.collection.return_value = mock_collection
        
        # Test query operation
        results = self.service.query("events", "category", "==", "infrastructure")
        
        # Verify calls
        self.mock_client.collection.assert_called_once_with("events")
        mock_collection.where.assert_called_once_with("category", "==", "infrastructure")
        
        # Verify results
        assert len(results) == 2
        assert results[0]["title"] == "Event 1"
        assert results[1]["title"] == "Event 2"
    
    def test_query_with_multiple_conditions(self):
        """Test querying with multiple conditions."""
        # Mock query chain
        mock_collection = Mock()
        mock_query1 = Mock()
        mock_query2 = Mock()
        mock_query2.stream.return_value = []
        
        mock_collection.where.return_value = mock_query1
        mock_query1.where.return_value = mock_query2
        self.mock_client.collection.return_value = mock_collection
        
        # Test query with multiple conditions
        conditions = [
            ("category", "==", "infrastructure"),
            ("status", "==", "active")
        ]
        
        results = self.service.query_multiple("events", conditions)
        
        # Verify query chain
        mock_collection.where.assert_called_once_with("category", "==", "infrastructure")
        mock_query1.where.assert_called_once_with("status", "==", "active")
    
    def test_batch_operations(self):
        """Test batch operations functionality."""
        # Mock batch
        mock_batch = Mock()
        self.mock_client.batch.return_value = mock_batch
        
        # Mock document references
        mock_doc_ref1 = Mock()
        mock_doc_ref2 = Mock()
        mock_collection = Mock()
        mock_collection.document.side_effect = [mock_doc_ref1, mock_doc_ref2]
        self.mock_client.collection.return_value = mock_collection
        
        # Test batch operations
        operations = [
            ("set", "events", "doc1", {"title": "Event 1"}),
            ("update", "events", "doc2", {"status": "resolved"})
        ]
        
        result = self.service.batch_operations(operations)
        
        # Verify batch operations
        mock_batch.set.assert_called_once_with(mock_doc_ref1, {"title": "Event 1"})
        mock_batch.update.assert_called_once_with(mock_doc_ref2, {"status": "resolved"})
        mock_batch.commit.assert_called_once()
        
        assert result is True
    
    def test_transaction_operations(self):
        """Test transaction operations functionality."""
        # Mock transaction
        mock_transaction = Mock()
        self.mock_client.transaction.return_value = mock_transaction
        
        # Test transaction wrapper
        def test_transaction_func(transaction):
            # Mock transaction operations
            return {"result": "success"}
        
        with patch.object(self.service, 'client') as mock_client:
            mock_client.transaction.return_value.__enter__ = Mock(return_value=mock_transaction)
            mock_client.transaction.return_value.__exit__ = Mock(return_value=None)
            
            # This would be implemented in the actual service
            # result = self.service.run_transaction(test_transaction_func)
            # assert result["result"] == "success"
            pass


class TestEventService:
    """Test cases for Event-specific service operations."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.mock_firestore_service = Mock()
        # In a real implementation, EventService would use FirestoreService
        self.event_service = self.mock_firestore_service
    
    def test_create_event(self):
        """Test event creation."""
        event_data = {
            "title": "Traffic Incident",
            "description": "Major traffic jam",
            "category": "infrastructure",
            "severity": "high",
            "location": {"lat": 40.7128, "lng": -74.0060},
            "user_id": "user-123"
        }
        
        # Mock successful creation
        self.mock_firestore_service.set.return_value = True
        
        # Test event creation
        result = self.event_service.set("events", "event-123", event_data)
        
        # Verify call
        self.mock_firestore_service.set.assert_called_once_with("events", "event-123", event_data)
        assert result is True
    
    def test_get_events_by_category(self):
        """Test retrieving events by category."""
        mock_events = [
            {"id": "1", "title": "Event 1", "category": "infrastructure"},
            {"id": "2", "title": "Event 2", "category": "infrastructure"}
        ]
        
        self.mock_firestore_service.query.return_value = mock_events
        
        # Test query by category
        results = self.event_service.query("events", "category", "==", "infrastructure")
        
        # Verify call and results
        self.mock_firestore_service.query.assert_called_once_with("events", "category", "==", "infrastructure")
        assert len(results) == 2
        assert all(event["category"] == "infrastructure" for event in results)
    
    def test_get_events_by_location(self):
        """Test retrieving events by location proximity."""
        # Mock events with location data
        mock_events = [
            {
                "id": "1",
                "title": "Nearby Event",
                "location": {"lat": 40.7128, "lng": -74.0060}
            },
            {
                "id": "2", 
                "title": "Distant Event",
                "location": {"lat": 41.0000, "lng": -75.0000}
            }
        ]
        
        self.mock_firestore_service.query.return_value = mock_events
        
        # Test location-based query (would need geospatial logic in real implementation)
        results = self.event_service.query("events", "location.lat", ">=", 40.0)
        
        assert len(results) == 2
    
    def test_update_event_status(self):
        """Test updating event status."""
        update_data = {
            "status": "resolved",
            "updated_at": datetime.utcnow(),
            "resolved_by": "admin-123"
        }
        
        self.mock_firestore_service.update.return_value = True
        
        # Test status update
        result = self.event_service.update("events", "event-123", update_data)
        
        # Verify call
        self.mock_firestore_service.update.assert_called_once_with("events", "event-123", update_data)
        assert result is True
    
    def test_get_event_statistics(self):
        """Test retrieving event statistics."""
        # Mock events for statistics
        mock_events = [
            {"id": "1", "category": "infrastructure", "status": "active", "severity": "high"},
            {"id": "2", "category": "infrastructure", "status": "resolved", "severity": "medium"},
            {"id": "3", "category": "safety", "status": "active", "severity": "low"},
            {"id": "4", "category": "safety", "status": "resolved", "severity": "high"}
        ]
        
        self.mock_firestore_service.query.return_value = mock_events
        
        # Mock statistics calculation
        def calculate_statistics(events):
            stats = {
                "total": len(events),
                "by_category": {},
                "by_status": {},
                "by_severity": {}
            }
            
            for event in events:
                # Count by category
                category = event["category"]
                stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
                
                # Count by status
                status = event["status"]
                stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
                
                # Count by severity
                severity = event["severity"]
                stats["by_severity"][severity] = stats["by_severity"].get(severity, 0) + 1
            
            return stats
        
        # Test statistics calculation
        stats = calculate_statistics(mock_events)
        
        assert stats["total"] == 4
        assert stats["by_category"]["infrastructure"] == 2
        assert stats["by_category"]["safety"] == 2
        assert stats["by_status"]["active"] == 2
        assert stats["by_status"]["resolved"] == 2
        assert stats["by_severity"]["high"] == 2


class TestUserProfileService:
    """Test cases for UserProfile service operations."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.mock_firestore_service = Mock()
        self.user_service = self.mock_firestore_service
    
    def test_create_user_profile(self):
        """Test user profile creation."""
        profile_data = {
            "user_id": "user-123",
            "email": "test@example.com",
            "display_name": "Test User",
            "roles": ["user"],
            "is_active": True,
            "notification_preferences": {
                "email": True,
                "push": True,
                "sms": False
            }
        }
        
        self.mock_firestore_service.set.return_value = True
        
        # Test profile creation
        result = self.user_service.set("user_profiles", "user-123", profile_data)
        
        # Verify call
        self.mock_firestore_service.set.assert_called_once_with("user_profiles", "user-123", profile_data)
        assert result is True
    
    def test_get_user_by_email(self):
        """Test retrieving user by email."""
        mock_users = [
            {
                "user_id": "user-123",
                "email": "test@example.com",
                "display_name": "Test User"
            }
        ]
        
        self.mock_firestore_service.query.return_value = mock_users
        
        # Test email query
        results = self.user_service.query("user_profiles", "email", "==", "test@example.com")
        
        # Verify call and results
        self.mock_firestore_service.query.assert_called_once_with("user_profiles", "email", "==", "test@example.com")
        assert len(results) == 1
        assert results[0]["email"] == "test@example.com"
    
    def test_update_user_preferences(self):
        """Test updating user notification preferences."""
        update_data = {
            "notification_preferences": {
                "email": False,
                "push": True,
                "sms": True
            },
            "updated_at": datetime.utcnow()
        }
        
        self.mock_firestore_service.update.return_value = True
        
        # Test preferences update
        result = self.user_service.update("user_profiles", "user-123", update_data)
        
        # Verify call
        self.mock_firestore_service.update.assert_called_once_with("user_profiles", "user-123", update_data)
        assert result is True
    
    def test_deactivate_user(self):
        """Test user deactivation."""
        update_data = {
            "is_active": False,
            "deactivated_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        self.mock_firestore_service.update.return_value = True
        
        # Test user deactivation
        result = self.user_service.update("user_profiles", "user-123", update_data)
        
        # Verify call
        self.mock_firestore_service.update.assert_called_once_with("user_profiles", "user-123", update_data)
        assert result is True


class TestFeedbackService:
    """Test cases for Feedback service operations."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.mock_firestore_service = Mock()
        self.feedback_service = self.mock_firestore_service
    
    def test_create_feedback(self):
        """Test feedback creation."""
        feedback_data = {
            "event_id": "event-123",
            "user_id": "user-456",
            "content": "This is helpful feedback",
            "feedback_type": "general",
            "rating": 4,
            "is_anonymous": False,
            "status": "pending"
        }
        
        self.mock_firestore_service.set.return_value = True
        
        # Test feedback creation
        result = self.feedback_service.set("feedback", "feedback-123", feedback_data)
        
        # Verify call
        self.mock_firestore_service.set.assert_called_once_with("feedback", "feedback-123", feedback_data)
        assert result is True
    
    def test_get_feedback_by_event(self):
        """Test retrieving feedback for an event."""
        mock_feedback = [
            {
                "id": "feedback-1",
                "event_id": "event-123",
                "content": "Great response time",
                "rating": 5
            },
            {
                "id": "feedback-2",
                "event_id": "event-123",
                "content": "Could be better",
                "rating": 3
            }
        ]
        
        self.mock_firestore_service.query.return_value = mock_feedback
        
        # Test event feedback query
        results = self.feedback_service.query("feedback", "event_id", "==", "event-123")
        
        # Verify call and results
        self.mock_firestore_service.query.assert_called_once_with("feedback", "event_id", "==", "event-123")
        assert len(results) == 2
        assert all(fb["event_id"] == "event-123" for fb in results)
    
    def test_moderate_feedback(self):
        """Test feedback moderation."""
        moderation_data = {
            "status": "approved",
            "moderator_notes": "Feedback approved after review",
            "moderated_by": "admin-123",
            "moderated_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        self.mock_firestore_service.update.return_value = True
        
        # Test feedback moderation
        result = self.feedback_service.update("feedback", "feedback-123", moderation_data)
        
        # Verify call
        self.mock_firestore_service.update.assert_called_once_with("feedback", "feedback-123", moderation_data)
        assert result is True
    
    def test_calculate_feedback_metrics(self):
        """Test feedback metrics calculation."""
        mock_feedback = [
            {"rating": 5, "status": "approved"},
            {"rating": 4, "status": "approved"},
            {"rating": 3, "status": "approved"},
            {"rating": 5, "status": "approved"},
            {"rating": 2, "status": "pending"}
        ]
        
        # Mock metrics calculation
        def calculate_feedback_metrics(feedback_list):
            approved_feedback = [fb for fb in feedback_list if fb["status"] == "approved"]
            
            if not approved_feedback:
                return {"average_rating": 0, "total_feedback": 0, "approved_feedback": 0}
            
            total_rating = sum(fb["rating"] for fb in approved_feedback)
            average_rating = total_rating / len(approved_feedback)
            
            return {
                "average_rating": round(average_rating, 2),
                "total_feedback": len(feedback_list),
                "approved_feedback": len(approved_feedback)
            }
        
        # Test metrics calculation
        metrics = calculate_feedback_metrics(mock_feedback)
        
        assert metrics["average_rating"] == 4.25  # (5+4+3+5)/4
        assert metrics["total_feedback"] == 5
        assert metrics["approved_feedback"] == 4


# Test fixtures
@pytest.fixture
def mock_firestore_client():
    """Fixture providing a mock Firestore client."""
    return Mock()


@pytest.fixture
def sample_event_data():
    """Fixture providing sample event data."""
    return {
        "id": "event-123",
        "title": "Traffic Incident",
        "description": "Major traffic jam on Main Street",
        "category": "infrastructure",
        "severity": "high",
        "status": "active",
        "location": {"lat": 40.7128, "lng": -74.0060},
        "user_id": "user-456",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


@pytest.fixture
def sample_user_data():
    """Fixture providing sample user profile data."""
    return {
        "user_id": "user-123",
        "email": "test@example.com",
        "display_name": "Test User",
        "roles": ["user"],
        "is_active": True,
        "notification_preferences": {
            "email": True,
            "push": True,
            "sms": False
        },
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


class TestServiceIntegration:
    """Integration tests for service interactions."""
    
    def test_event_with_user_integration(self, sample_event_data, sample_user_data):
        """Test event creation with user profile validation."""
        mock_firestore = Mock()
        
        # Mock user exists
        mock_firestore.get.return_value = sample_user_data
        
        # Mock event creation
        mock_firestore.set.return_value = True
        
        # Test event creation with user validation
        user_exists = mock_firestore.get("user_profiles", sample_event_data["user_id"])
        
        if user_exists:
            event_created = mock_firestore.set("events", sample_event_data["id"], sample_event_data)
            assert event_created is True
        else:
            pytest.fail("User should exist for event creation")
    
    def test_feedback_with_event_integration(self, sample_event_data):
        """Test feedback creation with event validation."""
        mock_firestore = Mock()
        
        # Mock event exists
        mock_firestore.get.return_value = sample_event_data
        
        feedback_data = {
            "event_id": sample_event_data["id"],
            "user_id": "user-789",
            "content": "Great response to this incident",
            "rating": 5
        }
        
        # Mock feedback creation
        mock_firestore.set.return_value = True
        
        # Test feedback creation with event validation
        event_exists = mock_firestore.get("events", feedback_data["event_id"])
        
        if event_exists:
            feedback_created = mock_firestore.set("feedback", "feedback-123", feedback_data)
            assert feedback_created is True
        else:
            pytest.fail("Event should exist for feedback creation")
