from unittest.mock import Mock, mock_open, patch

from world_builder.errors import Err, Ok
from world_builder.prompts import (
    CURRENT_VERSION,
    ParserErrorType,
    PromptError,
    PromptErrorType,
    PromptVersion,
    _load_prompt_file,
    _validate_and_normalize_version,
    get_prompt_by_version,
    parse_prompt_result,
)


class TestPromptParsing:
    def test_parse_prompt_result_function_success(self):
        """Test the parse_prompt_result function with valid input."""
        result = parse_prompt_result(
            """
            <code-change>
                <summary>Test summary</summary>
                <files-to-change>
                    <file name="test1.py" />
                    <file name="test2.py" />
                    <file name="test3.py" />
                </files-to-change>
                <changes>
                    <change file-name="test1.py">
                        <modify start-line="1" end-line="5">Modified content</modify>
                    </change>
                    <change file-name="test2.py">
                        <add>New content</add>
                    </change>
                    <change file-name="test3.py">
                        <delete />
                    </change>
                </changes>
                <additional-steps>
                    <step>Run migration</step>
                    <step>Update documentation</step>
                </additional-steps>
                <verification>
                    <step>Run tests</step>
                    <step>Check logs</step>
                </verification>
            </code-change>
            """
        )

        assert result.is_ok()
        code_change = result.unwrap()
        assert code_change.summary == "Test summary"
        assert len(code_change.files_to_change) == 3

    def test_parse_prompt_result_empty_input(self):
        """Test parse_prompt_result function with empty input."""
        result = parse_prompt_result("")

        assert result.is_err()
        error = result.unwrap_err()
        assert error.type == ParserErrorType.INVALID_XML
        assert "Empty or whitespace-only markup" in error.source

    def test_parse_prompt_result_whitespace_only(self):
        """Test parse_prompt_result function with whitespace-only input."""
        result = parse_prompt_result("   \n\t   ")

        assert result.is_err()
        error = result.unwrap_err()
        assert error.type == ParserErrorType.INVALID_XML
        assert "Empty or whitespace-only markup" in error.source

    def test_parse_prompt_result_malformed_xml(self):
        """Test parse_prompt_result function with malformed XML."""
        malformed_xml = """
        <code-change>
            <summary>Test</summary>
            <unclosed-tag>
        </code-change>
        """

        result = parse_prompt_result(malformed_xml)

        assert result.is_err()
        error = result.unwrap_err()
        # Should be INVALID_XML for malformed XML, but some parsers
        # might categorize differently
        assert error.type in [
            ParserErrorType.INVALID_XML,
            ParserErrorType.PARSING_ERROR,
        ]
        assert (
            "Malformed XML" in error.source
            or "XMLSyntax" in error.source
            or "parsing" in error.source.lower()
        )

    def test_parse_prompt_result_wrong_root_element(self):
        """Test parse_prompt_result function with wrong root element."""
        wrong_root = """
        <wrong-element>
            <summary>Test</summary>
        </wrong-element>
        """

        result = parse_prompt_result(wrong_root)

        assert result.is_err()
        error = result.unwrap_err()
        assert error.type == ParserErrorType.MISSING_ELEMENT

    def test_parse_prompt_result_missing_required_fields(self):
        """Test parse_prompt_result function with missing required fields."""
        missing_summary = """
        <code-change>
            <files-to-change>
                <file name="test.py" />
            </files-to-change>
        </code-change>
        """

        result = parse_prompt_result(missing_summary)

        assert result.is_err()
        error = result.unwrap_err()
        assert error.type == ParserErrorType.PARSING_ERROR
        assert "Validation failed" in error.source

    def test_parse_prompt_result_invalid_attribute_types(self):
        """Test parse_prompt_result function with invalid attribute types."""
        invalid_types = """
        <code-change>
            <summary>Test</summary>
            <changes>
                <change file-name="test.py">
                    <modify start-line="not-a-number" end-line="15">
                        Content
                    </modify>
                </change>
            </changes>
        </code-change>
        """

        result = parse_prompt_result(invalid_types)

        assert result.is_err()
        error = result.unwrap_err()
        assert error.type == ParserErrorType.PARSING_ERROR


