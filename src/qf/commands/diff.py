"""Artifact diff command for comparing versions"""

import json
from difflib import unified_diff
from pathlib import Path
from typing import Any, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from qf.completions import complete_artifact_ids
from qf.utils import find_project_file

console = Console()


def find_artifact(artifact_id: str, status: str = "hot") -> Optional[Path]:
    """Find artifact file by ID and status"""
    workspace = Path(".questfoundry")
    if not workspace.exists():
        return None

    status_path = workspace / status
    if not status_path.exists():
        return None

    # Search in all status subdirectories
    for artifact_dir in status_path.iterdir():
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
                except (json.JSONDecodeError, KeyError, OSError):
                    continue

    return None


def get_artifact_content(
    artifact_id: str, status: str = "hot"
) -> Optional[dict[str, Any]]:
    """Load artifact data"""
    artifact_file = find_artifact(artifact_id, status)
    if not artifact_file:
        return None

    try:
        with open(artifact_file) as f:
            return json.load(f)  # type: ignore
    except (json.JSONDecodeError, OSError):
        return None


def diff_command(
    artifact_id: str = typer.Argument(
        ..., help="Artifact ID", autocompletion=complete_artifact_ids
    ),
    snapshot: Optional[str] = typer.Option(
        None, "--snapshot", help="Compare against snapshot"
    ),
    from_tu: Optional[str] = typer.Option(
        None, "--from", help="Compare from time unit (e.g., tu:1)"
    ),
    to_tu: Optional[str] = typer.Option(
        None, "--to", help="Compare to time unit (e.g., tu:2)"
    ),
) -> None:
    """Compare artifact versions across statuses or snapshots

    Examples:
        qf diff hook-001          # Compare hot vs cold
        qf diff hook-001 --snapshot snap-1  # Compare hot vs snapshot
        qf diff hook-001 --from tu:1 --to tu:2  # Compare between time units
    """
    # Check project exists
    project_file = find_project_file()
    if not project_file:
        console.print("[yellow]No project found in current directory[/yellow]")
        console.print(
            "\n[cyan]Tip:[/cyan] Run [green]qf init[/green] to create a new project"
        )
        raise typer.Exit(1)

    # Get artifact versions
    hot_artifact = get_artifact_content(artifact_id, "hot")
    if not hot_artifact:
        console.print(f"[red]Artifact not found: {artifact_id}[/red]")
        console.print(
            "\n[cyan]Tip:[/cyan] Run [green]qf list[/green] to see available artifacts"
        )
        raise typer.Exit(1)

    # Determine comparison source
    cold_artifact = None
    if snapshot:
        # Load from snapshot
        snapshot_file = Path(".questfoundry") / "snapshots" / f"{snapshot}.json"
        if snapshot_file.exists():
            try:
                with open(snapshot_file) as f:
                    snapshot_data = json.load(f)
                # Extract artifact from snapshot
                cold_artifact = snapshot_data.get("artifacts", {}).get(artifact_id)
            except (json.JSONDecodeError, OSError):
                console.print(f"[red]Could not load snapshot: {snapshot}[/red]")
                raise typer.Exit(1)
    elif from_tu or to_tu:
        # Compare between time units (placeholder for now)
        cold_artifact = get_artifact_content(artifact_id, "cold")
    else:
        # Default: compare hot vs cold
        cold_artifact = get_artifact_content(artifact_id, "cold")

    # Display header
    console.print()
    artifact_type = hot_artifact.get("type", "unknown")
    console.print(
        Panel(
            f"[cyan]Artifact:[/cyan] {artifact_id}\n"
            f"[cyan]Type:[/cyan] {artifact_type}",
            title="[bold]Diff[/bold]",
            border_style="cyan",
        )
    )

    # If no comparison artifact, just show current
    if not cold_artifact:
        console.print("\n[yellow]No previous version found for comparison[/yellow]")
        console.print("\n[bold]Current Version:[/bold]\n")
        syntax = Syntax(
            json.dumps(hot_artifact, indent=2),
            "json",
            theme="monokai",
            line_numbers=True,
        )
        console.print(syntax)
        console.print()
        return

    # Generate diff
    hot_str = json.dumps(hot_artifact, indent=2).splitlines(keepends=True)
    cold_str = json.dumps(cold_artifact, indent=2).splitlines(keepends=True)

    diff_lines = list(
        unified_diff(cold_str, hot_str, fromfile="Cold", tofile="Hot", lineterm="")
    )

    if not diff_lines:
        console.print("\n[green]✓ No differences found[/green]\n")
        return

    # Display diff with coloring and calculate statistics
    console.print("\n[bold]Changes:[/bold]\n")
    added_count = 0
    removed_count = 0
    for line in diff_lines:
        line = line.rstrip("\n")
        if line.startswith("+") and not line.startswith("+++"):
            console.print(f"[green]{line}[/green]")
            added_count += 1
        elif line.startswith("-") and not line.startswith("---"):
            console.print(f"[red]{line}[/red]")
            removed_count += 1
        elif line.startswith("@@"):
            console.print(f"[cyan]{line}[/cyan]")
        else:
            console.print(line)

    console.print()
    stats = f"[green]{added_count} added[/green], [red]{removed_count} removed[/red]"
    console.print(f"[dim]Statistics: {stats}[/dim]")
    console.print()
