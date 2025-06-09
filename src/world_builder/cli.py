import pyperclip  # type: ignore
import typer
from rich import print as pprint
from rich.syntax import Syntax

from world_builder.errors import Err, Ok
from world_builder.prompts import PromptError, PromptErrorType, get_prompt_by_version

app = typer.Typer(
    help="""
        A CLI for instructing and interpreting
        code corrections and suggestions from LLMs.
    """,
)


def _print_prompt_usage_helper(prompt: str):
    pprint(
        "[bold light_pink1]:astonished: Looks like you forgot a command "
        "or are using this CLI for the first time![/bold light_pink1]\n"
    )
    pprint(
        "[italic navajo_white3]:books: Read the [bold]README[/bold] "
        "for more information on how to use this CLI."
        "[bold] Or follow the guide at <insert URL here>[/bold]"
        "[/italic navajo_white3]\n"
    )
    pprint(
        ":white_check_mark: [bold light_steel_blue3]To get started using this tool, "
        "prompt an LLM (of your choosing) with the following:[/bold light_steel_blue3]"
    )

    # Print the prompt in a syntax-highlighted format
    pprint("")
    pprint(Syntax(prompt, "markdown", line_numbers=True))
    pprint("")

    # Copy the prompt to the clipboard
    pyperclip.copy(prompt)

    pprint(
        ":clipboard: [bold italic light_steel_blue3]The prompt has also "
        "been copied to your clipboard! "
        "Paste it into your LLM interface to get started."
        "[/bold italic light_steel_blue3]\n"
    )


def _handle_prompt_error(error: PromptError) -> None:
    """Handle errors related to prompts."""
    match error.type:
        case PromptErrorType.NOT_FOUND:
            print(f"Prompt not found: {error.source}")
        case PromptErrorType.INVALID_VERSION:
            print(f"Invalid version: {error.source}")
        case PromptErrorType.IO_ERROR:
            print(f"File error: {error.source}")
        case _:
            print(f"An unexpected error occurred: {error.source}")

    raise typer.Exit(code=1)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    # If no subcommand is invoked, show the default prompt usage
    if ctx.invoked_subcommand is None:
        # Get the default prompt for version v0.1
        # TODO(SeedyROM): This needs to be based on the libraries latest version
        result = get_prompt_by_version("v0.1")

        # Handle the result of getting the prompt text
        match result:
            case Ok(prompt):
                _print_prompt_usage_helper(prompt)
            case Err(error):
                _handle_prompt_error(error)

        raise typer.Exit()


if __name__ == "__main__":  # pragma: no cover
    app()
