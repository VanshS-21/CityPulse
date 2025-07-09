"""
Pub/Sub integration tests for CityPulse E2E test suite.

This module tests Pub/Sub topic creation, message publishing,
subscription management, and message consumption.
"""

import pytest
import json
import time
from typing import List, Dict, Any

from google.cloud import pubsub_v1
from google.cloud.exceptions import NotFound

from ..config.test_config import get_all_configs
from ..utils.gcp_helpers import PubSubHelper, generate_unique_resource_name
from ..utils.data_generators import generate_citizen_report, generate_iot_data
from ..utils.test_helpers import TestTimer, wait_for_condition


@pytest.fixture(scope="module")
def configs():
    """Get test configurations."""
    return get_all_configs()


@pytest.fixture(scope="module")
def pubsub_helper(configs):
    """Create PubSub helper instance."""
    helper = PubSubHelper(configs["gcp"].project_id)
    yield helper
    helper.cleanup()


class TestPubSubTopics:
    """Test Pub/Sub topic operations."""
    
    def test_create_citizen_reports_topic(self, pubsub_helper, configs):
        """Test creating citizen reports topic."""
        topic_name = generate_unique_resource_name("test-citizen-reports")
        
        with TestTimer("topic creation"):
            topic_path = pubsub_helper.create_test_topic(topic_name)
        
        assert topic_path is not None
        assert topic_name in topic_path
        
        # Verify topic exists
        publisher = pubsub_v1.PublisherClient()
        try:
            publisher.get_topic(request={"topic": topic_path})
        except NotFound:
            pytest.fail(f"Topic {topic_path} was not created")
    
    def test_create_iot_data_topic(self, pubsub_helper, configs):
        """Test creating IoT data topic."""
        topic_name = generate_unique_resource_name("test-iot-data")
        
        with TestTimer("IoT topic creation"):
            topic_path = pubsub_helper.create_test_topic(topic_name)
        
        assert topic_path is not None
        assert topic_name in topic_path


class TestPubSubSubscriptions:
    """Test Pub/Sub subscription operations."""
    
    def test_create_subscription_for_topic(self, pubsub_helper, configs):
        """Test creating subscription for a topic."""
        topic_name = generate_unique_resource_name("test-topic")
        subscription_name = generate_unique_resource_name("test-subscription")
        
        # Create topic first
        topic_path = pubsub_helper.create_test_topic(topic_name)
        
        # Create subscription
        with TestTimer("subscription creation"):
            subscription_path = pubsub_helper.create_test_subscription(
                topic_path, subscription_name
            )
        
        assert subscription_path is not None
        assert subscription_name in subscription_path
        
        # Verify subscription exists
        subscriber = pubsub_v1.SubscriberClient()
        try:
            subscriber.get_subscription(request={"subscription": subscription_path})
        except NotFound:
            pytest.fail(f"Subscription {subscription_path} was not created")


class TestMessagePublishing:
    """Test message publishing to Pub/Sub topics."""
    
    def test_publish_citizen_report_messages(self, pubsub_helper, configs):
        """Test publishing citizen report messages."""
        topic_name = generate_unique_resource_name("test-citizen-reports")
        topic_path = pubsub_helper.create_test_topic(topic_name)
        
        # Generate test messages
        messages = [
            generate_citizen_report(valid=True) for _ in range(5)
        ]
        
        with TestTimer("message publishing"):
            message_ids = pubsub_helper.publish_messages(topic_path, messages)
        
        assert len(message_ids) == 5
        assert all(isinstance(msg_id, str) for msg_id in message_ids)
    
    def test_publish_iot_data_messages(self, pubsub_helper, configs):
        """Test publishing IoT data messages."""
        topic_name = generate_unique_resource_name("test-iot-data")
        topic_path = pubsub_helper.create_test_topic(topic_name)
        
        # Generate test messages
        messages = [
            generate_iot_data(valid=True) for _ in range(10)
        ]
        
        with TestTimer("IoT message publishing"):
            message_ids = pubsub_helper.publish_messages(topic_path, messages)
        
        assert len(message_ids) == 10
        assert all(isinstance(msg_id, str) for msg_id in message_ids)
    
    def test_publish_invalid_messages(self, pubsub_helper, configs):
        """Test publishing invalid messages (should still succeed at Pub/Sub level)."""
        topic_name = generate_unique_resource_name("test-invalid-messages")
        topic_path = pubsub_helper.create_test_topic(topic_name)
        
        # Generate invalid messages
        invalid_messages = [
            {"invalid": "data", "missing": "required_fields"},
            {"malformed": True, "timestamp": "not_a_timestamp"},
            "not_even_json_object"
        ]
        
        with TestTimer("invalid message publishing"):
            message_ids = pubsub_helper.publish_messages(topic_path, invalid_messages)
        
        # Pub/Sub should accept any message, validation happens in pipeline
        assert len(message_ids) == 3
        assert all(isinstance(msg_id, str) for msg_id in message_ids)


