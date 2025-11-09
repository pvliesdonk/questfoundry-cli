"""Loop execution summary formatting"""

from datetime import datetime
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from qf.formatting.loop_progress import LoopProgressTracker

console = Console()


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string like "2m 34s" or "45s"
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)

    if minutes > 0:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def create_artifact_table(artifacts: list[dict[str, Any]]) -> Table:
    """
    Create a Rich table for displaying created/modified artifacts.

    Args:
        artifacts: List of artifact dictionaries with id, type, action keys

    Returns:
        Rich Table object
    """
    table = Table(title="Artifacts", show_header=True, header_style="bold cyan")
    table.add_column("ID", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Action", style="green")

    for artifact in artifacts:
        action_color = "green" if artifact["action"] == "created" else "yellow"
        table.add_row(
            artifact["id"],
            artifact["type"],
            f"[{action_color}]{artifact['action']}[/{action_color}]",
        )

    return table


def display_loop_summary(
    loop_name: str,
    loop_abbrev: str,
    duration: float,
    tu_id: str | None = None,
    artifacts: list[dict[str, Any]] | None = None,
    activities: list[dict[str, Any]] | None = None,
    next_action: str | None = None,
    created_at: datetime | None = None,
) -> None:
    """
    Display comprehensive loop execution summary.

    Args:
        loop_name: Display name of the loop
        loop_abbrev: Loop abbreviation (e.g., "HH")
        duration: Total execution time in seconds
        tu_id: Transaction Unit ID created (if any)
        artifacts: List of artifacts created/modified
        activities: List of activities performed
        next_action: Suggested next step
        created_at: Timestamp when the loop was created (defaults to now)
    """
    # header panel
    header_text = Text()
    header_text.append(f"{loop_name}", style="bold cyan")
    header_text.append(f" ({loop_abbrev})", style="dim")
    header_text.append(f"\nCompleted in {format_duration(duration)}", style="green")

    console.print()
    console.print(
        Panel(header_text, title="Loop Execution Summary", border_style="cyan")
    )

    # TU information (if created)
    if tu_id:
        console.print()
        tu_panel = Text()
        tu_panel.append("Transaction Unit: ", style="bold")
        tu_panel.append(tu_id, style="cyan")
        timestamp = created_at if created_at else datetime.now()
        created_time = timestamp.strftime('%Y-%m-%d %H:%M')
        tu_panel.append(f"\nCreated: {created_time}", style="dim")
        console.print(Panel(tu_panel, title="TU Brief", border_style="cyan"))

    # artifacts table
    if artifacts:
        console.print()
        console.print(create_artifact_table(artifacts))

    # activities tree (if available)
    if activities:
        console.print()
        tree = Tree("[bold]Activities[/bold]")
        for activity in activities:
            status = activity.get("status", "completed")
            duration_text = ""
            if activity.get("end") and activity.get("start"):
                dur = activity["end"] - activity["start"]
                duration_text = f" ({dur:.1f}s)"

            if status == "completed":
                icon = "✓"
                color = "green"
            elif status == "running":
                icon = "→"
                color = "yellow"
            else:
                icon = "⚠"
                color = "yellow"

            tree.add(f"[{color}]{icon} {activity['activity']}{duration_text}[/{color}]")

        console.print(tree)

    # next action suggestion
    if next_action:
        console.print()
        console.print(
            Panel(
                f"[bold]Suggested next step:[/bold]\n{next_action}",
                title="Next Action",
                border_style="yellow",
            )
        )

    console.print()


def display_quick_summary(
    loop_name: str, duration: float, artifacts_count: int
) -> None:
    """
    Display a quick one-line summary.

    Args:
        loop_name: Display name of the loop
        duration: Total execution time in seconds
        artifacts_count: Number of artifacts created/modified
    """
    console.print(
        f"\n[green]✓[/green] {loop_name} completed in {format_duration(duration)} "
        f"({artifacts_count} artifacts)\n"
    )


def suggest_next_loop(current_loop: str) -> str | None:
    """
    Suggest the next logical loop based on current loop.

    Args:
        current_loop: Current loop name (kebab-case)

    Returns:
        Suggested next loop command, or None
    """
    # common workflow progressions (using kebab-case)
    # values can be either a string or a list of strings for multiple options
    sequences: dict[str, str | list[str]] = {
        "story-spark": "hook-harvest",
        "hook-harvest": "lore-deepening",
        "lore-deepening": "codex-expansion",
        "codex-expansion": "style-tuneup",
        "style-tuneup": ["art-touchup", "audio-pass"],
        "art-touchup": "binding-run",
        "audio-pass": "binding-run",
        "translation-pass": "binding-run",
        "binding-run": "narration-dry-run",
        "narration-dry-run": "gatecheck",
        "gatecheck": "post-mortem",
        "post-mortem": "archive-snapshot",
    }

    next_loop = sequences.get(current_loop)
    if next_loop:
        if isinstance(next_loop, list):
            # Multiple options
            formatted = [f"[green]qf run {loop}[/green]" for loop in next_loop]
            options = " or ".join(formatted)
            return f"Run {options}"
        else:
            # Single option
            return f"Run [green]qf run {next_loop}[/green]"
    return None


def display_iteration_summary_panel(tracker: LoopProgressTracker) -> None:
    """
    Display iteration summary for multi-iteration loops.

    Shows iteration count, step revisions, and stabilization status.

    Args:
        tracker: LoopProgressTracker with execution data
    """
    if not tracker.is_multi_iteration:
        return

    text = Text()
    text.append("Iterations: ", style="bold cyan")
    text.append(f"{len(tracker.iterations)}", style="cyan")

    total_steps = sum(len(i.steps) for i in tracker.iterations)
    revised_steps = sum(i.revised_steps for i in tracker.iterations)

    text.append(f"\nTotal steps: {total_steps}", style="cyan")

    if revised_steps > 0:
        revision_pct = (revised_steps / total_steps * 100) if total_steps > 0 else 0
        text.append(
            f"\nRevisions: {revised_steps} ({revision_pct:.0f}%)", style="yellow"
        )

    text.append("\n")
    if tracker.stabilized:
        text.append("Status: ", style="bold")
        text.append("Stabilized", style="green")
    else:
        text.append("Status: ", style="bold")
        text.append("In Progress", style="yellow")

    console.print()
    console.print(Panel(text, title="Iteration Summary", border_style="cyan"))


def display_revision_details(tracker: LoopProgressTracker) -> None:
    """
    Display detailed revision information for multi-iteration loops.

    Shows which steps were revised in each iteration.

    Args:
        tracker: LoopProgressTracker with execution data
    """
    if not tracker.is_multi_iteration or len(tracker.iterations) < 2:
        return

    tree = Tree("[bold]Revisions by Iteration[/bold]")

    for iteration in tracker.iterations:
        if iteration.revised_steps > 0:
            iter_node = tree.add(
                f"[cyan]Iteration {iteration.iteration_number}[/cyan]"
            )
            revised_count = iteration.revised_steps
            iter_node.add(f"[yellow]{revised_count} steps revised[/yellow]")

            # Show revised step names
            for step in iteration.steps:
                if step.is_revision:
                    iter_node.add(f"  • {step.name}")

    console.print()
    console.print(tree)
