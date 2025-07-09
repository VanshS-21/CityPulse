"""
Shared service layer for CityPulse platform.

This module provides unified services that can be used across all components
of the CityPulse platform (API, data models, pipelines, etc.).
"""

import logging
from typing import Type, TypeVar, Optional, List, Dict, Any
from datetime import datetime

from google.cloud import firestore, bigquery
from google.cloud.exceptions import NotFound

from shared_config import get_config, get_database_config, get_collections_config
from shared_exceptions import (
    DatabaseException, handle_database_error, log_exception, ErrorCode
)

logger = logging.getLogger(__name__)

# Import data models - this will work once we set up the proper imports
try:
    from data_models.firestore_models.base_model import BaseModel
    from data_models.firestore_models import Event, UserProfile, Feedback
    from data_models.services.firestore_service import FirestoreService
except ImportError:
    logger.warning("Data models not available - using fallback implementations")
    BaseModel = None
    Event = None
    UserProfile = None
    Feedback = None
    FirestoreService = None

T = TypeVar('T')


class UnifiedDatabaseService:
    """
    Unified database service that provides a consistent interface
    for both Firestore and BigQuery operations.
    """
    
    def __init__(self, config=None):
        """Initialize the unified database service."""
        self.config = config or get_config()
        self.db_config = get_database_config()
        self.collections = get_collections_config()
        
        # Initialize clients
        self._init_firestore_client()
        self._init_bigquery_client()
        
        # Initialize Firestore service if available
        if FirestoreService:
            self.firestore_service = FirestoreService(
                project_id=self.db_config.project_id,
                credentials_path=self.db_config.credentials_path
            )
        else:
            self.firestore_service = None
    
    def _init_firestore_client(self):
        """Initialize Firestore client."""
        try:
            if self.db_config.credentials_path:
                self.firestore_client = firestore.Client.from_service_account_json(
                    self.db_config.credentials_path,
                    project=self.db_config.project_id
                )
            else:
                self.firestore_client = firestore.Client(project=self.db_config.project_id)
            logger.info("Firestore client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firestore client: {e}")
            self.firestore_client = None
    
    def _init_bigquery_client(self):
        """Initialize BigQuery client."""
        try:
            if self.db_config.credentials_path:
                self.bigquery_client = bigquery.Client.from_service_account_json(
                    self.db_config.credentials_path,
                    project=self.db_config.project_id
                )
            else:
                self.bigquery_client = bigquery.Client(project=self.db_config.project_id)
            logger.info("BigQuery client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize BigQuery client: {e}")
            self.bigquery_client = None
    
    # Firestore operations
    def get_document(self, collection_name: str, doc_id: str, model_class: Type[T] = None) -> Optional[T]:
        """Get a document from Firestore."""
        if not self.firestore_client:
            raise RuntimeError("Firestore client not initialized")
        
        try:
            doc_ref = self.firestore_client.collection(collection_name).document(doc_id)
            doc = doc_ref.get()
            
            if not doc.exists:
                return None
            
            data = doc.to_dict()
            data['id'] = doc.id
            
            # If model class is provided and available, convert to model instance
            if model_class and hasattr(model_class, 'from_firestore'):
                return model_class.from_firestore(doc.id, data)
            
            return data
        except Exception as e:
            db_error = handle_database_error("get", collection_name, e, doc_id)
            log_exception(logger, db_error)
            raise db_error
    
    def add_document(self, collection_name: str, data: Dict[str, Any], doc_id: str = None) -> str:
        """Add a document to Firestore."""
        if not self.firestore_client:
            raise RuntimeError("Firestore client not initialized")
        
        try:
            collection_ref = self.firestore_client.collection(collection_name)
            
            # Add timestamps
            now = datetime.utcnow()
            data['created_at'] = now
            data['updated_at'] = now
            
            if doc_id:
                doc_ref = collection_ref.document(doc_id)
                doc_ref.set(data)
                return doc_id
            else:
                doc_ref = collection_ref.add(data)[1]
                return doc_ref.id
        except Exception as e:
            db_error = handle_database_error("add", collection_name, e)
            log_exception(logger, db_error)
            raise db_error
    
    def update_document(self, collection_name: str, doc_id: str, data: Dict[str, Any]) -> None:
        """Update a document in Firestore."""
        if not self.firestore_client:
            raise RuntimeError("Firestore client not initialized")
        
        try:
            # Add update timestamp
            data['updated_at'] = datetime.utcnow()
            
            doc_ref = self.firestore_client.collection(collection_name).document(doc_id)
            doc_ref.update(data)
        except Exception as e:
            db_error = handle_database_error("update", collection_name, e, doc_id)
            log_exception(logger, db_error)
            raise db_error
    
    def delete_document(self, collection_name: str, doc_id: str) -> None:
        """Delete a document from Firestore."""
        if not self.firestore_client:
            raise RuntimeError("Firestore client not initialized")
        
        try:
            doc_ref = self.firestore_client.collection(collection_name).document(doc_id)
            doc_ref.delete()
        except Exception as e:
            logger.error(f"Error deleting document {doc_id} from {collection_name}: {e}")
            raise
    
    def query_documents(
        self,
        collection_name: str,
        filters: List[tuple] = None,
        order_by: str = None,
        limit: int = None,
        offset: int = None,
        model_class: Type[T] = None
    ) -> List[T]:
        """Query documents from Firestore."""
        if not self.firestore_client:
            raise RuntimeError("Firestore client not initialized")
        
        try:
            query = self.firestore_client.collection(collection_name)
            
            # Apply filters
            if filters:
                for field, operator, value in filters:
                    query = query.where(field, operator, value)
            
            # Apply ordering
            if order_by:
                query = query.order_by(order_by)
            
            # Apply pagination
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            
            docs = query.stream()
            results = []
            
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                
                # Convert to model instance if class provided
                if model_class and hasattr(model_class, 'from_firestore'):
                    results.append(model_class.from_firestore(doc.id, data))
                else:
                    results.append(data)
            
            return results
        except Exception as e:
            logger.error(f"Error querying {collection_name}: {e}")
            raise
    
    # BigQuery operations
    def insert_bigquery_rows(self, table_name: str, rows: List[Dict[str, Any]]) -> None:
        """Insert rows into BigQuery table."""
        if not self.bigquery_client:
            raise RuntimeError("BigQuery client not initialized")
        
        try:
            table_id = f"{self.db_config.project_id}.{self.db_config.bigquery_dataset}.{table_name}"
            table = self.bigquery_client.get_table(table_id)
            
            errors = self.bigquery_client.insert_rows_json(table, rows)
            if errors:
                logger.error(f"BigQuery insert errors: {errors}")
                raise RuntimeError(f"Failed to insert rows: {errors}")
            
            logger.info(f"Successfully inserted {len(rows)} rows into {table_id}")
        except Exception as e:
            logger.error(f"Error inserting rows into BigQuery table {table_name}: {e}")
            raise
    
    def query_bigquery(self, query: str) -> List[Dict[str, Any]]:
        """Execute a BigQuery query."""
        if not self.bigquery_client:
            raise RuntimeError("BigQuery client not initialized")
        
        try:
            query_job = self.bigquery_client.query(query)
            results = query_job.result()
            
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Error executing BigQuery query: {e}")
            raise
    
    # Convenience methods for specific collections
    def get_event(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get an event by ID."""
        return self.get_document(self.collections.events, event_id, Event)
    
    def add_event(self, event_data: Dict[str, Any]) -> str:
        """Add a new event."""
        return self.add_document(self.collections.events, event_data)
    
    def update_event(self, event_id: str, event_data: Dict[str, Any]) -> None:
        """Update an event."""
        self.update_document(self.collections.events, event_id, event_data)
    
    def delete_event(self, event_id: str) -> None:
        """Delete an event."""
        self.delete_document(self.collections.events, event_id)
    
    def query_events(self, filters: List[tuple] = None, **kwargs) -> List[Dict[str, Any]]:
        """Query events."""
        return self.query_documents(self.collections.events, filters, model_class=Event, **kwargs)
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user profile by ID."""
        return self.get_document(self.collections.user_profiles, user_id, UserProfile)
    
    def add_user_profile(self, user_id: str, user_data: Dict[str, Any]) -> str:
        """Add a new user profile with specific ID."""
        return self.add_document(self.collections.user_profiles, user_data, user_id)

    def update_user_profile(self, user_id: str, update_data: Dict[str, Any]) -> None:
        """Update a user profile."""
        self.update_document(self.collections.user_profiles, user_id, update_data)

    def delete_user_profile(self, user_id: str) -> None:
        """Delete a user profile."""
        self.delete_document(self.collections.user_profiles, user_id)
    
    def get_feedback(self, feedback_id: str) -> Optional[Dict[str, Any]]:
        """Get feedback by ID."""
        return self.get_document(self.collections.feedback, feedback_id, Feedback)
    
    def add_feedback(self, feedback_data: Dict[str, Any]) -> str:
        """Add new feedback."""
        return self.add_document(self.collections.feedback, feedback_data)


# Global service instance
_service_instance = None


def get_database_service(config=None) -> UnifiedDatabaseService:
    """
    Get the global database service instance.
    
    Args:
        config: Optional configuration override
        
    Returns:
        UnifiedDatabaseService instance
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = UnifiedDatabaseService(config)
    return _service_instance


def reset_database_service():
    """Reset the global service instance (useful for testing)."""
    global _service_instance
    _service_instance = None