class TestPromptsValidation:
    """Test cases for prompts.py validation functions to achieve 100% coverage."""

    def test_validate_and_normalize_version_enum_input(self):
        """Test _validate_and_normalize_version with PromptVersion enum."""
        result = _validate_and_normalize_version(PromptVersion.V0_1)

        assert result.is_ok()
        assert result.unwrap() == "v0.1"

    def test_validate_and_normalize_version_valid_string(self):
        """Test _validate_and_normalize_version with valid string."""
        result = _validate_and_normalize_version("v0.1")

        assert result.is_ok()
        assert result.unwrap() == "v0.1"

    def test_validate_and_normalize_version_valid_string_case_insensitive(self):
        """Test _validate_and_normalize_version with valid string (different case)."""
        result = _validate_and_normalize_version("V0.1")

        assert result.is_ok()
        assert result.unwrap() == "v0.1"

    def test_validate_and_normalize_version_valid_string_with_whitespace(self):
        """Test _validate_and_normalize_version with valid string with whitespace."""
        result = _validate_and_normalize_version("  v0.1  ")

        assert result.is_ok()
        assert result.unwrap() == "v0.1"

    def test_validate_and_normalize_version_invalid_string(self):
        """Test _validate_and_normalize_version with invalid string."""
        result = _validate_and_normalize_version("invalid_version")

        assert result.is_err()
        error = result.unwrap_err()
        assert error.type == PromptErrorType.NOT_FOUND
        assert "Unknown version 'invalid_version'" in error.source
        assert "Valid: ['v0.1']" in error.source

    def test_validate_and_normalize_version_invalid_type(self):
        """Test _validate_and_normalize_version with invalid type."""
        result = _validate_and_normalize_version(123)  # Invalid type

        assert result.is_err()
        error = result.unwrap_err()
        assert error.type == PromptErrorType.INVALID_VERSION
        assert "Version must be a string or PromptVersion enum" in error.source


class TestPromptsFileLoading:
    """Test cases for prompts.py file loading functions to achieve 100% coverage."""

    @patch("world_builder.prompts.Path")
    def test_load_prompt_file_success(self, mock_path):
        """Test _load_prompt_file with successful file reading."""
        # Mock the file path and its methods
        mock_file_path = Mock()
        mock_file_path.exists.return_value = True
        mock_path.return_value.parent.__truediv__.return_value.__truediv__.return_value = mock_file_path  # noqa: E501

        test_content = "Test prompt content"

        with patch("builtins.open", mock_open(read_data=test_content)):
            result = _load_prompt_file("v0.1")

        assert result.is_ok()
        assert result.unwrap() == test_content

    @patch("world_builder.prompts.Path")
    def test_load_prompt_file_not_found(self, mock_path):
        """Test _load_prompt_file when file doesn't exist."""
        # Mock the file path and its methods
        mock_file_path = Mock()
        mock_file_path.exists.return_value = False
        mock_path.return_value.parent.__truediv__.return_value.__truediv__.return_value = mock_file_path  # noqa: E501

        result = _load_prompt_file("v0.1")

        assert result.is_err()
        error = result.unwrap_err()
        assert error.type == PromptErrorType.NOT_FOUND
        assert "does not exist" in error.source

    @patch("world_builder.prompts.Path")
    def test_load_prompt_file_permission_error(self, mock_path):
        """Test _load_prompt_file with permission error."""
        # Mock the file path and its methods
        mock_file_path = Mock()
        mock_file_path.exists.return_value = True
        mock_path.return_value.parent.__truediv__.return_value.__truediv__.return_value = mock_file_path  # noqa: E501

        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            result = _load_prompt_file("v0.1")

        assert result.is_err()
        error = result.unwrap_err()
        assert error.type == PromptErrorType.IO_ERROR
        assert "Permission denied" in error.source

    @patch("world_builder.prompts.Path")
    def test_load_prompt_file_file_not_found_during_read(self, mock_path):
        """Test _load_prompt_file with FileNotFoundError during read."""
        # Mock the file path and its methods
        mock_file_path = Mock()
        mock_file_path.exists.return_value = True
        mock_path.return_value.parent.__truediv__.return_value.__truediv__.return_value = mock_file_path  # noqa: E501

        with patch("builtins.open", side_effect=FileNotFoundError("File disappeared")):
            result = _load_prompt_file("v0.1")

        assert result.is_err()
        error = result.unwrap_err()
        assert error.type == PromptErrorType.NOT_FOUND
        assert "File disappeared" in error.source

    @patch("world_builder.prompts.Path")
    def test_load_prompt_file_generic_exception(self, mock_path):
        """Test _load_prompt_file with generic exception."""
        # Mock the file path and its methods
        mock_file_path = Mock()
        mock_file_path.exists.return_value = True
        mock_path.return_value.parent.__truediv__.return_value.__truediv__.return_value = mock_file_path  # noqa: E501

        with patch("builtins.open", side_effect=Exception("Generic error")):
            result = _load_prompt_file("v0.1")

        assert result.is_err()
        error = result.unwrap_err()
        assert error.type == PromptErrorType.UNKNOWN_ERROR
        assert "Generic error" in error.source


