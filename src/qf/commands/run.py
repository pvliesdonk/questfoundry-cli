"""Loop execution commands"""

import time
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel

from qf.utils import find_project_file

app = typer.Typer(help="Execute loops")
console = Console()

# All 13 loops from Layer 2 spec (02-dictionary/loop_names.md)
LOOPS = {
    # Discovery loops
    "story-spark": {
        "display_name": "Story Spark",
        "abbrev": "SS",
        "category": "Discovery",
        "description": "Generate initial story concepts and hooks",
    },
    "hook-harvest": {
        "display_name": "Hook Harvest",
        "abbrev": "HH",
        "category": "Discovery",
        "description": "Generate and collect story hooks",
    },
    "lore-deepening": {
        "display_name": "Lore Deepening",
        "abbrev": "LD",
        "category": "Discovery",
        "description": "Expand and deepen world lore",
    },
    # Refinement loops
    "codex-expansion": {
        "display_name": "Codex Expansion",
        "abbrev": "CE",
        "category": "Refinement",
        "description": "Expand codex entries with detail",
    },
    "style-tuneup": {
        "display_name": "Style Tune-up",
        "abbrev": "ST",
        "category": "Refinement",
        "description": "Polish and align content style",
    },
    # Asset loops
    "art-touchup": {
        "display_name": "Art Touch-up",
        "abbrev": "AT",
        "category": "Asset",
        "description": "Generate and refine artwork",
    },
    "audio-pass": {
        "display_name": "Audio Pass",
        "abbrev": "AP",
        "category": "Asset",
        "description": "Generate audio assets",
    },
    "translation-pass": {
        "display_name": "Translation Pass",
        "abbrev": "TP",
        "category": "Asset",
        "description": "Translate content to other languages",
    },
    # Export loops
    "binding-run": {
        "display_name": "Binding Run",
        "abbrev": "BR",
        "category": "Export",
        "description": "Generate player-facing views",
    },
    "narration-dry-run": {
        "display_name": "Narration Dry-Run",
        "abbrev": "NDR",
        "category": "Export",
        "description": "Test narration flow",
    },
    "gatecheck": {
        "display_name": "Gatecheck",
        "abbrev": "GC",
        "category": "Export",
        "description": "Run quality checks",
    },
    "post-mortem": {
        "display_name": "Post-Mortem",
        "abbrev": "PM",
        "category": "Export",
        "description": "Analyze and document project outcomes",
    },
    "archive-snapshot": {
        "display_name": "Archive Snapshot",
        "abbrev": "AS",
        "category": "Export",
        "description": "Create project snapshot for archiving",
    },
}


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
        if loop_info["display_name"].lower() == loop_name.lower():
            return loop_id

    # invalid loop name
    console.print(f"[red]Error: Unknown loop '{loop_name}'[/red]")
    console.print("\n[cyan]Available loops:[/cyan]")
    for loop_id, loop_info in LOOPS.items():
        console.print(
            f"  • {loop_info['display_name']} ({loop_id}) - {loop_info['description']}"
        )
    raise typer.Exit(1)


@app.command()
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
    workspace = Path(".questfoundry")
    if not workspace.exists():
        console.print("[red]Error: Workspace not found[/red]")
        raise typer.Exit(1)

    # show warning for interactive mode
    if interactive:
        console.print(
            "[yellow]Note: Interactive mode will be available "
            "in a future release.[/yellow]\n"
        )

    # execute loop (placeholder - will integrate with Layer 6 Showrunner)
    console.print(
        Panel(
            f"[bold cyan]{loop_info['display_name']}[/bold cyan]\n"
            f"[dim]{loop_info['description']}[/dim]",
            title=f"Loop Execution - {loop_info['abbrev']}",
            border_style="cyan",
        )
    )

    console.print(
        "\n[yellow]Note: Loop execution will integrate with questfoundry-py "
        "Showrunner in a future release.[/yellow]"
    )
    console.print("\n[dim]For now, this command validates loop configuration.[/dim]\n")

    # placeholder execution (will be replaced with actual showrunner call)
    console.print("[green]✓ Loop configuration validated[/green]")
    console.print(f"[green]✓ Workspace ready for {loop_info['display_name']}[/green]")
