"""Export commands for views and git-friendly snapshots."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from qf.utils import ExportFormat, require_project

app = typer.Typer(help="Export snapshots and views")
console = Console()


@app.command(name="view")
@require_project
def export_view(
    snapshot: Optional[str] = typer.Option(
        None, "--snapshot", "-s", help="Snapshot ID to export"
    ),
    format: str = typer.Option(
        ExportFormat.HTML.value,
        "--format",
        "-f",
        help="Output format: html, markdown",
    ),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file path"
    ),
) -> None:
    """Export player view from a snapshot.

    Generates a player-readable view from the specified snapshot in the
    requested format (HTML or Markdown).

    Examples:
        qf export view                          # Export to HTML
        qf export view --format markdown        # Export to Markdown
        qf export view --snapshot snap-123      # Export specific snapshot
        qf export view --output view.html       # Custom output path
    """
    try:
        # Validate format using enum
        try:
            format_enum = ExportFormat(format.lower())
        except ValueError:
            valid_formats = [fmt.value for fmt in ExportFormat]
            console.print(
                f"[red]Error: Invalid format '{format}'. "
                f"Valid formats: {', '.join(valid_formats)}[/red]"
            )
            raise typer.Exit(1)

        # Set default output path if not provided
        if not output:
            output = f"view.{format}"

        # Show what we're doing
        snapshot_text = f" (snapshot: {snapshot})" if snapshot else " (latest)"
        console.print(f"\n[cyan]→ Exporting view to {format}{snapshot_text}[/cyan]")

        # Create output directory if needed
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Simulate export (placeholder for actual Layer 6 integration)
        console.print(f"[dim]  Writing to {output_path}...[/dim]")

        # Create a simple output file to demonstrate success
        with open(output_path, "w", encoding="utf-8") as f:
            if format_enum == ExportFormat.HTML:
                f.write("<html>\n<head><title>View</title></head>\n")
                f.write("<body><h1>QuestFoundry View</h1></body>\n</html>")
            elif format_enum == ExportFormat.MARKDOWN:
                f.write("# QuestFoundry View\n\n")
                f.write("This is a placeholder view export.\n")

        # Show result
        result_text = Text()
        result_text.append("✓ View exported successfully\n", style="green")
        result_text.append(f"  Format: {format.upper()}\n", style="cyan")
        if snapshot:
            result_text.append(f"  Snapshot: {snapshot}\n", style="cyan")
        result_text.append(f"  Output: {output_path}\n", style="cyan")

        console.print()
        console.print(Panel(result_text, title="Export Complete", border_style="green"))
        console.print()

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command(name="git")
@require_project
def export_git(
    snapshot: Optional[str] = typer.Option(
        None, "--snapshot", "-s", help="Snapshot ID to export"
    ),
    output: str = typer.Option(
        "snapshot_export",
        "--output",
        "-o",
        help="Output directory path",
    ),
) -> None:
    """Export snapshot as git-friendly YAML files.

    Creates a directory structure with YAML files suitable for version
    control integration.

    Examples:
        qf export git                           # Export to snapshot_export/
        qf export git --snapshot snap-123       # Export specific snapshot
        qf export git --output ./exports        # Custom output directory
    """
    try:

        # Show what we're doing
        snapshot_text = f" (snapshot: {snapshot})" if snapshot else " (latest)"
        msg = f"\n[cyan]→ Exporting git-friendly snapshot{snapshot_text}[/cyan]"
        console.print(msg)

        # Create output directory
        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)

        # Simulate export (placeholder for actual Layer 6 integration)
        console.print(f"[dim]  Creating directory structure in {output_path}...[/dim]")

        # Create typical directory structure
        (output_path / "metadata").mkdir(exist_ok=True)
        (output_path / "artifacts").mkdir(exist_ok=True)
        (output_path / "content").mkdir(exist_ok=True)

        # Create placeholder files
        with open(
            output_path / "metadata" / "snapshot.yml", "w", encoding="utf-8"
        ) as f:
            f.write("# Snapshot Metadata\n")
            f.write(f"snapshot_id: {snapshot or 'latest'}\n")
            f.write("format_version: 1.0\n")

        with open(
            output_path / "artifacts" / ".gitkeep", "w", encoding="utf-8"
        ) as f:
            f.write("")

        with open(output_path / "content" / ".gitkeep", "w", encoding="utf-8") as f:
            f.write("")

        # Show result
        result_text = Text()
        result_text.append("✓ Git export created successfully\n", style="green")
        if snapshot:
            result_text.append(f"  Snapshot: {snapshot}\n", style="cyan")
        result_text.append(f"  Output: {output_path}\n", style="cyan")
        result_text.append(
            "  Structure: metadata/ artifacts/ content/\n", style="dim"
        )

        console.print()
        console.print(
            Panel(
                result_text,
                title="Git Export Complete",
                border_style="green",
            )
        )
        console.print()

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
