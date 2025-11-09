"""Loop execution summary formatting"""

from datetime import datetime
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

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
        created_time = datetime.now().strftime('%Y-%m-%d %H:%M')
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
        Suggested next loop display name, or None
    """
    # common workflow progressions
    sequences = {
        "story-spark": "Hook Harvest",
        "hook-harvest": "Lore Deepening",
        "lore-deepening": "Codex Expansion",
        "codex-expansion": "Style Tune-up",
        "style-tuneup": "Art Touch-up or Audio Pass",
        "art-touchup": "Binding Run",
        "audio-pass": "Binding Run",
        "translation-pass": "Binding Run",
        "binding-run": "Narration Dry-Run",
        "narration-dry-run": "Gatecheck",
        "gatecheck": "Post-Mortem",
        "post-mortem": "Archive Snapshot",
    }

    next_loop = sequences.get(current_loop)
    if next_loop:
        return f"Run [green]qf run {next_loop.lower().replace(' ', '-')}[/green]"
    return None
