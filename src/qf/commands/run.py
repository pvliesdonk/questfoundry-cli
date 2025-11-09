"""Loop execution commands"""

import time
from pathlib import Path

import typer
import yaml
from rich.console import Console
from rich.panel import Panel

from qf.formatting.loop_summary import display_loop_summary, suggest_next_loop
from qf.formatting.progress import ActivityTracker
from qf.utils import WORKSPACE_DIR, find_project_file

console = Console()


def _load_loops() -> dict[str, dict[str, str]]:
    """Load loop definitions from YAML configuration file."""
    loops_file = Path(__file__).parent.parent / "data" / "loops.yml"
    with open(loops_file, "r") as f:
        loops = yaml.safe_load(f)
        return loops if loops is not None else {}


# All 13 loops from Layer 2 spec (02-dictionary/loop_names.md)
LOOPS = _load_loops()


def validate_loop_name(loop_name: str) -> str:
    """
    Validate and normalize loop name.

    Args:
        loop_name: Loop name to validate (kebab-case or display name)

    Returns:
        Normalized kebab-case loop name

    Raises:
        typer.Exit: If loop name is invalid
    """
    # normalize to lowercase and replace spaces with hyphens
    normalized = loop_name.lower().strip().replace(" ", "-")

    # check if it's a valid loop name
    if normalized in LOOPS:
        return normalized

    # check if it matches any display name (case-insensitive)
    for loop_id, loop_info in LOOPS.items():
        display_name = str(loop_info["display_name"])
        if display_name.lower() == loop_name.lower():
            return loop_id

    # invalid loop name
    console.print(f"[red]Error: Unknown loop '{loop_name}'[/red]")
    console.print("\n[cyan]Available loops:[/cyan]")
    for loop_id, loop_info in LOOPS.items():
        console.print(
            f"  • {loop_info['display_name']} ({loop_id}) - {loop_info['description']}"
        )
    raise typer.Exit(1)


def run(
    loop_name: str = typer.Argument(..., help="Loop name to execute"),
    interactive: bool = typer.Option(
        False, "--interactive", "-i", help="Enable interactive mode (coming soon)"
    ),
) -> None:
    """Execute a loop"""
    # check if in a project
    project_file = find_project_file()
    if not project_file:
        console.print("[yellow]No project found in current directory[/yellow]")
        console.print(
            "\n[cyan]Tip:[/cyan] Run [green]qf init[/green] to create a new project"
        )
        raise typer.Exit(1)

    # validate loop name
    loop_id = validate_loop_name(loop_name)
    loop_info = LOOPS[loop_id]

    # check workspace exists
    workspace = Path(WORKSPACE_DIR)
    if not workspace.exists():
        console.print("[red]Error: Workspace not found[/red]")
        raise typer.Exit(1)

    # show warning for interactive mode
    if interactive:
        console.print(
            "[yellow]Note: Interactive mode will be available "
            "in a future release.[/yellow]\n"
        )

    # execute loop with progress tracking
    console.print(
        Panel(
            f"[bold cyan]{loop_info['display_name']}[/bold cyan]\n"
            f"[dim]{loop_info['description']}[/dim]",
            title=f"Loop Execution - {loop_info['abbrev']}",
            border_style="cyan",
        )
    )

    console.print(
        "\n[yellow]Note: Full loop execution will integrate with questfoundry-py "
        "Showrunner in a future release.[/yellow]"
    )
    console.print("[dim]Demonstrating progress tracking and summary display...[/dim]\n")

    # placeholder execution with progress tracking
    tracker = ActivityTracker(loop_info['display_name'])

    # simulate loop activities
    tracker.start_activity("Initializing loop context")
    time.sleep(0.5)
    tracker.complete_activity()

    tracker.start_activity("Loading project configuration")
    time.sleep(0.3)
    tracker.complete_activity()

    tracker.start_activity("Validating workspace")
    time.sleep(0.2)
    tracker.complete_activity()

    tracker.start_activity(f"Executing {loop_info['display_name']}")
    time.sleep(0.5)
    tracker.complete_activity()

    # display summary
    next_action = suggest_next_loop(loop_id)
    display_loop_summary(
        loop_name=loop_info['display_name'],
        loop_abbrev=loop_info['abbrev'],
        duration=tracker.get_duration(),
        tu_id=None,  # will be populated when integrated with Layer 6
        artifacts=[],  # will be populated when integrated with Layer 6
        activities=tracker.activities,
        next_action=next_action,
    )
