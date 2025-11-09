"""Loop execution commands"""

import time
from pathlib import Path

import typer
import yaml
from rich.console import Console
from rich.panel import Panel

from qf.formatting.iterations import (
    display_efficiency_metrics,
    display_full_iteration_history,
)
from qf.formatting.loop_progress import LoopProgressTracker
from qf.formatting.loop_summary import display_loop_summary, suggest_next_loop
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
    console.print("[dim]Demonstrating multi-iteration progress tracking...[/dim]\n")

    # Initialize iteration tracker for multi-iteration support
    progress_tracker = LoopProgressTracker(loop_name=loop_info['display_name'])
    progress_tracker.start_loop()

    # Simulate multi-iteration execution
    # Iteration 1: First pass execution
    progress_tracker.start_iteration(1)

    # Simulate steps in iteration 1
    step1 = progress_tracker.start_step("Context initialization", "Lore Weaver")
    time.sleep(0.2)
    progress_tracker.complete_step(step1)

    step2 = progress_tracker.start_step("Topology analysis", "Plotwright")
    time.sleep(0.3)
    progress_tracker.complete_step(step2)

    step3 = progress_tracker.start_step("Quality validation", "Gatekeeper")
    time.sleep(0.2)
    # Simulate quality gate failure
    progress_tracker.block_step(step3, ["Topology inconsistency detected"])

    progress_tracker.complete_iteration()
    progress_tracker.record_showrunner_decision("Revising topology analysis (Step 2)")

    # Iteration 2: Revision cycle
    progress_tracker.start_iteration(2)

    # Revised step (second-pass)
    step2_revised = progress_tracker.start_step(
        "Topology analysis (revised)", "Plotwright", is_revision=True
    )
    time.sleep(0.25)
    progress_tracker.complete_step(step2_revised)

    # Re-run quality validation
    step3_rerun = progress_tracker.start_step("Quality validation", "Gatekeeper")
    time.sleep(0.2)
    progress_tracker.complete_step(step3_rerun)

    # Mark as stabilized
    progress_tracker.mark_stabilized()
    progress_tracker.complete_iteration()

    # Display iteration history
    display_full_iteration_history(progress_tracker)
    display_efficiency_metrics(progress_tracker)

    # Display summary
    next_action = suggest_next_loop(loop_id)
    display_loop_summary(
        loop_name=loop_info['display_name'],
        loop_abbrev=loop_info['abbrev'],
        duration=progress_tracker.total_duration,
        tu_id=None,  # will be populated when integrated with Layer 6
        artifacts=[],  # will be populated when integrated with Layer 6
        activities=[],
        next_action=next_action,
    )