class TestMessageConsumption:
    """Test message consumption from Pub/Sub subscriptions."""
    
    def test_consume_published_messages(self, pubsub_helper, configs):
        """Test consuming messages from a subscription."""
        topic_name = generate_unique_resource_name("test-consumption")
        subscription_name = generate_unique_resource_name("test-consumption-sub")
        
        # Create topic and subscription
        topic_path = pubsub_helper.create_test_topic(topic_name)
        subscription_path = pubsub_helper.create_test_subscription(
            topic_path, subscription_name
        )
        
        # Publish test messages
        test_messages = [
            generate_citizen_report(event_id=f"test-{i}") for i in range(3)
        ]
        
        message_ids = pubsub_helper.publish_messages(topic_path, test_messages)
        
        # Wait a moment for messages to be available
        time.sleep(5)
        
        # Pull messages from subscription
        subscriber = pubsub_v1.SubscriberClient()
        
        def check_messages_available():
            response = subscriber.pull(
                request={
                    "subscription": subscription_path,
                    "max_messages": 10
                }
            )
            return len(response.received_messages) >= 3
        
        # Wait for messages to be available
        messages_available = wait_for_condition(
            check_messages_available,
            timeout=60,
            check_interval=5,
            description="messages available in subscription"
        )
        
        assert messages_available, "Messages were not available in subscription"
        
        # Pull and verify messages
        response = subscriber.pull(
            request={
                "subscription": subscription_path,
                "max_messages": 10
            }
        )
        
        received_messages = response.received_messages
        assert len(received_messages) >= 3
        
        # Verify message content
        received_event_ids = []
        for received_message in received_messages:
            try:
                data = json.loads(received_message.message.data.decode('utf-8'))
                received_event_ids.append(data.get('event_id'))
                
                # Acknowledge the message
                subscriber.acknowledge(
                    request={
                        "subscription": subscription_path,
                        "ack_ids": [received_message.ack_id]
                    }
                )
            except json.JSONDecodeError:
                pytest.fail("Received message is not valid JSON")
        
        # Verify we received the expected messages
        expected_event_ids = [msg['event_id'] for msg in test_messages]
        for expected_id in expected_event_ids:
            assert expected_id in received_event_ids


class TestPubSubErrorHandling:
    """Test error handling scenarios."""
    
    def test_publish_to_nonexistent_topic(self, configs):
        """Test publishing to a non-existent topic."""
        publisher = pubsub_v1.PublisherClient()
        nonexistent_topic = publisher.topic_path(
            configs["gcp"].project_id, 
            "nonexistent-topic-12345"
        )
        
        message_data = json.dumps({"test": "data"}).encode('utf-8')
        
        with pytest.raises(Exception):
            future = publisher.publish(nonexistent_topic, message_data)
            future.result(timeout=30)  # This should raise an exception
    
    def test_create_duplicate_topic(self, pubsub_helper, configs):
        """Test creating a topic that already exists."""
        topic_name = generate_unique_resource_name("test-duplicate")
        
        # Create topic first time
        topic_path1 = pubsub_helper.create_test_topic(topic_name)
        
        # Create same topic again (should not raise error)
        topic_path2 = pubsub_helper.create_test_topic(topic_name)
        
        assert topic_path1 == topic_path2


class TestPubSubPerformance:
    """Test Pub/Sub performance characteristics."""
    
    def test_bulk_message_publishing(self, pubsub_helper, configs):
        """Test publishing a large number of messages."""
        topic_name = generate_unique_resource_name("test-bulk-publishing")
        topic_path = pubsub_helper.create_test_topic(topic_name)
        
        # Generate 100 test messages
        messages = [
            generate_citizen_report(event_id=f"bulk-{i}") for i in range(100)
        ]
        
        with TestTimer("bulk message publishing") as timer:
            message_ids = pubsub_helper.publish_messages(topic_path, messages)
        
        assert len(message_ids) == 100
        assert timer.duration < 60  # Should complete within 60 seconds
        
        # Calculate throughput
        throughput = len(messages) / timer.duration
        print(f"Publishing throughput: {throughput:.2f} messages/second")
        
        # Reasonable throughput expectation
        assert throughput > 1.0  # At least 1 message per second
