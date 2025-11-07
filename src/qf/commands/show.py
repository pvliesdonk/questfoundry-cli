"""Artifact inspection command"""

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from qf.utils import find_project_file

console = Console()


def find_artifact(artifact_id: str) -> Path | None:
    """Find artifact file by ID"""
    workspace = Path(".questfoundry")
    if not workspace.exists():
        return None

    # Search in all hot workspace subdirectories
    hot_path = workspace / "hot"
    if not hot_path.exists():
        return None

    for artifact_dir in hot_path.iterdir():
        if artifact_dir.is_dir():
            # Try exact match
            artifact_file = artifact_dir / f"{artifact_id}.json"
            if artifact_file.exists():
                return artifact_file

            # Try matching by ID in file content
            for json_file in artifact_dir.glob("*.json"):
                try:
                    with open(json_file) as f:
                        data = json.load(f)
                    if data.get("id") == artifact_id:
                        return json_file
                except (json.JSONDecodeError, KeyError):
                    continue

    return None


def show_artifact(artifact_id: str = typer.Argument(..., help="Artifact ID")) -> None:
    """Show detailed artifact information"""

    # Find project
    project_file = find_project_file()
    if not project_file:
        console.print("[yellow]No project found in current directory[/yellow]")
        console.print(
            "\n[cyan]Tip:[/cyan] Run [green]qf init[/green] to create a new project"
        )
        raise typer.Exit(1)

    # Find artifact
    artifact_file = find_artifact(artifact_id)
    if not artifact_file:
        console.print(f"[red]Artifact not found: {artifact_id}[/red]")
        console.print(
            "\n[cyan]Tip:[/cyan] Run [green]qf list[/green] to see available artifacts"
        )
        raise typer.Exit(1)

    try:
        # Load artifact
        with open(artifact_file) as f:
            data = json.load(f)

        # Display header
        console.print()
        artifact_type = data.get("type", "Unknown")
        artifact_status = data.get("status", "unknown")

        console.print(
            Panel(
                f"[cyan]Type:[/cyan] {artifact_type}\n"
                f"[cyan]Status:[/cyan] {artifact_status}\n"
                f"[cyan]File:[/cyan] {artifact_file}",
                title=f"[bold]{artifact_id}[/bold]",
                border_style="cyan",
            )
        )

        # Display full JSON
        console.print("\n[bold]Artifact Data:[/bold]\n")
        syntax = Syntax(
            json.dumps(data, indent=2),
            "json",
            theme="monokai",
            line_numbers=True,
        )
        console.print(syntax)
        console.print()

    except json.JSONDecodeError:
        console.print(f"[red]Error: Invalid JSON in {artifact_file}[/red]")
        raise typer.Exit(1)
    except (OSError, PermissionError) as e:
        # File not found, permission denied, or other I/O errors
        console.print(f"[red]Error reading artifact: {e}[/red]")
        raise typer.Exit(1)
