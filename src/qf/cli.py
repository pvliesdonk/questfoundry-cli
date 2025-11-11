"""Main CLI application"""

import sys
import typer

from .commands import artifact, check, config, generate, provider, run, schema, validate
from .commands.bind import app as bind_app
from .commands.diff import diff_command
from .commands.export import app as export_app
from .commands.history import history_command
from .commands.init import init_command
from .commands.list import list_artifacts
from .commands.quickstart import quickstart
from .commands.search import search_command
from .commands.shell import shell_command
from .commands.show import show_artifact
from .commands.status import status_command
from .logging_config import setup_logging
from .utils.formatting import print_header, print_success
from .version import get_version

# Check for verbose flag early and setup logging
_verbose = "--verbose" in sys.argv or "-v" in sys.argv
setup_logging(verbose=_verbose)

app = typer.Typer(
    name="qf",
    help="QuestFoundry command-line interface",
    no_args_is_help=True,
    add_completion=True,
)

# Add command groups
app.add_typer(schema.app, name="schema", help="Manage schemas")
app.add_typer(validate.app, name="validate", help="Validate artifacts and envelopes")
app.add_typer(artifact.app, name="artifact", help="Work with artifacts")
app.add_typer(config.app, name="config", help="Manage project configuration")
app.add_typer(provider.app, name="provider", help="Manage AI providers")
app.add_typer(check.app, name="check", help="Run quality checks")
app.add_typer(generate.app, name="generate", help="Generate assets from artifacts")
app.add_typer(export_app, name="export", help="Export snapshots and views")
app.add_typer(bind_app, name="bind", help="Bind and render views from snapshots")

# Add project commands
app.command(name="init", help="Initialize a new project")(init_command)
app.command(name="status", help="Show project status")(status_command)
app.command(name="list", help="List artifacts")(list_artifacts)
app.command(name="show", help="Show artifact details")(show_artifact)
app.command(name="history", help="Show project history")(history_command)
app.command(name="quickstart", help="Start guided quickstart workflow")(quickstart)
app.command(name="run", help="Execute a loop")(run.run)
app.command(name="diff", help="Compare artifact versions")(diff_command)
app.command(name="search", help="Search artifacts")(search_command)
app.command(name="shell", help="Start interactive shell")(shell_command)


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
