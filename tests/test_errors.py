from enum import Enum

from world_builder.errors import Error


# Test enum for our error types
class ErrorTestType(Enum):
    VALIDATION_ERROR = "Validation failed"
    NETWORK_ERROR = "Network connection failed"
    FILE_NOT_FOUND = "File not found"


class TestErrors:
    """Test cases for the Error class."""

    def test_error_creation_with_type_only(self):
        """Test creating an error with just the type."""
        error = Error(type=ErrorTestType.VALIDATION_ERROR)

        assert error.type == ErrorTestType.VALIDATION_ERROR
        assert error.source is None
        assert error.context == {}

    def test_error_creation_with_string_source(self):
        """Test creating an error with a string source."""
        error = Error(type=ErrorTestType.NETWORK_ERROR, source="Connection timeout")

        assert error.type == ErrorTestType.NETWORK_ERROR
        assert error.source == "Connection timeout"
        assert error.context == {}

    def test_error_creation_with_exception_source(self):
        """Test creating an error with an exception source."""
        exception = ValueError("Invalid input")
        error = Error(type=ErrorTestType.VALIDATION_ERROR, source=exception)

        assert error.type == ErrorTestType.VALIDATION_ERROR
        assert error.source == exception
        assert error.context == {}

    def test_error_creation_with_context(self):
        """Test creating an error with initial context."""
        context = {"user_id": 123, "action": "login"}
        error = Error(type=ErrorTestType.VALIDATION_ERROR, context=context)

        assert error.type == ErrorTestType.VALIDATION_ERROR
        assert error.source is None
        assert error.context == context

    def test_error_creation_with_all_fields(self):
        """Test creating an error with all fields populated."""
        exception = FileNotFoundError("config.json")
        context = {"filename": "config.json", "path": "/etc/app/"}

        error = Error(
            type=ErrorTestType.FILE_NOT_FOUND, source=exception, context=context
        )

        assert error.type == ErrorTestType.FILE_NOT_FOUND
        assert error.source == exception
        assert error.context == context

    def test_message_property(self):
        """Test that message property returns the enum value."""
        error = Error(type=ErrorTestType.VALIDATION_ERROR)
        assert error.message == "Validation failed"

        error2 = Error(type=ErrorTestType.NETWORK_ERROR)
        assert error2.message == "Network connection failed"

    def test_with_context_empty_kwargs(self):
        """Test with_context with no arguments."""
        original_error = Error(
            type=ErrorTestType.VALIDATION_ERROR, context={"original": "value"}
        )

        new_error = original_error.with_context()

        # Should return a new instance with same context
        assert new_error is not original_error
        assert new_error.type == original_error.type
        assert new_error.source == original_error.source
        assert new_error.context == {"original": "value"}

    def test_with_context_new_keys(self):
        """Test with_context adding new context keys."""
        original_error = Error(
            type=ErrorTestType.VALIDATION_ERROR, context={"original": "value"}
        )

        new_error = original_error.with_context(user_id=123, action="submit")

        assert new_error is not original_error
        assert new_error.type == original_error.type
        assert new_error.source == original_error.source
        assert new_error.context == {
            "original": "value",
            "user_id": 123,
            "action": "submit",
        }

    def test_with_context_overwrite_existing_keys(self):
        """Test with_context overwriting existing context keys."""
        original_error = Error(
            type=ErrorTestType.VALIDATION_ERROR,
            context={"user_id": 123, "action": "login"},
        )

        new_error = original_error.with_context(user_id=456, status="failed")

        assert new_error.context == {
            "user_id": 456,  # Overwritten
            "action": "login",  # Preserved
            "status": "failed",  # Added
        }

    def test_with_context_preserves_other_fields(self):
        """Test that with_context preserves type and source."""
        exception = ValueError("test")
        original_error = Error(type=ErrorTestType.VALIDATION_ERROR, source=exception)

        new_error = original_error.with_context(test="value")

        assert new_error.type == ErrorTestType.VALIDATION_ERROR
        assert new_error.source == exception

    def test_str_message_only(self):
        """Test string representation with just message."""
        error = Error(type=ErrorTestType.VALIDATION_ERROR)
        assert str(error) == "Validation failed"

    def test_str_with_string_source(self):
        """Test string representation with string source."""
        error = Error(type=ErrorTestType.NETWORK_ERROR, source="Connection timeout")
        expected = "Network connection failed | Source: Connection timeout"
        assert str(error) == expected

    def test_str_with_exception_source(self):
        """Test string representation with exception source."""
        exception = FileNotFoundError("config.json not found")
        error = Error(type=ErrorTestType.FILE_NOT_FOUND, source=exception)
        expected = "File not found | Source: config.json not found"
        assert str(error) == expected

    def test_str_with_context_only(self):
        """Test string representation with context but no source."""
        error = Error(
            type=ErrorTestType.VALIDATION_ERROR,
            context={"field": "email", "value": "invalid"},
        )
        expected = "Validation failed | Context: field=email, value=invalid"
        assert str(error) == expected

    def test_str_with_source_and_context(self):
        """Test string representation with both source and context."""
        error = Error(
            type=ErrorTestType.VALIDATION_ERROR,
            source="Invalid email format",
            context={"field": "email", "user_id": 123},
        )
        expected = "Validation failed | Source: Invalid email format | Context: field=email, user_id=123"  # noqa: E501
        assert str(error) == expected

    def test_str_with_empty_context(self):
        """Test string representation with explicitly empty context."""
        error = Error(type=ErrorTestType.VALIDATION_ERROR, context={})
        assert str(error) == "Validation failed"

    def test_str_with_complex_context_values(self):
        """Test string representation with complex context values."""
        error = Error(
            type=ErrorTestType.VALIDATION_ERROR,
            context={
                "list": [1, 2, 3],
                "dict": {"nested": "value"},
                "none": None,
                "bool": True,
            },
        )
        result = str(error)
        assert "Validation failed | Context:" in result
        assert "list=[1, 2, 3]" in result
        assert "dict={'nested': 'value'}" in result
        assert "none=None" in result
        assert "bool=True" in result