class TestPromptsIntegration:
    """Integration tests for prompts.py functions to achieve 100% coverage."""

    @patch("world_builder.prompts._load_prompt_file")
    @patch("world_builder.prompts._validate_and_normalize_version")
    def test_get_prompt_by_version_success_chain(self, mock_validate, mock_load):
        """Test get_prompt_by_version with successful chain."""
        # Mock successful validation
        mock_validate.return_value = Ok("v0.1")
        # Mock successful file loading
        mock_load.return_value = Ok("Test prompt content")

        result = get_prompt_by_version("v0.1")

        assert result.is_ok()
        assert result.unwrap() == "Test prompt content"
        mock_validate.assert_called_once_with("v0.1")
        mock_load.assert_called_once_with("v0.1")

    @patch("world_builder.prompts._validate_and_normalize_version")
    def test_get_prompt_by_version_validation_failure(self, mock_validate):
        """Test get_prompt_by_version with validation failure."""
        # Mock validation failure
        validation_error = PromptError(
            type=PromptErrorType.INVALID_VERSION, source="Invalid version"
        )
        mock_validate.return_value = Err(validation_error)

        result = get_prompt_by_version("invalid")

        assert result.is_err()
        error = result.unwrap_err()
        assert error.type == PromptErrorType.INVALID_VERSION
        assert error.source == "Invalid version"

    @patch("world_builder.prompts._load_prompt_file")
    @patch("world_builder.prompts._validate_and_normalize_version")
    def test_get_prompt_by_version_load_failure(self, mock_validate, mock_load):
        """Test get_prompt_by_version with file loading failure."""
        # Mock successful validation
        mock_validate.return_value = Ok("v0.1")
        # Mock file loading failure
        load_error = PromptError(
            type=PromptErrorType.IO_ERROR, source="File read error"
        )
        mock_load.return_value = Err(load_error)

        result = get_prompt_by_version("v0.1")

        assert result.is_err()
        error = result.unwrap_err()
        assert error.type == PromptErrorType.IO_ERROR
        assert error.source == "File read error"

    def test_get_prompt_by_version_default_version(self):
        """Test get_prompt_by_version with default version."""
        with patch(
            "world_builder.prompts._validate_and_normalize_version"
        ) as mock_validate:
            with patch("world_builder.prompts._load_prompt_file") as mock_load:
                mock_validate.return_value = Ok("v0.1")
                mock_load.return_value = Ok("Default prompt")

                _ = get_prompt_by_version()  # No version specified

                # Should be called with CURRENT_VERSION
                mock_validate.assert_called_once_with(CURRENT_VERSION)

    def test_get_prompt_by_version_enum_input(self):
        """Test get_prompt_by_version with PromptVersion enum input."""
        with patch(
            "world_builder.prompts._validate_and_normalize_version"
        ) as mock_validate:
            with patch("world_builder.prompts._load_prompt_file") as mock_load:
                mock_validate.return_value = Ok("v0.1")
                mock_load.return_value = Ok("Enum prompt")

                _ = get_prompt_by_version(PromptVersion.V0_1)

                mock_validate.assert_called_once_with(PromptVersion.V0_1)
