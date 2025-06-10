from enum import Enum
from typing import Annotated, List, Optional
from xml.etree.ElementTree import ParseError

from lxml.etree import XMLSyntaxError
from pydantic import StringConstraints, ValidationError
from pydantic_xml import BaseXmlModel, attr, element, wrapped
from pydantic_xml.errors import ParsingError

from world_builder.errors import Err, Error, Ok, Result


class ParserErrorType(Enum):
    """Error types for the parser."""

    INVALID_XML = "Invalid XML format"
    MISSING_ELEMENT = "Required element is missing"
    PARSING_ERROR = "Error parsing XML"


ParserError = Error[ParserErrorType]


class File(BaseXmlModel, tag="file"):  # type: ignore[call-arg]
    """Data structure to hold file information."""

    name: str = attr("name")


class ModifyChange(BaseXmlModel, tag="modify"):  # type: ignore[call-arg]
    """Data structure to hold modifications to a file."""

    start_line: Optional[int] = attr("start-line", default=None)
    end_line: Optional[int] = attr("end-line", default=None)
    content: Annotated[str, StringConstraints(strip_whitespace=True)]


class AddChange(BaseXmlModel, tag="add"):  # type: ignore[call-arg]
    """Data structure to hold additions to a file."""

    content: Annotated[str, StringConstraints(strip_whitespace=True)]


class DeleteChange(BaseXmlModel, tag="delete"):  # type: ignore[call-arg]
    """Data structure to hold deletions from a file."""

    # No content needed for delete, just the tag itself
    pass


class Change(BaseXmlModel, tag="change"):  # type: ignore[call-arg]
    """Data structure to hold changes made to a file."""

    file_name: str = attr("file-name")
    modifications: List[ModifyChange] = element("modify", default_factory=list)
    additions: List[AddChange] = element("add", default_factory=list)
    deletions: List[DeleteChange] = element("delete", default_factory=list)


class CodeChanges(BaseXmlModel, tag="code-change"):  # type: ignore[call-arg]
    """Data structure to hold a code change request."""

    summary: Annotated[str, StringConstraints(strip_whitespace=True)] = element(
        "summary"
    )
    files_to_change: list[File] = wrapped(
        "files-to-change", element("file", default_factory=list)
    )
    changes: list[Change] = wrapped("changes", element("change", default_factory=list))
    additional_steps: list[str] = wrapped(
        "additional-steps", element("step", default_factory=list)
    )
    verification_steps: list[str] = wrapped(
        "verification", element("step", default_factory=list)
    )


def parse_markup(markup: str) -> Result[CodeChanges, ParserError]:
    """
    Parse the provided XML markup into a CodeChanges object.

    Args:
        markup (str): The XML markup to parse.

    Returns:
        Result[CodeChanges, ParserError]: A Result containing the parsed CodeChanges
        object or an error if parsing fails.
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
        # (e.g., root element not found, namespace issues)
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
        # (e.g., required fields missing, type conversion failures)
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

    except ParseError as xml_pe:
        # Low-level XML parsing errors (malformed XML) - standard library
        return Err(
            ParserError(
                type=ParserErrorType.INVALID_XML,
                source=f"Malformed XML: {str(xml_pe)}",
            ).with_context(
                markup=markup,
                operation="xml_parsing",
                error_type="ParseError",
                line_number=getattr(xml_pe, "lineno", None),
                column=getattr(xml_pe, "offset", None),
            )
        )

    except Exception as e:
        # Handle lxml XMLSyntaxError specifically
        if isinstance(e, XMLSyntaxError):
            return Err(
                ParserError(
                    type=ParserErrorType.INVALID_XML,
                    source=f"Malformed XML: {str(e)}",
                ).with_context(
                    markup=markup,
                    operation="xml_parsing",
                    error_type="XMLSyntaxError",
                    line_number=getattr(e, "lineno", None),
                    column=getattr(e, "offset", None),
                )
            )

        # Check if it's any other XML syntax error by name
        elif "XMLSyntax" in str(type(e).__name__) or "XMLSyntax" in str(type(e)):
            return Err(
                ParserError(
                    type=ParserErrorType.INVALID_XML,
                    source=f"Malformed XML: {str(e)}",
                ).with_context(
                    markup=markup,
                    operation="xml_parsing",
                    error_type=type(e).__name__,
                    line_number=getattr(e, "lineno", None),
                    column=getattr(e, "offset", None),
                )
            )

        # Catch-all for any other unexpected errors
        return Err(
            ParserError(
                type=ParserErrorType.PARSING_ERROR,
                source=f"Unexpected error during parsing: {str(e)}",
            ).with_context(
                markup=markup,
                operation="general_parsing",
                error_type=type(e).__name__,
                error_module=type(e).__module__,
            )
        )

    except ValueError as ve:
        # Value errors (e.g., invalid attribute values, type conversion issues)
        return Err(
            ParserError(
                type=ParserErrorType.INVALID_XML,
                source=f"Invalid value in XML: {str(ve)}",
            ).with_context(
                markup=markup, operation="value_parsing", error_type="ValueError"
            )
        )

    except UnicodeDecodeError as ude:
        # Encoding issues
        return Err(
            ParserError(
                type=ParserErrorType.INVALID_XML,
                source=f"Text encoding error: {str(ude)}",
            ).with_context(
                markup=markup,
                operation="encoding",
                error_type="UnicodeDecodeError",
                encoding=getattr(ude, "encoding", None),
            )
        )

    except MemoryError:
        # Handle extremely large XML documents
        return Err(
            ParserError(
                type=ParserErrorType.PARSING_ERROR,
                source="XML document too large to process",
            ).with_context(
                markup=markup[:100] + "..." if len(markup) > 100 else markup,
                operation="memory_allocation",
                error_type="MemoryError",
                markup_size=len(markup),
            )
        )

    except RecursionError:
        # Handle deeply nested XML structures
        return Err(
            ParserError(
                type=ParserErrorType.PARSING_ERROR,
                source="XML document too deeply nested",
            ).with_context(
                markup=markup[:100] + "..." if len(markup) > 100 else markup,
                operation="recursion_limit",
                error_type="RecursionError",
            )
        )
