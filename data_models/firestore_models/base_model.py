"""
Base Pydantic model for Firestore documents.

This module provides a Pydantic-based base class for all Firestore document
models, offering automatic data validation, type enforcement, and common
functionality for serialization and deserialization.

Example:
    ```python
    class Product(BaseModel):
        name: str
        price: float

        @classmethod
        def collection_name(cls) -> str:
            return 'products'
    ```
"""
from datetime import datetime
from typing import Any, Dict, Optional, Type, TypeVar

from pydantic import BaseModel as PydanticBaseModel, Field, ConfigDict

# Type variable for generic class methods
T = TypeVar('T', bound='BaseModel')


class BaseModel(PydanticBaseModel):
    """
    Base Pydantic model for all Firestore documents.

    Provides common fields and functionality for:
    - Automatic data validation and type enforcement.
    - Document ID management.
    - Timestamp tracking (created_at, updated_at).
    - Serialization/deserialization.

    Attributes:
        id (Optional[str]): The document ID in Firestore. Can be auto-generated.
        created_at (datetime): Timestamp of creation (auto-set).
        updated_at (datetime): Timestamp of last update (auto-updated on save).
    """
    id: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_firestore_dict(self, exclude_id: bool = True) -> Dict[str, Any]:
        """
        Convert the model to a dictionary for Firestore.

        Args:
            exclude_id (bool): If True, the 'id' field is excluded from the dict.
                               Defaults to True, as Firestore document ID is
                               stored separately from its data.

        Returns:
            Dict[str, Any]: A dictionary representation of the model.
        """
        # Pydantic's model_dump is used for serialization
        data = self.model_dump(exclude={'id'} if exclude_id else None)

        return data

    @classmethod
    def from_firestore(cls: Type[T], doc_id: str, data: Dict[str, Any]) -> Optional[T]:
        """
        Create a model instance from Firestore document data.

        Args:
            doc_id (str): The Firestore document ID.
            data (Dict[str, Any]): The document data from Firestore.

        Returns:
            An instance of the model class, or None if data is empty.
        """
        if not data:
            return None

        # Pydantic model is instantiated with the combined data
        return cls(id=doc_id, **data)

    def __eq__(self, other: Any) -> bool:
        """Compare two model instances for equality, ignoring ID and timestamps."""
        if not isinstance(other, self.__class__):
            return NotImplemented

        # Compare dictionaries, excluding fields that are auto-generated or external
        self_dict = self.model_dump(exclude={'created_at', 'updated_at'})
        other_dict = other.model_dump(exclude={'created_at', 'updated_at'})

        return self_dict == other_dict

    def __repr__(self) -> str:
        """
        Return a string representation of the model.
        """
        return f'<{self.__class__.__name__} id={self.id}>'

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
