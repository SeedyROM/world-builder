from enum import Enum
from pathlib import Path

from world_builder.errors import Err, Error, Ok, Result


class PromptErrorType(Enum):
    NOT_FOUND = "Prompt not found"
    INVALID_VERSION_VALUE = "Invalid prompt version value"
    INVALID_VERSION = "Invalid prompt version"
    IO_ERROR = "Input/Output error"
    UNKNOWN_ERROR = "An unknown error occurred"


class PromptVersion(Enum):
    V0_1 = "v0.1"
    V0_1_1 = "v0.1.1"


# Type alias for convenience
PromptError = Error[PromptErrorType]


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
                Error(
                    type=PromptErrorType.NOT_FOUND,
                    source=f"Unknown version '{normalized}'. Valid: {valid_versions}",
                ).with_context(
                    input_version=version,
                    normalized_version=normalized,
                    valid_versions=valid_versions,
                )
            )
    else:
        return Err(
            Error(
                type=PromptErrorType.INVALID_VERSION,
                source="Version must be a string or PromptVersion enum",
            ).with_context(input_type=type(version).__name__, input_value=str(version))
        )


def _load_prompt_file(version: str) -> Result[str, PromptError]:
    """Load the prompt file based on the version."""
    prompt_file_path = Path(__file__).parent / "data" / f"{version}.md"

    print(f"Looking for prompt file at: {prompt_file_path}")

    if not prompt_file_path.exists():
        return Err(
            Error(
                type=PromptErrorType.NOT_FOUND,
                source=f"Prompt file '{prompt_file_path}' does not exist.",
            ).with_context(
                file_path=str(prompt_file_path), version=version, operation="file_load"
            )
        )

    try:
        with open(prompt_file_path, "r", encoding="utf-8") as file:
            return Ok(file.read())
    except PermissionError as e:
        return Err(
            Error(
                type=PromptErrorType.IO_ERROR,
                source=f"Permission denied: {e}",
            ).with_context(
                file_path=str(prompt_file_path),
                operation="read",
                error_type="permission_denied",
            )
        )
    except FileNotFoundError as e:
        # This shouldn't happen since we check exists(), but just in case
        return Err(
            Error(
                type=PromptErrorType.NOT_FOUND,
                source=f"File disappeared: {e}",
            ).with_context(file_path=str(prompt_file_path), operation="read")
        )
    except Exception as e:
        return Err(
            Error(
                type=PromptErrorType.UNKNOWN_ERROR,
                source=str(e),
            ).with_context(
                file_path=str(prompt_file_path),
                operation="read",
                exception_type=type(e).__name__,
            )
        )


def get_prompt_by_version(version: str | PromptVersion) -> Result[str, PromptError]:
    return _validate_and_normalize_version(version).and_then(_load_prompt_file)
