"""
Firestore service for handling database operations.
"""
from datetime import datetime
from typing import Type, TypeVar, Optional, List

from google.cloud import firestore

from data_models.firestore_models.base_model import BaseModel

T = TypeVar('T', bound=BaseModel)


class FirestoreRepository:
    """Generic repository for Firestore operations."""

    def __init__(self, client: firestore.Client):
        self.client = client

    def get(self, model_class: Type[T], doc_id: str) -> Optional[T]:
        """
        Retrieves a document from Firestore and converts it to a model instance.

        Args:
            model_class: The model class to convert the document to.
            doc_id: The ID of the document to retrieve.

        Returns:
            An instance of the model class, or None if the document does not exist.
        """
        doc_ref = self.client.collection(model_class.collection_name()).document(doc_id)
        doc = doc_ref.get()
        return model_class.from_firestore(doc.id, doc.to_dict()) if doc.exists else None

    def add(self, model_instance: T) -> T:
        """
        Adds a new document to Firestore.

        Args:
            model_instance: The model instance to add.

        Returns:
            The model instance with the ID and timestamps set.
        """
        model_instance.updated_at = datetime.utcnow()
        collection_ref = self.client.collection(model_instance.collection_name())
        if model_instance.id:
            doc_ref = collection_ref.document(model_instance.id)
        else:
            doc_ref = collection_ref.document()
            model_instance.created_at = datetime.utcnow()  # Set created_at for new docs

        doc_ref.set(model_instance.to_firestore_dict())
        model_instance.id = doc_ref.id
        return model_instance

    def update(self, model_instance: T) -> None:
        """
        Updates an existing document in Firestore.

        Args:
            model_instance: The model instance to update.
        """
        if not model_instance.id:
            raise ValueError("Document ID is required for updates.")
        model_instance.updated_at = datetime.utcnow()
        doc_ref = self.client.collection(model_instance.collection_name()).document(model_instance.id)
        doc_ref.update(model_instance.to_firestore_dict())

    def delete(self, model_class: Type[T], doc_id: str) -> None:
        """
        Deletes a document from Firestore.

        Args:
            model_class: The model class of the document to delete.
            doc_id: The ID of the document to delete.
        """
        self.client.collection(model_class.collection_name()).document(doc_id).delete()

    def query(self, model_class: Type[T], **kwargs) -> List[T]:
        """
        Queries a collection in Firestore.

        Args:
            model_class: The model class to query.
            **kwargs: The query parameters.

        Returns:
            A list of model instances that match the query.
        """
        query = self.client.collection(model_class.collection_name())
        for key, value in kwargs.items():
            if isinstance(value, tuple):
                query = query.where(key, value[0], value[1])
            else:
                query = query.where(key, '==', value)
        return [model_class.from_firestore(doc.id, doc.to_dict()) for doc in query.stream()]


class FirestoreService:
    """Service class for high-level Firestore operations."""

    def __init__(self, project_id: str = None, credentials_path: str = None):
        if credentials_path:
            self.client = firestore.Client.from_service_account_json(credentials_path, project=project_id)
        else:
            self.client = firestore.Client(project=project_id)
        self.repository = FirestoreRepository(self.client)

    def get_document(self, model_class: Type[T], doc_id: str) -> Optional[T]:
        """Retrieves a document from Firestore."""
        return self.repository.get(model_class, doc_id)

    def add_document(self, model_instance: T) -> T:
        """Adds a document to Firestore."""
        return self.repository.add(model_instance)

    def update_document(self, model_instance: T) -> None:
        """Updates a document in Firestore."""
        self.repository.update(model_instance)

    def delete_document(self, model_class: Type[T], doc_id: str) -> None:
        """Deletes a document from Firestore."""
        self.repository.delete(model_class, doc_id)

    def query_documents(self, model_class: Type[T], **kwargs) -> List[T]:
        """Queries documents in Firestore."""
        return self.repository.query(model_class, **kwargs)
