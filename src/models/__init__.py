"""
MongoDB Document Models using Beanie ODM.
"""

from typing import Optional
from uuid import uuid4, UUID
from datetime import datetime

from beanie import Document
from pydantic import Field


class BaseDocument(Document):
    """Base document model with common fields for all documents."""
    
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()), alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        # Use optimistic concurrency control
        use_revision = True
        # Keep null values in the document
        keep_nulls = False


__all__ = ["BaseDocument"]