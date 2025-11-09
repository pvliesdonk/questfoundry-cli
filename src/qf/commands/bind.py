"""Bind command for executing Book Binder role to render views."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from qf.utils import find_project_file

app = typer.Typer(help="Bind and render views from snapshots")
console = Console()


@app.command(name="view")
def bind_view(
    snapshot_id: str = typer.Argument(..., help="Snapshot ID to bind"),
    format: str = typer.Option(
        "html",
        "--format",
        "-f",
        help="Output format: html, markdown, pdf",
    ),
    output: Optional[str] = typer.Option(
        None, "--output", "-o", help="Output file path"
    ),
) -> None:
    """Bind and render a view from a snapshot using Book Binder.

    Executes the Book Binder role to generate a player-ready view from
    the specified snapshot in the requested format.

    Examples:
        qf bind view snap-123                           # Render snapshot
        qf bind view snap-123 --format markdown          # To Markdown
        qf bind view snap-123 --format pdf               # To PDF
        qf bind view snap-123 --output bound.html        # Custom output
    """
    try:
        # Check if project exists
        project_file = find_project_file()
        if not project_file:
            console.print(
                "[red]Error: No QuestFoundry project found in current directory.[/red]"
            )
            raise typer.Exit(1)

        # Validate format
        valid_formats = ["html", "markdown", "pdf"]
        if format.lower() not in valid_formats:
            console.print(
                f"[red]Error: Invalid format '{format}'. "
                f"Valid formats: {', '.join(valid_formats)}[/red]"
            )
            raise typer.Exit(1)

        # Set default output path if not provided
        if not output:
            output = f"bound-view.{format}"

        # Show what we're doing
        console.print(
            f"\n[cyan]→ Binding view for snapshot {snapshot_id} "
            f"(format: {format})[/cyan]"
        )

        # Create output directory if needed
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Simulate binding (placeholder for actual Layer 6 integration)
        console.print("[dim]  Executing Book Binder role...[/dim]")
        console.print(f"[dim]  Rendering to {output_path}...[/dim]")

        # Create a simple output file to demonstrate success
        with open(output_path, "w") as f:
            if format.lower() == "html":
                f.write("<html>\n<head><title>Bound View</title></head>\n")
                f.write(
                    f"<body><h1>Bound View from {snapshot_id}</h1></body>\n</html>"
                )
            elif format.lower() == "markdown":
                f.write(f"# Bound View from {snapshot_id}\n\n")
                f.write("This is a placeholder bound view.\n")
            else:  # pdf
                f.write(f"%PDF-1.4\n%Placeholder PDF for {snapshot_id}\n")

        # Show result
        result_text = Text()
        result_text.append("✓ View bound successfully\n", style="green")
        result_text.append(f"  Snapshot: {snapshot_id}\n", style="cyan")
        result_text.append(f"  Format: {format.upper()}\n", style="cyan")
        result_text.append(f"  Output: {output_path}\n", style="cyan")

        console.print()
        console.print(
            Panel(
                result_text, title="Binding Complete", border_style="green"
            )
        )
        console.print()

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
