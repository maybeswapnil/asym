"""
Utility functions and helpers.
"""

import hashlib
import secrets
import string
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import UUID


def generate_random_string(length: int = 32) -> str:
    """Generate a random string of specified length."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_hash(data: str, algorithm: str = "sha256") -> str:
    """Generate hash for given data."""
    if algorithm == "sha256":
        return hashlib.sha256(data.encode()).hexdigest()
    elif algorithm == "md5":
        return hashlib.md5(data.encode()).hexdigest()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")


def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string."""
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parse datetime from string."""
    return datetime.strptime(dt_str, format_str)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing or replacing unsafe characters."""
    # Remove or replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Ensure filename is not empty
    if not filename:
        filename = f"file_{generate_random_string(8)}"
    
    return filename


def validate_email(email: str) -> bool:
    """Basic email validation."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """Mask sensitive data, showing only the last few characters."""
    if len(data) <= visible_chars:
        return '*' * len(data)
    
    masked_length = len(data) - visible_chars
    return '*' * masked_length + data[-visible_chars:]


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries."""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def convert_uuid_to_str(obj: Any) -> Any:
    """Convert UUID objects to strings in nested data structures."""
    if isinstance(obj, UUID):
        return str(obj)
    elif isinstance(obj, dict):
        return {key: convert_uuid_to_str(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_uuid_to_str(item) for item in obj]
    else:
        return obj


def paginate_query_params(page: int = 1, page_size: int = 20, max_page_size: int = 100) -> Dict[str, int]:
    """Calculate skip and limit values for pagination."""
    # Ensure page is at least 1
    page = max(1, page)
    
    # Ensure page_size is within bounds
    page_size = min(max(1, page_size), max_page_size)
    
    # Calculate skip value
    skip = (page - 1) * page_size
    
    return {
        "skip": skip,
        "limit": page_size,
        "page": page,
        "page_size": page_size
    }


def calculate_pagination_info(total: int, page: int, page_size: int) -> Dict[str, Any]:
    """Calculate pagination information."""
    total_pages = (total + page_size - 1) // page_size  # Ceiling division
    has_next = page < total_pages
    has_prev = page > 1
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_prev": has_prev,
        "next_page": page + 1 if has_next else None,
        "prev_page": page - 1 if has_prev else None,
    }
