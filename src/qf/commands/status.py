"""Project status command"""

import json
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.table import Table

console = Console()


def find_project_file() -> Path | None:
    """Find .qfproj file in current directory"""
    project_files = list(Path.cwd().glob("*.qfproj"))
    if project_files:
        return project_files[0]
    return None


def load_project_metadata(project_file: Path) -> Any:
    """Load project metadata from .qfproj file"""
    with open(project_file) as f:
        return json.load(f)


def status_command() -> None:
    """Show current project status"""

    # Find project file
    project_file = find_project_file()

    if not project_file:
        console.print("[yellow]No project found in current directory[/yellow]")
        console.print(
            "\n[cyan]Tip:[/cyan] Run [green]qf init[/green] to create a new project"
        )
        raise typer.Exit(1)

    try:
        # Load project metadata
        metadata = load_project_metadata(project_file)

        # Display project info
        console.print("\n[bold cyan]Project Information[/bold cyan]\n")

        info_table = Table(show_header=False, box=None, padding=(0, 2))
        info_table.add_column("Key", style="cyan")
        info_table.add_column("Value", style="white")

        info_table.add_row("Project", metadata.get("name", "Unknown"))
        info_table.add_row("Description", metadata.get("description", "N/A"))
        info_table.add_row("Version", metadata.get("version", "0.1.0"))
        info_table.add_row("Project File", str(project_file))

        console.print(info_table)

        # Check workspace
        workspace = Path(".questfoundry")
        if workspace.exists():
            console.print("\n[bold cyan]Workspace Status[/bold cyan]\n")

            ws_table = Table(show_header=False, box=None, padding=(0, 2))
            ws_table.add_column("Component", style="cyan")
            ws_table.add_column("Status", style="white")

            ws_table.add_row("Hot workspace", "✓ Initialized")
            ws_table.add_row("Config", "✓ Present")

            # Check for artifacts (when Layer 6 is ready)
            hot_hooks = workspace / "hot" / "hooks"
            hot_canon = workspace / "hot" / "canon"

            if hot_hooks.exists():
                hook_count = len(list(hot_hooks.glob("*.json")))
                ws_table.add_row("Hooks", f"{hook_count} items")

            if hot_canon.exists():
                canon_count = len(list(hot_canon.glob("*.json")))
                ws_table.add_row("Canon", f"{canon_count} items")

            console.print(ws_table)
        else:
            console.print(
                "\n[yellow]Warning: .questfoundry workspace not found[/yellow]"
            )
            console.print("[cyan]Tip:[/cyan] The project may need to be re-initialized")

        # Future sections (placeholder for Layer 6 integration)
        console.print(
            "\n[dim]Note: Active roles, pending artifacts, and TU history "
            "will be available once Layer 6 integration is complete.[/dim]\n"
        )

    except json.JSONDecodeError:
        console.print(f"[red]Error: Invalid project file: {project_file}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error reading project: {e}[/red]")
        raise typer.Exit(1)
