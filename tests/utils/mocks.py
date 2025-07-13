"""
Centralized mock services for testing.
Provides consistent mock implementations for external services.
"""

from typing import Dict, Any, List, Optional, Union
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime
import json
import uuid

# Import shared models
import sys
sys.path.append('server')

from shared_models import EventCore, UserProfile, Feedback


class MockFirestoreService:
    """Mock Firestore service for testing."""
    
    def __init__(self):
        self.documents = {}
        self.collections = {}
        self.call_history = []
        self.should_fail = False
        self.failure_message = "Mock Firestore failure"
    
    def add_document(self, document: Union[EventCore, UserProfile, Feedback], collection: str = None):
        """Mock adding a document to Firestore."""
        self.call_history.append(('add_document', document, collection))

        if self.should_fail:
            raise Exception(self.failure_message)

        # Generate document ID based on document type
        if hasattr(document, 'user_id') and isinstance(document, UserProfile):
            doc_id = document.user_id
        elif hasattr(document, 'id'):
            doc_id = document.id
        elif hasattr(document, 'metadata') and 'event_id' in document.metadata:
            doc_id = document.metadata['event_id']
        else:
            doc_id = str(uuid.uuid4())

        collection_name = collection or self._get_collection_name(document)

        if collection_name not in self.documents:
            self.documents[collection_name] = {}

        self.documents[collection_name][doc_id] = document
        return doc_id
    
    def get_document(self, doc_id: str, collection: str):
        """Mock getting a document from Firestore."""
        self.call_history.append(('get_document', doc_id, collection))
        
        if self.should_fail:
            raise Exception(self.failure_message)
        
        return self.documents.get(collection, {}).get(doc_id)
    
    def update_document(self, doc_id: str, updates: Dict[str, Any], collection: str):
        """Mock updating a document in Firestore."""
        self.call_history.append(('update_document', doc_id, updates, collection))
        
        if self.should_fail:
            raise Exception(self.failure_message)
        
        if collection in self.documents and doc_id in self.documents[collection]:
            # Simple update simulation
            document = self.documents[collection][doc_id]
            for key, value in updates.items():
                setattr(document, key, value)
            return True
        return False
    
    def delete_document(self, doc_id: str, collection: str):
        """Mock deleting a document from Firestore."""
        self.call_history.append(('delete_document', doc_id, collection))
        
        if self.should_fail:
            raise Exception(self.failure_message)
        
        if collection in self.documents and doc_id in self.documents[collection]:
            del self.documents[collection][doc_id]
            return True
        return False
    
    def query_documents(self, collection: str, filters: Dict[str, Any] = None, limit: int = None):
        """Mock querying documents from Firestore."""
        self.call_history.append(('query_documents', collection, filters, limit))
        
        if self.should_fail:
            raise Exception(self.failure_message)
        
        documents = list(self.documents.get(collection, {}).values())
        
        # Simple filtering simulation
        if filters:
            filtered_docs = []
            for doc in documents:
                match = True
                for key, value in filters.items():
                    if not hasattr(doc, key) or getattr(doc, key) != value:
                        match = False
                        break
                if match:
                    filtered_docs.append(doc)
            documents = filtered_docs
        
        if limit:
            documents = documents[:limit]
        
        return documents
    
    def _get_collection_name(self, document) -> str:
        """Get collection name based on document type."""
        if isinstance(document, EventCore):
            return 'events'
        elif isinstance(document, UserProfile):
            return 'users'
        elif isinstance(document, Feedback):
            return 'feedback'
        else:
            return 'unknown'
    
    def reset(self):
        """Reset the mock service state."""
        self.documents.clear()
        self.collections.clear()
        self.call_history.clear()
        self.should_fail = False
    
    def set_failure_mode(self, should_fail: bool, message: str = None):
        """Set the mock to fail operations."""
        self.should_fail = should_fail
        if message:
            self.failure_message = message


