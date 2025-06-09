import typer
from result import Err, Ok

from world_builder.prompts import PromptErrorType, get_prompt_by_version

app = typer.Typer(help="My awesome CLI tool")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """My awesome CLI tool"""
    if ctx.invoked_subcommand is None:
        result = get_prompt_by_version("v0.1")
        match result:
            case Ok(prompt):
                print(f"Loaded prompt: {prompt[:50]}...")
            case Err(error):
                match error.type:
                    case PromptErrorType.NOT_FOUND:
                        print(f"Prompt not found: {error.source}")
                    case PromptErrorType.INVALID_VERSION:
                        print(f"Invalid version: {error.source}")
                    case PromptErrorType.IO_ERROR:
                        print(f"File error: {error.source}")
        raise typer.Exit()


@app.command()
def hello(
    name: str = typer.Argument("World", help="Name to greet"),
    count: int = typer.Option(1, "--count", "-c", help="Number of greetings"),
    polite: bool = typer.Option(False, "--polite", "-p", help="Add please"),
):
    """Say hello to someone"""
    greeting = "Hello"
    if polite:  # pragma: no cover
        greeting = "Hello please"

    for _ in range(count):
        typer.echo(f"{greeting} {name}!")


@app.command()
def goodbye(name: str = typer.Argument("BBQ Squirrel", help="Name to say goodbye to")):
    """Say goodbye to someone"""
    typer.echo(f"Goodbye {name}!")  # pragma: no cover


if __name__ == "__main__":  # pragma: no cover
    app()
