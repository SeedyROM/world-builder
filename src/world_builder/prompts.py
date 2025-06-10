from enum import Enum
from pathlib import Path
from xml.etree.ElementTree import ParseError

from lxml.etree import XMLSyntaxError
from pydantic import ValidationError
from pydantic_xml import ParsingError

from world_builder.data import CodeChanges
from world_builder.errors import Err, Error, Ok, Result


class PromptErrorType(Enum):
    """Types of errors that can occur when working with prompts."""

    NOT_FOUND = "Prompt not found"
    INVALID_VERSION_VALUE = "Invalid prompt version value"
    INVALID_VERSION = "Invalid prompt version"
    IO_ERROR = "Input/Output error"
    UNKNOWN_ERROR = "An unknown error occurred"


class ParserErrorType(Enum):
    """Error types for parsing the prompt result."""

    INVALID_XML = "Invalid XML format"
    MISSING_ELEMENT = "Required element is missing"
    PARSING_ERROR = "Error parsing XML"


PromptError = Error[PromptErrorType]
ParserError = Error[ParserErrorType]


class PromptVersion(Enum):
    """Accepted prompt versions."""

    V0_1 = "v0.1"


CURRENT_VERSION = PromptVersion.V0_1


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
    prompt_file_path = Path(__file__).parent / "prompts" / f"{version}.md"

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
        # Catch-all for any other exceptions
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


def get_prompt_by_version(
    version: str | PromptVersion = CURRENT_VERSION,
) -> Result[str, PromptError]:
    """
    Get the prompt content for a specific version.
    Valid versions are defined in the `PromptVersion` enum.

    ### NOTE:
    **If you've never seen a result method chain before, this is a good example.**

    It uses the `and_then` method (from `Result`, similar to rust)
    to chain the result of validating the version with the result of loading the prompt
    file and returns the final result, which is either the prompt content or an error.
    This is encoded as `Result[str, PromptError]`, meaning it can either be
    a successful result containing the prompt content wrapped in `Ok`,
    or an error wrapped in `Err` with a specific error type `PromptError`.

    When methods share a common error type, you can compose them as such to
    create a more readable and maintainable code flow for more complex operations
    with reliable error handling.

    It's also possible to convert/collude the value/error types
    from the first method to the second in the chain (and so on and so forth),
    in this case we keep the same error type for simplicity.

    :param version: The version of the prompt to retrieve.
    :returns: Result containing either the prompt content (Ok) or an error (Err)
    """
    return _validate_and_normalize_version(version).and_then(_load_prompt_file)


def parse_prompt_result(markup: str) -> Result[CodeChanges, ParserError]:
    """
    Parse the provided XML markup into a CodeChanges object.

    :params markup: The XML markup to parse.
    :returns: Result containing either the parsed CodeChanges object (Ok)
              or a ParserError (Err) with detailed context.
    """
    # Validate input
    if not markup or not markup.strip():
        return Err(
            ParserError(
                type=ParserErrorType.INVALID_XML,
                source="Empty or whitespace-only markup provided",
            ).with_context(markup=markup, operation="input_validation")
        )

    try:
        code_changes = CodeChanges.from_xml(markup)
        return Ok(code_changes)

    except ParsingError as pe:
        # pydantic-xml specific parsing errors
        return Err(
            ParserError(
                type=ParserErrorType.MISSING_ELEMENT,
                source=f"XML structure error: {str(pe)}",
            ).with_context(
                markup=markup,
                operation="xml_structure_parsing",
                error_type="ParsingError",
            )
        )

    except ValidationError as ve:
        # Pydantic validation errors
        error_details = []
        for error in ve.errors():
            loc = " -> ".join(str(x) for x in error["loc"]) if error["loc"] else "root"
            error_details.append(f"{loc}: {error['msg']}")

        return Err(
            ParserError(
                type=ParserErrorType.PARSING_ERROR,
                source=f"Validation failed: {'; '.join(error_details)}",
            ).with_context(
                markup=markup,
                operation="validation",
                error_type="ValidationError",
                error_count=len(ve.errors()),
            )
        )

    except (ParseError, XMLSyntaxError) as xml_error:
        # Handle both standard library and lxml XML parsing errors
        return Err(
            ParserError(
                type=ParserErrorType.INVALID_XML,
                source=f"Malformed XML: {str(xml_error)}",
            ).with_context(
                markup=markup,
                operation="xml_parsing",
                error_type=type(xml_error).__name__,
                line_number=getattr(xml_error, "lineno", None),
                column=getattr(xml_error, "offset", None),
            )
        )

    except Exception as e:  # pragma: no cover
        # Catch-all for any other unexpected errors
        return Err(
            ParserError(
                type=ParserErrorType.PARSING_ERROR,
                source=f"Unexpected error during parsing: {str(e)}",
            ).with_context(
                markup=markup,
                operation="general_parsing",
                error_type=type(e).__name__,
            )
        )
