from typing import Annotated, List, Optional

from pydantic import StringConstraints
from pydantic_xml import BaseXmlModel, attr, element, wrapped


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
