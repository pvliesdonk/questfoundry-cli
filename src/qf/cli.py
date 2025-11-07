"""Main CLI application"""

import typer

from .commands import artifact, schema, validate
from .utils.formatting import print_header, print_success
from .version import get_version

app = typer.Typer(
    name="qf",
    help="QuestFoundry command-line interface",
    no_args_is_help=True,
)

# Add command groups
app.add_typer(schema.app, name="schema", help="Manage schemas")
app.add_typer(validate.app, name="validate", help="Validate artifacts and envelopes")
app.add_typer(artifact.app, name="artifact", help="Work with artifacts")


@app.command()
def version() -> None:
    """Show version"""
    print_success(f"questfoundry-cli v{get_version()}")


@app.command()
def info() -> None:
    """Show QuestFoundry information"""
    print_header("QuestFoundry")
    typer.echo("Layer 7: Command-Line Interface")
    typer.echo(f"Version: {get_version()}")
    typer.echo("Documentation: https://github.com/pvliesdonk/questfoundry-spec")


if __name__ == "__main__":
    app()
