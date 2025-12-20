
from typing import Any, Dict


class ApplicationContextHolder:
    _context: Dict[str, Any] = {}

    @classmethod
    def set(cls, name: str, value: Any):
        cls._context[name] = value

    @classmethod
    def get(cls, name: str) -> Any:
        if name not in cls._context:
            raise KeyError(f"Bean '{name}' not found in application context")
        return cls._context[name]

    @classmethod
    def contains(cls, name: str) -> bool:
        return name in cls._context
