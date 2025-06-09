from dataclasses import dataclass, field
from typing import Any, Dict, Generic, Optional, Protocol, TypeVar


# Protocols
class ErrorCode(Protocol):
    value: str


# Base generic error
E = TypeVar("E", bound=ErrorCode)


@dataclass
class Error(Generic[E]):
    """Generic error structure"""

    code: E
    source: Optional[Exception | str] = None
    context: Dict[str, Any] = field(default_factory=dict)

    @property
    def message(self) -> str:
        return self.code.value

    def with_context(self, **kwargs) -> "Error[E]":
        """Add context information"""
        new_context = {**self.context, **kwargs}
        return Error(code=self.code, source=self.source, context=new_context)

    def __str__(self) -> str:
        parts = [self.message]
        if self.source:
            parts.append(f"Source: {self.source}")
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            parts.append(f"Context: {context_str}")
        return " | ".join(parts)
