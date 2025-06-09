from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Generic, Optional, Protocol, TypeVar

# Re-export result types for convenience
from result import Err, Ok, Result  # noqa: F401


# Updated protocol to work with Python's Enum
class Errortype(Protocol):
    value: str


# Alternative: Just use Enum directly as the bound
E = TypeVar("E", bound=Enum)  # Change this line


@dataclass
class Error(Generic[E]):
    """Generic error structure"""

    type: E
    source: Optional[Exception | str] = None
    context: Dict[str, Any] = field(default_factory=dict)

    @property
    def message(self) -> str:
        return self.type.value

    def with_context(self, **kwargs) -> "Error[E]":
        """Add context information"""
        new_context = {**self.context, **kwargs}
        return Error(type=self.type, source=self.source, context=new_context)

    def __str__(self) -> str:
        parts = [self.message]
        if self.source:
            parts.append(f"Source: {self.source}")
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            parts.append(f"Context: {context_str}")
        return " | ".join(parts)


# Explicitly list what should be available when importing from this module
__all__ = ["Error", "Ok", "Err", "Result"]
