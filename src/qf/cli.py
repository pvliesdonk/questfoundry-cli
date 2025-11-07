"""Main CLI application"""

import typer

from .commands import artifact, config, provider, schema, validate
from .commands.history import history_command
from .commands.init import init_command
from .commands.list import list_artifacts
from .commands.show import show_artifact
from .commands.status import status_command
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
app.add_typer(config.app, name="config", help="Manage project configuration")
app.add_typer(provider.app, name="provider", help="Manage AI providers")

# Add project commands
app.command(name="init", help="Initialize a new project")(init_command)
app.command(name="status", help="Show project status")(status_command)
app.command(name="list", help="List artifacts")(list_artifacts)
app.command(name="show", help="Show artifact details")(show_artifact)
app.command(name="history", help="Show project history")(history_command)


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
