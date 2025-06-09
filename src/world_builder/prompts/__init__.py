from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

from result import Err, Ok, Result


class PromptErrorType(Enum):
    NOT_FOUND = "Prompt not found"
    INVALID_VERSION_VALUE = "Invalid prompt version value"
    INVALID_VERSION = "Invalid prompt version"
    IO_ERROR = "Input/Output error"
    UNKNOWN_ERROR = "An unknown error occurred"


@dataclass
class PromptError:
    type: PromptErrorType
    source: Optional[Exception | str] = None


class PromptVersion(Enum):
    V0_1 = "v0.1"


def _validate_and_normalize_version(
    version: str | PromptVersion,
) -> Result[str, PromptError]:
    """Validate and normalize version input."""
    if isinstance(version, PromptVersion):
        return Ok(version.value)
    elif isinstance(version, str):
        normalized = version.lower().strip()
        # Check if it's a valid version
        valid_versions = [v.value for v in PromptVersion]
        if normalized in valid_versions:
            return Ok(normalized)
        else:
            return Err(
                PromptError(
                    type=PromptErrorType.NOT_FOUND,
                    source=f"Unknown version '{normalized}'. Valid: {valid_versions}",
                )
            )
    else:
        return Err(
            PromptError(
                type=PromptErrorType.INVALID_VERSION,
                source="Version must be a string or PromptVersion enum",
            )
        )


def _load_prompt_file(version: str) -> Result[str, PromptError]:
    """Load the prompt file based on the version."""
    prompt_file_path = Path(__file__).parent / "data" / f"{version}.md"

    print(f"Looking for prompt file at: {prompt_file_path}")

    if not prompt_file_path.exists():
        return Err(
            PromptError(
                type=PromptErrorType.NOT_FOUND,
                source=f"Prompt file '{prompt_file_path}' does not exist.",
            )
        )

    try:
        with open(prompt_file_path, "r", encoding="utf-8") as file:
            return Ok(file.read())
    except Exception as e:
        return Err(
            PromptError(
                type=PromptErrorType.IO_ERROR,
                source=str(e),
            )
        )


def get_prompt_by_version(version: str | PromptVersion) -> Result[str, PromptError]:
    return _validate_and_normalize_version(version).and_then(_load_prompt_file)