class MockBigQueryService:
    """Mock BigQuery service for testing."""
    
    def __init__(self):
        self.tables = {}
        self.query_results = {}
        self.call_history = []
        self.should_fail = False
        self.failure_message = "Mock BigQuery failure"
    
    def insert_rows(self, table_name: str, rows: List[Dict[str, Any]]):
        """Mock inserting rows into BigQuery."""
        self.call_history.append(('insert_rows', table_name, len(rows)))
        
        if self.should_fail:
            raise Exception(self.failure_message)
        
        if table_name not in self.tables:
            self.tables[table_name] = []
        
        self.tables[table_name].extend(rows)
        return len(rows)
    
    def query(self, sql: str, parameters: Dict[str, Any] = None):
        """Mock executing a BigQuery query."""
        self.call_history.append(('query', sql, parameters))
        
        if self.should_fail:
            raise Exception(self.failure_message)
        
        # Return pre-configured results or empty list
        query_key = sql.strip().lower()
        return self.query_results.get(query_key, [])
    
    def create_table(self, table_name: str, schema: List[Dict[str, str]]):
        """Mock creating a BigQuery table."""
        self.call_history.append(('create_table', table_name, schema))
        
        if self.should_fail:
            raise Exception(self.failure_message)
        
        self.tables[table_name] = []
        return True
    
    def set_query_result(self, sql: str, result: List[Dict[str, Any]]):
        """Set a pre-configured result for a specific query."""
        query_key = sql.strip().lower()
        self.query_results[query_key] = result
    
    def get_table_data(self, table_name: str) -> List[Dict[str, Any]]:
        """Get all data from a mock table."""
        return self.tables.get(table_name, [])
    
    def reset(self):
        """Reset the mock service state."""
        self.tables.clear()
        self.query_results.clear()
        self.call_history.clear()
        self.should_fail = False


class MockPubSubService:
    """Mock Pub/Sub service for testing."""
    
    def __init__(self):
        self.topics = {}
        self.subscriptions = {}
        self.published_messages = []
        self.call_history = []
        self.should_fail = False
        self.failure_message = "Mock Pub/Sub failure"
    
    def publish_message(self, topic: str, message: Dict[str, Any], attributes: Dict[str, str] = None):
        """Mock publishing a message to Pub/Sub."""
        self.call_history.append(('publish_message', topic, message, attributes))
        
        if self.should_fail:
            raise Exception(self.failure_message)
        
        message_data = {
            'topic': topic,
            'message': message,
            'attributes': attributes or {},
            'timestamp': datetime.utcnow().isoformat(),
            'message_id': str(uuid.uuid4())
        }
        
        self.published_messages.append(message_data)
        
        if topic not in self.topics:
            self.topics[topic] = []
        self.topics[topic].append(message_data)
        
        return message_data['message_id']
    
    def create_topic(self, topic_name: str):
        """Mock creating a Pub/Sub topic."""
        self.call_history.append(('create_topic', topic_name))
        
        if self.should_fail:
            raise Exception(self.failure_message)
        
        if topic_name not in self.topics:
            self.topics[topic_name] = []
        return True
    
    def create_subscription(self, subscription_name: str, topic_name: str):
        """Mock creating a Pub/Sub subscription."""
        self.call_history.append(('create_subscription', subscription_name, topic_name))
        
        if self.should_fail:
            raise Exception(self.failure_message)
        
        self.subscriptions[subscription_name] = {
            'topic': topic_name,
            'messages': []
        }
        return True
    
    def get_messages_for_topic(self, topic: str) -> List[Dict[str, Any]]:
        """Get all messages published to a topic."""
        return self.topics.get(topic, [])
    
    def get_published_messages(self) -> List[Dict[str, Any]]:
        """Get all published messages."""
        return self.published_messages.copy()
    
    def reset(self):
        """Reset the mock service state."""
        self.topics.clear()
        self.subscriptions.clear()
        self.published_messages.clear()
        self.call_history.clear()
        self.should_fail = False


