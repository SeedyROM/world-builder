from typer.testing import CliRunner

from world_builder.cli import app

runner = CliRunner()


def test_hello_default():
    result = runner.invoke(app, ["hello"])
    assert result.exit_code == 0
    assert "Hello World!" in result.stdout


def test_hello_with_name():
    result = runner.invoke(app, ["hello", "Python"])
    assert result.exit_code == 0
    assert "Hello Python!" in result.stdout


def test_hello_with_count():
    result = runner.invoke(app, ["hello", "Test", "--count", "3"])
    assert result.exit_code == 0
    assert result.stdout.count("Hello Test!") == 3


def test_hello_polite():
    result = runner.invoke(app, ["hello", "Test", "--polite"])
    assert result.exit_code == 0
    assert "Hello please Test!" in result.stdout


def test_goodbye():
    result = runner.invoke(app, ["goodbye", "Python"])
    assert result.exit_code == 0
    assert "Goodbye Python!" in result.stdout


def test_goodbye_default():
    result = runner.invoke(app, ["goodbye"])
    assert result.exit_code == 0
    assert "Goodbye BBQ Squirrel!" in result.stdout


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "My awesome CLI tool" in result.stdout
