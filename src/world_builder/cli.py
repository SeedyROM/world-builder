import typer

app = typer.Typer(help="My awesome CLI tool")


@app.command()
def hello(
    name: str = typer.Argument("World", help="Name to greet"),
    count: int = typer.Option(1, "--count", "-c", help="Number of greetings"),
    polite: bool = typer.Option(False, "--polite", "-p", help="Add please"),
):
    """Say hello to someone"""
    greeting = "Hello"
    if polite:
        greeting = "Hello please"

    for _ in range(count):
        typer.echo(f"{greeting} {name}!")


@app.command()
def goodbye(name: str = typer.Argument("World")):
    """Say goodbye to someone"""
    typer.echo(f"Goodbye {name}!")


if __name__ == "__main__":  # pragma: no cover
    app()