class MockStorageService:
    """Mock Cloud Storage service for testing."""
    
    def __init__(self):
        self.buckets = {}
        self.call_history = []
        self.should_fail = False
        self.failure_message = "Mock Storage failure"
    
    def upload_file(self, bucket_name: str, file_name: str, file_content: bytes, content_type: str = None):
        """Mock uploading a file to Cloud Storage."""
        self.call_history.append(('upload_file', bucket_name, file_name, len(file_content), content_type))
        
        if self.should_fail:
            raise Exception(self.failure_message)
        
        if bucket_name not in self.buckets:
            self.buckets[bucket_name] = {}
        
        self.buckets[bucket_name][file_name] = {
            'content': file_content,
            'content_type': content_type,
            'size': len(file_content),
            'uploaded_at': datetime.utcnow().isoformat()
        }
        
        return f"gs://{bucket_name}/{file_name}"
    
    def download_file(self, bucket_name: str, file_name: str) -> bytes:
        """Mock downloading a file from Cloud Storage."""
        self.call_history.append(('download_file', bucket_name, file_name))
        
        if self.should_fail:
            raise Exception(self.failure_message)
        
        if bucket_name in self.buckets and file_name in self.buckets[bucket_name]:
            return self.buckets[bucket_name][file_name]['content']
        
        raise FileNotFoundError(f"File {file_name} not found in bucket {bucket_name}")
    
    def delete_file(self, bucket_name: str, file_name: str):
        """Mock deleting a file from Cloud Storage."""
        self.call_history.append(('delete_file', bucket_name, file_name))
        
        if self.should_fail:
            raise Exception(self.failure_message)
        
        if bucket_name in self.buckets and file_name in self.buckets[bucket_name]:
            del self.buckets[bucket_name][file_name]
            return True
        return False
    
    def list_files(self, bucket_name: str, prefix: str = None) -> List[str]:
        """Mock listing files in a bucket."""
        self.call_history.append(('list_files', bucket_name, prefix))
        
        if self.should_fail:
            raise Exception(self.failure_message)
        
        if bucket_name not in self.buckets:
            return []
        
        files = list(self.buckets[bucket_name].keys())
        
        if prefix:
            files = [f for f in files if f.startswith(prefix)]
        
        return files
    
    def reset(self):
        """Reset the mock service state."""
        self.buckets.clear()
        self.call_history.clear()
        self.should_fail = False


class MockAIService:
    """Mock AI service for testing."""
    
    def __init__(self):
        self.responses = {}
        self.call_history = []
        self.should_fail = False
        self.failure_message = "Mock AI service failure"
    
    def analyze_text(self, text: str, prompt: str = None) -> Dict[str, Any]:
        """Mock AI text analysis."""
        self.call_history.append(('analyze_text', text, prompt))
        
        if self.should_fail:
            raise Exception(self.failure_message)
        
        # Return pre-configured response or default
        response_key = f"text:{text[:50]}"
        return self.responses.get(response_key, {
            'summary': f"Analysis of: {text[:50]}...",
            'category': 'Other',
            'sentiment': 'neutral',
            'confidence': 0.85
        })
    
    def analyze_image(self, image_data: bytes, prompt: str = None) -> Dict[str, Any]:
        """Mock AI image analysis."""
        self.call_history.append(('analyze_image', len(image_data), prompt))
        
        if self.should_fail:
            raise Exception(self.failure_message)
        
        return self.responses.get('image_analysis', {
            'objects_detected': ['road', 'vehicle', 'building'],
            'description': 'Urban scene with traffic',
            'confidence': 0.92
        })
    
    def set_response(self, key: str, response: Dict[str, Any]):
        """Set a pre-configured response for testing."""
        self.responses[key] = response
    
    def reset(self):
        """Reset the mock service state."""
        self.responses.clear()
        self.call_history.clear()
        self.should_fail = False


class MockServiceContainer:
    """Container for all mock services."""
    
    def __init__(self):
        self.firestore = MockFirestoreService()
        self.bigquery = MockBigQueryService()
        self.pubsub = MockPubSubService()
        self.storage = MockStorageService()
        self.ai = MockAIService()
    
    def reset_all(self):
        """Reset all mock services."""
        self.firestore.reset()
        self.bigquery.reset()
        self.pubsub.reset()
        self.storage.reset()
        self.ai.reset()
    
    def set_all_failure_mode(self, should_fail: bool, message: str = "Mock service failure"):
        """Set all services to failure mode."""
        self.firestore.set_failure_mode(should_fail, message)
        self.bigquery.should_fail = should_fail
        self.bigquery.failure_message = message
        self.pubsub.should_fail = should_fail
        self.pubsub.failure_message = message
        self.storage.should_fail = should_fail
        self.storage.failure_message = message
        self.ai.should_fail = should_fail
        self.ai.failure_message = message
