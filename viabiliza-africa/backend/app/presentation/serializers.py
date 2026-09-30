from dataclasses import asdict, is_dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


def to_dict(obj) -> dict | list | str | int | float | bool | None:
    """Serializa DTOs dataclass para JSON."""
    if obj is None:
        return None
    if is_dataclass(obj) and not isinstance(obj, type):
        return {key: to_dict(value) for key, value in asdict(obj).items()}
    if isinstance(obj, dict):
        return {key: to_dict(value) for key, value in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_dict(item) for item in obj]
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, Enum):
        return obj.value
    return obj
