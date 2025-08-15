"""
Base service classes and interfaces.
"""

from abc import ABC
from typing import Any, Dict, List, Optional, TypeVar
from uuid import UUID

from ..repositories import BaseRepository

ModelType = TypeVar("ModelType")
RepositoryType = TypeVar("RepositoryType", bound=BaseRepository)


class BaseService(ABC):
    """
    Abstract base service class.
    
    Provides common business logic operations.
    """
    
    def __init__(self, repository: RepositoryType):
        self.repository = repository
    
    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Get an entity by ID."""
        return await self.repository.get_by_id(id)
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelType]:
        """Get all entities with optional filtering and pagination."""
        return await self.repository.get_all(skip=skip, limit=limit, filters=filters)
    
    async def create(self, obj_data: Dict[str, Any]) -> ModelType:
        """Create a new entity."""
        # Override this method to add business logic validation
        return await self.repository.create(obj_data)
    
    async def update(self, id: UUID, obj_data: Dict[str, Any]) -> Optional[ModelType]:
        """Update an existing entity."""
        # Override this method to add business logic validation
        return await self.repository.update(id, obj_data)
    
    async def delete(self, id: UUID) -> bool:
        """Delete an entity by ID."""
        return await self.repository.delete(id)
    
    async def exists(self, id: UUID) -> bool:
        """Check if an entity exists by ID."""
        return await self.repository.exists(id)
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities with optional filtering."""
        return await self.repository.count(filters)
