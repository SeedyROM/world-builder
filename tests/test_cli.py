import pytest
from typer.testing import CliRunner

from world_builder.cli import app


class TestCLI:
    """Test suite for the CLI application."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_hello_default(self):
        result = self.runner.invoke(app, ["hello"])
        assert result.exit_code == 0
        assert "Hello World!" in result.stdout

    def test_hello_with_name(self):
        result = self.runner.invoke(app, ["hello", "Python"])
        assert result.exit_code == 0
        assert "Hello Python!" in result.stdout

    def test_hello_with_count(self):
        result = self.runner.invoke(app, ["hello", "Test", "--count", "3"])
        assert result.exit_code == 0
        assert result.stdout.count("Hello Test!") == 3

    def test_hello_polite(self):
        result = self.runner.invoke(app, ["hello", "Test", "--polite"])
        assert result.exit_code == 0
        assert "Hello please Test!" in result.stdout

    def test_goodbye(self):
        result = self.runner.invoke(app, ["goodbye", "Python"])
        assert result.exit_code == 0
        assert "Goodbye Python!" in result.stdout

    def test_goodbye_default(self):
        result = self.runner.invoke(app, ["goodbye"])
        assert result.exit_code == 0
        assert "Goodbye BBQ Squirrel!" in result.stdout

    def test_help(self):
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "My awesome CLI tool" in result.stdout


class TestHelloCommand:
    """Focused tests for the hello command."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.runner = CliRunner()

    @pytest.mark.parametrize(
        "name,expected",
        [
            ("World", "Hello World!"),
            ("Python", "Hello Python!"),
            ("Test", "Hello Test!"),
        ],
    )
    def test_hello_with_different_names(self, name, expected):
        result = self.runner.invoke(app, ["hello", name])
        assert result.exit_code == 0
        assert expected in result.stdout

    @pytest.mark.parametrize("count", [1, 2, 3, 5])
    def test_hello_with_different_counts(self, count):
        result = self.runner.invoke(app, ["hello", "Test", "--count", str(count)])
        assert result.exit_code == 0
        assert result.stdout.count("Hello Test!") == count


class TestGoodbyeCommand:
    """Focused tests for the goodbye command."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.runner = CliRunner()

    def test_goodbye_with_name(self):
        result = self.runner.invoke(app, ["goodbye", "Python"])
        assert result.exit_code == 0
        assert "Goodbye Python!" in result.stdout

    def test_goodbye_default(self):
        result = self.runner.invoke(app, ["goodbye"])
        assert result.exit_code == 0
        assert "Goodbye BBQ Squirrel!" in result.stdout
