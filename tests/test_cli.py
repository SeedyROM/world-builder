from unittest.mock import Mock, patch

import pytest
import typer
from typer.testing import CliRunner

from world_builder.cli import _handle_prompt_error, _print_prompt_usage_helper, app
from world_builder.errors import Err, Ok
from world_builder.prompts import (
    PromptError,
    PromptErrorType,
)


class TestCLI:
    """Test cases for cli.py to achieve 100% coverage."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("world_builder.cli.get_prompt_by_version")
    @patch("world_builder.cli._print_prompt_usage_helper")
    def test_main_callback_no_subcommand_success(
        self, mock_print_helper, mock_get_prompt
    ):
        """Test main callback when no subcommand is provided and prompt is found."""
        # Mock successful prompt retrieval
        test_prompt = "Test prompt content"
        mock_get_prompt.return_value = Ok(test_prompt)

        # Run the CLI without any command
        result = self.runner.invoke(app, [])

        # Verify the call and exit
        mock_get_prompt.assert_called_once_with()
        mock_print_helper.assert_called_once_with(test_prompt)
        assert result.exit_code == 0

    @patch("world_builder.cli.get_prompt_by_version")
    @patch("world_builder.cli._handle_prompt_error")
    def test_main_callback_no_subcommand_error(
        self, mock_handle_error, mock_get_prompt
    ):
        """
        Test main callback when no subcommand is
        provided and prompt retrieval fails.
        """
        # Mock failed prompt retrieval
        test_error = PromptError(type=PromptErrorType.NOT_FOUND, source="Test error")
        mock_get_prompt.return_value = Err(test_error)

        # Mock the error handler to raise typer.Exit to avoid actual exit
        mock_handle_error.side_effect = typer.Exit(code=1)

        # Run the CLI without any command
        result = self.runner.invoke(app, [])

        # Verify the call and error handling
        mock_get_prompt.assert_called_once_with()
        mock_handle_error.assert_called_once_with(test_error)
        assert result.exit_code == 1

    @patch("world_builder.cli.pyperclip.copy")
    @patch("world_builder.cli.pprint")
    def test_print_prompt_usage_helper(self, mock_pprint, mock_copy):
        """Test the _print_prompt_usage_helper function."""
        test_prompt = "This is a test prompt"

        _print_prompt_usage_helper(test_prompt)

        # Verify that pyperclip.copy was called with the prompt
        mock_copy.assert_called_once_with(test_prompt)

        # Verify that pprint was called multiple times (for different messages)
        assert mock_pprint.call_count >= 5  # Multiple print statements

    def test_handle_prompt_error_not_found(self):
        """Test _handle_prompt_error for NOT_FOUND error type."""
        error = PromptError(type=PromptErrorType.NOT_FOUND, source="test_source")

        with patch("builtins.print") as mock_print:
            with pytest.raises(typer.Exit) as exc_info:
                _handle_prompt_error(error)

            mock_print.assert_called_once_with("Prompt not found: test_source")
            assert exc_info.value.exit_code == 1

    def test_handle_prompt_error_invalid_version(self):
        """Test _handle_prompt_error for INVALID_VERSION error type."""
        error = PromptError(type=PromptErrorType.INVALID_VERSION, source="test_version")

        with patch("builtins.print") as mock_print:
            with pytest.raises(typer.Exit) as exc_info:
                _handle_prompt_error(error)

            mock_print.assert_called_once_with("Invalid version: test_version")
            assert exc_info.value.exit_code == 1

    def test_handle_prompt_error_io_error(self):
        """Test _handle_prompt_error for IO_ERROR error type."""
        error = PromptError(type=PromptErrorType.IO_ERROR, source="file_error")

        with patch("builtins.print") as mock_print:
            with pytest.raises(typer.Exit) as exc_info:
                _handle_prompt_error(error)

            mock_print.assert_called_once_with("File error: file_error")
            assert exc_info.value.exit_code == 1

    def test_handle_prompt_error_unknown_type(self):
        """Test _handle_prompt_error for unknown error type."""
        # Create a mock error with an unknown type
        error = Mock()
        error.type = "UNKNOWN_TYPE"
        error.source = "unknown_error"

        with patch("builtins.print") as mock_print:
            with pytest.raises(typer.Exit) as exc_info:
                _handle_prompt_error(error)

            mock_print.assert_called_once_with(
                "An unexpected error occurred: unknown_error"
            )
            assert exc_info.value.exit_code == 1
