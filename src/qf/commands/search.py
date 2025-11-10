"""Full-text search command for artifacts"""

import json
import re
from pathlib import Path
from typing import Any, Optional

import typer
from rich.console import Console
from rich.table import Table

from qf.utils import find_project_file

console = Console()


def search_artifacts(
    query: str,
    artifact_type: Optional[str] = None,
    field: Optional[str] = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """Search artifacts by query, type, and field"""
    results: list[dict[str, Any]] = []
    workspace = Path(".questfoundry")

    if not workspace.exists():
        return results

    # Escape query to treat special regex characters as literals
    escaped_query = re.escape(query)

    # Search in hot and cold
    for status in ["hot", "cold"]:
        status_path = workspace / status
        if not status_path.exists():
            continue

        for artifact_dir in status_path.iterdir():
            if not artifact_dir.is_dir():
                continue

            for json_file in artifact_dir.glob("*.json"):
                try:
                    with open(json_file) as f:
                        artifact = json.load(f)

                    # Filter by artifact type field if specified
                    if (
                        artifact_type
                        and artifact.get("type", "").lower() != artifact_type.lower()
                    ):
                        continue

                    # Search in specified field or all fields
                    if field:
                        content = str(artifact.get(field, ""))
                        if re.search(escaped_query, content, re.IGNORECASE):
                            results.append(artifact)
                    else:
                        # Search in all fields
                        artifact_str = json.dumps(artifact)
                        if re.search(escaped_query, artifact_str, re.IGNORECASE):
                            results.append(artifact)

                except (json.JSONDecodeError, OSError):
                    continue

    # Remove duplicates (keep first occurrence)
    seen_ids: set[Any] = set()
    unique_results: list[dict[str, Any]] = []
    for result in results:
        artifact_id = result.get("id")
        # Skip if no ID or if ID already seen
        if artifact_id is None or artifact_id in seen_ids:
            continue
        seen_ids.add(artifact_id)
        unique_results.append(result)

    return unique_results[:limit]


def search_command(
    query: str = typer.Argument(..., help="Search query"),
    type_filter: Optional[str] = typer.Option(
        None, "--type", help="Filter by artifact type (e.g., hooks, loops)"
    ),
    field: Optional[str] = typer.Option(
        None, "--field", help="Search in specific field (e.g., title, content)"
    ),
    limit: int = typer.Option(50, "--limit", help="Maximum results to return"),
) -> None:
    """Search artifacts by full-text query

    Examples:
        qf search "dragon"
        qf search "important" --field title
        qf search "test" --type hooks
        qf search "story" --limit 10
    """
    # Check project exists
    project_file = find_project_file()
    if not project_file:
        console.print("[yellow]No project found in current directory[/yellow]")
        console.print(
            "\n[cyan]Tip:[/cyan] Run [green]qf init[/green] to create a new project"
        )
        raise typer.Exit(1)

    # Perform search
    results = search_artifacts(
        query, artifact_type=type_filter, field=field, limit=limit
    )

    if not results:
        console.print(f"\n[yellow]No results found for: {query}[/yellow]\n")
        return

    # Display results in table
    console.print()
    table = Table(title=f"Search Results: {query}")
    table.add_column("ID", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Title", style="green")
    table.add_column("Status", style="yellow")

    for artifact in results:
        artifact_id = artifact.get("id", "unknown")
        artifact_type = artifact.get("type", "unknown")
        title = artifact.get("title", "")
        status = artifact.get("status", "unknown")

        # Truncate title first (before adding markup)
        if len(title) > 50:
            title = title[:47] + "..."

        # Highlight matches in title (case-insensitive)
        if query.lower() in title.lower():
            # Use case-insensitive regex replacement
            title = re.sub(
                re.escape(query), f"[bold]{query}[/bold]", title, flags=re.IGNORECASE
            )

        table.add_row(artifact_id, artifact_type, title, status)

    console.print(table)

    # Show summary
    summary = f"\n[dim]Found {len(results)} result"
    if len(results) != 1:
        summary += "s"
    if len(results) == limit:
        summary += f" (showing first {limit})"
    summary += "[/dim]\n"
    console.print(summary)
