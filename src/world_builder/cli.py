import typer

from world_builder.errors import Err, Ok
from world_builder.prompts import PromptErrorType, get_prompt_by_version

app = typer.Typer(
    help="""
        A CLI for instructing and interpreting
        code corrections and suggestions from LLMs.
    """,
)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        result = get_prompt_by_version("v0.1")
        match result:
            case Ok(prompt):
                print(f"Loaded prompt: {prompt[:128]}...")
            case Err(error):
                match error.type:
                    case PromptErrorType.NOT_FOUND:
                        print(f"Prompt not found: {error.source}")
                    case PromptErrorType.INVALID_VERSION:
                        print(f"Invalid version: {error.source}")
                    case PromptErrorType.IO_ERROR:
                        print(f"File error: {error.source}")
        raise typer.Exit()


if __name__ == "__main__":  # pragma: no cover
    app()
