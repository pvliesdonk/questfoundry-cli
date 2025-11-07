"""Artifact listing command"""

import json
from pathlib import Path
from typing import Optional

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


def list_artifacts(
    artifact_type: Optional[str] = typer.Argument(None, help="Artifact type to list"),
    status: Optional[str] = typer.Option(
        None, "--status", "-s", help="Filter by status"
    ),
) -> None:
    """List artifacts in the current project"""

    # Find project
    project_file = find_project_file()
    if not project_file:
        console.print("[yellow]No project found in current directory[/yellow]")
        console.print(
            "\n[cyan]Tip:[/cyan] Run [green]qf init[/green] to create a new project"
        )
        raise typer.Exit(1)

    workspace = Path(".questfoundry")
    if not workspace.exists():
        console.print("[red]Error: Workspace not found[/red]")
        raise typer.Exit(1)

    # Determine which artifact types to list
    if artifact_type:
        types_to_list = [artifact_type]
    else:
        types_to_list = ["hooks", "canon", "codex", "tus", "artifacts"]

    # Display artifacts
    for atype in types_to_list:
        hot_path = workspace / "hot" / atype

        if not hot_path.exists():
            if artifact_type:  # Only show error if specific type requested
                console.print(f"[yellow]No {atype} found in workspace[/yellow]")
            continue

        # Get all JSON files
        artifact_files = list(hot_path.glob("*.json"))

        if not artifact_files:
            if artifact_type:
                console.print(f"[yellow]No {atype} found[/yellow]")
            continue

        # Create table
        table = Table(title=f"{atype.title()} Artifacts")
        table.add_column("ID", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("File", style="dim")

        for artifact_file in sorted(artifact_files):
            try:
                with open(artifact_file) as f:
                    data = json.load(f)

                # Extract fields (structure will vary by artifact type)
                artifact_id = data.get("id", artifact_file.stem)
                artifact_status = data.get("status", "unknown")
                artifact_subtype = data.get("type", atype)

                # Apply status filter
                if status and artifact_status != status:
                    continue

                table.add_row(
                    artifact_id,
                    artifact_subtype,
                    artifact_status,
                    artifact_file.name,
                )
            except (json.JSONDecodeError, KeyError):
                # Skip invalid files
                continue

        if table.row_count > 0:
            console.print()
            console.print(table)

    # If no artifacts at all
    if not any((workspace / "hot" / t).exists() for t in types_to_list):
        console.print("\n[dim]No artifacts in workspace yet.[/dim]")
        console.print(
            "[dim]Artifacts will appear here once you start working with loops.[/dim]\n"
        )
