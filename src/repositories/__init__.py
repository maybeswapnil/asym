"""
Base repository pattern for MongoDB data access layer using Beanie ODM.
"""

from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from abc import ABC, abstractmethod

from beanie import Document
from pymongo import ASCENDING, DESCENDING

DocumentType = TypeVar("DocumentType", bound=Document)


class BaseRepository(Generic[DocumentType], ABC):
    """
    Base repository class providing common database operations for MongoDB.
    
    This class provides a generic interface for CRUD operations
    that can be inherited by specific document repositories.
    """
    
    def __init__(self, document_class: Type[DocumentType]):
        self.document_class = document_class
    
    async def get_by_id(self, id: str) -> Optional[DocumentType]:
        """Get a document by ID."""
        return await self.document_class.get(id)
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        sort: Optional[Dict[str, int]] = None
    ) -> List[DocumentType]:
        """Get all documents with optional filtering, pagination and sorting."""
        query = {}
        
        # Apply filters if provided
        if filters:
            for field, value in filters.items():
                query[field] = value
        
        # Build query
        result = self.document_class.find(query)
        
        # Apply sorting
        if sort:
            for field, direction in sort.items():
                result = result.sort([(field, direction)])
        
        # Apply pagination
        result = result.skip(skip).limit(limit)
        
        return await result.to_list()
    
    async def create(self, obj_data: Dict[str, Any]) -> DocumentType:
        """Create a new document."""
        document = self.document_class(**obj_data)
        await document.create()
        return document
    
    async def update(self, id: str, obj_data: Dict[str, Any]) -> Optional[DocumentType]:
        """Update an existing document."""
        # Remove None values to avoid overwriting with None
        obj_data = {k: v for k, v in obj_data.items() if v is not None}
        
        document = await self.get_by_id(id)
        if not document:
            return None
        
        # Update fields
        for field, value in obj_data.items():
            if hasattr(document, field):
                setattr(document, field, value)
        
        await document.save()
        return document
    
    async def delete(self, id: str) -> bool:
        """Delete a document by ID."""
        document = await self.get_by_id(id)
        if not document:
            return False
        
        await document.delete()
        return True
    
    async def exists(self, id: str) -> bool:
        """Check if a document exists by ID."""
        document = await self.get_by_id(id)
        return document is not None
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count documents with optional filtering."""
        query = {}
        
        if filters:
            for field, value in filters.items():
                query[field] = value
        
        return await self.document_class.find(query).count()
    
    async def find_one(self, filters: Dict[str, Any]) -> Optional[DocumentType]:
        """Find a single document by filters."""
        return await self.document_class.find_one(filters)
    
    async def find_many(
        self,
        filters: Dict[str, Any],
        skip: int = 0,
        limit: int = 100,
        sort: Optional[Dict[str, int]] = None
    ) -> List[DocumentType]:
        """Find multiple documents by filters."""
        result = self.document_class.find(filters)
        
        # Apply sorting
        if sort:
            for field, direction in sort.items():
                result = result.sort([(field, direction)])
        
        # Apply pagination
        result = result.skip(skip).limit(limit)
        
        return await result.to_list()


__all__ = ["BaseRepository"]
