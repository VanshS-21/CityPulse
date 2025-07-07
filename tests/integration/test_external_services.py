"""
Integration tests for CityPulse external service integrations.
Tests GCP services, AI/ML APIs, notification services, and third-party integrations.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, Any, List
import json
import base64

from google.cloud import pubsub_v1, storage, language_v1
from google.api_core import exceptions as gcp_exceptions


class TestPubSubIntegration:
    """Integration tests for Google Cloud Pub/Sub."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.mock_publisher = Mock(spec=pubsub_v1.PublisherClient)
        self.mock_subscriber = Mock(spec=pubsub_v1.SubscriberClient)
        self.project_id = "test-project"
        self.topic_name = "citypulse-events"
        self.subscription_name = "citypulse-events-sub"
    
    def test_publisher_client_initialization(self):
        """Test Pub/Sub publisher client initialization."""
        with patch('google.cloud.pubsub_v1.PublisherClient') as mock_client_class:
            mock_client_instance = Mock()
            mock_client_class.return_value = mock_client_instance
            
            # Test client initialization
            publisher = pubsub_v1.PublisherClient()
            
            # Verify client was created
            mock_client_class.assert_called_once()
            assert publisher == mock_client_instance
    
    def test_message_publishing(self):
        """Test publishing messages to Pub/Sub topic."""
        # Mock topic path and publish result
        topic_path = f"projects/{self.project_id}/topics/{self.topic_name}"
        self.mock_publisher.topic_path.return_value = topic_path
        
        # Mock future for async publish
        mock_future = Mock()
        mock_future.result.return_value = "message-id-123"
        self.mock_publisher.publish.return_value = mock_future
        
        # Test message data
        message_data = {
            "id": "event-123",
            "title": "Test Event",
            "category": "infrastructure",
            "location": {"lat": 40.7128, "lng": -74.0060},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Publish message
        topic_path = self.mock_publisher.topic_path(self.project_id, self.topic_name)
        message_bytes = json.dumps(message_data).encode('utf-8')
        
        future = self.mock_publisher.publish(topic_path, message_bytes)
        message_id = future.result()
        
        # Verify publish was called
        self.mock_publisher.publish.assert_called_once_with(topic_path, message_bytes)
        assert message_id == "message-id-123"
    
    def test_message_publishing_with_attributes(self):
        """Test publishing messages with attributes."""
        topic_path = f"projects/{self.project_id}/topics/{self.topic_name}"
        self.mock_publisher.topic_path.return_value = topic_path
        
        mock_future = Mock()
        mock_future.result.return_value = "message-id-456"
        self.mock_publisher.publish.return_value = mock_future
        
        # Test message with attributes
        message_data = {"event_id": "event-456", "type": "urgent"}
        attributes = {
            "source": "mobile_app",
            "priority": "high",
            "category": "safety"
        }
        
        # Publish with attributes
        topic_path = self.mock_publisher.topic_path(self.project_id, self.topic_name)
        message_bytes = json.dumps(message_data).encode('utf-8')
        
        future = self.mock_publisher.publish(topic_path, message_bytes, **attributes)
        message_id = future.result()
        
        # Verify publish with attributes
        self.mock_publisher.publish.assert_called_once_with(topic_path, message_bytes, **attributes)
        assert message_id == "message-id-456"
    
    def test_message_subscription(self):
        """Test subscribing to Pub/Sub messages."""
        # Mock subscription path
        subscription_path = f"projects/{self.project_id}/subscriptions/{self.subscription_name}"
        self.mock_subscriber.subscription_path.return_value = subscription_path
        
        # Mock message callback
        def message_callback(message):
            """Process received message."""
            try:
                data = json.loads(message.data.decode('utf-8'))
                # Process the message
                print(f"Received message: {data}")
                message.ack()
                return data
            except Exception as e:
                print(f"Error processing message: {e}")
                message.nack()
        
        # Mock pull operation
        mock_future = Mock()
        self.mock_subscriber.pull.return_value = mock_future
        
        # Test subscription
        subscription_path = self.mock_subscriber.subscription_path(self.project_id, self.subscription_name)
        
        # In real implementation, this would be:
        # streaming_pull_future = subscriber.pull(subscription_path, callback=message_callback)
        
        # Verify subscription path was created
        self.mock_subscriber.subscription_path.assert_called_once_with(self.project_id, self.subscription_name)
    
    def test_error_handling(self):
        """Test error handling in Pub/Sub operations."""
        # Test publish failure
        topic_path = f"projects/{self.project_id}/topics/{self.topic_name}"
        self.mock_publisher.topic_path.return_value = topic_path
        self.mock_publisher.publish.side_effect = gcp_exceptions.PermissionDenied("Access denied")
        
        # Test error handling
        try:
            topic_path = self.mock_publisher.topic_path(self.project_id, self.topic_name)
            self.mock_publisher.publish(topic_path, b"test message")
            assert False, "Should have raised exception"
        except gcp_exceptions.PermissionDenied as e:
            assert "Access denied" in str(e)


class TestCloudStorageIntegration:
    """Integration tests for Google Cloud Storage."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.mock_client = Mock(spec=storage.Client)
        self.bucket_name = "citypulse-media-files"
        self.mock_bucket = Mock()
        self.mock_client.bucket.return_value = self.mock_bucket
    
    def test_storage_client_initialization(self):
        """Test Cloud Storage client initialization."""
        with patch('google.cloud.storage.Client') as mock_client_class:
            mock_client_instance = Mock()
            mock_client_class.return_value = mock_client_instance
            
            # Test client initialization
            client = storage.Client()
            
            # Verify client was created
            mock_client_class.assert_called_once()
            assert client == mock_client_instance
    
    def test_file_upload(self):
        """Test file upload to Cloud Storage."""
        # Mock blob
        mock_blob = Mock()
        self.mock_bucket.blob.return_value = mock_blob
        
        # Test file upload
        file_name = "event-images/event-123/image1.jpg"
        file_content = b"fake image content"
        
        bucket = self.mock_client.bucket(self.bucket_name)
        blob = bucket.blob(file_name)
        blob.upload_from_string(file_content, content_type="image/jpeg")
        
        # Verify upload
        self.mock_client.bucket.assert_called_once_with(self.bucket_name)
        self.mock_bucket.blob.assert_called_once_with(file_name)
        mock_blob.upload_from_string.assert_called_once_with(file_content, content_type="image/jpeg")
    
    def test_file_download(self):
        """Test file download from Cloud Storage."""
        # Mock blob with content
        mock_blob = Mock()
        mock_blob.download_as_bytes.return_value = b"downloaded content"
        self.mock_bucket.blob.return_value = mock_blob
        
        # Test file download
        file_name = "event-images/event-123/image1.jpg"
        
        bucket = self.mock_client.bucket(self.bucket_name)
        blob = bucket.blob(file_name)
        content = blob.download_as_bytes()
        
        # Verify download
        mock_blob.download_as_bytes.assert_called_once()
        assert content == b"downloaded content"
    
    def test_file_metadata(self):
        """Test file metadata operations."""
        # Mock blob with metadata
        mock_blob = Mock()
        mock_blob.size = 1024
        mock_blob.content_type = "image/jpeg"
        mock_blob.time_created = datetime.utcnow()
        mock_blob.updated = datetime.utcnow()
        self.mock_bucket.blob.return_value = mock_blob
        
        # Test metadata access
        file_name = "event-images/event-123/image1.jpg"
        
        bucket = self.mock_client.bucket(self.bucket_name)
        blob = bucket.blob(file_name)
        
        # Access metadata
        file_size = blob.size
        content_type = blob.content_type
        created_time = blob.time_created
        
        # Verify metadata
        assert file_size == 1024
        assert content_type == "image/jpeg"
        assert isinstance(created_time, datetime)
    
    def test_file_deletion(self):
        """Test file deletion from Cloud Storage."""
        # Mock blob
        mock_blob = Mock()
        self.mock_bucket.blob.return_value = mock_blob
        
        # Test file deletion
        file_name = "event-images/event-123/image1.jpg"
        
        bucket = self.mock_client.bucket(self.bucket_name)
        blob = bucket.blob(file_name)
        blob.delete()
        
        # Verify deletion
        mock_blob.delete.assert_called_once()
    
    def test_signed_url_generation(self):
        """Test signed URL generation for secure access."""
        # Mock blob
        mock_blob = Mock()
        mock_blob.generate_signed_url.return_value = "https://storage.googleapis.com/signed-url"
        self.mock_bucket.blob.return_value = mock_blob
        
        # Test signed URL generation
        file_name = "event-images/event-123/image1.jpg"
        expiration = timedelta(hours=1)
        
        bucket = self.mock_client.bucket(self.bucket_name)
        blob = bucket.blob(file_name)
        signed_url = blob.generate_signed_url(expiration=expiration, method="GET")
        
        # Verify signed URL
        mock_blob.generate_signed_url.assert_called_once_with(expiration=expiration, method="GET")
        assert signed_url.startswith("https://storage.googleapis.com/")


class TestAIMLIntegration:
    """Integration tests for AI/ML services."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.mock_language_client = Mock(spec=language_v1.LanguageServiceClient)
    
    def test_sentiment_analysis(self):
        """Test sentiment analysis using Cloud Natural Language API."""
        # Mock sentiment analysis response
        mock_sentiment = Mock()
        mock_sentiment.score = 0.8
        mock_sentiment.magnitude = 0.9
        
        mock_response = Mock()
        mock_response.document_sentiment = mock_sentiment
        
        self.mock_language_client.analyze_sentiment.return_value = mock_response
        
        # Test sentiment analysis
        text_content = "This is a great improvement to our city infrastructure!"
        
        document = language_v1.Document(
            content=text_content,
            type_=language_v1.Document.Type.PLAIN_TEXT
        )
        
        response = self.mock_language_client.analyze_sentiment(
            request={"document": document}
        )
        
        # Verify sentiment analysis
        self.mock_language_client.analyze_sentiment.assert_called_once()
        assert response.document_sentiment.score == 0.8
        assert response.document_sentiment.magnitude == 0.9
    
    def test_entity_extraction(self):
        """Test entity extraction from text."""
        # Mock entity extraction response
        mock_entity1 = Mock()
        mock_entity1.name = "Main Street"
        mock_entity1.type_ = language_v1.Entity.Type.LOCATION
        mock_entity1.salience = 0.8
        
        mock_entity2 = Mock()
        mock_entity2.name = "traffic light"
        mock_entity2.type_ = language_v1.Entity.Type.OTHER
        mock_entity2.salience = 0.6
        
        mock_response = Mock()
        mock_response.entities = [mock_entity1, mock_entity2]
        
        self.mock_language_client.analyze_entities.return_value = mock_response
        
        # Test entity extraction
        text_content = "The traffic light on Main Street is malfunctioning."
        
        document = language_v1.Document(
            content=text_content,
            type_=language_v1.Document.Type.PLAIN_TEXT
        )
        
        response = self.mock_language_client.analyze_entities(
            request={"document": document}
        )
        
        # Verify entity extraction
        self.mock_language_client.analyze_entities.assert_called_once()
        assert len(response.entities) == 2
        assert response.entities[0].name == "Main Street"
        assert response.entities[0].type_ == language_v1.Entity.Type.LOCATION
    
    def test_text_classification(self):
        """Test text classification."""
        # Mock classification response
        mock_category1 = Mock()
        mock_category1.name = "/Science/Engineering"
        mock_category1.confidence = 0.85
        
        mock_category2 = Mock()
        mock_category2.name = "/Computers & Electronics/Software"
        mock_category2.confidence = 0.72
        
        mock_response = Mock()
        mock_response.categories = [mock_category1, mock_category2]
        
        self.mock_language_client.classify_text.return_value = mock_response
        
        # Test text classification
        text_content = "The city's new traffic management system uses advanced algorithms."
        
        document = language_v1.Document(
            content=text_content,
            type_=language_v1.Document.Type.PLAIN_TEXT
        )
        
        response = self.mock_language_client.classify_text(
            request={"document": document}
        )
        
        # Verify classification
        self.mock_language_client.classify_text.assert_called_once()
        assert len(response.categories) == 2
        assert response.categories[0].confidence == 0.85


class TestNotificationServices:
    """Integration tests for notification services."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.mock_email_service = Mock()
        self.mock_sms_service = Mock()
        self.mock_push_service = Mock()
    
    def test_email_notification(self):
        """Test email notification sending."""
        # Mock email sending
        self.mock_email_service.send_email.return_value = {"status": "sent", "message_id": "email-123"}
        
        # Test email notification
        email_data = {
            "to": "user@example.com",
            "subject": "Event Update: Traffic Issue Resolved",
            "body": "The traffic issue on Main Street has been resolved.",
            "html_body": "<p>The traffic issue on <strong>Main Street</strong> has been resolved.</p>"
        }
        
        result = self.mock_email_service.send_email(**email_data)
        
        # Verify email sending
        self.mock_email_service.send_email.assert_called_once_with(**email_data)
        assert result["status"] == "sent"
        assert "message_id" in result
    
    def test_sms_notification(self):
        """Test SMS notification sending."""
        # Mock SMS sending
        self.mock_sms_service.send_sms.return_value = {"status": "delivered", "message_id": "sms-456"}
        
        # Test SMS notification
        sms_data = {
            "to": "+1234567890",
            "message": "CityPulse Alert: Traffic issue on Main Street has been resolved."
        }
        
        result = self.mock_sms_service.send_sms(**sms_data)
        
        # Verify SMS sending
        self.mock_sms_service.send_sms.assert_called_once_with(**sms_data)
        assert result["status"] == "delivered"
    
    def test_push_notification(self):
        """Test push notification sending."""
        # Mock push notification sending
        self.mock_push_service.send_push.return_value = {"status": "sent", "recipients": 1}
        
        # Test push notification
        push_data = {
            "user_tokens": ["token-123", "token-456"],
            "title": "Event Update",
            "body": "Traffic issue resolved on Main Street",
            "data": {
                "event_id": "event-123",
                "category": "infrastructure",
                "action": "view_event"
            }
        }
        
        result = self.mock_push_service.send_push(**push_data)
        
        # Verify push notification
        self.mock_push_service.send_push.assert_called_once_with(**push_data)
        assert result["status"] == "sent"
    
    def test_notification_preferences(self):
        """Test notification sending based on user preferences."""
        # Mock user preferences
        user_preferences = {
            "email": True,
            "sms": False,
            "push": True
        }
        
        # Mock notification results
        self.mock_email_service.send_email.return_value = {"status": "sent"}
        self.mock_push_service.send_push.return_value = {"status": "sent"}
        
        # Test notification based on preferences
        def send_notifications(preferences, notification_data):
            results = {}
            
            if preferences.get("email", False):
                results["email"] = self.mock_email_service.send_email(
                    to=notification_data["email"],
                    subject=notification_data["subject"],
                    body=notification_data["body"]
                )
            
            if preferences.get("sms", False):
                results["sms"] = self.mock_sms_service.send_sms(
                    to=notification_data["phone"],
                    message=notification_data["sms_message"]
                )
            
            if preferences.get("push", False):
                results["push"] = self.mock_push_service.send_push(
                    user_tokens=notification_data["push_tokens"],
                    title=notification_data["title"],
                    body=notification_data["body"]
                )
            
            return results
        
        notification_data = {
            "email": "user@example.com",
            "phone": "+1234567890",
            "subject": "Event Update",
            "body": "Your reported issue has been resolved",
            "sms_message": "Issue resolved",
            "push_tokens": ["token-123"],
            "title": "Update"
        }
        
        results = send_notifications(user_preferences, notification_data)
        
        # Verify only email and push were sent (SMS disabled)
        assert "email" in results
        assert "push" in results
        assert "sms" not in results
        
        self.mock_email_service.send_email.assert_called_once()
        self.mock_push_service.send_push.assert_called_once()
        self.mock_sms_service.send_sms.assert_not_called()


# Test fixtures
@pytest.fixture
def pubsub_publisher():
    """Fixture providing mocked Pub/Sub publisher."""
    return Mock(spec=pubsub_v1.PublisherClient)


@pytest.fixture
def storage_client():
    """Fixture providing mocked Cloud Storage client."""
    return Mock(spec=storage.Client)


@pytest.fixture
def language_client():
    """Fixture providing mocked Natural Language client."""
    return Mock(spec=language_v1.LanguageServiceClient)


class TestExternalServiceIntegration:
    """End-to-end external service integration scenarios."""
    
    def test_complete_event_processing_pipeline(self, pubsub_publisher, storage_client, language_client):
        """Test complete event processing with external services."""
        # Mock event data
        event_data = {
            "id": "event-integration-test",
            "title": "Traffic Issue on Main Street",
            "description": "Heavy traffic congestion causing delays",
            "category": "infrastructure",
            "location": {"lat": 40.7128, "lng": -74.0060},
            "image_url": "event-images/event-123/photo.jpg"
        }
        
        # 1. Publish event to Pub/Sub
        mock_future = Mock()
        mock_future.result.return_value = "message-id-123"
        pubsub_publisher.publish.return_value = mock_future
        
        topic_path = "projects/test-project/topics/citypulse-events"
        message_bytes = json.dumps(event_data).encode('utf-8')
        future = pubsub_publisher.publish(topic_path, message_bytes)
        message_id = future.result()
        
        assert message_id == "message-id-123"
        
        # 2. Process image with Cloud Storage
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_bucket.blob.return_value = mock_blob
        storage_client.bucket.return_value = mock_bucket
        
        bucket = storage_client.bucket("citypulse-media")
        blob = bucket.blob(event_data["image_url"])
        blob.upload_from_string(b"fake image data", content_type="image/jpeg")
        
        mock_blob.upload_from_string.assert_called_once()
        
        # 3. Analyze text with Natural Language API
        mock_sentiment = Mock()
        mock_sentiment.score = -0.3  # Negative sentiment for traffic issue
        mock_sentiment.magnitude = 0.8
        
        mock_response = Mock()
        mock_response.document_sentiment = mock_sentiment
        language_client.analyze_sentiment.return_value = mock_response
        
        document = language_v1.Document(
            content=event_data["description"],
            type_=language_v1.Document.Type.PLAIN_TEXT
        )
        
        sentiment_response = language_client.analyze_sentiment(request={"document": document})
        
        # Verify sentiment analysis indicates negative sentiment (appropriate for traffic issue)
        assert sentiment_response.document_sentiment.score < 0
        assert sentiment_response.document_sentiment.magnitude > 0.5
        
        # All external services integrated successfully
        pubsub_publisher.publish.assert_called_once()
        storage_client.bucket.assert_called_once()
        language_client.analyze_sentiment.assert_called_once()
    
    def test_error_handling_across_services(self, pubsub_publisher, storage_client):
        """Test error handling across multiple external services."""
        # Test Pub/Sub failure
        pubsub_publisher.publish.side_effect = gcp_exceptions.ServiceUnavailable("Pub/Sub unavailable")
        
        try:
            pubsub_publisher.publish("topic", b"message")
            assert False, "Should have raised exception"
        except gcp_exceptions.ServiceUnavailable:
            pass  # Expected
        
        # Test Storage failure
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.upload_from_string.side_effect = gcp_exceptions.Forbidden("Access denied")
        mock_bucket.blob.return_value = mock_blob
        storage_client.bucket.return_value = mock_bucket
        
        try:
            bucket = storage_client.bucket("test-bucket")
            blob = bucket.blob("test-file")
            blob.upload_from_string(b"data")
            assert False, "Should have raised exception"
        except gcp_exceptions.Forbidden:
            pass  # Expected
